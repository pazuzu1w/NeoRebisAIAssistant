from datetime import datetime


class ChatHistory:
    def __init__(self):
        self.history = []

    def append_message(self, sender, message):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.history.append(f"[{timestamp}] {sender}: {message}")

    def get_history(self):
        return "\n".join(self.history)