"""
Route definitions and endpoints for the Flask application.
"""

from typing import * # to specify funtion inputs and outputs
from app.utils import *

# flask dependencies
from flask import Blueprint, request, render_template, jsonify, session

import uuid

# =============================================================
# Set up routes
# =============================================================

# A blueprint for all routes
routes_bp = Blueprint('routes_bp', __name__)

@routes_bp.route('/')
def home():
    return render_template('site/home.html', loading=True)

@routes_bp.route('/viewer')
def view():
    return render_template("site/viewer.html")

@routes_bp.route('/upload', methods=['POST'])
def upload_file():
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id

    input_folder = os.path.join('app/static', session_id, 'input')
    output_folder = os.path.join('app/static', session_id, 'output')

    # Create session folders if they don't exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # Set default values
    output_file = "app/static/output/output.html"
    format = "gray"

    # Check for the 'files[]' part in the request
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files submitted'}), 400  # Bad Request
    
    print("Uploading files...")

    # Retrieve the list of files from the request
    file_list = request.files.getlist('files[]')
    print('filelist', file_list)

    # Process each file and store filenames
    filenames = []
    excel_files = []
    for file in file_list:
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        if not allowed_file(file.filename):
            return jsonify({'error': 'One or more of your files has a disallowed extension. Allowed extensions are: ' + ", ".join([str(i) for i in ALLOWED_EXTENSIONS])})
        
        # Save uploaded files to session input folder
        if file and allowed_file(file.filename):
            file.save(os.path.join(input_folder, file.filename))
    
    # Process uploaded files and save output to session output folder
    excel_files = [file for file in file_list if is_spreadsheet(file.filename)]
    print('test', excel_files)
    if len(excel_files) != 1:
        return jsonify({'error': 'Please upload exactly one Excel file'})
    
    # define output path
    output_file = os.path.join(output_folder, 'output.html')

    # create ixbrl file
    print("Converting Excel to inline XBRL...")
    write_html(file_list, output_file, format)
    # create page for the interactive viewer (prints progress in create_viewer_html fn)
    viewer_file_name = "app/templates/site/viewer.html"
    create_viewer_html(output_file, viewer_file_name)

    return jsonify({'message': 'Files successfully uploaded'})


@routes_bp.route('/check_session')
def check_session():
    if 'session_id' in session:
        session_id = session['session_id']
        return f"Session ID: {session_id}"
    else:
        return "Session not found"


@routes_bp.route('/upload/complete', methods=['GET'])
def successful_upload():
    return render_template("site/upload.html")