"""
Route definitions and endpoints for the Flask application.
"""

from typing import * # to specify funtion inputs and outputs
from app.utils import *

# flask dependencies
from flask import Blueprint,  Response, stream_with_context, request, render_template, session, redirect, url_for, send_from_directory, current_app, send_file

import uuid
import time

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
    session_id = str(uuid.uuid4())
    session['session_id'] = session_id
    update_session_timestamp(session)

    # This gets the *directory* containing the current file (not where your shell is, but where THIS .py file is).
    PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
    base_path = os.path.join(PROJECT_ROOT, 'static', 'sessions_data')

    def generate():
        try:
            yield "data: Initializing upload\n\n"
            input_folder, output_folder = create_session_folders(base_path, session_id)
            output_file = os.path.join(output_folder, "output.html")
            format = "gray"

            file_list, error = get_file_list(request, 'files[]')
            if error:
                yield f"data: Error: {error}\n\n"
                return

            yield "data: Uploading files\n\n"
            time.sleep(1)

            saved_files, error = validate_and_save_files(file_list, ALLOWED_EXTENSIONS, input_folder)
            if error:
                yield f"data: Error: {error}\n\n"
                return

            yield "data: Processing and validating files\n\n"
            time.sleep(1)

            excels, error = find_excel_files(saved_files, is_spreadsheet)
            if error:
                yield f"data: Error: {error}\n\n"
                return

            yield "data: Creating iXBRL file\n\n"
            write_html(saved_files, output_file, format)

            yield "data: Creating viewer\n\n"
            viewer_output_path = os.path.join(output_folder)
            try:
                create_viewer_html(output_file, viewer_output_path)
            except Exception as e:
                yield f"data: Error creating viewer: {str(e)}\n\n"
                return

            yield "data: Conversion finishing...\n\n"
            yield f"data: complete:{session_id}\n\n"

        except Exception as e:
            yield f"data: Error: {str(e)}\n\n"

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