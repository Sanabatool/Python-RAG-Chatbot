def parse_command(command):
    command = command.lower()

    if "enroll" in command and "python" in command:
        return {"action": "enroll", "course_id": 1}
    elif "dashboard" in command:
        return {"action": "go_dashboard"}
    else:
        return {"action": "unknown"}
