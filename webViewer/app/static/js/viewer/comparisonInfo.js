// spinner animation
const styleEl = document.createElement('style');
styleEl.textContent = '@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }';
document.head.appendChild(styleEl);

const showLoading = () => document.getElementById('loading').style.display = 'flex';
const hideLoading = () => document.getElementById('loading').style.display = 'none';

const dataElement = document.getElementById('params-data');
if (!dataElement) {
    console.error('File info data element not found');
}

const paramObject = JSON.parse(dataElement.textContent);

let userKey = null;

let dataResult = null;

console.log("paramObject", paramObject);

function initPage(data) {
    dataResult = data.content;
    console.log("Data received:", dataResult);
    hideLoading();

    connectDownloadButton();

    fillFilesInfo()

    fillComparisonInfo();

    loadViewer();
}

function displayTree(newick) {

    const container = document.getElementById(
        "compGraphsDiv"
    );

    container.innerHTML = "";

    try {

        const root = parseNewick(newick);

        drawTree(root, container);

    } catch (error) {

        console.error(
            "Error while displaying Newick tree:",
            error
        );
    }
}

function connectButtonViewer(viewer, modelColors) {
    document.querySelectorAll('input[id^="style_"]').forEach(button => {

        button.addEventListener('click', () => {

            const style = button.id.replace('style_', '');

            modelColors.forEach((color, index) => {
                viewer.setStyle({ model: index }, { [style]: { color: color } });
            });
            viewer.render();
        });
    });
}

function hslToHex(h, s, l) {
    s /= 100;
    l /= 100;

    const k = n => (n + h / 30) % 12;
    const a = s * Math.min(l, 1 - l);

    const f = n =>
        l - a * Math.max(
            -1,
            Math.min(k(n) - 3, Math.min(9 - k(n), 1))
        );

    const r = Math.round(255 * f(0));
    const g = Math.round(255 * f(8));
    const b = Math.round(255 * f(4));

    return "#" +
        r.toString(16).padStart(2, "0") +
        g.toString(16).padStart(2, "0") +
        b.toString(16).padStart(2, "0");
}

function getModelColor(index, total) {
    const hue = (index / total) * 360;

    return hslToHex(
        hue,
        70,
        50
    );
}

function loadViewer() {
    const container = document.getElementById('container-frame');

    const config = { id: "3DMol_viewer", backgroundColor: 'white' };
    const viewer = $3Dmol.createViewer(container, config);

    const models = Object.entries(dataResult.cleaned_dataset);
    const modelColors = [];

    models.forEach(([name, data], index) => {

        viewer.addModel(data.content, 'pdb');

        const color = getModelColor(index, models.length);

        modelColors.push(color);

        viewer.setStyle({ model: index },{cartoon: {color: color}});
    });

    viewer.zoomTo();
    viewer.zoom(1.2, 1000);

    const viewerHeight = window.innerHeight - 200;
    container.style.height = viewerHeight + "px";
    document.getElementById('3DMol_viewer').style.height = viewerHeight + "px";
    viewer.resize();
    viewer.render();

    window.addEventListener('resize', () => {
        const viewerHeight = window.innerHeight - 200;
        container.style.height = viewerHeight + "px";
        document.getElementById('3DMol_viewer').style.height = viewerHeight + "px";
        viewer.resize();
        viewer.render();
    });

    connectButtonViewer(viewer, modelColors);
}

function fillFilesInfo() {
    const filesNameDiv = document.getElementById("FilesNameDiv");

    let i = 0;
    
    for ( [name, data] of Object.entries(dataResult.cleaned_dataset)) {
        i++;
        let innerHTML = `<div class="col-3" id="fileName${i}">${name}</div>`;
        filesNameDiv.insertAdjacentHTML('beforeend', innerHTML);
    }

}

function fillComparisonInfo() { 

    const comparisonInfoDiv = document.getElementById("comparisonInfoDiv");

    for ( [name, data] of Object.entries(dataResult)) {
        if (String(name).toLowerCase().endsWith(".svg")) {

            const svg = resizeSVG(data.content);

            const innerHTML = `
                <div class="row mb-2">
                    <div class="col-12 fw-bold">${name}</div>
                    <div class="col-12">
                        <div class="svg-container">${svg}</div>
                    </div>
                </div>
            `;

            comparisonInfoDiv.insertAdjacentHTML('beforeend', innerHTML);
        } 
        else if(String(name).toLowerCase().endsWith(".nwk")) {
            displayTree(data.content);
        }
    }
}

function resizeSVG(svgContent) {

    const parser = new DOMParser();
    const doc = parser.parseFromString(svgContent, "image/svg+xml");

    const svg = doc.documentElement;

    svg.removeAttribute("width");
    svg.removeAttribute("height");

    svg.setAttribute("width", "75%");

    return new XMLSerializer().serializeToString(svg);
}

function connectDownloadButton() {

    const buttonDownloadZip = document.getElementById("buttonDownloadZip");
    buttonDownloadZip.addEventListener("click", async () => {
        try {
            const zip = new JSZip();

            addFolderToZip(zip, dataResult);

            const blob = await zip.generateAsync({
                type: "blob"
            });

            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");
            link.href = url;
            link.download = "analized_folder.zip";
            document.body.appendChild(link);
            link.click();
            link.remove();

            setTimeout(() => {
                URL.revokeObjectURL(url);
            }, 1000);

        } catch (error) {
            console.error("Error creating ZIP:", error);
        }
    });
}

function addFolderToZip(zip, data) {

    for (const [name, content] of Object.entries(data)) {
        // FICHIER
        if (content && typeof content === "object" && content.encoding !== undefined) {
            if (content.encoding === "base64") {
                zip.file(name, content.content, {
                    base64: true
                });

            } else if (content.encoding === "utf8") {

                zip.file(name, content.content);

            } else {
                throw new Error(
                    `Unknown encoding: ${content.encoding}`
                );
            }
        }
        // DOSSIER
        else {
            const folder = zip.folder(name);
            addFolderToZip(folder, content);
        }
    }
}

function compareParams(params1, params2) {
    return JSON.stringify(params1) === JSON.stringify(params2);
}

function saveDataInDB(userKey, params, data) {
    fetch(`/api-database-comparison/saveDataWithUserKey/${userKey}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            parameter: params,
            data: data
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            console.log("Data saved successfully with userKey");
        }
        else {
            console.error("Error saving data with userKey:", data.message);
        }
    })
    .catch(error => {
        console.error("Error during fetch for saving data with userKey:", error);
    });
}

async function fetchData() {
    fetch("/api-hot-comp/comparison", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(paramObject)
    })
    .then(response => response.json())
    .then(async data => {

        if (data.status !== "success") {
            throw new Error("Error from comparison API: " + data.message);
        }

        if (!userKey) {
            console.log("No userKey found, generating new userKey");
            userKey = await fetch("/api-key/generateUserKey", {
                method: "GET",
                headers: {
                    "Content-Type": "application/json"
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === "success") {
                    saveUserKey(data.user_key);
                }
                else {
                    console.error("Error generating userKey:", data.message);
                }
                return data.user_key;
            })
            .catch(error => {
                console.error("Error generating userKey:", error);
            });
        }

        saveDataInDB(userKey, paramObject, data);
        initPage(data);
    })
    .catch(error => {
        console.error("Error:", error);
        hideLoading();
        showErrorPopup("Error from comparison. Please try again later.");
    });
}

onload = async function () {

    showLoading();

    userKey = await getUserKey();

    console.log("userKey", userKey);

    if (userKey) {
        fetch(`/api-database-comparison/getDataWhithUserKey/` + userKey, {
            method: "GET",
            headers: {
                "Content-Type": "application/json"
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                if (compareParams(data.parameter, paramObject)) {

                    console.log("Params match, loading cached data");

                    initPage(data.data);
                }
                else {
                    console.log("Params do not match, fetching new data");
                    fetchData(paramObject);
                }
            }
            else {
                console.log("No cached data found, fetching new data");
                fetchData(paramObject);
            }
        })
        .catch(error => {
            console.error("Error fetching data:", error);
            hideLoading();
            showErrorPopup("Error from database. Please try again later.");
        });
    }
    else {
        console.log("No user key found, fetching new data");
        fetchData(paramObject);
    }
};