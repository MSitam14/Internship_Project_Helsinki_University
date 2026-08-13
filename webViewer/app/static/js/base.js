const logo = document.getElementById("divNavBarLogo");

logo.addEventListener("click", () => {
    window.location.href = "{{ url_for('viewer.index') }}";
});

const sidebar = document.getElementById("sidebar");
const toggleBtn = document.getElementById("toggleBtn");

// Restaurer
if (localStorage.getItem("sidebarCollapsed") === "true") {
    sidebar.classList.add("collapsed");
}

// Sauvegarder
toggleBtn.addEventListener("click", () => {

    sidebar.classList.toggle("collapsed");

    localStorage.setItem(
        "sidebarCollapsed",
        sidebar.classList.contains("collapsed")
    );
});

function showErrorPopup(text) {
    const modal = document.createElement("div");

    modal.innerHTML = `
                <div class="modal fade" id="errorModal" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">

                            <div class="modal-header">
                                <h5 class="modal-title">Error</h5>
                            </div>

                            <div class="modal-body">
                                <p>${text}</p>
                            </div>

                            <div class="modal-footer">
                                <button type="button" class="btn btn-primary" id="errorHomeButton">
                                    Return to home
                                </button>
                            </div>

                        </div>
                    </div>
                </div>
            `;

    document.body.appendChild(modal);

    const modalElement = document.getElementById("errorModal");
    const bootstrapModal = new bootstrap.Modal(modalElement, {
        backdrop: "static",
        keyboard: false
    });
    bootstrapModal.show();

    document.getElementById("errorHomeButton").addEventListener("click", () => {
        window.location.href = "/";
    });

    // Supprime la modal du DOM après fermeture
    modalElement.addEventListener("hidden.bs.modal", () => {
        modalElement.remove();
    });
}