from rapidfuzz import fuzz
from memory.conversation_memory import memory
import re


# ============================================================
# COURSE MODULE
# ============================================================
#
# Responsibilities:
#
# 1. Identify explicitly mentioned courses
# 2. Recognize course abbreviations such as:
#       ML, AI, CS, DS
# 3. Detect course intent
# 4. Answer course-specific questions
# 5. Remember explicitly mentioned courses
# 6. Handle follow-up questions
# 7. Compare courses
#
# IMPORTANT:
#
# Course identification and intent detection are SEPARATE.
#
# RapidFuzz is ONLY used as a fallback for course identification.
# ============================================================


print("\n========================================")
print("COURSE MODULE LOADED")
print("========================================")


# ============================================================
# 1. HELPER FUNCTIONS
# ============================================================


def normalize_text(text):
    """
    Normalize text for safer matching.
    """

    if not text:
        return ""

    text = str(text).lower().strip()

    # Replace punctuation with spaces
    text = re.sub(r"[^a-z0-9\s]", " ", text)

    # Remove duplicate spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


def duration_to_months(duration):
    """
    Convert common duration formats into months.
    """

    if duration is None:
        return 0

    duration = str(duration).lower().strip()

    match = re.search(
        r"(\d+(?:\.\d+)?)",
        duration
    )

    if not match:
        return 0

    number = float(match.group(1))

    if "year" in duration:
        return number * 12

    if "month" in duration:
        return number

    if "week" in duration:
        return number / 4

    if "day" in duration:
        return number / 30

    return number


def course_link(course):
    """
    Generate course details URL.
    """

    return (
        f"http://127.0.0.1:8000/"
        f"course-details/{course['id']}"
    )


# ============================================================
# 2. COURSE ALIASES
# ============================================================


COURSE_ALIASES = {

    "machine learning": [
        "ml",
        "machine learning",
        "machine learning basics",
    ],

    "computer science": [
        "cs",
        "computer science",
        "computer science basics",
    ],

    "artificial intelligence": [
        "ai",
        "artificial intelligence",
    ],

    "data science": [
        "ds",
        "data science",
    ],

    "deep learning": [
        "dl",
        "deep learning",
    ],

    "web development": [
        "web",
        "web development",
    ],

    "cyber security": [
        "cyber security",
        "cybersecurity",
        "cs security",
    ],

    "networking": [
        "networking",
        "network",
    ],

    "digital marketing": [
        "digital marketing",
        "marketing",
    ],
}


def get_course_aliases(course):
    """
    Return aliases applicable to a database course.
    """

    course_name = normalize_text(
        course.get("course_name", "")
    )

    aliases = [course_name]

    for key, values in COURSE_ALIASES.items():

        if key in course_name:

            aliases.extend(values)

    return list(set(aliases))


# ============================================================
# 3. COURSE ANSWER FUNCTIONS
# ============================================================


def full_course_details(course):

    return f"""
<h3>🎯 Course Found</h3>

<ul>

<li>
<b>Course:</b>
{course['course_name']}
</li>

<li>
<b>Description:</b>
{course.get('course_description', 'N/A')}
</li>

<li>
<b>Trainer:</b>
{course.get('trainer', 'N/A')}
</li>

<li>
<b>Price:</b>
${float(course['course_price']):.2f}
</li>

<li>
<b>Duration:</b>
{course.get('duration', 'N/A')}
</li>

<li>
<a href="{course_link(course)}" target="_blank">
🔗 View Course
</a>
</li>

</ul>
"""


def course_description(course):

    return f"""
<h3>📚 About {course['course_name']}</h3>

<p>
{course.get(
    'course_description',
    'No description available.'
)}
</p>
"""


def course_price(course):

    return f"""
<h3>💰 Course Price</h3>

<p>
<b>{course['course_name']}</b>
costs
<b>${float(course['course_price']):.2f}</b>.
</p>
"""


def course_trainer(course):

    return f"""
<h3>👨‍🏫 Trainer</h3>

<p>
<b>{course['course_name']}</b>
is taught by
<b>{course.get('trainer', 'N/A')}</b>.
</p>
"""


def course_duration(course):

    return f"""
<h3>⏱️ Course Duration</h3>

<p>
<b>{course['course_name']}</b>
takes
<b>{course.get('duration', 'N/A')}</b>.
</p>
"""


def course_learning_content(course):

    description = course.get(
        "course_description"
    )

    if not description:

        return f"""
<h3>📖 What You Learn</h3>

<p>
I don't have detailed curriculum information
for <b>{course['course_name']}</b> yet.
</p>
"""

    return f"""
<h3>📖 What You Learn</h3>

<p>
The <b>{course['course_name']}</b> course covers:
</p>

<p>
{description}
</p>
"""


# ============================================================
# 4. INTENT KEYWORDS
# ============================================================


TRAINER_KEYWORDS = [

    "trainer",
    "teacher",
    "mentor",
    "instructor",

    "who teaches",
    "who teach",
    "who taught",

    "who is the teacher",
    "who is the trainer",
    "who is the instructor",
    "who is the mentor",

]


PRICE_KEYWORDS = [

    "price",
    "cost",
    "fee",
    "fees",
    "charge",
    "charges",

    "how much",
    "how much does",
    "how much is",

    "pay",
    "payment",

]


DURATION_KEYWORDS = [

    "duration",
    "how long",
    "length",

    "how many months",
    "how many weeks",
    "how many days",

    "how much time",
    "take",

]


CONTENT_PHRASES = [

    "what does",
    "what will i learn",
    "what do i learn",
    "what can i learn",

    "what is taught",
    "what does it teach",
    "what does the course teach",
    "what does this course teach",

    "what will this course teach",

    "course teaches",

    "what topics",
    "topics",
    "content",
    "covered",
    "what is covered",

    "skills",
    "learning",
    "curriculum",
    "syllabus",

    "what will i study",
    "what do i study",
    "what can i study",

    "learn",
]


DESCRIPTION_PHRASES = [

    "about",
    "description",
    "explain",
    "explain it",
    "information",

    "tell me about",
    "tell me more",
    "more about it",
    "about it",
    "about the course",

]


FULL_DETAILS_PHRASES = [

    "full details",
    "complete details",
    "all details",
    "course details",
    "everything about",
    "all information",

]


# ============================================================
# 5. PHRASE MATCHING
# ============================================================


def contains_phrase(question, phrases):

    question = normalize_text(question)

    return any(
        phrase in question
        for phrase in phrases
    )


# ============================================================
# 6. INTENT DETECTION
# ============================================================


def detect_course_intent(question):

    question = normalize_text(question)

    print(
        "→ Intent detection question:",
        question
    )


    # ========================================================
    # TRAINER
    # ========================================================

    if contains_phrase(
        question,
        TRAINER_KEYWORDS
    ):

        print(
            "→ Intent matched: TRAINER"
        )

        return "trainer"


    # ========================================================
    # PRICE
    # ========================================================

    if contains_phrase(
        question,
        PRICE_KEYWORDS
    ):

        print(
            "→ Intent matched: PRICE"
        )

        return "price"


    # ========================================================
    # DURATION
    # ========================================================

    if contains_phrase(
        question,
        DURATION_KEYWORDS
    ):

        print(
            "→ Intent matched: DURATION"
        )

        return "duration"


    # ========================================================
    # CONTENT
    # ========================================================

    if contains_phrase(
        question,
        CONTENT_PHRASES
    ):

        print(
            "→ Intent matched: CONTENT"
        )

        return "content"


    # ========================================================
    # FULL DETAILS
    # ========================================================

    if contains_phrase(
        question,
        FULL_DETAILS_PHRASES
    ):

        print(
            "→ Intent matched: FULL_DETAILS"
        )

        return "full_details"


    # ========================================================
    # DESCRIPTION
    # ========================================================

    if contains_phrase(
        question,
        DESCRIPTION_PHRASES
    ):

        print(
            "→ Intent matched: DESCRIPTION"
        )

        return "description"


    print(
        "→ No course intent detected"
    )

    return None


# ============================================================
# 7. ANSWER COURSE INTENT
# ============================================================


def answer_course_intent(course, intent):

    if intent == "trainer":
        return course_trainer(course)

    if intent == "price":
        return course_price(course)

    if intent == "duration":
        return course_duration(course)

    if intent == "content":
        return course_learning_content(course)

    if intent == "description":
        return course_description(course)

    if intent == "full_details":
        return full_course_details(course)

    return None


# ============================================================
# 8. FIND EXPLICIT COURSE
# ============================================================


def find_course(question, courses):

    question_normalized = normalize_text(
        question
    )


    # ========================================================
    # STEP 1 — EXACT COURSE NAME / ALIAS
    # ========================================================

    for course in courses:

        aliases = get_course_aliases(
            course
        )

        for alias in aliases:

            alias = normalize_text(alias)

            if not alias:
                continue


            # ------------------------------------------------
            # Word-boundary matching for short aliases
            # ------------------------------------------------

            if len(alias) <= 3:

                pattern = (
                    r"\b"
                    + re.escape(alias)
                    + r"\b"
                )

                if re.search(
                    pattern,
                    question_normalized
                ):

                    print(
                        f"→ Alias matched: {alias} "
                        f"-> {course['course_name']}"
                    )

                    return course, 100


            else:

                if alias in question_normalized:

                    print(
                        f"→ Course matched: {alias} "
                        f"-> {course['course_name']}"
                    )

                    return course, 100


    # ========================================================
    # STEP 2 — FUZZY FALLBACK
    # ========================================================

    best_match = None
    max_score = 0

    for course in courses:

        course_name = normalize_text(
            course.get(
                "course_name",
                ""
            )
        )

        if not course_name:
            continue


        score = fuzz.partial_ratio(
            course_name,
            question_normalized
        )


        if score > max_score:

            max_score = score
            best_match = course


    # ========================================================
    # CONFIDENCE THRESHOLD
    # ========================================================

    if (
        best_match
        and max_score >= 85
    ):

        print(
            "→ Fuzzy course match:",
            best_match["course_name"]
        )

        print(
            "→ Fuzzy score:",
            max_score
        )

        return best_match, max_score


    return None, max_score


# ============================================================
# 9. FIND MULTIPLE EXPLICIT COURSES
# ============================================================


def find_courses(question, courses):
    """
    Find ALL explicitly mentioned courses.

    Used mainly for comparisons.

    Example:

        "Compare CS and ML"

    returns:

        [
            Computer Science Basics,
            Machine Learning Basics
        ]

    IMPORTANT:
    This uses the SAME alias system as find_course().
    """

    question_normalized = normalize_text(
        question
    )

    found_courses = []
    found_ids = set()


    for course in courses:

        aliases = get_course_aliases(
            course
        )

        matched = False


        for alias in aliases:

            alias = normalize_text(alias)

            if not alias:
                continue


            # ------------------------------------------------
            # Short aliases
            # ------------------------------------------------

            if len(alias) <= 3:

                pattern = (
                    r"\b"
                    + re.escape(alias)
                    + r"\b"
                )

                if re.search(
                    pattern,
                    question_normalized
                ):

                    matched = True
                    break


            # ------------------------------------------------
            # Normal aliases
            # ------------------------------------------------

            else:

                if alias in question_normalized:

                    matched = True
                    break


        if matched:

            course_id = course.get("id")

            if course_id not in found_ids:

                found_courses.append(course)
                found_ids.add(course_id)


    print(
        "→ Multiple courses found:",
        [
            c["course_name"]
            for c in found_courses
        ]
    )

    return found_courses


# ============================================================
# 10. COMPARISON DETECTOR
# ============================================================


def is_comparison_question(question):

    question_lower = normalize_text(
        question
    )


    comparison_phrases = [

        "compare",
        "comparison",

        "compare them",
        "compare these",
        "compare both",
        "compare the courses",

        "difference between",
        "differences between",

        "versus",

        "which one is cheaper",
        "which is cheaper",

        "which one is more expensive",
        "which is more expensive",

        "which one is longer",
        "which is longer",

        "which one is shorter",
        "which is shorter",

    ]


    # Normal phrase matching
    for phrase in comparison_phrases:

        if phrase in question_lower:

            return True


    # --------------------------------------------------------
    # Handle "vs" safely
    #
    # normalize_text("CS vs ML")
    #
    # becomes:
    #
    # "cs vs ml"
    #
    # We use word boundaries so "vs" is not matched
    # inside another word.
    # --------------------------------------------------------

    if re.search(
        r"\bvs\b",
        question_lower
    ):

        return True


    return False


# ============================================================
# 11. COMPARISON FUNCTIONS
# ============================================================


def compare_cheaper(course1, course2):

    price1 = float(
        course1["course_price"]
    )

    price2 = float(
        course2["course_price"]
    )


    if price1 == price2:

        return f"""
<h3>💰 Price Comparison</h3>

<p>
Both courses have the same price:
<b>${price1:.2f}</b>.
</p>
"""


    cheaper = (
        course1
        if price1 < price2
        else course2
    )


    return f"""
<h3>💰 Cheapest Course</h3>

<p>
<b>{cheaper['course_name']}</b>
is the cheaper course.
</p>

<ul>

<li>
{course1['course_name']}:
<b>${price1:.2f}</b>
</li>

<li>
{course2['course_name']}:
<b>${price2:.2f}</b>
</li>

</ul>
"""


def compare_expensive(course1, course2):

    price1 = float(
        course1["course_price"]
    )

    price2 = float(
        course2["course_price"]
    )


    if price1 == price2:

        return """
<h3>💵 Price Comparison</h3>

<p>
Both courses have the same price.
</p>
"""


    expensive = (
        course1
        if price1 > price2
        else course2
    )


    return f"""
<h3>💵 Most Expensive Course</h3>

<p>
<b>{expensive['course_name']}</b>
is more expensive.
</p>

<ul>

<li>
{course1['course_name']}:
<b>${price1:.2f}</b>
</li>

<li>
{course2['course_name']}:
<b>${price2:.2f}</b>
</li>

</ul>
"""


def compare_longer(course1, course2):

    duration1 = duration_to_months(
        course1.get("duration")
    )

    duration2 = duration_to_months(
        course2.get("duration")
    )


    if duration1 == duration2:

        return """
<h3>⏱️ Duration Comparison</h3>

<p>
Both courses have the same duration.
</p>
"""


    longer = (
        course1
        if duration1 > duration2
        else course2
    )


    return f"""
<h3>⏱️ Longer Course</h3>

<p>
<b>{longer['course_name']}</b>
is the longer course.
</p>

<ul>

<li>
{course1['course_name']}:
<b>{course1.get('duration', 'N/A')}</b>
</li>

<li>
{course2['course_name']}:
<b>{course2.get('duration', 'N/A')}</b>
</li>

</ul>
"""


def compare_shorter(course1, course2):

    duration1 = duration_to_months(
        course1.get("duration")
    )

    duration2 = duration_to_months(
        course2.get("duration")
    )


    if duration1 == duration2:

        return """
<h3>⏱️ Duration Comparison</h3>

<p>
Both courses have the same duration.
</p>
"""


    shorter = (
        course1
        if duration1 < duration2
        else course2
    )


    return f"""
<h3>⏱️ Shorter Course</h3>

<p>
<b>{shorter['course_name']}</b>
is the shorter course.
</p>

<ul>

<li>
{course1['course_name']}:
<b>{course1.get('duration', 'N/A')}</b>
</li>

<li>
{course2['course_name']}:
<b>{course2.get('duration', 'N/A')}</b>
</li>

</ul>
"""


def compare_general(course1, course2):

    return f"""
<h3>⚖️ Course Comparison</h3>

<table border="1" cellpadding="8">

<tr>
<th>Feature</th>
<th>{course1['course_name']}</th>
<th>{course2['course_name']}</th>
</tr>

<tr>
<td>💰 Price</td>
<td>${float(course1['course_price']):.2f}</td>
<td>${float(course2['course_price']):.2f}</td>
</tr>

<tr>
<td>⏱️ Duration</td>
<td>{course1.get('duration', 'N/A')}</td>
<td>{course2.get('duration', 'N/A')}</td>
</tr>

<tr>
<td>👨‍🏫 Trainer</td>
<td>{course1.get('trainer', 'N/A')}</td>
<td>{course2.get('trainer', 'N/A')}</td>
</tr>

<tr>
<td>📦 Package</td>
<td>{course1.get('package_name', 'N/A')}</td>
<td>{course2.get('package_name', 'N/A')}</td>
</tr>

</table>
"""


# ============================================================
# 12. COMPARISON HANDLER
# ============================================================


def handle_comparison(
    question,
    recent_courses,
    courses=None
):

    question_lower = normalize_text(
        question
    )


    # ========================================================
    # STEP 1
    # TRY TO FIND EXPLICIT COURSES
    # ========================================================

    explicit_courses = []

    if courses:

        explicit_courses = find_courses(
            question,
            courses
        )


    # ========================================================
    # STEP 2
    # USE EXPLICIT COURSES IF TWO FOUND
    # ========================================================

    if len(explicit_courses) >= 2:

        course1 = explicit_courses[0]
        course2 = explicit_courses[1]

        print(
            "→ Comparison courses found explicitly:"
        )

        print(
            "  1.",
            course1["course_name"]
        )

        print(
            "  2.",
            course2["course_name"]
        )


    # ========================================================
    # STEP 3
    # OTHERWISE USE RECENT MEMORY
    # ========================================================

    elif len(recent_courses) >= 2:

        course1 = recent_courses[-2]
        course2 = recent_courses[-1]

        print(
            "→ Using recent courses for comparison:"
        )

        print(
            "  1.",
            course1["course_name"]
        )

        print(
            "  2.",
            course2["course_name"]
        )


    else:

        print(
            "→ Not enough courses for comparison."
        )

        return None


    # ========================================================
    # CHEAPER
    # ========================================================

    if any(
        phrase in question_lower
        for phrase in [

            "cheaper",
            "cheapest",
            "less expensive",
            "lower price",
            "lowest price",
            "cost less",
            "least expensive",
            "which one costs less",
            "which costs less",

        ]
    ):

        return compare_cheaper(
            course1,
            course2
        )


    # ========================================================
    # MORE EXPENSIVE
    # ========================================================

    if any(
        phrase in question_lower
        for phrase in [

            "more expensive",
            "most expensive",
            "higher price",
            "highest price",
            "cost more",
            "most costly",

        ]
    ):

        return compare_expensive(
            course1,
            course2
        )


    # ========================================================
    # LONGER
    # ========================================================

    if any(
        phrase in question_lower
        for phrase in [

            "longer",
            "longest",
            "which takes longer",
            "which one takes longer",

        ]
    ):

        return compare_longer(
            course1,
            course2
        )


    # ========================================================
    # SHORTER
    # ========================================================

    if any(
        phrase in question_lower
        for phrase in [

            "shorter",
            "shortest",
            "which takes less time",
            "which one takes less time",

        ]
    ):

        return compare_shorter(
            course1,
            course2
        )


    # ========================================================
    # GENERAL COMPARISON
    # ========================================================

    if is_comparison_question(question):

        return compare_general(
            course1,
            course2
        )


    return None


# ============================================================
# 13. MEMORY FOLLOW-UP
# ============================================================


def is_course_followup(question):

    question_lower = normalize_text(
        question
    )


    reference_phrases = [

        "it",
        "its",
        "this course",
        "that course",
        "the course",
        "this",
        "that",

    ]


    course_phrases = [

        "price",
        "cost",
        "fee",
        "fees",

        "duration",
        "how long",

        "trainer",
        "teacher",
        "instructor",
        "mentor",

        "topics",
        "topic",
        "content",
        "curriculum",
        "syllabus",

        "what will i learn",
        "what do i learn",
        "what can i learn",

        "skills",
        "what is taught",
        "what does it teach",

        "suitable for beginners",
        "beginner",

        "prerequisite",
        "prerequisites",

    ]


    has_reference = any(
        phrase in question_lower
        for phrase in reference_phrases
    )


    has_course_topic = any(
        phrase in question_lower
        for phrase in course_phrases
    )


    if (
        has_reference
        and has_course_topic
    ):

        return True


    standalone_course_questions = [

        "who teaches",
        "who is the trainer",
        "who is the teacher",

        "how much does it cost",
        "how much is it",

        "how long does it take",

        "what topics are covered",

        "what will i learn",
        "what do i learn",

        "what skills will i learn",

        "is it suitable",
        "is this suitable",

    ]


    if any(
        phrase in question_lower
        for phrase in standalone_course_questions
    ):

        return True


    return False


def answer_from_memory(question):

    last_course = (
        memory.get_last_course()
    )


    if not last_course:

        print(
            "→ No remembered course"
        )

        return None


    if not is_course_followup(
        question
    ):

        print(
            "→ Question is not a course follow-up."
        )

        return None


    print(
        "→ Using remembered course:",
        last_course["course_name"]
    )


    intent = detect_course_intent(
        question
    )


    print(
        "→ Follow-up intent:",
        intent
    )


    response = answer_course_intent(
        last_course,
        intent
    )


    if response:

        print(
            "→ Answered by remembered course:",
            intent
        )

        return response


    return None


# ============================================================
# 14. MAIN PROCESS
# ============================================================


def process(
    question,
    courses
):

    question_lower = normalize_text(
        question
    )


    print(
        "\n========== COURSE MODULE =========="
    )

    print(
        "Question:",
        question
    )


    # ========================================================
    # STEP 1 — CHECK COMPARISON FIRST
    # ========================================================
    #
    # THIS IS THE MAIN FIX.
    #
    # Before:
    #
    # Compare CS and ML
    #        ↓
    # find_course()
    #        ↓
    # ML found
    #        ↓
    # no intent
    #        ↓
    # full_course_details(ML)
    #
    # Now:
    #
    # Compare CS and ML
    #        ↓
    # comparison detected
    #        ↓
    # find_courses()
    #        ↓
    # CS + ML
    #        ↓
    # compare
    #
    # ========================================================

    if is_comparison_question(
        question
    ):

        print(
            "→ Comparison question detected."
        )


        recent_courses = (
            memory.get_recent_courses()
        )


        print(
            "Recent courses:",
            [
                c["course_name"]
                for c in recent_courses
            ]
        )


        response = handle_comparison(
            question,
            recent_courses,
            courses
        )


        if response:

            print(
                "→ Answered by Course Comparison"
            )


            # ------------------------------------------------
            # Remember explicitly mentioned courses
            # ------------------------------------------------

            explicit_courses = find_courses(
                question,
                courses
            )


            for course in explicit_courses:

                memory.remember_course(
                    course
                )


            return response


        print(
            "→ Comparison detected but "
            "not enough course information."
        )

        # IMPORTANT:
        # Do NOT return here.
        #
        # Continue to normal course handling.
        # This allows the system to recover if the
        # comparison question was incomplete.


    # ========================================================
    # STEP 2 — FIND EXPLICIT COURSE
    # ========================================================

    print(
        "→ Searching for explicitly mentioned course..."
    )


    best_match, score = find_course(
        question,
        courses
    )


    # ========================================================
    # EXPLICIT COURSE FOUND
    # ========================================================

    if best_match:

        print(
            "→ Explicit course found:",
            best_match["course_name"]
        )


        print(
            "→ Match score:",
            score
        )


        # ----------------------------------------------------
        # Remember explicit course
        # ----------------------------------------------------

        memory.remember_course(
            best_match
        )


        print(
            "→ Remembered course:",
            best_match["course_name"]
        )


        # ----------------------------------------------------
        # Detect intent
        # ----------------------------------------------------

        intent = detect_course_intent(
            question
        )


        print(
            "→ Detected course intent:",
            intent
        )


        # ----------------------------------------------------
        # Answer intent
        # ----------------------------------------------------

        response = answer_course_intent(
            best_match,
            intent
        )


        if response:

            print(
                "→ Answered by Course:",
                intent
            )

            return response


        # ----------------------------------------------------
        # No specific intent
        # ----------------------------------------------------

        print(
            "→ No specific intent detected."
        )


        print(
            "→ Returning full course details."
        )


        return full_course_details(
            best_match
        )


    # ========================================================
    # NO EXPLICIT COURSE
    # ========================================================

    print(
        f"No confident course match found. "
        f"Best score={score}"
    )


    print(
        "→ No explicit course found"
    )


    # ========================================================
    # STEP 3 — CHECK MEMORY COMPARISON
    # ========================================================

    recent_courses = (
        memory.get_recent_courses()
    )


    print(
        "Recent courses:",
        [
            c["course_name"]
            for c in recent_courses
        ]
    )


    response = handle_comparison(
        question,
        recent_courses,
        courses
    )


    if response:

        print(
            "→ Answered by Course Comparison"
        )

        return response


    # ========================================================
    # STEP 4 — CHECK MEMORY FOLLOW-UP
    # ========================================================

    print(
        "→ Checking conversation memory..."
    )


    response = answer_from_memory(
        question
    )


    if response:

        return response


    # ========================================================
    # STEP 5 — NOTHING FOUND
    # ========================================================

    print(
        "→ Course module could not answer"
    )


    return None