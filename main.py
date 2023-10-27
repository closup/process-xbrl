"""
A script to convert an arbitrary Excel budget into XBRL format.

Last updated: October 2023, K. Wheelan

TODO:
NEXT ISSUE:
- replace contexts sheet with a dictionary w just relevant info (or sheet)
- replace contexts maps? -- replace with elements.xlsx?

CODE QUALITY:
- split functions into modules
- add all docstrings
- fix overflowing lines
- fix headers in html

IMMEDIATE:
- Create separate css document --> not working right
- Sheet object to supercede ix_list and Header; containing header and all ixs, and column names,
also n_header_lines, etc
also a set of contexts
"""

# =============================================================
# Dependencies
# =============================================================

import argparse # commandline parsing
import pandas as pd # data manipulation
import sys # file paths
from jinja2 import Environment, FileSystemLoader # html formating
from typing import * # to specify funtion inputs and outputs

from utils.Cell import Cell
from utils.Context import Context
from utils.Sheet import Sheet
from utils.constants import * #all global variables
from utils.helper_functions import clean

# =============================================================
# Function definitions
# =============================================================

def parse_commandline_args() -> Tuple[str, str]:
    """
    Parses command line arguments using argparser package to
    read in input and output file names.

    Outputs: 
     - input_file (str) : where to find the Excel spreadsheet for conversion
     - output_file (str) : where to save the ixbrl output html document
    """
    # Create custom parser for commandline runs
    parser = argparse.ArgumentParser()
    parser.add_argument('--i', type=str, metavar="input_file(xlsx)", required=True, help="Input xlsx file name")
    parser.add_argument('--o', type=str, metavar="output_file(html)", help="Output html file name")
    # parses commandline text and saves in the args object
    args = parser.parse_args()
    if args.i:
        input_file = args.i
    # if output file is not specified, save as .html version of the input file
    if args.o:
        output_file = args.o
    else:
        output_file = input_file.split(".")[0] + ".html"
    return(input_file, output_file)

def parse_contexts(contexts_file : str) -> Dict[str, Dict[str, str]]:
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
    context_name_map = {}
    for row in range(len(contexts)):
        name = contexts["Context_Name"][row].strip()
        _, _, header, _, _, index = contexts.iloc[row].apply(clean)
        if not context_name_map.get(index):
            context_name_map[index] = {header : name}
        else:
            context_name_map[index][header] = name
    return(context_name_map)


def write_html(input_xl : str,
               output_file : str,
               context_name_map : Dict[str, Dict[str, str]]):
    """ Docstring """
    # iterate through sheets, saving Sheet() objects
    input_xl = pd.ExcelFile(input_file)
    sheet_list = [Sheet(input_file, sheet_name, context_name_map) for sheet_name in input_xl.sheet_names]
    
    # Create a Jinja2 environment for html formating
    env = Environment(loader=FileSystemLoader('.'))

    # Load the template and render with vars
    template = env.get_template('templates/base.html')
    rendered_ixbrl = template.render(sheet_list = sheet_list)

    # Save the rendered template to output file
    with open(output_file, 'w') as write_location:
        write_location.write(rendered_ixbrl)
    print(f"Html file written to {output_file}")

# =============================================================
# Run file
# =============================================================

if __name__ == "__main__":
    input_file, output_file = parse_commandline_args()
    context_name_map = parse_contexts(contexts_path)
    write_html(input_file, output_file, context_name_map)
