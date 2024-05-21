window.addEventListener("beforeunload", function(event) {
    event.preventDefault()

    // Send an AJAX request to delete the session folder
    var sessionID = window.sessionID; // Get the session ID
    console.log('js session id', sessionID);
    var url = "/delete_session?session_id=" + encodeURIComponent(sessionID);
    var xhr = new XMLHttpRequest();
    xhr.open("GET", url);
    xhr.send();
});
