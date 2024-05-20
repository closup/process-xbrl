// Download XBRL as HTML and save it in session folder

function changeDownloadLocation() {
    var sessionID = "{{ session.get('session_id') }}";
    console.log(sessionID);

    var newURL = "/static/sessions_data/" + sessionID + "/output/output.html";
    
    // Set the new download location
    document.getElementById("downloadLink").setAttribute("href", newURL);
}