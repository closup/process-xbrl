"""
Route definitions and endpoints for the Flask application.
"""

from typing import * # to specify funtion inputs and outputs
from app.utils import *

# flask dependencies
from flask import Blueprint, request, render_template, jsonify

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
    # Set default values
    output_file = "app/static/output/output.html"
    format = "gray"

    # Check for the 'files[]' part in the request
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files submitted'}), 400  # Bad Request
    
    print("Uploading files...")

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
    # confirm that there is exactly one Excel file among the uploads
    if len(excel_files) != 1:
        return jsonify({'error': 'Please upload exactly one Excel file'})
    # create ixbrl file
    print("Converting Excel to inline XBRL...")
    write_html(file_list, output_file, format)
    # create page for the interactive viewer (prints progress in create_viewer_html fn)
    viewer_file_name = "app/templates/site/viewer.html"
    create_viewer_html(output_file, viewer_file_name)
    return jsonify({'message': 'Files successfully uploaded'})

@routes_bp.route('/upload/complete', methods=['GET'])
def successful_upload():
    return render_template("site/upload.html")