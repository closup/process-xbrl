"""
A script to convert an arbitrary Excel budget into XBRL format.

Last updated: September 2023, K. Wheelan
"""

# =============================================================
# Dependencies
# =============================================================

import xlsx2html
from bs4 import BeautifulSoup
import argparse
# added dependencies (KW)
import pandas as pd
import sys

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
IXBRL_TAG = "f'$<ix:nonFraction contextRef=\"{context}\" name=\"{name}\" unitRef=\"USD\" id=\"{statement}_{cell}\" decimals=\"0\" format=\"ixt:num-dot-decimal\">{value}</ix:nonFraction>\n'"

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
    return text.lower().strip()

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
        context_name_map[index] = {header : name}
        context_ref_map[index] = {header : ref}

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

def read_sheet(input_file):
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
        # reshape long for ease
        extra_left_cols = 2
        id_cols, val_cols = sheet_data.columns[:extra_left_cols], sheet_data.columns[extra_left_cols:]
        n_rows_orig = len(sheet_data) # num of rows before reshaping
        sheet_data = pd.melt(sheet_data, id_vars = id_cols, value_vars = val_cols)
        # look up contexts in context map
        sheet_data["context"] = context_name_map[index][sheet_data.columns[extra_left_cols]]
        # determine cells and resultant ids
        cols = [ALPHABET[i] for i in list(extra_left_cols + (sheet_data.index // n_rows_orig))]
        rows = list(n_header_lines + (sheet_data.index % n_rows_orig))
        sheet_data["cell"] = [c + str(r) for c in cols for r in rows]
        sheet_data["id"] = f'{sheet_name.replace(" ","")}_{sheet_data["cell"]}'
        print(sheet_data)

    

# =============================================================
# Run file
# =============================================================

if __name__ == "__main__":
    parse_commandline_args()
    parse_contexts(CONTEXTS_FILE)
    read_sheet(input_file)

input_file = "example.xlsx"
parse_contexts(CONTEXTS_FILE)
print(context_name_map)
read_sheet(input_file)