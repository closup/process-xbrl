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
from utils.word_comments import ExtractComments

# flask dependencies
from flask import Flask, request, render_template, session, jsonify, redirect, url_for, json
import gettext, shlex

from bs4 import BeautifulSoup

import mammoth
import string

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

def write_html(input_file : str,
               output_file : str,
               format : str,
               wordfiles: Dict[str, Dict[str, str]]):
    """ Create inline xbrl document and save as an html file at {output_file} location """
    # process sheets in the excel document
    acfr = Acfr(input_file)

    #extracted the contents from word
    # TODO: fix this hard coding
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

def create_viewer_html(output_file : str,
                       viewer_filepath : str = "templates/site/viewer.html"):
    """
    Runs Arelle and ixbrl-viewer submodules to create a viewer html and 
    accompanying javascript file.
    """
    viewer_filepath = os.path.join(ROOT, viewer_filepath)

    # command to run Arelle process
    plugins = os.path.join(ROOT, "dependencies", "ixbrl-viewer", "iXBRLViewerPlugin")
    # TODO: fix this 
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


# added the function for get the word conntent 
def extract_text_and_images_from_docx(file_path):

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
        
        if p_tag.text.strip() !='' :
            for char in p_tag.text:
                if char in string.ascii_letters:
                    validated = False 
                    break
                
                elif (len(p_tag.text)>5 and ('-' in p_tag.text or '%' in p_tag.text)):
                    validated = False 
                    break


            if validated:        
                p_html.append(p_tag)
    
    result = ExtractComments.get_comments_and_text(file_path,html)
    if result: 
        for  i in range (0,len(result['comments'])):
            comment, selected_text, p_count =result['comments'][i],result['selected_text'][i],result['count'][i]
            context_id = result['context_id'][i]
            p_html[p_count].replace_with(f'''\n\n<ix:nonFraction contextRef="{context_id}" name="acfr:{comment}" unitRef="pure" id="p{ExtractComments.p_id}" decimals="0" format="ixt:num-dot-decimal" >
    {selected_text}
</ix:nonFraction>\n\n''')
            ExtractComments.p_id +=1
            
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
