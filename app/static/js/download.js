// Download XBRL as HTML and save it in session folder

function changeDownloadLocation() {
    var sessionID = "{{ session.get('session_id') }}";
    window.alert(sessionID);

    // Get the current URL of the file to download
    var currentURL = "{{ url_for('static', filename='output/output.html') }}";

    // Define the new download location with session ID
    var newURL = currentURL.replace("output/output.html", sessionID + "/output/output.html");

    // Set the new download location
    document.getElementById("downloadLink").setAttribute("href", newURL);
}