from config import fetch_quiz_info

def process(question, tokens):

    quiz_keywords = [
        "quiz",
        "quizzes",
        "test",
        "tests",
        "mcq",
        "mcqs"
    ]

    if any(word in tokens for word in quiz_keywords) or any(k in question.lower() for k in quiz_keywords):

        quiz_count = fetch_quiz_info()

        return f"""
            <h3>📝 Quizzes</h3>
            <ul>
                <li>We have <b>{quiz_count} quizzes</b> available.</li>
                <li>You can practice MCQs and tests anytime!</li>
            </ul>
        """

    return None