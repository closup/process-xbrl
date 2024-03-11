function updateButton(value) {
    var fileName = value.split('\\').pop();
    
    if (fileName) {
        document.getElementById('convert-button').style.display = 'block';
        document.getElementById('convert-button').value = 'Convert ' + fileName;
    }
    
}
function updateDocsButton(files,labelId) {
    document.getElementById(labelId).style.backgroundColor = 'green'
    var newFileName = "";
    for (var i = 0; i < files.length; i++) {
        newFileName += files[i].name + ", ";
    }
    newFileName = newFileName.slice(0, -2); 
    
}

// Call this function whenever you want to set the previous file name
function startProcessing() {
    document.getElementById('loader').style.display = 'block';
    
}
