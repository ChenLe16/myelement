import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from oauth2client.service_account import ServiceAccountCredentials
import json
import re
import hashlib
import datetime as dt

# (Utility for checking email)
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email) is not None

# The Google Sheets function
# def append_to_gsheet(row, gsheet_name="MyElement_Subscribers", worksheet=0):
#     # Use Streamlit secrets
#     import streamlit as st
#     secrets = st.secrets["gcp_service_account"]
#     scopes = [
#         "https://www.googleapis.com/auth/spreadsheets",
#         "https://www.googleapis.com/auth/drive"
#     ]
#     credentials = Credentials.from_service_account_info(secrets, scopes=scopes)
#     gc = gspread.authorize(credentials)
#     sh = gc.open(gsheet_name)
#     ws = sh.get_worksheet(worksheet)
#     ws.append_row(row)

def append_to_gsheet(data):
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = json.loads(st.secrets["google_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    sheet = client.open("MyElement Leads").sheet1  # Adjust if needed
    # Deduplication: Check if the key (data[0]) already exists in the sheet; if so, skip appending
    key = data[0]
    if sheet.findall(key):
        return
    sheet.append_row(data)
    return 'added'

def make_unique_key(email, dob, birth_time, kind="SIMPLE"):
    key_source = f"{email}-{dob.strftime('%Y-%m-%d')}-{birth_time.strftime('%H:%M')}-{kind}"
    return hashlib.sha256(key_source.encode("utf-8")).hexdigest()