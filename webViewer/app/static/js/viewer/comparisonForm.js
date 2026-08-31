const filesInput = document.getElementById("filesInput");
const filesList = document.getElementById("filesList");

filesInput.addEventListener("change", () => {

    filesList.innerHTML = "";

    const files = filesInput.files;

    if (files.length < 2) {
        filesInput.setCustomValidity(
            "Please select at least 2 files."
        );
    } else {
        filesInput.setCustomValidity("");
    }

    for (const file of files) {

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
});