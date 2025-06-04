// Function to show the modal
function showModal() {
    const modal = document.getElementById("licenseModal");
    modal.style.display = "block";
}

// Function to close the modal
function closeModal() {
    const modal = document.getElementById("licenseModal");
    modal.style.display = "none";
}

// Show the modal when the page loads
window.onload = function() {
    showModal();
};