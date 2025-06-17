"""
Route definitions and endpoints for the Flask application.
"""

from typing import * # to specify funtion inputs and outputs
from app.utils import *

# flask dependencies
from flask import Blueprint, request, render_template, Response, stream_with_context, session, redirect, url_for, send_from_directory, current_app, send_file

import uuid, time

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
    if not session_id:
        return "Session not found", 404

    output_path = os.path.join(current_app.root_path, 'static', 'sessions_data', 
                              session_id, 'output')
    
    if not os.path.isdir(output_path):
        return "Directory not found", 404

    return send_from_directory(output_path, 'viewer.html')

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

            yield "data: Created folders\n\n"

            # Set default values
            output_file = os.path.join(output_folder, "output.html")
            format = "gray"
        
        except Exception as e:
            error_message = f"Error: {str(e)}"
            yield f"data: Error: {str(e)}\n\n"
            print(error_message)

        try: 
            # Check for the 'files[]' part in the request
            if 'files[]' not in request.files:
                yield "data: Error: No files submitted\n\n"
                return

            yield "data: Uploading files\n\n"
            time.sleep(1)

            # Retrieve the list of files from the request
            file_list = request.files.getlist('files[]')

            yield "data: Retrieving files\n\n"

        except Exception as e:
            error_message = f"Error: {str(e)}"
            yield f"data: Error: {str(e)}\n\n"
            print(error_message)

        # Process each file and store filenames
        try: 
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
            time.sleep(1)

        except Exception as e:
            error_message = f"Error: {str(e)}"
            yield f"data: Error: {str(e)}\n\n"
            print(error_message)
            

        try:
            # Process uploaded files and save output to session output folder
            excel_files = [file for file in file_list if is_spreadsheet(file.filename)]

            if len(excel_files) == 0:
                yield "data: Error: An Excel file is missing\n\n"
                return
            elif len(excel_files) != 1:
                yield "data: Error: Please upload exactly one Excel file\n\n"
                return
        except Exception as e:
            error_message = f"Error: {str(e)}"
            yield f"data: Error: {str(e)}\n\n"
            print(error_message)

        try: 
            # create ixbrl file
            yield "data: Creating iXBRL file\n\n"
            write_html(file_list, output_file, format)

            yield "data: Creating viewer\n\n"
            viewer_output_path = f'app/static/sessions_data/{session_id}/output/'
        except Exception as e:
            error_message = f"Error: {str(e)}"
            yield f"data: Error: {str(e)}\n\n"
            print(error_message)
            
        try:
                create_viewer_html(output_file, viewer_output_path)
                print('viewer created\n')
        except Exception as e:
                print(f"Error creating viewer: {str(e)}")
                yield f"data: Error creating viewer: {str(e)}\n\n"
                return
            
        yield "data: Conversion finishing...\n\n"
        yield f"data: complete:{session_id}\n\n"  # Make sure this line is present

    return Response(stream_with_context(generate()), content_type='text/event-stream')

@routes_bp.route('/upload/complete', methods=['GET'])
def successful_upload():
    print("Entering successful_upload function")
    session_id = request.args.get('session_id') or session.get('session_id')
    
    if not session_id:
        print("No session ID found")
        return redirect(url_for('routes_bp.home'))

    try:
        # Generate the ZIP file with HTML and images
        generate_zip_file(session_id)
        return render_template("site/upload.html", session_id=session_id)
    except Exception as e:
        print(f"Error in successful_upload: {str(e)}")
        return redirect(url_for('routes_bp.home'))

@routes_bp.route('/download_zip/<session_id>')
def download_zip(session_id):
    try:
        # Use current_app.root_path to get absolute path
        zip_path = os.path.join(current_app.root_path, 'static', 'sessions_data', 
                              session_id, 'output', 'converted_xbrl.zip')
        
        if not os.path.exists(zip_path):
            print(f"ZIP file not found at: {zip_path}")
            return redirect(url_for('routes_bp.home'))
            
        print(f"Sending file from: {zip_path}")
        
        return send_file(
            zip_path,
            mimetype='application/zip',
            as_attachment=True,
            download_name='converted_xbrl.zip'
        )
    except Exception as e:
        print(f"Error in download_zip: {str(e)}")
        return redirect(url_for('routes_bp.home'))

@routes_bp.route('/serve_image/<session_id>/<filename>')
def serve_image(session_id, filename):
    # Specify the directory to send from.
    images_directory = os.path.join(current_app.root_path, 'static/sessions_data', session_id, 'input/img')
    return send_from_directory(images_directory, filename)

@routes_bp.route('/license')
def license():
    return render_template('site/license.html', loading=True)