let uploadedFilePath = ""; // Variable to store uploaded file path

// Handle PDF Upload
document.getElementById("upload-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const formData = new FormData();
    const fileInput = document.getElementById("file");
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch("/upload", { method: "POST", body: formData });
        const result = await response.json();

        if (response.ok) {
            alert(result.message);
            uploadedFilePath = result.file_path; // Save file path
        } else {
            alert(`Upload failed: ${result.error}`);
        }
    } catch (error) {
        console.error("Error uploading file:", error);
        alert("An error occurred while uploading the file.");
    }
});

// Handle Question Submission
document.getElementById("ask-form").addEventListener("submit", async (e) => {
    e.preventDefault();

    const question = document.getElementById("question").value;

    if (!uploadedFilePath) {
        alert("Please upload a PDF before asking a question.");
        return;
    }

    try {
        const response = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question, file_path: uploadedFilePath }),
        });

        const result = await response.json();

        if (response.ok) {
            document.getElementById("response").innerText = result.response;
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        console.error("Error fetching response:", error);
        alert("An error occurred while fetching the response.");
    }
});
