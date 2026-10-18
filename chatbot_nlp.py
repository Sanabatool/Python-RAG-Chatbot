import re
import spacy

nlp = spacy.load("en_core_web_sm")


def handle_smalltalk(question):
    greetings = ["hello", "hi", "hey", "assalam", "salam"]
    thanks = ["thanks", "thank you", "shukriya"]
    how_are_you = ["how are you", "kese ho", "kaisi ho", "how is it going"]
    goodbye = ["bye", "goodbye", "khuda hafiz", "Allah hafiz"]
    feeling = ["i am sad", "i am happy", "i am stressed", "i am confused", "i feel bad"]
    compliment = ["you are smart", "you are helpful", "you are amazing", "i like you"]
    identity = ["who are you", "what is your name"]
    capability = ["what can you do", "how can you help me"]

    question = question.lower()

    doc = nlp(question.lower())

    words = [token.text for token in doc]

    if any(greeting in words for greeting in greetings):
        return "Hello! How can I assist you today?"
    elif any(phrase in question for phrase in how_are_you):
        return "I'm just a bot, but I'm here to help you as best I can!"
    elif any(word in question for word in thanks):
        return "You're very welcome! Feel free to ask anything else."
    elif any(word in question for word in goodbye):
        return "Goodbye! Take care and best of luck with your learning."
    elif any(word in question for word in feeling):
        return "I'm here for you. If you're feeling overwhelmed, maybe a course can help boost your confidence."
    elif any(word in question for word in compliment):
        return "You're too kind! I'm here to assist you anytime."
    elif any(word in question for word in identity):
        return "I'm your virtual learning assistant. You can ask me anything about courses, topics, or help."
    elif any(word in question for word in capability):
        return "I can help you find the best courses, understand topics, or guide you through our LMS. Just ask!"

    return None


def clean_question(question):
    return re.sub(r'[^a-zA-Z0-9\s]', '', question).lower()


def detect_intent(question):
    question = clean_question(question)

    if any(keyword in question for keyword in ["top rated", "best courses", "highest rating"]):
        return "top_rated"
    elif any(keyword in question for keyword in ["free", "without cost", "no payment"]):
        return "free_courses"
    elif any(keyword in question for keyword in ["cheap", "low price", "affordable"]):
        return "cheap_courses"
    elif any(keyword in question for keyword in ["expensive", "high price", "premium"]):
        return "expensive_courses"
    elif any(keyword in question for keyword in ["course on", "course for", "related to"]):
        return "course_search"
    elif any(keyword in question for keyword in ["who are you", "what is your name", "how can you help"]):
        return "smalltalk"
    elif any(keyword in question for keyword in ["features", "capabilities", "functions", "tools", "modules", "services", "benefits"]):
        return "platform_features"
    return "general"



def detect_intent_and_entities(user_input):
    doc = nlp(user_input.lower())
    intent = None
    entity = None

    if "enroll" in user_input:
        intent = "enroll_course"
        for ent in doc.ents:
            if ent.label_ in ["ORG", "PRODUCT", "WORK_OF_ART"] or "course" in ent.text:
                entity = ent.text
    elif "price" in user_input:
        intent = "ask_price"
    elif "who is the tutor" in user_input or "instructor" in user_input:
        intent = "ask_tutor"

    return intent, entity
