import telebot
from telebot import types
import gspread as gs
import os
from oauth2client.service_account import ServiceAccountCredentials
import logging
import time

logger = logging.getLogger(__name__)

CREDS_PATH = os.environ.get('CREDS_PATH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

client = gs.authorize(
    credentials=ServiceAccountCredentials.from_json_keyfile_name(
        filename=os.path.expanduser(path=CREDS_PATH),
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
)

sheet_participants = client.open('participants').worksheet('production')
content_participants = sheet_participants.get_all_values()
usernames = sheet_participants.col_values(2)
chat_ids = sheet_participants.col_values(1)[1:]

bot = telebot.TeleBot(token=BOT_TOKEN, threaded=False)

for chat_id in chat_ids:
    try:
        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(types.InlineKeyboardButton("Да, я буду участвовать", callback_data='set_active'))
        keyboard.add(types.InlineKeyboardButton("Нет, я пропущу эту жеребёвку", callback_data='skip'))
        bot.send_message(chat_id, 'Привет! \nСегодня будет проводиться жеребьёвка, в которой будет определена пара, '
                                  'с которой тебе нужно сходить на Random Coffee в ближайшие две недели. '
                                  '\n\nГотов(-а) ли ты участвовать в этот раз?', reply_markup=keyboard)
        print(f'Message sent to chat_id {chat_id}')
    except Exception as e:
        print(f"Something went wrong with chat_id {chat_id}")
        print(e)

@bot.callback_query_handler(func=lambda callback: True)
def callback_action(callback):
    if callback.data == 'set_active':
        username = callback.message.chat.username
        rownum = usernames.index(username) + 1
        sheet_participants.update_cell(rownum, 5, '1')
        print(f'{username} is participating')

        bot.send_message(
            callback.message.chat.id,
            "Супер! Теперь ты участвуешь в жеребьёвке. Тебе придёт сообщение о твоей паре."
        )

        bot.delete_message(
            message_id=callback.message.id,
            chat_id=callback.message.chat.id
        )

    elif callback.data == 'skip':
        username = callback.message.chat.username
        print(f'{username} is not participating')

        bot.send_message(
            callback.message.chat.id,
            "Ты не участвуешь в текущей жеребьёвке."
        )

        bot.delete_message(
            message_id=callback.message.id,
            chat_id=callback.message.chat.id
        )

if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True)

        except Exception as e:
            logger.error(e)
            time.sleep(3)