import os
from .constants import *
from .helper_functions import *
from .xbrl_processing import *

def create_session_folders(base_path, session_id):
    input_folder = os.path.join(base_path, session_id, 'input')
    output_folder = os.path.join(base_path, session_id, 'output')
    os.makedirs(input_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)
    return input_folder, output_folder

def get_file_list(request, field_name='files[]'):
    """Return file list or error message if not present."""
    if field_name not in request.files:
        return None, "No files submitted"
    file_list = request.files.getlist(field_name)
    if not file_list or all(f.filename == '' for f in file_list):
        return None, "No selected file"
    return file_list, None

def validate_and_save_files(file_list, allowed_exts, input_folder):
    """Check file types and save, return (saved_file_list, error)"""
    saved_files = []
    for file in file_list:
        if not allowed_file(file.filename):
            allowed_str = ', '.join(allowed_exts)
            return None, f"Disallowed file extension. Allowed: {allowed_str}"
        save_path = os.path.join(input_folder, file.filename)
        file.save(save_path)
        saved_files.append(file)
    return saved_files, None

def find_excel_files(file_list, is_excel_fn):
    excels = [f for f in file_list if is_excel_fn(f.filename)]
    if len(excels) == 0:
        return None, "An Excel file is missing"
    elif len(excels) != 1:
        return None, "Please upload exactly one Excel file"
    return excels, None