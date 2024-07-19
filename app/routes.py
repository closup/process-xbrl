"""
Route definitions and endpoints for the Flask application.
"""

from typing import * # to specify funtion inputs and outputs
from app.utils import *

# flask dependencies
from flask import Blueprint, request, render_template, jsonify, send_file, session, redirect, url_for, send_from_directory, current_app

import uuid

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
    session_id = session.get('session_id')
    print('pulled', session_id)

    session_template_path = os.path.join('static', 'sessions_data', session_id, 'output')
    full_path = os.path.join(current_app.root_path, session_template_path)
    
    print('session_template_path:', session_template_path)
    print('full_path:', full_path)
    
    if not os.path.isdir(full_path):
        return "Directory not found", 404

    return send_from_directory(full_path, 'viewer.html')

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
    output_file = os.path.join(output_folder, "viewer.html")
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
    if len(excel_files) == 0:
        return jsonify({'error': 'An Excel file is missing'}), 400
    elif len(excel_files) != 1:
        return jsonify({'error': 'Please upload exactly one Excel file'}), 400
    
    # define output path
    output_file = os.path.join(output_folder, 'viewer.html')

    # create ixbrl file
    print("Converting Excel to inline XBRL...")
    write_html(file_list, output_file, format)
    # create page for the interactive viewer (prints progress in create_viewer_html fn)
    # TEMP viewer_output_path = "app/templates/site/viewer.html"
    viewer_output_path = f'app/static/sessions_data/{session_id}/output/'
    create_viewer_html(output_file, viewer_output_path)

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

    # make sure output.html can generate images
    modify_img_paths(session_id)
    # Generate the ZIP file and save it
    generate_zip_file(session_id)

    print('before download url set')
    download_url = url_for('static', filename=f'sessions_data/{session_id}/output/converted_xbrl.zip')
    print('download url is', download_url)

    return render_template("site/upload.html", session_id=session_id, download_url=download_url)

@routes_bp.route('/serve_image/<session_id>/<filename>')
def serve_image(session_id, filename):
    # Specify the directory to send from.
    images_directory = os.path.join(current_app.root_path, 'static/sessions_data', session_id, 'input/img')
    return send_from_directory(images_directory, filename)