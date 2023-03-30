from shuffler import gen_session
import pandas as pd
import gspread as gs
import gspread_dataframe as gd
import os
from oauth2client.service_account import ServiceAccountCredentials

CREDS_PATH = os.environ.get('CREDS_PATH')

client = gs.authorize(
    credentials=ServiceAccountCredentials.from_json_keyfile_name(
        filename=os.path.expanduser(path=CREDS_PATH),
        scopes=["https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive"]
    )
)

sheet_participants = client.open("participants").worksheet('production')
content_participants = sheet_participants.get_all_values()
participants_df = pd.DataFrame(content_participants[1:], columns=content_participants[0])

ids = participants_df[participants_df.is_active == "1"]['id']

sheet_pairing = client.open('pairing_log').worksheet('production')
content_pairing = sheet_pairing.get_all_values()
pairing_log_df = pd.DataFrame(content_pairing[1:], columns=content_pairing[0])
pairing_log_df['session_id'] = pd.to_numeric(pairing_log_df['session_id'])
last_session_id = pairing_log_df['session_id'].max()
previous_sessions = pairing_log_df[pairing_log_df['session_id'] >= last_session_id - 3]

new_session = gen_session(
        session_id = last_session_id + 1,
        participant_ids = ids,
        previous_sessions = previous_sessions,
        attempts = 20
)

print(new_session)

updated_df = pairing_log_df.append(new_session)
gd.set_with_dataframe(sheet_pairing, updated_df)