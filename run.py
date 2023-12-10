from Bot import TelegramBot
from Message import Message

from os import environ
from requests import get

TOKEN = environ.get("TOKEN")

bot = TelegramBot(TOKEN)

@bot.command("/bin", description = "Get Bin Information!")
def get_bin(bot: TelegramBot, message: Message):
    bin_information = get(f"https://bincheckerfree.com/bin/{message.text[5:]}").json()
    response = "\n".join([f"<b>{key}</b>: {value}" for key, value in bin_information.items()])
    bot.send_message(message.chat.id, response, protect_content = True, parse_mode = "HTML")

@bot.command("/pin", require_slash=False, description = "Pin this message!")
def get_bin(bot: TelegramBot, message: Message):
    bot.pin_message(message)
    bot.reply_message(message, "Pinned!")

if __name__ == "__main__":
    bot.run()