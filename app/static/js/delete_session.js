window.addEventListener("beforeunload", function(event) {
    // Send an AJAX request to delete the session folder
    var sessionID = "{{ session.get('session_id') }}";  // Get the session ID
    console.log(sessionID);
    var url = "/delete_session?session_id=" + sessionID;
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.send();
});
