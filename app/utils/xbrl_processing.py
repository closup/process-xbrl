"""
Doc string
"""

# =============================================================
# Dependencies
# =============================================================

import sys
import os
import gettext, shlex
from bs4 import BeautifulSoup
from app.models import Acfr
from typing import *
from app.utils.constants import * #all global variables
from app.utils.helper_functions import *
from flask import render_template

# Make arelle imports possible
base_dir = os.path.abspath(nth_parent_dir(__file__, 3))
# Add the base directory to the sys.path
sys.path.append(base_dir)
# Also add the Arelle.arelle directory inside dependencies 
arelle_dir = os.path.join(base_dir, "dependencies", "Arelle")
sys.path.append(arelle_dir)
from arelle import CntlrCmdLine
from arelle.Locale import setApplicationLocale

# =============================================================
# Function definitions
# =============================================================

def write_html(file_list : List[Any],
               output_file : str,
               format : str,
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
                       viewer_outpath : str):
    """
    Runs Arelle and ixbrl-viewer submodules to create a viewer html and 
    accompanying javascript file.
    """
    viewer_filepath = os.path.join(ROOT, viewer_outpath, 'viewer.html')

    # command to run Arelle process
    plugins = os.path.join(ROOT, "dependencies", "ixbrl-viewer", "iXBRLViewerPlugin")
    viewer_url = "https://cdn.jsdelivr.net/npm/ixbrl-viewer@1.4.8/iXBRLViewerPlugin/viewer/dist/ixbrlviewer.js"
    args = f"--plugins={plugins} -f {output_file} --save-viewer {viewer_filepath} --viewer-url {viewer_url}"
    
    args = shlex.split(args)
    setApplicationLocale()
    gettext.install("arelle")
    print("Validating XBRL...")
    CntlrCmdLine.parseAndRun(args)

    # Read in the generated HTML
    print("Creating interactive viewer...")
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
    print("Writing files...")
    with open(viewer_filepath, 'w', encoding="utf8") as file:
        file.write(str(soup))

    viewer_js_path = os.path.join(viewer_outpath, 'ixbrlviewer.js')
    os.rename(viewer_js_path, 'app/static/js/ixbrlviewer.js')