const hotspot_type = [
    "C.1", "C.2", "C.3", "C.ar", "C.cat",
    "Co.oh", "Cr.oh", "N.1", "N.2", "N.3",
    "N.4", "N.am", "N.pl3", "O.2", "O.3",
    "O.3.wat", "O.co2", "P.3", "Ru.oh",
    "S.2", "S.3"
];

const container = document.getElementById("hotspotTypeSelection");

hotspot_type.forEach((type, index) => {

    const div = document.createElement("div");
    div.classList.add("col-md-2", "mb-2");

    div.innerHTML = `
        <div class="form-check">
            <input
                class="form-check-input hotspot-type"
                type="checkbox"
                id="hotspot_type_${index}"
                name="hotspot_type"
                value="${type}">
            
            <label
                class="form-check-label"
                for="hotspot_type_${index}">
                ${type}
            </label>
        </div>
    `;

    container.appendChild(div);
});

const selectAllButton = document.getElementById("selectAllHotspot");
const deselectAllButton = document.getElementById("deselectAllHotspot");

selectAllButton.addEventListener("click", () => {

    document.querySelectorAll(".hotspot-type").forEach(checkbox => {
        checkbox.checked = true;
    });

});

deselectAllButton.addEventListener("click", () => {

    document.querySelectorAll(".hotspot-type").forEach(checkbox => {
        checkbox.checked = false;
    });

});