const filesInput = document.getElementById("filesInput");
const filesList = document.getElementById("filesList");
const MAX_TOTAL_SIZE = 10000 * 1024;

filesInput.addEventListener("change", () => {

    filesList.innerHTML = "";

    const files = filesInput.files;

    let totalSize = 0;

    for (const file of files) {

        totalSize += file.size;

        const div = document.createElement("div");

        div.classList.add("me-2");
        div.textContent = file.name;
        div.classList.add(
            "border",
            "rounded",
            "p-2",
            "mb-1"
        );

        filesList.appendChild(div);
    }

    if (totalSize > MAX_TOTAL_SIZE) {

        filesInput.setCustomValidity(
            "The total file size must not exceed 10 000 KB."
        );
    } else if (files.length < 2) {
        filesInput.setCustomValidity(
            "Please select at least 2 files."
        );
    } else {
        filesInput.setCustomValidity("");
    }
});


const dataset_statusInput = document.getElementById("dataset_status");

dataset_statusInput.addEventListener("change", () => {
    if (dataset_statusInput.checked) {
        document.getElementById("tmalign_reference").disabled = false;
    } else {
        document.getElementById("tmalign_reference").disabled = true;
        document.getElementById("tmalign_reference").value = "";
    }
});