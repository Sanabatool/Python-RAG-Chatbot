class ConversationMemory:

    def __init__(self):

        # Current / last course
        self.last_course = None
        self.last_topic = None
        self.last_trainer = None

        # Courses discussed in the current conversation
        self.recent_courses = []

        # Conversation history
        self.history = []

    # ----------------------------
    # Remember course
    # ----------------------------

    def remember_course(self, course):

        self.last_course = course
        self.last_topic = course["course_name"]
        self.last_trainer = course["trainer"]

        # Avoid duplicate courses
        self.recent_courses = [
            c for c in self.recent_courses
            if c["id"] != course["id"]
        ]

        # Add newest course
        self.recent_courses.append(course)

        # Keep only last 3 discussed courses
        if len(self.recent_courses) > 3:
            self.recent_courses.pop(0)

        print("Remembered course:", course["course_name"])

    # ----------------------------
    # Find course from question
    # ----------------------------

    def remember_course_from_courses(self, question, courses):

        question_lower = question.lower()

        for course in courses:

            if course["course_name"].lower() in question_lower:

                self.remember_course(course)

                return course

        return None

    # ----------------------------
    # Get last course
    # ----------------------------

    def get_last_course(self):
        return self.last_course

    # ----------------------------
    # Get last topic
    # ----------------------------

    def get_last_topic(self):
        return self.last_topic

    # ----------------------------
    # Get last trainer
    # ----------------------------

    def get_last_trainer(self):
        return self.last_trainer

    # ----------------------------
    # Get recent courses
    # ----------------------------

    def get_recent_courses(self):
        return self.recent_courses

    # ----------------------------
    # Conversation History
    # ----------------------------

    def add_message(self, role, message):

        self.history.append({
            "role": role,
            "message": message
        })

        # Keep last 10 messages
        if len(self.history) > 10:
            self.history.pop(0)

    def get_history(self):
        return self.history


memory = ConversationMemory()