const fileInput = document.getElementById("fileInput");
const selectedFile = document.getElementById("selectedFile");
const uploadStatus = document.getElementById("uploadStatus");
const fileList = document.getElementById("fileList");

// Azure Backend URL
const API_BASE_URL =
    "https://cloudbackupphotoswebsite-c5ftd2dkccathaeu.eastasia-01.azurewebsites.net";


// ==========================================
// SELECT FILE
// ==========================================

fileInput.addEventListener("change", function () {

    const file = fileInput.files[0];

    if (file) {

        selectedFile.textContent =
            "Selected: " + file.name;

        console.log("File selected:", file.name);
    }

});


// ==========================================
// UPLOAD FILE
// ==========================================

async function uploadFile() {

    console.log("Upload button clicked");

    const file = fileInput.files[0];

    if (!file) {

        uploadStatus.textContent =
            "❌ Please choose a file first.";

        return;
    }

    uploadStatus.textContent =
        "☁️ Uploading...";

    const formData = new FormData();

    formData.append("file", file);

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/upload`,
            {
                method: "POST",
                body: formData
            }
        );

        console.log(
            "Upload response:",
            response.status
        );

        const result = await response.json();

        console.log(
            "Upload result:",
            result
        );

        if (result.success) {

            uploadStatus.textContent =
                "✅ File uploaded successfully to Azure!";

            fileInput.value = "";

            selectedFile.textContent =
                "No file selected";

            // Refresh My Files
            loadFiles();

        } else {

            uploadStatus.textContent =
                "❌ Upload failed: " +
                result.message;

        }

    } catch (error) {

        console.error(
            "Upload error:",
            error
        );

        uploadStatus.textContent =
            "❌ Cannot connect to backend.";

    }

}


// ==========================================
// LOAD FILES
// ==========================================

async function loadFiles() {

    try {

        const response = await fetch(
            `${API_BASE_URL}/api/files`
        );

        const result = await response.json();

        console.log(
            "Files from Azure:",
            result
        );

        if (!result.success) {

            fileList.innerHTML =
                "❌ Could not load files.";

            return;
        }

        fileList.innerHTML = "";

        if (result.files.length === 0) {

            fileList.innerHTML =
                "No files uploaded yet.";

            return;
        }


        // Display every file
        result.files.forEach(function(file) {

            const div =
                document.createElement("div");

            div.className = "file-card";

            div.innerHTML = `

                <h3>📄 ${file.name}</h3>

                <p>
                    Size: ${file.size} bytes
                </p>

                <a
                    href="${API_BASE_URL}/api/download/${encodeURIComponent(file.name)}"
                    target="_blank">

                    👁️ View / Download

                </a>

                <br><br>

                <button
                    onclick="deleteFile('${encodeURIComponent(file.name)}')">

                    🗑️ Delete

                </button>

            `;

            fileList.appendChild(div);

        });

    }

    catch (error) {

        console.error(
            "File loading error:",
            error
        );

        fileList.innerHTML =
            "❌ Cannot connect to backend.";

    }

}


// ==========================================
// DELETE FILE
// ==========================================

async function deleteFile(filename) {

    // Convert filename back to normal text
    filename = decodeURIComponent(filename);

    const confirmDelete = confirm(
        "Are you sure you want to delete " +
        filename +
        "?"
    );

    if (!confirmDelete) {

        return;
    }


    try {

        const response = await fetch(
            `${API_BASE_URL}/api/delete/` +
            encodeURIComponent(filename),
            {
                method: "DELETE"
            }
        );


        const result = await response.json();


        if (result.success) {

            alert(
                "✅ File deleted successfully!"
            );

            // Refresh My Files
            loadFiles();

        } else {

            alert(
                "❌ Delete failed: " +
                result.message
            );

        }

    }

    catch (error) {

        console.error(
            "Delete error:",
            error
        );

        alert(
            "❌ Cannot connect to backend."
        );

    }

}


// ==========================================
// LOAD FILES WHEN WEBSITE OPENS
// ==========================================

loadFiles();
