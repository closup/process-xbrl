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
    """makes lowercase and removes excess whitespace"""
    try:
        text = str(text)
    except: 
        return text
    return text.lower().strip().replace(" ", "_")

# def d_to_i(name, context):
#     """
#     Replace D contexts with I contexts
#     This function should be overwritten with a lookup table
#     """
#     if name in conf.d_to_i_contexts and context[0] == 'D':
#         return "I" + context[1:]
#     return context