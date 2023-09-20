"""
A script to convert an arbitrary Excel budget into XBRL format.

Last updated: September 2023, K. Wheelan
"""

# =============================================================
# Dependencies
# =============================================================

#import xlsx2html
from bs4 import BeautifulSoup
import argparse
# added dependencies (KW)
import pandas as pd
import numpy as np
import sys
import re # regular express package

import conf # configuration 

# import conf # configuration module (conf.py) contains globals
# import pprint
# import html
# import os
# import re

# =============================================================
# Global variables (can be moved to conf.py later)
# =============================================================

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

global context_name_map
context_name_map = {}
global context_ref_map
context_ref_map = {}

CONTEXTS_FILE = 'contexts.xlsx'
CELL_STYLE = "f'style=\"border-collapse: collapse; height: 15.0pt; text-align:right; font-size:{font_size}px\"'"
HTML_BASE_TD =  "f'<td id=\"{statement}_{cell}\" style=\"{style}\">\n{ix}</td>'"
IXBRL_TAG = "f'$<ix:nonFraction contextRef=\"{context}\" name=\"{name}\" unitRef=\"USD\" id=\"{statement}_{cell}\" decimals=\"0\" format=\"{format}\" {minus}>{value}</ix:nonFraction>\n'"

# =============================================================
# Function definitions
# =============================================================

def parse_commandline_args():
    """
    Parses command line arguments using argparser package to
    read in input and output file names to global vars.
    """

    # Create custom parser for commandline runs
    parser = argparse.ArgumentParser()
    parser.add_argument('--i', type=str, metavar="input_file(xlsx)", required=True, help="Input xlsx file name")
    parser.add_argument('--o', type=str, metavar="output_file(html)", help="Output html file name")

    # parses commandline text and saves in the args object
    args = parser.parse_args()

    global input_file
    global output_file
    if args.i:
        input_file = args.i

    # if output file is not specified, save as .html version of the input file
    if args.o:
        output_file = args.o
    else:
        output_file = input_file.split(".")[0] + ".html"

def clean(text):
    """makes lowercase and removes excess whitespace"""
    try:
        text = str(text)
    except: 
        return text
    return text.lower().strip().replace(" ", "_")

def parse_contexts(contexts_file):
    """
    Function to parse contexts to create contexts reference
    dictionaries for later
    """   
    # open contexts excel sheet
    try:
        contexts = pd.read_excel(contexts_file)
    except:
        sys.exit("No context file!")
    # create the index as its own column
    contexts['index'] = contexts['Scope'] + "@" + contexts['Statement']
    # create contexts reference dictionaries
    global context_name_map
    global context_ref_map
    for row in range(len(contexts)):
        name = contexts["Context_Name"][row].strip()
        _, _, header, _, ref, index = contexts.iloc[row].apply(clean)
        if not context_name_map.get(index):
            context_name_map[index] = {header : name}
            context_ref_map[index] = {header : ref}
        else:
            context_name_map[index][header] = name
            context_ref_map[index][header] = ref
            
def process_header(sheet):
        """
        Function to extract excel header data and clean sheet
        """
        # read header data
        n_header_lines = sheet[sheet.columns[-1]].first_valid_index()
        #### HARDCODING ####
        scope = clean(sheet["City of Clayton"][0])
        statement = clean(sheet["City of Clayton"][1])
        index = f"{scope}@{statement}"
        return n_header_lines, index

def clean_sheet(input_file):
    """
    Function to read budget excel sheet and match contexts
    """   
    input_xl = pd.ExcelFile(input_file)
    for sheet_name in input_xl.sheet_names:
        # read in one sheet of the excel doc
        sheet_data = pd.read_excel(input_xl, sheet_name=sheet_name)        
        # read header data, remove header, and reassign column names
        n_header_lines, index = process_header(sheet_data)
        sheet_data.columns = sheet_data.iloc[n_header_lines].apply(clean)
        sheet_data = sheet_data.drop(list(range(n_header_lines + 1)))
        # add an index for the original row number (# dropped rows + row # - 1 header row)
        sheet_data["row"] = list(n_header_lines + sheet_data.index - 1)

        # reshape long for ease
        extra_left_cols = 2  # HARDCODING # 1 for xbrl element + 1 for row labels
        id_cols, val_cols = list(sheet_data.columns[:extra_left_cols]), list(sheet_data.columns[extra_left_cols:])
        id_cols += ["row"]
        n_rows_orig = len(sheet_data) # num of rows before reshaping
        sheet_data = pd.melt(sheet_data, id_vars = id_cols, value_vars = val_cols, var_name = "header")
        # look up contexts in context map
        sheet_data["context"] = sheet_data["header"].map(context_name_map[index])
        # determine cells and resultant ids
        cols = [ALPHABET[i] for i in list(extra_left_cols + (sheet_data.index // n_rows_orig))]
        cells = [c + str(r) for c,r in zip(cols, sheet_data["row"])]
        sheet_data["id"] = [f'{sheet_name.replace(" ","")}_{cell}' for cell in cells]
    return sheet_data

def d_to_i(name, context):
    """
    Replace D contexts with I contexts
    ? Unclear why we do this
    """
    if name in conf.d_to_i_contexts and context[0] == 'D':
        return "I" + context[1:]
    return context

def format_value(value):
    """ Make a nice looking numerica entry w/ commas etc"""
    # remove any non-numbers
    value = re.match("([/$-/ ]*)([0123456789na]*)", str(value)).group(2)
    if value == "":
        value = 0
    if value == "nan":
        return ""
    # allow for decimals
    if int(value) == float(value): 
        value = int(value)
    else: 
        value = float(value)
    # add commas
    return '{:,}'.format(int(value))

def process_cell(sheet_data):
    """
    """
    # translate D to I contexts 
    # ? Clarify reason
    sheet_data['context'] = sheet_data.apply(lambda x: d_to_i(x.xbrl_element, x.context), axis=1)
    # identify negative values and strip sign
    sheet_data["sign"] = sheet_data.apply(lambda x: re.match("^(-*)(\$*)(.*)", str(x.value)).group(1), axis = 1)
    sheet_data['sign'].replace({'-': 'sign = "-"'}, inplace=True)
    # format values
    sheet_data['value'] = sheet_data['value'].map(format_value)
    # define ixbrl format ('ixt:fixed-zero' or 'ixt:num-dot-decimal')
    print(sheet_data['value'])

    # define dollar, minus, format, value
    # trim unnecessary characters at the start of the value
    # format xml

    # try:
    #     outstring = td.string
    #     outstring_int = td.string
    #     # process $
    #     if td.string[0] == "$":
    #         dollar = "$"
    #         outstring = td.string[1:]
    #         outstring_int = td.string[1:]
    #     else:
    #         dollar = ""
    #     # 
    #     if outstring[0] == "-":
    #         if len(outstring) > 1 and outstring[1] == '$':
    #             outstring_int = outstring_int[1:]
    #             minus = "-$"
    #         else:
    #             minus = "-"
    #         sign = ' sign="-"'
    #         outstring = outstring_int[1:]
    #     else:
    #         minus = ""
    #         sign = ""
    #     if td.string == "-" or td.string == "$ -":
    #         minus = ""
    #         sign = ""
    #         value = ''
    #         # value = ' value="0"'  -- Arelle throwing error when I use this
    #         format = 'ixt:fixed-zero'
    #         outstring = "-"
    #     else:
    #         format = 'ixt:num-dot-decimal'
    #         value = ""
    #     row = id[(len(sheet_name)+2):]
        
    #     cell_id = col + row
    #     id = sheet_name.replace(" ","_") + "_" + cell_id
    #     content = f'{dollar}{minus}<ix:nonFraction contextRef="{context}" name="{name}" unitRef="USD" id="{id}" decimals="0" format="{format}"{sign}{value}>' + \
    #         outstring + '</ix:nonFraction>'
    #     return content
    # except Exception as e:
    #     return None

    

# =============================================================
# Run file
# =============================================================

if __name__ == "__main__":
    parse_commandline_args()
    parse_contexts(CONTEXTS_FILE)
    #print(context_name_map)
    sheet = clean_sheet(input_file)
    process_cell(sheet)

# input_file = "example.xlsx"
# parse_contexts(CONTEXTS_FILE)
# print(context_name_map)
# read_sheet(input_file)