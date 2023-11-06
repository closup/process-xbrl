"""
Helper functions for utils/ and main.py
"""

# dependencies
import re

def format_value(value):
    """ Make a nice looking numerica entry w/ commas etc"""
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
    return text.lower().strip().replace(" ", "_")

def print_nicely(txt):
    words = txt.replace("_", "-").split('-')  
    capitalized_words = [word.capitalize() for word in words] 
    return " ".join(capitalized_words) 

def view_date(date):
    """ format date as needed """
    return date.strftime("%Y-%m-%d")