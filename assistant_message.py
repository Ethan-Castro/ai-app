class AssistantMessage:
    def __init__(self, message_id: str, role: str, text: str):
        self.message_id = message_id
        self.role = role
        self.text = text

    def __repr__(self):
        return f"AssistantMessage(message_id={self.message_id}, role={self.role}, text={self.text})"
