"""
A script to convert an arbitrary Excel budget into XBRL format.

Last updated: March 2024, K. Wheelan
"""

# =============================================================
# Dependencies
# =============================================================

import sys
import os
from typing import * # to specify funtion inputs and outputs
from utils.Acfr import Acfr
from utils.constants import * #all global variables
from utils.helper_functions import *

# flask dependencies
from flask import Flask, request, render_template, jsonify
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
# Flask setup
# =============================================================

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.static_folder = 'static'

# =============================================================
# Function definitions
# =============================================================

def write_html(file_list : List[Any],
               output_file : str,
               format : str,
               #word_filepaths: List[str]
               ):
    """ 
    Create inline xbrl document and save as an html file at {output_file} location 
    """
    # process sheets in the excel document
    acfr = Acfr(file_list)

    # Load the template and render with vars
    rendered_ixbrl = render_template('xbrl/base.html', acfr = acfr, format = format)
    
    # Save the rendered template to output file
    with open(output_file, 'w', encoding="utf8") as write_location:
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
    with open(viewer_filepath, 'r', encoding="utf8") as file:
        html_content = file.read()

    # Parse the HTML with BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')

    # Find the script tag we wish to modify
    script_tag = soup.find('script', {'src': 'ixbrlviewer.js'})
    if script_tag:
        # Update the src attribute
        script_tag['src'] = '{{ url_for(\'static\', filename=\'js/ixbrlviewer.js\') }}'

    # Write the modified HTML back out
    with open(viewer_filepath, 'w', encoding="utf8") as file:
        file.write(str(soup))

    os.rename('templates/site/ixbrlviewer.js', 'static/js/ixbrlviewer.js')

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
    write_html(file_list, output_file, format)
    viewer_file_name = "templates/site/viewer.html"
    create_viewer_html(output_file, viewer_file_name)
    return jsonify({'message': 'Files successfully uploaded'})

@app.route('/upload/complete', methods=['GET'])
def successful_upload():
    return render_template("site/upload.html")

# =============================================================
# Run file
# =============================================================

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
