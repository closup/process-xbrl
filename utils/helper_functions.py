"""
Helper functions for utils/ and main.py
"""

# dependencies
import re
from utils.constants import *
from typing import *

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