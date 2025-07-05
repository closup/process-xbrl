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
// document.getElementById('upload').addEventListener('change', updateButton);

function handleUploadError(errorMessage) {
    document.getElementById('loader').style.display = 'none'; // hide loader wheel
    alert(errorMessage);    // Shows the alert with the error message
    document.getElementById('upload').value = ''; // Clear the file input
    updateButton(); // Update the file list and button state
}

function startProcessing(event) {
    event.preventDefault();
    
    // Get files in the current display order
    const fileList = document.getElementById('fileList');
    const orderedFiles = Array.from(fileList.children).map(li => {
        const fileName = li.querySelector('.filename').textContent;
        return Array.from(document.getElementById('upload').files)
            .find(file => file.name === fileName);
    });
    
    // Create new FormData with ordered files
    let formData = new FormData();
    orderedFiles.forEach(file => {
        formData.append('files[]', file);
    });

    document.getElementById('loader').style.display = 'block';
    
    const notyf = new Notyf({
        duration: 1000,  // Set default duration to 5 seconds
        position: {x:'left',y:'top'},
        types: [
            {
                type: 'info',
                background: '#00B2A9',
                icon: false
            },
            {
                type: 'error',
                duration: 5000,  // Explicitly set for error messages
                background: '#FF0000',
                dismissible: true
            }
        ]
    });

    let notificationId = notyf.open({
        type: 'info',
        message: 'Starting process...'
    });

    // Debugging
    console.log("FormData keys:");
    for (let p of formData.entries()) {
        console.log(p[0], p[1]);
    }

    // Send POST request to initiate the upload
    fetch('/upload', {
        method: 'POST',
        body: formData,
        headers: {
            'Accept-Encoding': 'identity'
        }
    }).then(response => {

        const reader = response.body.getReader();
        const decoder = new TextDecoder();

        function readStream() {
            reader.read().then(({ done, value }) => {
                if (done) {
                    console.log('Stream complete');
                    return;
                }

                const chunk = decoder.decode(value, { stream: true });

                const lines = chunk.split('\n');
                lines.forEach(line => {

                    if (line.startsWith('data:')) {
                        const message = line.slice(5).trim();
                        console.log('Processed message:', message);

                        if (message.startsWith('complete:')) {
                            console.log('Conversion complete, redirecting...');
                            const sessionId = message.split(':')[1];
                            const newTabUrl = `/upload/complete?session_id=${sessionId}`;
                            
                            notyf.dismiss(notificationId);
                            notyf.success('Conversion complete. Redirecting...');
                            document.getElementById('loader').style.display = 'none';
                            document.getElementById('uploadForm').reset();
                            updateButton();

                            window.location.href = newTabUrl;

                        } else {
                            notyf.dismiss(notificationId);
                            notificationId = notyf.open({
                                type: 'info',
                                message: message
                            });
                        }

                        if (message.startsWith('Error:')) {
                            console.log('Error received:', message);
                            document.getElementById('loader').style.display = 'none';
                            notyf.dismiss(notificationId);
                            notyf.error({
                                message: message,
                                duration: 5000,  // 5 seconds
                                dismissible: true
                            });
                            document.getElementById('uploadForm').reset();
                            updateButton();
                        }
                    }
                });

                readStream();
            }).catch(error => {
                console.error('Error in readStream:', error);
                notyf.error('An error occurred during processing');
                document.getElementById('loader').style.display = 'none';
                document.getElementById('uploadForm').reset();
                updateButton();
            });
        }

        readStream();
    }).catch(error => {
        console.error('Error:', error);
        document.getElementById('loader').style.display = 'none';
        notyf.error('An error occurred during upload');
        document.getElementById('uploadForm').reset();
        updateButton();
    });
}