@app.route('/')
def home():
    return render_template('site/home.html', loading=True)

@app.route('/viewer')
def view(viewer_file_name = "site/viewer.html"):
    return render_template(viewer_file_name)

@app.route('/upload', methods=['POST'])
def upload_file(output_file = "static/output/output.html", format = "gray"):
    # Check for the 'files[]' part in the request
    if 'files[]' not in request.files:
        return jsonify({'error': 'No files submitted'}), 400  # Bad Request
    
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
    if len(excel_files) != 1:
        return jsonify({'error': 'Please upload exactly one Excel file'})
    write_html(file_list, output_file, format)
    viewer_file_name = "templates/site/viewer.html"
    create_viewer_html(output_file, viewer_file_name)
    return jsonify({'message': 'Files successfully uploaded'})

@app.route('/upload/complete', methods=['GET'])
def successful_upload():
    return render_template("site/upload.html")