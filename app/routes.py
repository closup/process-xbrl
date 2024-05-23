"""
Route definitions and endpoints for the Flask application.
"""

from typing import * # to specify funtion inputs and outputs
from app.utils import *

# flask dependencies
from flask import Blueprint, request, render_template, jsonify, session, redirect, url_for, send_from_directory, current_app

import uuid, shutil

# =============================================================
# Set up routes
# =============================================================

# A blueprint for all routes
routes_bp = Blueprint('routes_bp', __name__)

@routes_bp.route('/')
def home():
    if check_session_expiry(session):
        return redirect(url_for('routes_bp.home'))
    
    return render_template('site/home.html', loading=True)

@routes_bp.route('/viewer')
def view():
    return render_template("site/viewer.html")

@routes_bp.route('/upload', methods=['POST'])
def upload_file():
    # Generate a unique session ID
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    update_session_timestamp(session)

    input_folder = os.path.join('app/static/sessions_data/', session_id, 'input')
    output_folder = os.path.join('app/static/sessions_data/', session_id, 'output')

    # Create session folders if they don't exist
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    # Set default values
    output_file = os.path.join(output_folder, "output.html")
    format = "gray"

    # Check for the 'files[]' part in the request
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files submitted'}), 400  # Bad Request
    
    print("Uploading files...")

    # Retrieve the list of files from the request
    file_list = request.files.getlist('files[]')

    # Process each file and store filenames
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
    # TODO Change location of saving
    viewer_file_name = "app/templates/site/viewer.html"
    create_viewer_html(output_file, viewer_file_name)

    return jsonify({'message': 'Files successfully uploaded'})

@routes_bp.route('/upload/complete', methods=['GET'])
def successful_upload():
    # Check if session has expired
    if check_session_expiry(session):
        return redirect(url_for('routes_bp.home'))

    # Get the current session ID
    session_id = session.get('session_id')
    print('in successful upload func, id is: ', session_id)
    
    update_session_timestamp(session)

    download_url = url_for('static', filename=f'sessions_data/{session_id}/output/output.html')


    return render_template("site/upload.html", session_id=session_id, download_url=download_url)

@routes_bp.route('/serve_image/<filename>')
def serve_image(filename):
    # Specify the directory to send from.
    images_directory = os.path.join(current_app.root_path, 'static/img')
    return send_from_directory(images_directory, filename)