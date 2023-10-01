"""
A script to convert an arbitrary Excel budget into XBRL format.

Last updated: September 2023, K. Wheelan

TODO:
- replace contexts sheet with a dictionary w just relevant info (or sheet)
- figure out contexts objects
- replace contexts maps? -- replace with elements.xlsx?
- split functions into modules
- add all docstrings
- fix overflowing lines
- add header to html docs
- get base html to work
"""

# =============================================================
# Dependencies
# =============================================================

import argparse # commandline parsing
import pandas as pd # data manipulation
import sys # file paths
from jinja2 import Environment, FileSystemLoader # html formating
from typing import * # to specify funtion inputs and outputs

from utils.IX import IX
from utils.Context import Context
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
            
def process_header(sheet : pd.core.frame.DataFrame) -> Tuple[int, str]:
        """
        Function to extract excel header data and clean sheet
        """
        # read header data
        n_header_lines = sheet[sheet.columns[-1]].first_valid_index()
        #### HARDCODING ####
        scope = clean(sheet["City of Clayton"][0])
        statement = clean(sheet["City of Clayton"][1])
        return n_header_lines, f"{scope}@{statement}"

def clean_sheet(input_file : str) -> Tuple[pd.core.frame.DataFrame, str]:
    """
    Function to read budget excel sheet and match contexts

    Input:
    - input_file (str) : where to look for the excel financial statement

    Output
    - sheet_data (pandas df) : Cleaned excel data
    - index (str) : scope@statment (ex. TODO )
    """   
    input_xl = pd.ExcelFile(input_file)
    for sheet_name in input_xl.sheet_names:
        # read in one sheet of the excel doc
        sheet_data = pd.read_excel(input_xl, sheet_name=sheet_name)        
        
        # read header data, remove header, and reassign column names
        n_header_lines, scope_statement = process_header(sheet_data)
        sheet_data.columns = sheet_data.iloc[n_header_lines].apply(clean)
        sheet_data = sheet_data.drop(list(range(n_header_lines + 1)))
        
        # add an index for the original row number (# dropped rows + row # - 1 header row)
        sheet_data["row"] = list(n_header_lines + sheet_data.index - 1)
       
        # reshape long for ease
        extra_left_cols = 2  # HARDCODING # 1 for xbrl element + 1 for row labels
        id_cols = list(sheet_data.columns[:extra_left_cols])
        val_cols = list(sheet_data.columns[extra_left_cols:])
        id_cols += ["row"]
        n_rows_orig = len(sheet_data) # num of rows before reshaping
        sheet_data = pd.melt(sheet_data, id_vars = id_cols, value_vars = val_cols, var_name = "header")
        
        # determine cells and resultant ids
        cols = [ALPHABET[i] for i in list(extra_left_cols + (sheet_data.index // n_rows_orig))]
        sheet_data['col'] = cols
        cells = [c + str(r) for c,r in zip(cols, sheet_data["row"])]
        sheet_data["id"] = [f'{sheet_name.replace(" ","")}_{cell}' for cell in cells]
        # set up to create header in the html table -- True if first row
        sheet_data["row_start"] = [(r == min(sheet_data["row"])) for r in sheet_data["row"]]
    return sheet_data, scope_statement

def process_cells(input_file : str) -> List[IX]:
    """
    Create an IX object for each cell
    """
    ix_list = []
    df, scope_statement = clean_sheet(input_file)
    # sort the sheet by row, then column for easy html parsing
    df = df.sort_values(by=['row', 'col'])
    for i, row in df.iterrows():
        ix = IX(row["nan"], row["xbrl_element"], row["id"], row["value"], 
                scope_statement, row["header"], context_name_map)
        ix_list.append(ix)
    return(ix_list)

def process_contexts(ix_list : List[IX]) -> Set[Context]:
    """
    Create a set of Context objects; one for each used context
    in the list of cell data with IXBRL tags
    """
    return({})

def write_final_html(ix_list : List[IX], output_file : str):
    """ Docstring """
    # Create a Jinja2 environment
    env = Environment(loader=FileSystemLoader('.'))
    # Load the template and render with vars
    template = env.get_template('templates/base.html')
    rendered_ixbrl = template.render(ix_list = ix_list)

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
    ix_list = process_cells(input_file)
    write_final_html(ix_list, output_file)


# input_file = "example.xlsx"
# parse_contexts(CONTEXTS_FILE)
# print(context_name_map)
# read_sheet(input_file)