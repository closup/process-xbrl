function updateButton(value) {
    var fileName = value.split('\\').pop();
    if (fileName) {
        document.getElementById('convert-button').style.display = 'block';
        document.getElementById('convert-button').value = 'Convert ' + fileName;
    }
}

function startProcessing() {
  document.getElementById('loader').style.display = 'block';
}