class Chat:
    def __init__(self, update):
        self.id = update["message"]["chat"]["id"]
        self.message_id = update["message"]["message_id"]
        