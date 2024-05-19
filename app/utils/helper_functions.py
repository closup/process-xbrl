"""
Helper functions for utils/ and main.py
"""

# dependencies
import re
from app.utils.constants import *
from typing import *
from datetime import datetime, timedelta, timezone
import shutil
import os

def nth_parent_dir(file, n):
    """ give file path for n directories up"""
    if n == 1:
        return os.path.dirname(file)
    else:
        return os.path.dirname(nth_parent_dir(file, n-1))

def format_value(value):
    """ Make a nice looking numerical entry w/ commas etc"""
    # remove any non-numbers
    value = re.match("([/$/ ]*)([-0123456789na]*)", str(value)).group(2)
    if value == "nan": 
        return "" # keep blank values blank (not zeros)
    if value == "-":
        return 0
    # allow for decimals
    if int(value) == float(value): 
        return int(value)
    return float(value)

def clean(text):
    """remove excess whitespace"""
    try:
        text = str(text)
    except: 
        return text
    return text.lower().strip().replace(" ", "_").replace(":","")

def print_nicely(txt):
    """ Apply snake case and add spaces (renders sheet titles for HTML) """
    words = txt.replace("_", "-").split('-')  
    capitalized_words = [word.capitalize() for word in words] 
    return " ".join(capitalized_words) 

def get_col_no_spaces(text):
    """ Capitalize each word but remove spaces """
    return print_nicely(text).replace(" ", "")

def check_ext(filename : str, file_extensions : List[str]) -> bool:
    """ Check file extension against a list of allowable extensions """
    return '.' in filename and filename.rsplit('.', 1)[1] in file_extensions 

def allowed_file(filename : str) -> bool:
    """ Check file extension against all allowed extensions """
    return check_ext(filename, ALLOWED_EXTENSIONS)

def is_spreadsheet(filename : str) -> bool:
    """ Check file extension against allowed extensions for spreadsheets """
    return check_ext(filename, SPREADSHEET_EXTENSIONS)

# SESSION
SESSION_TIMEOUT_SECONDS = 60

# Function to check session expiry
def check_session_expiry(session):
    if 'session_id' in session:
        session_timestamp = session.get('session_timestamp')
        if session_timestamp:
            # Make session_expiry_time offset-aware
            session_expiry_time = session_timestamp + timedelta(seconds=SESSION_TIMEOUT_SECONDS)
            session_expiry_time = session_expiry_time.replace(tzinfo=timezone.utc)

            # Make current_time offset-aware
            current_time = datetime.now(timezone.utc)

            if current_time > session_expiry_time:
                # Session has expired, delete session and associated data
                session_id = session['session_id']
                session_folder_path = os.path.join('app/static/sessions_data', session_id)
                if os.path.exists(session_folder_path):
                    shutil.rmtree(session_folder_path)  # Delete the session folder
                session.clear()  # Clear the session data
                print("Session expired for session ID:", session_id)
                return True
    return False

# Function to update session timestamp
def update_session_timestamp(session):
    session['session_timestamp'] = datetime.now(timezone.utc)