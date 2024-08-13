"""
Route definitions and endpoints for the Flask application.
"""

from typing import * # to specify funtion inputs and outputs
from app.utils import *

# flask dependencies
from flask import Blueprint, request, render_template, jsonify, Response, stream_with_context, session, redirect, url_for, send_from_directory, current_app

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

    def generate():
        try:
            yield "data: Initializing upload\n\n"

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
                yield "data: Error: No files submitted\n\n"
                return

            yield "data: Uploading files\n\n"

            # Retrieve the list of files from the request
            file_list = request.files.getlist('files[]')

            # Process each file and store filenames
            excel_files = []
            for file in file_list:
                if file.filename == '':
                    yield "data: Error: No selected file\n\n"
                    return
                if not allowed_file(file.filename):
                    yield f"data: Error: Disallowed file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}\n\n"
                    return
                
                # Save uploaded files to session input folder
                if file and allowed_file(file.filename):
                    file.save(os.path.join(input_folder, file.filename))

            yield "data: Processing and validating files\n\n"

            # Process uploaded files and save output to session output folder
            excel_files = [file for file in file_list if is_spreadsheet(file.filename)]

            if len(excel_files) == 0:
                yield "data: Error: An Excel file is missing\n\n"
                return
            elif len(excel_files) != 1:
                yield "data: Error: Please upload exactly one Excel file\n\n"
                return

            # create ixbrl file
            yield "data: Creating iXBRL file\n\n"
            write_html(file_list, output_file, format)

            yield "data: Creating viewer\n\n"
            viewer_output_path = f'app/static/sessions_data/{session_id}/output/'
            create_viewer_html(output_file, viewer_output_path)
            print('viewer created\n')

            yield "data: Conversion finishing...\n\n"

        except Exception as e:
            error_message = f"Error: {str(e)}"
            yield f"data: Error: {str(e)}\n\n"
            print(error_message)

    return Response(stream_with_context(generate()), content_type='text/event-stream')

@routes_bp.route('/upload/complete', methods=['GET'])
def successful_upload():
    # Check if session has expired
    if check_session_expiry(session):
        print("Session has expired")
        return redirect(url_for('routes_bp.home'))

    # Get the current session ID
    session_id = session.get('session_id')
    print('in successful upload func, id is: ', session_id)
    
    if not session_id:
        print("No session ID found")
        return redirect(url_for('routes_bp.home'))

    update_session_timestamp(session)

    try:
        # make sure output.html can generate images
        modify_img_paths(session_id)
        # Generate the ZIP file and save it
        generate_zip_file(session_id)

        print('before download url set')
        download_url = url_for('static', filename=f'sessions_data/{session_id}/output/converted_xbrl.zip')
        print('download url is', download_url)

        return render_template("site/upload.html", session_id=session_id, download_url=download_url)
    except Exception as e:
        print(f"Error in successful_upload: {str(e)}")
        return redirect(url_for('routes_bp.home'))

@routes_bp.route('/serve_image/<session_id>/<filename>')
def serve_image(session_id, filename):
    # Specify the directory to send from.
    images_directory = os.path.join(current_app.root_path, 'static/sessions_data', session_id, 'input/img')
    return send_from_directory(images_directory, filename)