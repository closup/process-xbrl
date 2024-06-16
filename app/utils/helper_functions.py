"""
Helper functions for utils/ and main.py
"""

# dependencies
import re
from app.utils.constants import *
from typing import *
from datetime import datetime, timedelta, timezone
import shutil
import os, zipfile
from bs4 import BeautifulSoup
from io import BytesIO

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
 
                session_folder_path = os.path.join('app/static/sessions_data')
                if os.path.exists(session_folder_path):
                    # Iterate over subfolders and delete them
                    for root, dirs, files in os.walk(session_folder_path):
                        for directory in dirs:
                            shutil.rmtree(os.path.join(root, directory))
                    print("All expired sessions deleted successfully.")
                    
                session.clear()  # Clear the session data
                return True
    return False

# Function to update session timestamp
def update_session_timestamp(session):
    session['session_timestamp'] = datetime.now(timezone.utc)

def modify_img_paths(session_id):
    # Define the path to the HTML file
    html_file_path = os.path.join('app', 'static', 'sessions_data', session_id, 'output', 'output.html')

    # Read the HTML file
    with open(html_file_path, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Find all <img> tags and modify their src attribute
    for img_tag in soup.find_all('img'):
        src = img_tag.get('src')
        if src and src.startswith('/static/sessions_data/'):
            # Truncate '/static/sessions_data' from the src attribute
            new_src = src.replace('/static/sessions_data', '')
            img_tag['src'] = new_src

    # Save the modified HTML back to the file
    with open(html_file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

# Generates a zip file to download once conversion is complete
def generate_zip_file(session_id):
    output_dir = os.path.join('app/static', 'sessions_data', session_id, 'output')
    html_file_path = os.path.join(output_dir, 'output.html')
    img_directory_path = os.path.join('app/static', 'sessions_data', session_id, 'input', 'img')
    zip_file_path = os.path.join(output_dir, 'converted_xbrl.zip')

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Debug prints to check paths
    print(f"HTML file path: {html_file_path}")
    print(f"Image directory path: {img_directory_path}")
    print(f"ZIP file path: {zip_file_path}")

    # Create ZIP file
    with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        # Add HTML file to zip
        if os.path.exists(html_file_path):
            print(f"Adding HTML file to zip: {html_file_path}")
            zf.write(html_file_path, os.path.basename(html_file_path))
        else:
            print(f"HTML file not found: {html_file_path}")
        
        # Add images to zip
        if os.path.exists(img_directory_path):
            for root, dirs, files in os.walk(img_directory_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_name = os.path.relpath(file_path, img_directory_path)
                    print(f"Adding image to zip: {file_path} as {archive_name}")
                    zf.write(file_path, archive_name)
        else:
            print(f"Image directory not found: {img_directory_path}")
    
    zf.close()