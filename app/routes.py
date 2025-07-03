"""
Route definitions and endpoints for the Flask application.
"""

from typing import * # to specify funtion inputs and outputs
from app.utils import *

# flask dependencies
from flask import Blueprint, request, render_template, session, redirect, url_for, send_from_directory, current_app, send_file

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
    return generate(session_id)

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