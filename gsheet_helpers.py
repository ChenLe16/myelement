import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import re
import hashlib
import datetime as dt

SHEET_NAME = "MyElement Leads"
EMAIL_PATTERN = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")

def is_valid_email(email: str) -> bool:
    """Check if the provided email string is a valid email address.
    
    Args:
        email: The email address to validate.
        
    Returns:
        True if the email is valid, False otherwise.
    """
    return EMAIL_PATTERN.match(email) is not None

def append_to_gsheet(data: list) -> str:
    """Append a row of data to the Google Sheet if the key is not a duplicate.
    
    Args:
        data: A list of values representing a row to append.
        
    Returns:
        'added' if the row was added,
        'duplicate' if the key already exists,
        'error: <message>' if an error occurred.
    """
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        creds_dict = json.loads(st.secrets["google_service_account"])
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        sheet = client.open(SHEET_NAME).sheet1  # Adjust if needed
        key = data[0]
        if sheet.findall(key):
            return 'duplicate'
        sheet.append_row(data)
        return 'added'
    except Exception as e:
        return f'error: {str(e)}'

def make_unique_key(email: str, dob: dt.date, birth_time: dt.time, kind: str = "SIMPLE") -> str:
    """Generate a unique SHA-256 hash key based on email, date of birth, birth time, and kind.
    
    Args:
        email: The email address.
        dob: The date of birth as a datetime.date object.
        birth_time: The birth time as a datetime.time object.
        kind: A string indicating the kind of key (default is "SIMPLE").
        
    Returns:
        A SHA-256 hex digest string representing the unique key.
    """
    key_source = f"{email}-{dob.strftime('%Y-%m-%d')}-{birth_time.strftime('%H:%M')}-{kind}"
    return hashlib.sha256(key_source.encode("utf-8")).hexdigest()