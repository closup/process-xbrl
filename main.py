"""
A script to convert an arbitrary Excel budget into XBRL format.

Last updated: Feb 2024, K. Wheelan
"""

# =============================================================
# Dependencies
# =============================================================

import sys
import os
import pandas as pd # data manipulation
from typing import * # to specify funtion inputs and outputs

# from utils.Cell import Cell
# from utils.Context import Context
from utils.Sheet import Sheet
from utils.Acfr import Acfr
from utils.constants import * #all global variables
from utils.helper_functions import clean

from werkzeug.utils import secure_filename

# flask dependencies
from flask import Flask, request, render_template, jsonify, redirect, url_for, json
import gettext, shlex

from bs4 import BeautifulSoup

# Make arelle imports possible
base_dir = os.path.abspath(os.path.dirname(__file__))
# Add the base directory to the sys.path
sys.path.append(base_dir)
# Also add the Arelle.arelle directory inside dependencies 
arelle_dir = os.path.join(base_dir, "dependencies", "Arelle")
sys.path.append(arelle_dir)
from arelle import CntlrCmdLine
from arelle.Locale import setApplicationLocale

# =============================================================
# Constants
# =============================================================

ROOT = os.getcwd()
UPLOAD_FOLDER = 'static/input_files/webapp_uploads' # set to your own path
SPREADSHEET_EXTENSIONS = ['xlsx', 'xls']
ALLOWED_EXTENSIONS = SPREADSHEET_EXTENSIONS + ['docx', 'doc']

# =============================================================
# Flask setup
# =============================================================

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.static_folder = 'static'

# =============================================================
# Function definitions
# =============================================================

# def parse_contexts(contexts_file : str) -> Dict[str, Dict[str, str]]:
#     """
#     Function to parse contexts to create contexts reference
#     dictionaries for later
#     """   
#     # open contexts excel sheet
#     pd.read_excel(contexts_file)
#     try:
#         contexts = pd.read_excel(contexts_file)
#     except:
#         sys.exit("No context file!")
#     # create the index as its own column
#     contexts['index'] = contexts['Scope'] + "@" + contexts['Statement']
#     # create contexts reference dictionaries
#     context_name_map = {}
#     for row in range(len(contexts)):
#         name = contexts["Context_Name"][row].strip()
#         _, _, header, _, _, index = contexts.iloc[row].apply(clean)
#         if not context_name_map.get(index):
#             context_name_map[index] = {header : name}
#         else:
#             context_name_map[index][header] = name
#     return(context_name_map)


def write_html(input_file : str,
               output_file : str,
               format : str):
    """ Create inline xbrl document and save as an html file at {output_file} location """
    # iterate through sheets, saving Sheet() objects
    input_xl = pd.ExcelFile(input_file)
    # create a list of all the readable Excel sheets
    sheets = []
    for sheet_name in input_xl.sheet_names:
        if not(sheet_name in ["Label Dropdowns", "Master Info"]):
            sheets.append(Sheet(input_file, sheet_name)) 
    acfr = Acfr(sheets)

    # Load the template and render with vars
    rendered_ixbrl = render_template('xbrl/base.html', acfr = acfr, format = format)

    # Save the rendered template to output file
    with open(output_file, 'w') as write_location:
        write_location.write(rendered_ixbrl)

def create_viewer_html(output_file : str,
                       viewer_filepath : str = "templates/site/viewer.html"):
    """
    Runs Arelle and ixbrl-viewer submodules to create a viewer html and 
    accompanying javascript file.
    """
    viewer_filepath = os.path.join(ROOT, viewer_filepath)

    # command to run Arelle process
    plugins = os.path.join(ROOT, "dependencies", "ixbrl-viewer", "iXBRLViewerPlugin")
    viewer_url = "https://cdn.jsdelivr.net/npm/ixbrl-viewer@1.4.8/iXBRLViewerPlugin/viewer/dist/ixbrlviewer.js"
    args = f"--plugins={plugins} -f {output_file} --save-viewer {viewer_filepath} --viewer-url {viewer_url}"
    
    args = shlex.split(args)
    setApplicationLocale()
    gettext.install("arelle")
    CntlrCmdLine.parseAndRun(args)

    # Read in the generated HTML
    with open(viewer_filepath, 'r') as file:
        html_content = file.read()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the script tag we wish to modify
    script_tag = soup.find('script', {'src': 'ixbrlviewer.js'})
    if script_tag:
        # Update the src attribute
        script_tag['src'] = '{{ url_for(\'static\', filename=\'js/ixbrlviewer.js\') }}'

    # Write the modified HTML back out
    with open(viewer_filepath, 'w') as file:
        file.write(str(soup))

    os.rename('templates/site/ixbrlviewer.js', 'static/js/ixbrlviewer.js')

def check_ext(filename : str, file_extensions : List[str]) -> bool:
    """ Check file extension against a list of allowable extensions """
    return '.' in filename and filename.rsplit('.', 1)[1] in file_extensions 

def allowed_file(filename : str) -> bool:
    """ Check file extension against all allowed extensions """
    return check_ext(filename, ALLOWED_EXTENSIONS)

def is_spreadsheet(filename : str) -> bool:
    """ Check file extension against allowed extensions for spreadsheets """
    return check_ext(filename, SPREADSHEET_EXTENSIONS)

# =============================================================
# Flask
# =============================================================

@app.route('/')
def home():
    return render_template('site/home.html', loading=True)

@app.route('/viewer')
def view(viewer_file_name = "site/viewer.html"):
    return render_template(viewer_file_name)

@app.route('/upload', methods=['POST'])
def upload_file(output_file = "static/output/output.html", format = "gray"):
    # Check for the 'files[]' part in the request
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files submitted'}), 400  # Bad Request
    
    # Retrieve the list of files from the request
    file_list = request.files.getlist('files[]')

    # Process each file and store filenames
    filenames = []
    excel_files = []
    for file in file_list:
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'One or more of your files has a disallowed extension. Allowed extensions are: ' + ", ".join([str(i) for i in ALLOWED_EXTENSIONS])})
        if file and allowed_file(file.filename):  # allowed files are excel and docx
            filenames.append(file.filename)
        if is_spreadsheet(file.filename):
            excel_files += [file]
    if len(excel_files) != 1:
        return jsonify({'error': 'Please upload exactly one Excel file'})
    write_html(excel_files[0], output_file, format)
    #viewer_file_name = "templates/site/viewer.html"
    #create_viewer_html(output_file, viewer_file_name)
    return jsonify({'message': 'Files successfully uploaded'})

@app.route('/upload/complete', methods=['GET'])
def successful_upload():
    return render_template("site/upload.html")

# =============================================================
# Run file
# =============================================================

if __name__ == "__main__":
    contexts_path = "static/input_files/contexts.xlsx"
    #context_name_map = parse_contexts(contexts_path)
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
