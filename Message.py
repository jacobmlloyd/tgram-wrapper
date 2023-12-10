from Chat import Chat

class Message:
    def __init__(self, update):
        self.chat = Chat(update)
        self.text = update["message"]["text"]
        self.id = update["message"]["message_id"]
        self.username = update["message"]["from"]["username"]
        self.date = update["message"]["date"]
        self.parse_mode = "HTML"