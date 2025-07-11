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
from flask import render_template, url_for

# Make arelle imports possible
base_dir = os.path.abspath(nth_parent_dir(__file__, 3))
# Add the base directory to the sys.path
sys.path.append(base_dir)
# Also add the Arelle.arelle directory inside dependencies 
arelle_dir = os.path.join(base_dir, "dependencies", "Arelle")
sys.path.append(arelle_dir)
from arelle import CntlrCmdLine
from arelle.Locale import setApplicationLocale
from arelle.CntlrCmdLine import parseAndRun
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

    # Check that file exists
    if not os.path.exists(output_file):
        raise FileNotFoundError(f"Output file does not exist: {output_file}")

    output_file = os.path.abspath(output_file)
    viewer_filepath = os.path.join(ROOT, viewer_outpath, 'viewer.html')

    # command to run Arelle process
    viewer_url = "https://cdn.jsdelivr.net/npm/ixbrl-viewer@1.4.48/iXBRLViewerPlugin/viewer/dist/ixbrlviewer.js"
    args = f"--plugins=ixbrl-viewer -f {output_file} --save-viewer {viewer_filepath} --viewer-url {viewer_url}"
    
    args = shlex.split(args)
    setApplicationLocale()
    gettext.install("arelle")
    print("Validating XBRL...")
    try:
        parseAndRun(args)
        print("XBRL validation complete")
    except Exception as e:
        print(f"Error during XBRL validation: {str(e)}")
        raise
    
    # Read in the generated HTML
    print("Creating interactive viewer...")
    try:
        with open(viewer_filepath, 'r', encoding="utf8") as file:
            html_content = file.read()
        print("HTML content read successfully")
    except Exception as e:
        print(f"Error reading HTML file: {str(e)}")
        return

    # Parse the HTML with BeautifulSoup
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        print("HTML parsed successfully")
    except Exception as e:
        print(f"Error parsing HTML: {str(e)}")
        return

    # Find the script tag we wish to modify
    script_tag = soup.find('script', {'src': 'ixbrlviewer.js'})
    if script_tag:
        # Update the src attribute
        script_tag['src'] = url_for('static', filename='js/ixbrlviewer.js')
        print("Script tag updated")
    else:
        print("Error: JS script tag not found for viewer HTML")

    # Write the modified HTML back out
    print("Writing modified HTML file...")
    try:
        with open(viewer_filepath, 'w', encoding="utf8") as file:
            file.write(str(soup))
        print("Modified HTML file written successfully")
    except Exception as e:
        print(f"Error writing modified HTML file: {str(e)}")
        return

    # Move the ixbrlviewer.js file
    viewer_js_path = os.path.join(viewer_outpath, 'ixbrlviewer.js')
    destination_js_path = 'app/static/js/ixbrlviewer.js'
    print(f"Moving {viewer_js_path} to {destination_js_path}")
    try:
        os.rename(viewer_js_path, destination_js_path)
        print("ixbrlviewer.js moved successfully")
    except Exception as e:
        print(f"Error moving ixbrlviewer.js: {str(e)}")

    print("create_viewer_html function completed")