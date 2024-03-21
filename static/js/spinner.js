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

function updateSubmitButtonState() {
  var input = document.getElementById('upload');
  var convertButton = document.getElementById('convert-button');
  if(input.files.length > 0) { // Check if any files were selected
      convertButton.style.display = 'block'; // Show the convert button
      convertButton.value = 'Combine and convert ' + input.files.length + ' file(s)'; // Display the number of files
  } else {
      convertButton.style.display = 'none'; // Hide the convert button if no files are selected
  }
}

function updateButton() {
  var input = document.getElementById('upload');
  var fileList = document.getElementById('fileList');
  var dragInstruction = document.getElementById('dragInstruction');
  var fileInputButtonText = document.getElementById('fileInputButtonText');
  fileList.innerHTML = ''; // Clear the existing list

  // Update label text and drag instructions
  if (input.files && input.files.length > 0) {
      dragInstruction.style.display = 'block'; // Show the drag instruction text
      fileInputButtonText.textContent = 'Choose new files';  // Change button text
  } else {
      dragInstruction.style.display = 'none'; // Hide the drag instruction text
      fileInputButtonText.textContent = 'Choose File(s)'; // Reset button text to original
  }

  Array.from(input.files).forEach((file, index) => {
    let li = document.createElement('li');
    li.textContent = file.name;
    li.setAttribute('class', 'draggable');
    li.setAttribute('draggable', true);
    fileList.appendChild(li);
  });

  makeDraggable(); // Make the new file list items draggable
  updateSubmitButtonState(); // Update the display of the submit button
}

function clearAndHideFileList() {
  var fileListElement = document.getElementById('fileList');
  var submitButton = document.getElementById('convert-button');
  var dragInstruction = document.getElementById('dragInstruction');

  // Clear the current file list
  fileListElement.innerHTML = '';
  
  // Hide the file list, drag instructions, and submit button
  fileListElement.style.display = 'none';
  submitButton.style.display = 'none';
  if (dragInstruction) {
      dragInstruction.style.display = 'none';
  }
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
document.getElementById('upload').addEventListener('change', updateFileList);

function handleUploadError(errorMessage) {
  document.getElementById('loader').style.display = 'none'; // hide loader wheel
  alert(errorMessage);    // Shows the alert with the error message
  clearAndHideFileList(); // Clears and hides the file list
  submitButton.style.display = 'none';
          if (dragInstruction) {
              dragInstruction.style.display = 'none';
          }
}

function startProcessing(event) {
  event.preventDefault();  // Stops the normal form submission process
  
  // Show the loader as soon as the process starts
  document.getElementById('loader').style.display = 'block';

  var formData = new FormData();
  var fileListElement = document.getElementById('fileList');

  // Iterate over the list and append each file to FormData
  Array.from(fileListElement.children).forEach((listItem) => {
      var fileName = listItem.textContent;
      var fileInput = document.getElementById('upload');
      for (var i = 0; i < fileInput.files.length; i++) {
          if (fileInput.files[i].name === fileName) {
              formData.append('files[]', fileInput.files[i]);
              break;
          }
      }
  });

  // AJAX request to Flask backend
  fetch('/upload', {
      method: 'POST',
      body: formData,
  })
  .then(response => {
    // Make sure to handle HTTP errors even if the response is not ok
    if (!response.ok) {
        throw new Error('Network response was not ok');
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
      //document.getElementById('loader').style.display = 'none'; // hide loader wheel
      //handleUploadError('An unexpected error occurred. Please try again.');
  });
}