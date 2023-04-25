import telebot
import gspread as gs
import gspread_dataframe as gd
import os
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials

CREDS_PATH = os.environ.get('CREDS_PATH')
BOT_TOKEN = os.environ.get('BOT_TOKEN')

bot = telebot.TeleBot(token=BOT_TOKEN)

client = gs.authorize(
    credentials=ServiceAccountCredentials.from_json_keyfile_name(
        filename=os.path.expanduser(path=CREDS_PATH),
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
)

sheet_pairing = client.open('pairing_log').worksheet('production')
content_pairing = sheet_pairing.get_all_values()
pairing_log_df = pd.DataFrame(content_pairing[1:], columns=content_pairing[0])
pairing_log_df['session_id'] = pd.to_numeric(pairing_log_df['session_id'])
last_session_id = pairing_log_df['session_id'].max()
last_session = pairing_log_df[pairing_log_df['session_id'] == last_session_id]

sheet_participants = client.open('participants').worksheet('production')
content_participants = sheet_participants.get_all_values()
participants_df = pd.DataFrame(content_participants[1:], columns=content_participants[0])

chat_ids = sheet_participants.col_values(1)

session_full_info = pd.merge(last_session, participants_df,  how='left', left_on=['first'], right_on = 'id')
session_full_info = pd.merge(session_full_info, participants_df,  how='left', left_on=['second'], right_on = 'id')

message = []

for i in range(len(last_session)):
    row = f"{session_full_info['first_name_x'].iloc[i]} идёт с {session_full_info['first_name_y'].iloc[i]}"
    message.append(row)

for chat_id in chat_ids:
    try:
        if len(last_session) == len(participants_df[participants_df['is_active'] == '1']):
            bot.send_message(chat_id, 'Это информация о парах на ближайшие две недели.')
        else:
            bot.send_message(chat_id, 'Это информация о парах на ближайшие две недели.'
                                        '\n\nВ этот раз участников было нечётное количество, поэтому образовалась пара из трёх человек. '
                                        'В такой паре можно пойти на Random Coffee сразу втроём.')

        bot.send_message(chat_id, "\n".join(sorted(message)))

        print(f'Message sent to chat_id {chat_id}')

    except Exception as e:
        print(f"Something went wrong with chat_id {chat_id}")
        print(e)

participants_df['is_active'] = 0
gd.set_with_dataframe(sheet_participants, participants_df)