// Make items draggable
function makeDraggable() {
    const draggables = document.querySelectorAll('.draggable');
    const container = document.getElementById('fileList');

    draggables.forEach(draggable => {
        draggable.addEventListener('dragstart', function(event) {
            draggable.classList.add('dragging');
            event.dataTransfer.setData('text/plain', null); // Necessary to make draggable in Firefox
        });

        draggable.addEventListener('dragend', function() {
            draggable.classList.remove('dragging');
        });
    });

    container.addEventListener('dragover', function(event) {
        event.preventDefault();
        const afterElement = getDragAfterElement(container, event.clientY);
        const draggable = document.querySelector('.dragging');
        if (afterElement == null) {
            container.appendChild(draggable);
        } else {
            container.insertBefore(draggable, afterElement);
        }
    });
}

// Helper function to determine where to insert dragged item
function getDragAfterElement(container, y) {
    const draggableElements = [...container.querySelectorAll('.draggable:not(.dragging)')];

    return draggableElements.reduce((closest, child) => {
        const box = child.getBoundingClientRect();
        const offset = y - box.top - box.height / 2;
        if (offset < 0 && offset > closest.offset) {
            return { offset: offset, element: child };
        } else {
            return closest;
        }
    }, { offset: Number.NEGATIVE_INFINITY }).element;
}

function updateButton() {
    var input = document.getElementById('upload');
    var fileList = document.getElementById('fileList');
    var dragInstruction = document.getElementById('dragInstruction');
    var fileInputButtonText = document.getElementById('fileInputButtonText');
    var convertButton = document.getElementById('convert-button');

    fileList.innerHTML = ''; // Clear the existing list

    // Update label text and drag instructions
    if (input.files && input.files.length > 0) {
        dragInstruction.style.display = 'block'; // Show the drag instruction text
        fileInputButtonText.textContent = 'Choose new files';  // Change button text
        convertButton.style.display = 'block'; // Show the convert button
        convertButton.value = 'Combine and convert file(s)'; // Display a generic message
    } else {
        dragInstruction.style.display = 'none'; // Hide the drag instruction text
        fileInputButtonText.textContent = 'Choose File(s)'; // Reset button text to original
        convertButton.style.display = 'none'; // Hide the convert button
    }

    Array.from(input.files).forEach((file, index) => {
        let li = document.createElement('li');
        li.setAttribute('class', 'draggable file-item');
        li.setAttribute('draggable', 'true');

        const fileNameSpan = document.createElement('span');
        fileNameSpan.textContent = file.name;
        fileNameSpan.setAttribute('class', 'filename');

        const deleteButton = document.createElement('button');
        deleteButton.textContent = 'Delete';
        deleteButton.setAttribute('class', 'delete-btn');

        deleteButton.addEventListener('click', function() {
            input.files = removeFileAtIndex(input.files, index); // Remove the file from the input
            li.remove(); // Remove the list item from the DOM
            updateButton(); // Update the button and file list
        });

        li.appendChild(fileNameSpan);
        li.appendChild(deleteButton);
        fileList.appendChild(li);
    });

    makeDraggable(); // Make the new file list items draggable
}

// Helper function to remove a file at a specific index from a FileList
function removeFileAtIndex(fileList, index) {
    const dataTransfer = new DataTransfer();
    Array.from(fileList).forEach((file, i) => {
        if (i !== index) {
            dataTransfer.items.add(file);
        }
    });
    return dataTransfer.files;
}

function clearAndHideFileList() {
    var fileListElement = document.getElementById('fileList');
    var submitButton = document.getElementById('convert-button');
    var dragInstruction = document.getElementById('dragInstruction');
    var fileInput = document.getElementById('upload');

    // Clear the current file list
    fileListElement.innerHTML = '';

    // Hide the file list, drag instructions, and submit button
    fileListElement.style.display = 'none';
    submitButton.style.display = 'none';
    if (dragInstruction) {
        dragInstruction.style.display = 'none';
    }

    // Clear the file input
    fileInput.value = '';
}

function updateFileList() {
    var fileInput = document.getElementById('upload');
    var fileListElement = document.getElementById('fileList');
    var submitButton = document.getElementById('convert-button');
    var dragInstruction = document.getElementById('dragInstruction');

    // Clear existing list
    fileListElement.innerHTML = '';

    // Populate list with new files
    for (var i = 0; i < fileInput.files.length; i++) {
        var listItem = document.createElement('li');
        listItem.textContent = fileInput.files[i].name;
        fileListElement.appendChild(listItem);
    }

    // Show the file list, drag instructions, and submit button if files are selected
    if (fileInput.files.length > 0) {
        fileListElement.style.display = '';
        submitButton.style.display = '';
        if (dragInstruction) {
            dragInstruction.style.display = '';
        }
    }
}

// Add event listener to file input to handle new selections
document.getElementById('upload').addEventListener('change', updateButton);

function handleUploadError(errorMessage) {
    document.getElementById('loader').style.display = 'none'; // hide loader wheel
    alert(errorMessage);    // Shows the alert with the error message
    document.getElementById('upload').value = ''; // Clear the file input
    updateButton(); // Update the file list and button state
}

function startProcessing(event) {
    event.preventDefault();  // Stops the normal form submission process

    // Show the loader as soon as the process starts
    document.getElementById('loader').style.display = 'block';

    var formData = new FormData();
    var input = document.getElementById('upload');

    // Iterate over the files and append each file to FormData
    Array.from(input.files).forEach((file) => {
        formData.append('files[]', file);
    });

    // AJAX request to Flask backend
    fetch('/upload', {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        // Make sure to handle HTTP errors even if the response is not ok
        if (response.redirected) {
            window.location.href = response.url;
        } else if (!response.ok) {
            return response.json().then(err => { throw err; });
        }
        return response.json();
    })
    .then(data => {
        if (data.error) {
            document.getElementById('loader').style.display = 'none'; // hide loader wheel
            handleUploadError(data.error);
        } else {
            // No error, proceed to the success page
            console.log('Success:', data);
            window.location.href = '/upload/complete';
        }
    })
    .catch(error => {
        console.error('Error:', error);
        document.getElementById('loader').style.display = 'none'; // hide loader wheel
        handleUploadError('An unexpected error occurred. Please try again.');
    });
}
