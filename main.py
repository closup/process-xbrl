"""
A script to convert an arbitrary Excel budget into XBRL format.

Last updated: Feb 2024, K. Wheelan
"""

# =============================================================
# Dependencies
# =============================================================

import subprocess
import sys
import os
import argparse # commandline parsing
import pandas as pd # data manipulation
from jinja2 import Environment, FileSystemLoader # html formating
from typing import * # to specify funtion inputs and outputs

# from utils.Cell import Cell
# from utils.Context import Context
from utils.Sheet import Sheet
from utils.Acfr import Acfr
from utils.constants import * #all global variables
from utils.helper_functions import clean
from utils.word_comments import ExtractComments

# flask dependencies
from flask import Flask, request, render_template, session
from werkzeug.utils import secure_filename
import gettext, shlex

from bs4 import BeautifulSoup

import mammoth
import string

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
               format : str,
               wordfiles: Dict[str, Dict[str, str]]):
    """ Create inline xbrl document and save as an htm`l file at {output_file} location """
    # iterate through sheets, saving Sheet() objects
    input_xl = pd.ExcelFile(input_file)
    acfr = Acfr([Sheet(input_file, sheet_name, context_name_map) for sheet_name in input_xl.sheet_names if sheet_name != "Label Dropdowns"])

    #extracted the contents from word
    cover_page, _ = extract_text_and_images_from_docx(wordfiles['cover'])
    auditors_letter, _ = extract_text_and_images_from_docx(wordfiles['auditor'])
    notes, _ = extract_text_and_images_from_docx(wordfiles['notes'])
    supplementary_info, _ = extract_text_and_images_from_docx(wordfiles['info'])
    statistical_section, _ = extract_text_and_images_from_docx(wordfiles['statistic'])

    # Load the template and render with vars
    rendered_ixbrl = render_template('xbrl/base.html', acfr = acfr, format = format,cover_page=cover_page, auditors_letter=auditors_letter,  notes=notes, supplementary_info=supplementary_info, statistical_section=statistical_section) 

    # Save the rendered template to output file
    with open(output_file, 'w', encoding="utf8") as write_location:
        write_location.write(rendered_ixbrl)

# def load_dependencies():
#     """ clone arelle and ixbrl viewer """
#     # Define the directories where the repositories should be
#     arelle_dir = "dependencies/Arelle"
#     ixbrl_viewer_dir = "dependencies/ixbrl-viewer"

#     # Check if the directories exist
#     arelle_version = "2.17.5"
#     ixbrl_viewer_version = "1.4.9"
#     if not os.path.exists(arelle_dir):
#         subprocess.run(["git", "clone", "https://github.com/Arelle/Arelle.git", arelle_dir], check=True)
#         subprocess.run(["git", "checkout", arelle_version], cwd=arelle_dir, check=True)
#     if not os.path.exists(ixbrl_viewer_dir):
#         subprocess.run(["git", "clone", "https://github.com/Workiva/ixbrl-viewer.git", ixbrl_viewer_dir], check=True)  
#         subprocess.run(["git", "checkout", ixbrl_viewer_version], cwd=ixbrl_viewer_dir, check=True)


def create_viewer_html(output_file : str,
                       viewer_filepath : str = "templates/site/viewer.html"):
    """
    Runs Arelle adn ixbrl-viewer submodules to create a viewer html and 
    accompanying javascript file.
    """
    viewer_filepath = os.path.join(ROOT, viewer_filepath)

    # Make arelle imports possible
    base_dir = os.path.abspath(os.path.dirname(__file__))
    # Add the base directory to the sys.path
    sys.path.append(base_dir)
    # Also add the Arelle.arelle directory inside dependencies 
    arelle_dir = os.path.join(base_dir, "dependencies", "Arelle")
    sys.path.append(arelle_dir)
    
    from arelle import CntlrCmdLine 
    from arelle.Locale import setApplicationLocale
    # command to run Arelle process
    plugins = os.path.join(ROOT, "dependencies", "ixbrl-viewer", "iXBRLViewerPlugin")
    
    viewer_filepath=viewer_filepath.replace("\\",'/') # added this for solve some errors in file directory  
    plugins=plugins.replace("\\",'/') # added this for solve some errors in file directory  
    # print(viewer_filepath,plugins)
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

    # os.rename('templates/site/ixbrlviewer.js', 'static/js/ixbrlviewer.js')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS  


# added the function for get the word conntent 
def extract_text_and_images_from_docx(file_path):
    
    from utils.constants import p_id

    result = mammoth.convert_to_html(file_path)
    html = result.value  # Extracted HTML content
    images = result.messages  # Extracted images, if any    
    updated_html =''
    soup = BeautifulSoup(html,"html.parser")
    p_html =[]
    # Remove a tags    
    for a in soup.find_all(['a']):
        a.decompose()

    for p_tag in soup.find_all('p'):
        validated =True
        
        if p_tag.text !='':
            for char in p_tag.text:
                if char in string.ascii_letters:
                    validated = False 
                    break

            if validated:        
                p_html.append(p_tag)
    result = ExtractComments.get_comments_and_text(file_path,html)
    if result: 
        for  i in range (0,len(result['comments'])):
            comment, selected_text, p_count =result['comments'][i],result['selected_text'][i],result['count'][i]
            context_id = result['context_id'][i]
            p_html[p_count].replace_with(f'''\n\n<ix:nonFraction contextRef="{context_id}" name="acfr:{comment}" unitRef="pure" id="p{p_id}" decimals="0" format="ixt:num-dot-decimal" >
    {selected_text}
</ix:nonFraction>\n\n''')
            p_id +=1
            
            
        updated_html = str(soup)
        updated_html = updated_html.replace('&gt;', '>')
        updated_html = updated_html.replace('&lt;', '<')           
        return updated_html,images
    
    updated_html = str(soup)
    return updated_html, images

# =============================================================
# Flask
# =============================================================

@app.route('/')
def home():
    return render_template('site/home.html', loading=True)

@app.route('/viewer')
def view(viewer_file_name = "site/viewer.html"):
    return render_template(viewer_file_name )

@app.route('/upload', methods=['POST'])
def upload_file(output_file = "static/output/output.html", format = "gray"):
    if 'file' not in request.files:
        return "No file"
    
    wordfiles={}
    # Example: Print the file names
    wordfiles['cover']= request.files['coverfile']
    wordfiles['auditor']= request.files['auditorfile']
    wordfiles['notes']= request.files['notesfile']
    wordfiles['info']= request.files['infofile']
    wordfiles['statistic']= request.files['statisticalfile']

    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    if file and allowed_file(file.filename):
        write_html(file, output_file, context_name_map, format,wordfiles)
        viewer_file_name = "templates/site/viewer.html"
        create_viewer_html(output_file, viewer_file_name)

        return render_template("site/upload.html")
    else:
        return 'Invalid file type'

@app.route('/processing')
def load():
    return render_template("site/processing.html")

# =============================================================
# Run file
# =============================================================

if __name__ == "__main__":
    contexts_path = "static/input_files/contexts.xlsx"
    context_name_map = parse_contexts(contexts_path)
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
