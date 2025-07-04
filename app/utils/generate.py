# import os
# from flask import request, Response, stream_with_context
# from .constants import *
# from .helper_functions import *
# from .xbrl_processing import *

# def create_folders(session_id):
#     input_folder = os.path.join('app/static/sessions_data/', session_id, 'input')
#     output_folder = os.path.join('app/static/sessions_data/', session_id, 'output')

#     # Create session folders if they don't exist
#     os.makedirs(input_folder, exist_ok=True)
#     os.makedirs(output_folder, exist_ok=True)

#     output_file = os.path.join(output_folder, "output.html")

#     return input_folder, output_file

# import os
# from flask import request, Response, stream_with_context
# from .constants import *
# from .helper_functions import *
# from .xbrl_processing import *

# def create_folders(session_id):
#     input_folder = os.path.join('app/static/sessions_data/', session_id, 'input')
#     output_folder = os.path.join('app/static/sessions_data/', session_id, 'output')

#     # Create session folders if they don't exist
#     os.makedirs(input_folder, exist_ok=True)
#     os.makedirs(output_folder, exist_ok=True)

#     output_file = os.path.join(output_folder, "output.html")

#     return input_folder, output_file

# def download_files(input_folder, files):
#         # Check for the 'files[]' part in the request
#         if 'files[]' not in files:
#             yield "data: Error: No files submitted\n\n"
#             return

#         # Retrieve the list of files from the request
#         file_list = files.getlist('files[]')

#         for file in file_list:
#             if file.filename == '':
#                 yield "data: Error: No selected file\n\n"
#                 return
#             if not allowed_file(file.filename):
#                 yield f"data: Error: Disallowed file extension. Allowed: {', '.join(ALLOWED_EXTENSIONS)}\n\n"
#                 return
            
#             # Save uploaded files to session input folder
#             if file and allowed_file(file.filename):
#                 file.save(os.path.join(input_folder, file.filename))

#         yield "data: Processing and validating files\n\n"
#         return file_list

# def check_for_excel(file_list):
#     excel_files = [file for file in file_list if is_spreadsheet(file.filename)]

#     if len(excel_files) == 0:
#         yield "data: Error: An Excel file is missing\n\n"
#         return
#     elif len(excel_files) != 1:
#         yield "data: Error: Please upload exactly one Excel file\n\n"
#         return

# def generate(session_id, files):
#     yield "data: Initializing upload\n\n"
#     input_folder, output_file = create_folders(session_id)

#     ok, file_list_or_error = download_files(input_folder, files)
#     if not ok:
#         yield f"data: {file_list_or_error}\n\n"
#         return

#     file_list = file_list_or_error

#     ok, error = check_for_excel(file_list)
#     if not ok:
#         yield f"data: {error}\n\n"
#         return

#     yield "data: Creating iXBRL file\n\n"
#     write_html(file_list, output_file, format)
#     yield "data: Creating viewer\n\n"
#     viewer_output_path = f'app/static/sessions_data/{session_id}/output/'

#     try:
#         create_viewer_html(output_file, viewer_output_path)
#     except Exception as e:
#         yield f"data: Error creating viewer: {str(e)}\n\n"
#         return

#     yield "data: Conversion finishing...\n\n"
#     yield f"data: complete:{session_id}\n\n"

# def check_for_excel(file_list):
#     excel_files = [file for file in file_list if is_spreadsheet(file.filename)]

#     if len(excel_files) == 0:
#         yield "data: Error: An Excel file is missing\n\n"
#         return
#     elif len(excel_files) != 1:
#         yield "data: Error: Please upload exactly one Excel file\n\n"
#         return

# def generate(session_id, files):
    
#     yield "data: Initializing upload\n\n"
#     # create folders
#     input_folder, output_file = create_folders(session_id)
#     # process uploaded files
#     file_list = download_files(input_folder, files)
#     # check for an excel file
#     check_for_excel(file_list)
#     # create XBRL file
#     yield "data: Creating iXBRL file\n\n"
#     write_html(file_list, output_file, format)
#     yield "data: Creating viewer\n\n"
#     viewer_output_path = f'app/static/sessions_data/{session_id}/output/'
        
#     try:
#         create_viewer_html(output_file, viewer_output_path)
#     except Exception as e:
#         yield f"data: Error creating viewer: {str(e)}\n\n"
#         return
        
#     yield "data: Conversion finishing...\n\n"
#     yield f"data: complete:{session_id}\n\n"  # Make sure this line is present

#     return Response(stream_with_context(generate()), content_type='text/event-stream')