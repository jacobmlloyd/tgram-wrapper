from Message import Message

import requests
from flask import Flask, request
from pyngrok import ngrok

class TelegramBot:
    """
    A Telegram Bot wrapper to handle messages and manage webhooks.
    """

    def __init__(self, token, ngrok_port=5000):
        """
        Initialize the Telegram Bot with a given token and ngrok port.
        """
        self.token = token
        self.command_handlers = {}

        self.app = Flask(__name__)
        self.ngrok_port = ngrok_port
        self.app.add_url_rule('/webhook', 'webhook', self.webhook, methods=['POST'])

    def run(self):
        """
        Start the bot by setting up the webhook and running the Flask app.
        """
        self.ngrok_tunnel = ngrok.connect(self.ngrok_port)
        webhook_url = f'{self.ngrok_tunnel.public_url}/webhook'
        self.set_webhook(webhook_url)
        try:
            self.delete_commands()
            self.add_commands()
            print(f'Webhook set to {webhook_url}')
            self.app.run(port=self.ngrok_port)
        finally:
            self.delete_webhook()
            ngrok.disconnect(self.ngrok_tunnel.public_url)

    def set_webhook(self, url):
        """
        Set the webhook URL for the Telegram bot.
        """
        response = requests.get(f'https://api.telegram.org/bot{self.token}/setWebhook?url={url}')
        return response.json()

    def delete_webhook(self):
        """
        Delete the current webhook for the Telegram bot.
        """
        response = requests.get(f'https://api.telegram.org/bot{self.token}/deleteWebhook')
        return response.json()

    def webhook(self):
        """
        Handle incoming webhook requests from Telegram.
        """
        update = request.get_json()
        self.handle_update(update)
        return 'OK'
    
    def delete_commands(self):
        """
        Delete all currently registered commands.
        """
        response = requests.get(f'https://api.telegram.org/bot{self.token}/deleteMyCommands')
        return response.json()
    
    def add_commands(self):
        """
        Add all currently registered commands.
        """
        commands = []
        for command in self.command_handlers:
            commands.append({"command": command, "description": self.command_handlers[command]["description"]})
        response = requests.post(f'https://api.telegram.org/bot{self.token}/setMyCommands', json={"commands": commands})
        print(response.json())

    def command(self, command, require_slash: bool = True, description: str = None):
        """
        Decorator to register a command handler function.
        """
        def decorator(handler):
            self.command_handlers[command] = {"handler": handler, "require_slash": require_slash, "description": description}
            return handler
        return decorator

    def handle_message(self, update):
        """
        Handle new messages and execute registered commands.
        """
        message = update['message']
        if 'text' in message:
            text = message['text'].lower()
            if text.startswith('/'):
                command = text.split()[0].split('@')[0]
                if command in self.command_handlers:
                    self.command_handlers[command]["handler"](self, Message(update))
            else:
                for command in self.command_handlers:
                    if not self.command_handlers[command]["require_slash"] and command[1:] in text:
                        self.command_handlers[command]["handler"](self, Message(update))

    def handle_update(self, update):
        """
        Process each update received from Telegram.
        """
        if 'message' in update:
            self.handle_message(update)

    def send_message(self, chat_id, text, protect_content = False, parse_mode = "HTML"):
        """
        Send a message via the Telegram bot.

        Args:
            chat_id (str or int): The chat ID to send the message to.
            text (str): The text of the message.
            protect_content (bool): Whether to protect the message from forwarding.
        """
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        data = {'chat_id': chat_id, 'text': text, 'protect_content': protect_content, 'parse_mode': parse_mode}
        requests.post(url, data=data)

    def reply_message(self, message: Message, text, protect_content = False):
        """
        Reply to a message via the Telegram bot.

        Args:
            message (Message): The Message object to reply to.
            text (str): The text of the message.
            protect_content (bool): Whether to protect the message from forwarding.
        """
        url = f'https://api.telegram.org/bot{self.token}/sendMessage'
        data = {'chat_id': message.chat.id, 'text': text, 'reply_to_message_id': message.id, 'protect_content': protect_content}
        requests.post(url, data=data)

    def pin_message(self, message: Message):
        """
        Pin a message in a chat.

        Args:
            message (Message): The Message object to pin.
        """
        url = f'https://api.telegram.org/bot{self.token}/pinChatMessage'
        data = {'chat_id': message.chat.id, 'message_id': message.id}
        response = requests.post(url, data=data)
        if not response.json()["ok"]:
            self.send_message(message.chat.id, "I can't pin messages here!")