import re
from difflib import SequenceMatcher

from modules.smalltalk_module import process as process_smalltalk
from modules.quiz_module import process as process_quiz
from modules.price_module import process as process_price
from modules.course_module import process as process_course
from modules.ai_module import process as process_ai
from services.rag_service import ask_rag


# ------------------------------------------------------------
# Settings
# ------------------------------------------------------------

NOT_FOUND_TEXT = "couldn't find that information"

# Words that mean the user refers to something said earlier
PRONOUNS = {
    "it", "its", "this", "that", "these", "those",
    "they", "them", "their", "he", "she", "him", "her"
}

# Questions that are clearly about the platform, not the book.
PLATFORM_KEYWORDS = [
    "price", "cost", "fee", "fees", "trainer", "teacher", "tutor",
    "instructor", "duration", "enroll", "enrol", "certificate",
    "package", "how long", "how much", "rating",
    "course detail", "course details", "details of the course",
    "about the course", "this course", "its course", "the course"
]

# Words that mean the question is about many courses, not one
GENERAL_WORDS = {
    "all", "every", "list", "cheapest", "compare", "comparison",
    "which", "available", "courses", "packages", "between"
}

# Phrases like "from book" are removed before searching,
# because they say nothing about the topic.
FILLER_PHRASES = [
    "according to the book", "according to book",
    "from the book", "from book", "in the book", "in book",
    "from the document", "from the documents", "from notes",
    "what does the book say about", "what does the book say",
    "what does the document say about", "what does the document say",
    "yes", "please", "i want to know about", "explain"
]

# Words ignored when matching course names
GENERIC_NAME_WORDS = {
    "course", "courses", "basics", "basic", "introduction",
    "intro", "to", "the", "and", "of", "in", "for", "a"
}


# ------------------------------------------------------------
# Text helpers
# ------------------------------------------------------------

def _words(text):
    return set(re.findall(r"[a-z']+", text.lower()))


def _has_pronoun(text):
    return bool(_words(text) & PRONOUNS)


def _clean(text):
    """Remove filler phrases so only the topic remains."""
    cleaned = text.lower()
    for phrase in FILLER_PHRASES:
        cleaned = cleaned.replace(phrase, " ")
    return re.sub(r"\s+", " ", cleaned).strip(" ?.!,")


def _recent_user_questions(history, current_question, limit=4):
    """Last few user messages, excluding the current one."""
    if not history:
        return []

    user_messages = [
        item["message"]
        for item in history
        if item.get("role") == "user"
    ]

    # History may already contain the current question as its last item
    if user_messages and user_messages[-1].strip() == current_question.strip():
        user_messages = user_messages[:-1]

    return user_messages[-limit:]


def _is_not_found(response):
    return NOT_FOUND_TEXT in str(response).lower()


# ------------------------------------------------------------
# Book follow-up helper
# ------------------------------------------------------------

def build_search_question(question, history):
    """
    Turn a vague follow-up ("its types from book") into a
    standalone search query ("machine learning its types").
    Only used for retrieval; the user's original question is
    still what gets answered.
    """

    cleaned = _clean(question) or question

    if not _has_pronoun(question):
        return cleaned

    for previous in reversed(_recent_user_questions(history, question)):

        if not _has_pronoun(previous):
            topic = _clean(previous)
            print(f"→ Follow-up detected. Using topic: '{topic}'")
            return f"{topic} {cleaned}".strip()

    return cleaned


def resolve_followup(question, history):
    """
    Attach the earlier topic to a pronoun question so the course
    and price modules can find the right course.
    """

    if not _has_pronoun(question):
        return question

    for previous in reversed(_recent_user_questions(history, question)):

        if not _has_pronoun(previous):
            topic = _clean(previous)
            print(f"→ Course follow-up. Attaching topic: '{topic}'")
            return f"{question} (about {topic})"

    return question


# ------------------------------------------------------------
# Course finding (typo tolerant)
# ------------------------------------------------------------

def _squash(text):
    return re.sub(r"[^a-z0-9]", "", text.lower())


def _core_name(name):
    """'Machine Learning Basics' -> 'machinelearning'"""
    words = re.findall(r"[a-z0-9]+", name.lower())
    core = [w for w in words if w not in GENERIC_NAME_WORDS]
    return "".join(core or words)


def _match_score(core, squashed):
    """Best similarity of `core` against any part of `squashed`."""

    if len(core) < 3 or not squashed:
        return 0.0

    if core in squashed:
        return 1.0

    best = 0.0
    n = len(core)

    for size in (n - 1, n, n + 1):

        if size < 3 or size > len(squashed):
            continue

        for i in range(len(squashed) - size + 1):
            score = SequenceMatcher(
                None, core, squashed[i:i + size]
            ).ratio()
            best = max(best, score)

    return best


def find_courses(text, courses, threshold=0.85):
    """All courses mentioned in `text`, allowing typos."""

    squashed = _squash(text)
    found = []

    for course in courses or []:

        core = _core_name(course.get("course_name", ""))
        score = _match_score(core, squashed)

        if score >= threshold:
            found.append((score, course))

    found.sort(key=lambda item: item[0], reverse=True)

    return [course for _, course in found]


def find_course_in_context(question, history, courses):
    """
    Course named in the question, else the course from the most
    recent earlier message that named one.
    Returns (course, from_history) or (None, False).
    """

    in_question = find_courses(question, courses)

    if len(in_question) == 1:
        return in_question[0], False

    if len(in_question) > 1:
        return None, False      # comparison, let course module handle it

    for previous in reversed(_recent_user_questions(history, question)):

        matches = find_courses(previous, courses)

        if matches:
            print(f"→ Course from earlier message: "
                  f"{matches[0].get('course_name')}")
            return matches[0], True

    return None, False


# ------------------------------------------------------------
# Direct platform answers
# ------------------------------------------------------------

def answer_platform_question(course, question_lower):
    """Answer trainer / price / duration / rating from course data."""

    words = _words(question_lower)
    rows = []

    if words & {"trainer", "teacher", "tutor", "instructor"}:
        rows.append(("Trainer", course.get("trainer")))

    if words & {"duration"} or "how long" in question_lower:
        rows.append(("Duration", course.get("duration")))

    if words & {"price", "cost", "fee", "fees"} or "how much" in question_lower:
        rows.append(("Price", course.get("course_price")))

    if "rating" in words:
        rows.append(("Rating", course.get("rating")))

    # Nothing specific asked ("course details") -> show everything
    if not rows:
        rows = [
            ("Trainer", course.get("trainer")),
            ("Duration", course.get("duration")),
            ("Price", course.get("course_price")),
            ("Rating", course.get("rating")),
            ("Package", course.get("package_name")),
        ]

    html = f"<h3>{course.get('course_name')}</h3>\n"

    for label, value in rows:
        if value not in (None, ""):
            html += f"<p><b>{label}:</b> {value}</p>\n"

    return html


def ask_which_course(courses):
    names = [c.get("course_name") for c in courses or [] if c.get("course_name")]

    if not names:
        return "Which course do you mean? Please mention the course name."

    listed = "\n".join(f"<li>{name}</li>" for name in names)

    return (
        "<p>Which course do you mean? Available courses:</p>\n"
        f"<ul>\n{listed}\n</ul>"
    )


# ------------------------------------------------------------
# Router
# ------------------------------------------------------------

def route(question, tokens, courses, history=None):

    print("\n========== ROUTER ==========")
    print("Question:", question)

    question_lower = question.lower()

    # ============================================================
    # 1. SMALLTALK
    # ============================================================

    print("Checking Smalltalk...")

    response = process_smalltalk(question)

    if response:
        print("Answered by Smalltalk")
        return response

    # ============================================================
    # 2. QUIZ
    # ============================================================

    print("Checking Quiz...")

    response = process_quiz(question, tokens)

    if response:
        print("Answered by Quiz")
        return response

    # ============================================================
    # 3. PLATFORM QUESTION ABOUT ONE COURSE
    #    (trainer / price / duration / rating / details)
    # ============================================================

    is_platform_question = any(
        keyword in question_lower for keyword in PLATFORM_KEYWORDS
    )

    is_general_question = bool(_words(question_lower) & GENERAL_WORDS)

    if is_platform_question and not is_general_question:

        course, from_history = find_course_in_context(
            question, history, courses
        )

        if course:
            print("Answered by COURSE (direct):", course.get("course_name"))
            return answer_platform_question(course, question_lower)

    # ============================================================
    # 4. BOOK FIRST (RAG, documents only)
    # ============================================================

    if not is_platform_question:

        print("Checking BOOK (RAG)...")

        search_question = build_search_question(question, history)
        print("Search query:", search_question)

        response = ask_rag(
            question,
            search_question=search_question,
            source="rag_document"      # book chunks only
        )

        if response and not _is_not_found(response):
            print("Answered by BOOK")
            return response

        print("→ Not found in book, checking other sources...")

    # ============================================================
    # 5. COURSE MODULE (fallback + general course questions)
    # ============================================================

    course_question = resolve_followup(question, history)

    print("Checking Course...")

    response = process_course(course_question, courses)

    if response:
        print("Answered by Course")
        return response

    # ============================================================
    # 6. PRICE MODULE (fallback + general price questions)
    # ============================================================

    print("Checking Price...")

    response = process_price(course_question, tokens)

    if response:
        print("Answered by Price")
        return response

    # ============================================================
    # 7. PLATFORM QUESTION BUT NO COURSE FOUND -> ask, don't guess
    # ============================================================

    if is_platform_question:
        print("→ Platform question, no course identified")
        return ask_which_course(courses)

    # ============================================================
    # 8. AI (last resort)
    # ============================================================

    print("Answered by AI")

    return process_ai(question)