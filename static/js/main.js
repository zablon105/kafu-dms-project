// ================= PREVIEW =================
function previewFile(fileUrl) {

    const modal = document.getElementById("previewModal");
    const frame = document.getElementById("previewFrame");

    if (!modal || !frame) return;

    let fullUrl = window.location.origin + fileUrl;
    let viewerUrl = "";

    if (fileUrl.toLowerCase().endsWith(".pdf")) {
        viewerUrl = fullUrl;
    } else {
        viewerUrl = "https://docs.google.com/gview?url=" + fullUrl + "&embedded=true";
    }

    frame.src = viewerUrl;
    modal.style.display = "block";
}

function closePreview() {

    const modal = document.getElementById("previewModal");
    const frame = document.getElementById("previewFrame");

    if (!modal || !frame) return;

    modal.style.display = "none";
    frame.src = "";
}

// Close modal outside click
window.addEventListener("click", function(event) {
    const modal = document.getElementById("previewModal");
    if (modal && event.target === modal) {
        closePreview();
    }
});


// ================= DELETE =================
function deleteDocument(button) {

    const docId = button.getAttribute("data-id");

    if (!confirm("Are you sure you want to delete this document?")) {
        return;
    }

    fetch("/delete/" + docId + "/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken()
        }
    })
    .then(function(response) {
        if (response.ok) {

            let row = button.closest("tr");
            if (row) row.remove();   // ✅ FIXED

            showToast("Document deleted successfully");
            addNotification("Document deleted");

        } else {
            showToast("Failed to delete document", "error");
        }
    })
    .catch(function(error) {
        console.error(error);
        showToast("Error deleting document", "error");
    });
}


// ================= CSRF =================
function getCSRFToken() {

    let cookieValue = null;
    let name = "csrftoken";

    if (document.cookie && document.cookie !== "") {

        let cookies = document.cookie.split(";");

        for (let i = 0; i < cookies.length; i++) {

            let cookie = cookies[i].trim();

            if (cookie.startsWith(name + "=")) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }

    return cookieValue;
}


// ================= SHARE =================
let currentDocId = null;

function openShareModal(button) {
    currentDocId = button.getAttribute("data-id");
    const modal = document.getElementById("shareModal");
    if (modal) modal.style.display = "block";
}

function closeShareModal() {
    const modal = document.getElementById("shareModal");
    if (modal) modal.style.display = "none";
}

function shareDocument() {

    const lecturerSelect = document.getElementById("lecturerSelect");

    if (!lecturerSelect) return;

    const lecturerId = lecturerSelect.value;

    if (!lecturerId) {
        alert("Please select a lecturer");
        return;
    }

    fetch("/share/" + currentDocId + "/", {
        method: "POST",
        headers: {
            "X-CSRFToken": getCSRFToken(),
            "Content-Type": "application/x-www-form-urlencoded"
        },
        body: "lecturer=" + lecturerId
    })
    .then(function(response) {
        if (response.ok) {
            showToast("Document shared successfully");
            addNotification("Document shared successfully");
            closeShareModal();
        } else {
            showToast("Failed to share document", "error");
        }
    })
    .catch(function(error) {
        console.error(error);
        showToast("Error sharing document", "error");
    });
}


// ================= LIVE SEARCH =================
const searchInput = document.getElementById("searchInput");

if (searchInput) {

    searchInput.addEventListener("keyup", function () {

        const query = searchInput.value;

        fetch("/?q=" + query)
        .then(response => response.text())
        .then(html => {

            let parser = new DOMParser();
            let doc = parser.parseFromString(html, "text/html");

            let newTable = doc.getElementById("documentTable");

            if (newTable) {
                document.getElementById("documentTable").innerHTML = newTable.innerHTML;
            }

        });
    });

}


// ================= AJAX PAGINATION =================
function loadPage(event, url) {

    event.preventDefault();

    fetch(url)
    .then(response => response.text())
    .then(html => {

        let parser = new DOMParser();
        let doc = parser.parseFromString(html, "text/html");

        let newTable = doc.getElementById("documentTable");
        let newPagination = doc.getElementById("paginationContainer");

        if (newTable) {
            document.getElementById("documentTable").innerHTML = newTable.innerHTML;
        }

        if (newPagination) {
            document.getElementById("paginationContainer").innerHTML = newPagination.innerHTML;
        }

    });
}


// ================= TOAST =================
function showToast(message, type="success") {

    const container = document.getElementById("toastContainer");
    if (!container) return;

    const toast = document.createElement("div");
    toast.className = "toast " + type;
    toast.innerText = message;

    container.appendChild(toast);

    setTimeout(() => {
        toast.remove();
    }, 3000);
}


// ================= DARK MODE =================
function toggleDarkMode() {

    document.body.classList.toggle("dark-mode");

    if (document.body.classList.contains("dark-mode")) {
        localStorage.setItem("darkMode", "enabled");
    } else {
        localStorage.setItem("darkMode", "disabled");
    }
}

window.addEventListener("DOMContentLoaded", function () {

    if (localStorage.getItem("darkMode") === "enabled") {
        document.body.classList.add("dark-mode");
    }

});



// ================= CHART =================
/// ================= SMART CHART =================
document.addEventListener("DOMContentLoaded", function () {

    const canvas = document.getElementById("uploadChart");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");

    let months = [];
    let counts = [];

    try {
        months = JSON.parse(document.getElementById("months-data").textContent);
        counts = JSON.parse(document.getElementById("counts-data").textContent);
    } catch (e) {
        console.warn("Fallback data used");
    }

    // ✅ HANDLE SINGLE DATA POINT
    if (months.length === 1) {
        months = ["", months[0], ""];
        counts = [counts[0], counts[0], counts[0]];
    }

    new Chart(ctx, {
        type: "line",
        data: {
            labels: months,
            datasets: [{
                label: "Documents Uploaded",
                data: counts,
                borderWidth: 3,
                tension: 0.4,
                fill: true,
                borderColor: "#4f46e5",
                backgroundColor: "rgba(79,70,229,0.1)",
                pointRadius: 5
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            }
        }
    });

});

// ================= SIDEBAR =================
function toggleSidebar() {

    const sidebar = document.querySelector(".sidebar");
    const main = document.querySelector(".main");

    if (!sidebar || !main) return;

    // Desktop collapse
    sidebar.classList.toggle("collapsed");
    main.classList.toggle("collapsed");

    // Mobile slide
    sidebar.classList.toggle("active");
}

// ================= DRAG & DROP UPLOAD =================
// ================= DRAG & DROP UPLOAD =================
document.addEventListener("DOMContentLoaded", function () {

    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const fileName = document.getElementById("fileName");

    if (!dropZone || !fileInput) return;

    // Click to open file picker
    dropZone.addEventListener("click", () => fileInput.click());

    // Show selected file
    fileInput.addEventListener("change", () => {

        if (fileInput.files.length > 0) {

            const name = fileInput.files[0].name;

            fileName.textContent = "Selected: " + name;

            // ✅ ADD NOTIFICATION (SAFE)
            if (typeof addNotification === "function") {
                addNotification("File selected: " + name);
            }

            // ✅ OPTIONAL TOAST (if you want)
            if (typeof showToast === "function") {
                showToast("File ready: " + name);
            }
        }
    });

    // Drag over
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    // Drag leave
    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    // Drop file
    dropZone.addEventListener("drop", (e) => {

        e.preventDefault();
        dropZone.classList.remove("dragover");

        const files = e.dataTransfer.files;

        if (files.length > 0) {

            fileInput.files = files;

            const name = files[0].name;

            fileName.textContent = "Selected: " + name;

            // ✅ ADD NOTIFICATION (SAFE)
            if (typeof addNotification === "function") {
                addNotification("File dropped: " + name);
            }

            // ✅ OPTIONAL TOAST
            if (typeof showToast === "function") {
                showToast("File ready: " + name);
            }
        }
    });

});
// ================= PASSWORD TOGGLE =================
function togglePassword() {

    const input = document.getElementById("passwordField");
    const icon = document.querySelector(".toggle-password");

    if (!input || !icon) return;

    if (input.type === "password") {
        input.type = "text";
        icon.classList.replace("fa-eye", "fa-eye-slash");
    } else {
        input.type = "password";
        icon.classList.replace("fa-eye-slash", "fa-eye");
    }
}

// ================= PAGE LOADER =================
window.addEventListener("load", function () {

    const loader = document.querySelector(".loader-bar");

    if (!loader) return;

    let width = 0;

    let interval = setInterval(() => {
        width += 10;
        loader.style.width = width + "%";

        if (width >= 100) {
            clearInterval(interval);
            setTimeout(() => {
                document.getElementById("pageLoader").style.display = "none";
            }, 300);
        }
    }, 50);
});

// ================= REAL PAGE LOADER =================
window.addEventListener("load", function () {

    const loader = document.getElementById("loader-screen");
    const text = document.getElementById("loadingText");
    const bar = document.getElementById("progressFill");

    if (!loader || !text || !bar) return;

    let progress = 0;

    let interval = setInterval(() => {

        progress += Math.floor(Math.random() * 10) + 5;

        if (progress > 100) progress = 100;

        text.innerText = progress + "%";
        bar.style.width = progress + "%";

        if (progress === 100) {
            clearInterval(interval);

            setTimeout(() => {
                loader.style.display = "none";
            }, 400);
        }

    }, 100);

});

// ================= NOTIFICATION SYSTEM =================
let notifications = [];
function toggleNotifications() {

    const dropdown = document.getElementById("notifDropdown");

    dropdown.classList.toggle("active");

    // mark as read
    fetch("/notifications/read/");
}

// ADD NOTIFICATION
function addNotification(message) {

    const dropdown = document.getElementById("notifDropdown");
    const count = document.getElementById("notifCount");

    if (!dropdown || !count) return;

    // Remove empty text
    const empty = dropdown.querySelector(".empty");
    if (empty) empty.remove();

    // Create item
    const item = document.createElement("div");
    item.className = "notif-item";
    item.innerText = message;

    dropdown.prepend(item);

    // Update count
    notifications.push(message);
    count.innerText = notifications.length;
}

document.addEventListener("DOMContentLoaded", function () {

    const bell = document.getElementById("notificationBell");
    const dropdown = document.getElementById("notificationDropdown");

    bell.addEventListener("click", function (e) {
        e.preventDefault();

        // Toggle dropdown
        if (dropdown.style.display === "none") {
            dropdown.style.display = "block";

            // Mark notifications as read
            fetch("/notifications/read/", {
                method: "POST",
                headers: {
                    "X-CSRFToken": getCSRFToken(),
                },
            }).then(() => {
                const count = document.getElementById("notifCount");
                if (count) count.style.display = "none";
            });

        } else {
            dropdown.style.display = "none";
        }
    });

});

// CSRF TOKEN HELPER
function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
}


// 🔄 AUTO FETCH EVERY 5 SECONDS
setInterval(fetchNotifications, 5000);

function fetchNotifications() {

    fetch("/notifications/fetch/")
    .then(response => response.json())
    .then(data => {

        const dropdown = document.getElementById("notifDropdown");
        const count = document.getElementById("notifCount");

        if (!dropdown) return;

        dropdown.innerHTML = "";

        if (data.notifications.length > 0) {

            data.notifications.forEach(n => {
                const div = document.createElement("div");
                div.className = "notif-item";
                div.innerText = n.message;
                dropdown.appendChild(div);
            });

            if (count) {
                count.style.display = "inline-block";
                count.innerText = data.notifications.length;
            }

        } else {
            dropdown.innerHTML = "<p class='empty'>No notifications</p>";
            if (count) count.style.display = "none";
        }

    });
}