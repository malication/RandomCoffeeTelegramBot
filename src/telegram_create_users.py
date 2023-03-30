import telebot
import gspread as gs
import os
from oauth2client.service_account import ServiceAccountCredentials
import logging
import time

logger = logging.getLogger(__name__)

CREDS_PATH = os.environ.get('CREDS_PATH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')
PASSWORD = os.environ.get('PASSWORD')

client = gs.authorize(
    credentials=ServiceAccountCredentials.from_json_keyfile_name(
        filename=os.path.expanduser(path=CREDS_PATH),
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
)

bot = telebot.TeleBot(token=BOT_TOKEN, threaded=False)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Для участия в Random Coffee Kaspi UX & Design необходимо ввести пароль")
    bot.register_next_step_handler(message, getpass)


def getpass(message):
    password = message.text.strip().lower()

    if password == PASSWORD:
        bot.send_message(message.chat.id, "Пароль верный, теперь ты сможешь участвовать в жеребьёвках")

        username = message.chat.username
        id = message.chat.id
        first_name = message.chat.first_name
        last_name = message.chat.last_name

        sheet_participants = client.open('participants').worksheet('production')
        content_participants = sheet_participants.get_all_values()
        usernames = [tuple[1] for tuple in content_participants[1:]]

        if username in usernames:
            print(f'User {username} already exists')
            bot.send_message(message.chat.id, "Ты уже зарегистрирован(-а)")

        else:
            body = [id, username, first_name, last_name, 0]
            sheet_participants.append_row(body, insert_data_option='INSERT_ROWS')
            print(f'User {username} has been created')

    elif password == '/start':
        start(message)

    else:
        bot.send_message(message.chat.id, "Неверный пароль, попробуй ещё раз")
        bot.register_next_step_handler(message, getpass)


@bot.message_handler(content_types=['text'])
def user_text(message):
    bot.send_message(message.chat.id, "Для начала работы с ботом введи команду “/start”")


if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)

        except Exception as e:
            logger.error(e)
            time.sleep(3)