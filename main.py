"""
A script to convert an arbitrary Excel budget into XBRL format.

Last updated: December 2023, K. Wheelan

TODO:
NEXT ISSUE:
- replace contexts maps? -- replace with elements.xlsx?
separate a setup file

CODE QUALITY:
- add all docstrings
"""

# =============================================================
# Dependencies
# =============================================================

import subprocess
import sys
import os
import platform # to check OS

import argparse # commandline parsing
import pandas as pd # data manipulation
from jinja2 import Environment, FileSystemLoader # html formating
from typing import * # to specify funtion inputs and outputs

# for opening in ixbrl viewers
import webbrowser

# from utils.Cell import Cell
# from utils.Context import Context
from utils.Sheet import Sheet
from utils.Acfr import Acfr
from utils.constants import * #all global variables
from utils.helper_functions import clean

# flask dependencies
from flask import Flask, request, render_template
from werkzeug.utils import secure_filename
import gettext, shlex

# =============================================================
# Constants
# =============================================================

ROOT = os.getcwd()
UPLOAD_FOLDER = 'static/input_files/webapp_uploads' # set to your own path
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls', 'tsv'}

# =============================================================
# Flask setup
# =============================================================

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.static_folder = 'static'

# =============================================================
# Function definitions
# =============================================================

def parse_commandline_args() -> Tuple[str, str, str, str]:
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
    parser.add_argument('--f', type=str, metavar="html_formating", help="HTML formating option('color','gray', or 'None')")
    parser.add_argument('--c', type=str, metavar="contexts file", help="file path to contexts file")
    # parses commandline text and saves in the args object
    args = parser.parse_args()
    input_file = args.i
    # if output file is not specified, save as .html version of the input file
    if args.o:
        output_file = args.o
    else:
        output_file = input_file.split(".")[0] + ".html"
    format = args.f 
    contexts_path = args.c
    return(input_file, output_file, format, contexts_path)

def parse_contexts(contexts_file : str) -> Dict[str, Dict[str, str]]:
    """
    Function to parse contexts to create contexts reference
    dictionaries for later
    """   
    # open contexts excel sheet
    pd.read_excel(contexts_file)
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


def write_html(input_file : str,
               output_file : str,
               context_name_map : Dict[str, Dict[str, str]],
               format : str):
    """ Create inline xbrl document and save as an html file at {output_file} location """
    # iterate through sheets, saving Sheet() objects
    input_xl = pd.ExcelFile(input_file)
    acfr = Acfr([Sheet(input_file, sheet_name, context_name_map) for sheet_name in input_xl.sheet_names if sheet_name != "Label Dropdowns"])
    
    # Create a Jinja2 environment for html formating
    env = Environment(loader=FileSystemLoader('.'))

    # Load the template and render with vars
    template = env.get_template('templates/base.html')
    rendered_ixbrl = template.render(acfr = acfr, format = format)

    # Save the rendered template to output file
    with open(output_file, 'w') as write_location:
        write_location.write(rendered_ixbrl)

    print("File written")

def load_dependencies():
    """ clone arelle and ixbrl viewer """
    # Define the directories where the repositories should be
    arelle_dir = "dependencies/arelle"
    ixbrl_viewer_dir = "dependencies/ixbrl-viewer"

    # Check if the directories exist
    arelle_version = "2.17.5"
    ixbrl_viewer_version = "1.4.9"
    if not os.path.exists(arelle_dir):
        subprocess.run(["git", "clone", "https://github.com/Arelle/Arelle.git", arelle_dir], check=True)
        subprocess.run(["git", "checkout", arelle_version], cwd=arelle_dir, check=True)
    if not os.path.exists(ixbrl_viewer_dir):
        subprocess.run(["git", "clone", "https://github.com/Workiva/ixbrl-viewer.git", ixbrl_viewer_dir], check=True)  
        subprocess.run(["git", "checkout", ixbrl_viewer_version], cwd=ixbrl_viewer_dir, check=True)


def create_viewer_html(output_file : str,
                       viewer_filepath : str = "ixbrl-viewer.html"):

    # This is very slow
    # TODO Speed up
    # Maybe it's downloading the dependencies each time?
    # TODO add a javascript progress wheel
    
    load_dependencies()
    viewer_filepath = os.path.join(ROOT, viewer_filepath)

    # Make arelle imports possible
    base_dir = os.path.abspath(os.path.dirname(__file__))
    # Add the base directory to the sys.path
    sys.path.append(base_dir)
    # Also add the arelle.arelle directory inside dependencies 
    arelle_dir = os.path.join(base_dir, "dependencies/arelle")
    sys.path.append(arelle_dir)

    from dependencies.arelle.arelle import CntlrCmdLine
    from dependencies.arelle.arelle.Locale import setApplicationLocale

    # command to run Arelle process
    plugins = os.path.join(ROOT, "dependencies", "ixbrl-viewer", "iXBRLViewerPlugin")
    viewer_url = "https://cdn.jsdelivr.net/npm/ixbrl-viewer@1.4.8/iXBRLViewerPlugin/viewer/dist/ixbrlviewer.js"
    viewer_filepath = os.path.join("templates", viewer_filepath)
    args = f"--plugins={plugins} -f {output_file} --save-viewer {viewer_filepath} --viewer-url {viewer_url}"
    
    args = shlex.split(args)
    setApplicationLocale()
    gettext.install("arelle")
    CntlrCmdLine.parseAndRun(args)
    print("created html")
    return(viewer_filepath)

# =============================================================
# Flask
# =============================================================

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS  

@app.route("/")
def index(active = "inactive"):
    return render_template('upload.html', active = active)

@app.route('/viewer')
def view(viewer_file_name = "ixbrl-viewer.html"):
    return render_template(viewer_file_name)


@app.route('/upload', methods=['POST'])
def upload_file(output_file = "static/output/output.html", format = "gray"):
    if 'file' not in request.files:
        return "No file"
    
    file = request.files['file']

    if file.filename == '':
        return 'No selected file'
        
    if file and allowed_file(file.filename):
        render_template("processing.html")
        write_html(file, output_file, context_name_map, format)
        viewer_file_name = "viewer.html"
        create_viewer_html(output_file, viewer_file_name)
        return index(active = "")
    else:
        return 'Invalid file type'

# =============================================================
# Run file
# =============================================================

if __name__ == "__main__":
    contexts_path = "static/input_files/contexts.xlsx"
    context_name_map = parse_contexts(contexts_path)
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
    
