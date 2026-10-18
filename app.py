from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import re
import spacy
from chatbot_nlp import detect_intent, detect_intent_and_entities
from modules.router import route
from memory.conversation_memory import memory


from config import (
    fetch_courses,
    fetch_courses_count,
    fetch_top_rated_courses
)

app = Flask(__name__)
CORS(app)

nlp = spacy.load("en_core_web_sm")

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/favicon.ico')
def favicon():
    return '', 204


@app.route('/chatbot', methods=['POST'])
def chatbot():
    data = request.get_json()
    question = data.get('question')

    if not question:
        return jsonify({
            "error": "Please provide 'question' in the request body."
        }), 400

    memory.add_message("user", question)

    # --- Intent detection first ---
    intent = detect_intent(question)

    if intent == "platform_features":
        return jsonify({"response": """
            <h3>🚀 Key Features of our E-learning Platform</h3>
            <ul>
                <li>📚 <b>Course Management</b>: Admins and teachers can create, update, and manage courses.</li>
                <li>🎥 <b>Learning Content</b>: Video lessons, documents, quizzes, and interactive content.</li>
                <li>🧑‍🏫 <b>Role-based Access</b>: Separate dashboards for Admin, Teacher, and Student.</li>
                <li>💳 <b>Payment Integration</b>: Secure enrollment and payments for premium courses.</li>
                <li>📝 <b>Quizzes & Assessments</b>: Students can take quizzes and track progress.</li>
                <li>📈 <b>Progress Tracking</b>: Students can mark lessons complete and finish courses.</li>
                <li>🏆 <b>Certificates</b>: Auto-generate completion certificates.</li>
                <li>💬 <b>Chatbot Support</b>: Ask me about courses, prices, or guidance anytime!</li>
            </ul>
        """})

    courses = fetch_courses()

    print("\n===== MEMORY BEFORE ROUTING =====")
    print("Last course:", memory.get_last_course())
    print("Last topic:", memory.get_last_topic())
    print("Last trainer:", memory.get_last_trainer())
    print("History:", memory.get_history())

    doc = nlp(question.lower())
    tokens = [token.text for token in doc]

    response = route(question, tokens, courses)

    if response:
        memory.add_message("assistant", response)
        return jsonify({"response": response})

    response = analyze_question(question, courses)

    memory.add_message("assistant", response)

    return jsonify({
        "response": response
    })


def analyze_question(question, courses):
    doc = nlp(question.lower())
    tokens = [token.text for token in doc]
    # --- Intent & Entity extraction ---
    intent, entity = detect_intent_and_entities(question)

    # 📝 Enrollment
    if intent == "enroll_course":
        return f"""
            <h3>📝 Enroll in a Course</h3>
            <ul>
                <li>I can help you enroll in <b>{entity or 'a course'}</b>.</li>
                <li>Please confirm the course name if it's unclear.</li>
            </ul>
        """

    # 💰 Ask price of a specific course
    if intent == "ask_price" and entity:
        for course in courses:
            if entity.lower() in course['course_name'].lower():
                return f"""
                    <h3>💰 Course Price</h3>
                    <ul>
                        <li><b>{course['course_name']}</b> costs ${course['course_price']}.</li>
                        <li>Trainer: {course['trainer']}</li>
                    </ul>
                """
        return f"Sorry, I couldn’t find pricing info for {entity}."

    # 🎓 Ask tutor of a specific course
    if intent == "ask_tutor" and entity:
        for course in courses:
            if entity.lower() in course['course_name'].lower():
                return f"""
                    <h3>🎓 Tutor Info</h3>
                    <ul>
                        <li><b>{course['course_name']}</b> is taught by <b>{course['trainer']}</b>.</li>
                    </ul>
                """
        return f"Sorry, I couldn’t find tutor info for {entity}."

    # --- Show all courses ---
    if "all courses" in question or "show courses" in question or "available courses" in question:
        response = "<h3>📚 Available Courses</h3><ul>"
        for c in courses:
            response += f"<li>{c['course_name']} — ${c['course_price']}</li>"
        response += "</ul>"
        return response

    # --- Total course count ---
    if "total" in tokens or "how many" in question and "course" in question:
        total_courses = fetch_courses_count()
        return f"""
            <h3>📊 Total Courses</h3>
            <ul>
                <li>We currently offer <b>{total_courses} courses</b>.</li>
            </ul>
        """

    # --- Top rated / best rated ---
    if "top rated" in question or "best rated" in question or "highest rating" in question:
        top_courses = fetch_top_rated_courses()
        response = "<h3>🌟 Top-Rated Courses</h3><ul>"
        for c in top_courses:
            response += f"<li><b>{c['course_name']}</b> ({c['rating']}⭐) by {c['trainer']} — ${c['price']}</li>"
        response += "</ul>"
        return response

    # --- Free courses ---
    if "free" in tokens:
        free_courses = [c for c in courses if c['course_price'] == 0]
        if free_courses:
            response = "<h3>🆓 Free Courses</h3><ul>"
            for c in free_courses:
                response += f"<li>{c['course_name']}</li>"
            response += "</ul>"
            return response
        return "Currently, no free courses are available."

    # --- Courses under X price ---
    match = re.search(r'under (\d+)', question)
    if match:
        limit = int(match.group(1))
        under_courses = [c for c in courses if c['course_price'] <= limit]
        if under_courses:
            response = f"<h3>💰 Courses under {limit}</h3><ul>"
            for c in under_courses:
                response += f"<li>{c['course_name']} — ${c['course_price']}</li>"
            response += "</ul>"
            return response
        return f"No courses found under {limit}."


if __name__ == "__main__":
    app.run(debug=True)
