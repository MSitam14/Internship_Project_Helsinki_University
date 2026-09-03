// spinner animation
const styleEl = document.createElement('style');
styleEl.textContent = '@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }';
document.head.appendChild(styleEl);

import * as cif from "../../tools/cifParser/cif.mjs";

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

function buildCIFFromAtomSite(dataBlockName, atomSite) {

    const fields = Object.keys(atomSite);

    if (fields.length === 0) {
        throw new Error("atom_site ne contient aucun champ.");
    }

    const lines = [];

    lines.push(`data_${dataBlockName}`);
    lines.push("#");

    lines.push("loop_");

    for (const field of fields) {
        lines.push(`_atom_site.${field}`);
    }

    const firstField = atomSite[fields[0]];

    const rowCount = firstField.length;

    function formatCIFValue(value) {

        if (value === null || value === undefined) {
            return "?";
        }

        const stringValue = String(value);

        if (
            stringValue === "?" ||
            stringValue === "."
        ) {
            return stringValue;
        }

        if (stringValue === "") {
            return "''";
        }

        if (
            /\s/.test(stringValue) ||
            stringValue.includes("'") ||
            stringValue.includes('"')
        ) {

            if (!stringValue.includes('"')) {
                return `"${stringValue}"`;
            }

            if (!stringValue.includes("'")) {
                return `'${stringValue}'`;
            }

            return `'''${stringValue}'''`;
        }

        return stringValue;
    }

    for (let row = 0; row < rowCount; row++) {

        const values = [];

        for (const field of fields) {

            const value = atomSite[field][row];

            values.push(
                formatCIFValue(value)
            );
        }

        lines.push(values.join(" "));
    }

    lines.push("#");

    return lines.join("\n") + "\n";
}

function extractModelsFromCIF(parsedCif) {

    const blockNames = Object.keys(parsedCif);

    if (blockNames.length === 0) {
        throw new Error("Aucun data block trouvé dans le CIF.");
    }

    const block = parsedCif[blockNames[0]];


    if (!block.atom_site) {
        throw new Error("La catégorie _atom_site est absente du CIF.");
    }

    const atomSite = block.atom_site;

    const modelField = "pdbx_PDB_model_num";

    if (!Array.isArray(atomSite[modelField])) {
        throw new Error(
            `_atom_site.${modelField} est absent ou invalide.`
        );
    }

    const modelNumbers = atomSite[modelField];

    const fields = Object.keys(atomSite);

    const uniqueModels = [
        ...new Set(modelNumbers)
    ].sort((a, b) => Number(a) - Number(b));

    const models = {};

    for (const modelNumber of uniqueModels) {

        models[modelNumber] = {};

        for (const field of fields) {
            models[modelNumber][field] = [];
        }
    }

    for (let i = 0; i < modelNumbers.length; i++) {

        const modelNumber = modelNumbers[i];

        for (const field of fields) {

            const values = atomSite[field];

            if (!Array.isArray(values)) {
                continue;
            }

            models[modelNumber][field].push(
                values[i]
            );
        }
    }

    const result = [];

    for (const modelNumber of uniqueModels) {

        const modelAtomSite = models[modelNumber];

        const modelCIF = buildCIFFromAtomSite(
            blockNames[0],
            modelAtomSite
        );

        result.push([
            `Model_${modelNumber}`,
            {
                content: modelCIF,
                encoding: 'utf8',
                atomSite: modelAtomSite
            }
        ]);
    }

    return result;
}

function extractBoxCornersFromCIF(parsedCif) {

    const blockNames = Object.keys(parsedCif);

    if (blockNames.length === 0) {
        throw new Error("Aucun data block trouvé dans le CIF.");
    }

    const block = parsedCif[blockNames[0]];

    let boxCoordCif = block.grid_corner;

    if (block._pocket_corner) {
        boxCoordCif = block.pocket_corner;
    }

    let returnBoxCoord = [];

    for(let i = 0; i < 8; i++) {

        returnBoxCoord.push([
            boxCoordCif.Cartn_x[i],
            boxCoordCif.Cartn_y[i],
            boxCoordCif.Cartn_z[i]
        ]);
    }

    return returnBoxCoord;
}

function getBoxParameters(boxCorners) {

    const xs = boxCorners.map(corner => corner[0]);
    const ys = boxCorners.map(corner => corner[1]);
    const zs = boxCorners.map(corner => corner[2]);

    const minX = Math.min(...xs);
    const maxX = Math.max(...xs);

    const minY = Math.min(...ys);
    const maxY = Math.max(...ys);

    const minZ = Math.min(...zs);
    const maxZ = Math.max(...zs);

    return {
        center: {
            x: (minX + maxX) / 2,
            y: (minY + maxY) / 2,
            z: (minZ + maxZ) / 2
        },

        dimensions: {
            w: maxX - minX,
            h: maxY - minY,
            d: maxZ - minZ
        }
    };
}

async function loadViewer() {
    const container = document.getElementById('container-frame');

    const config = { id: "3DMol_viewer", backgroundColor: 'white' };
    const viewer = $3Dmol.createViewer(container, config);

    const parsedCif = await cif.loadCIF(atob(dataResult.cleaned_dataset["cleaned_dataset.cif"].content), 1);

    const models = extractModelsFromCIF(parsedCif) 
    
    const modelColors = [];

    models.forEach(([name, data], index) => {

        viewer.addModel(data.content, 'cif');

        const color = getModelColor(index, models.length);

        modelColors.push(color);

        viewer.setStyle({ model: index },{cartoon: {color: color}});
    });

    viewer.zoomTo();
    viewer.zoom(1.2, 1000);

    const viewerHeight = window.innerHeight - 200;
    container.style.height = viewerHeight + "px";
    document.getElementById('3DMol_viewer').style.height = viewerHeight + "px";

    window.addEventListener('resize', () => {
        const viewerHeight = window.innerHeight - 200;
        container.style.height = viewerHeight + "px";
        document.getElementById('3DMol_viewer').style.height = viewerHeight + "px";
        viewer.resize();
        viewer.render();
    });

    const boxCoord = extractBoxCornersFromCIF(parsedCif); // [[x1, y1, z1], [x2, y2, z2], ..., [x8, y8, z8]]
    const boxParams = getBoxParameters(boxCoord);

    viewer.addBox({
        center: boxParams.center,
        dimensions: boxParams.dimensions,
        color: "black",
        opacity: 1,
        wireframe: true
    });
    

    viewer.resize();
    viewer.render();

    connectButtonViewer(viewer, modelColors);
}

function fillFilesInfo() {
    const filesNameDiv = document.getElementById("FilesNameDiv");

    let name, data;
    let i = 0;
    
    for ( [name, data] of Object.entries(paramObject.pdbList)) {
        i++;
        let innerHTML = `<div class="col-2" id="fileName${i}">${name}</div>`;
        filesNameDiv.insertAdjacentHTML('beforeend', innerHTML);
    }

    document.getElementById("grid_spacing").textContent = paramObject.params.global_parameters.grid_spacing;

    const pocketResNameDiv = document.getElementById("pocket_res_name");
    if (paramObject.params.global_parameters.pocket_res_name != "False") {
        pocketResNameDiv.textContent = paramObject.params.global_parameters.pocket_res_name;
    } else {
        pocketResNameDiv.textContent = "No pocket residue name provided";
    }

    const pocket_res_idDiv = document.getElementById("pocket_res_id");
    if (paramObject.params.global_parameters.pocket_res_id != "") {
        pocket_res_idDiv.textContent = paramObject.params.global_parameters.pocket_res_id;
    } else {
        pocket_res_idDiv.textContent = "No pocket residue ID provided";
    }

    const lig_chainDiv = document.getElementById("lig_chain");
    if (paramObject.params.global_parameters.lig_chain != "False") {
        lig_chainDiv.textContent = paramObject.params.global_parameters.lig_chain;
    } else {
        lig_chainDiv.textContent = "No ligand chain provided";
    }

    document.getElementById("pocket_size").textContent = paramObject.params.global_parameters.pocket_size;
    document.getElementById("discard_hetatm").textContent = paramObject.params.global_parameters.discard_hetatm;
    document.getElementById("discard_hydrogen").textContent = paramObject.params.global_parameters.discard_hydrogen;
    document.getElementById("discard_water").textContent = paramObject.params.global_parameters.discard_water;

    const discard_chainsDiv = document.getElementById("discard_chains");
    if (paramObject.params.global_parameters.discard_chains != "") {
        discard_chainsDiv.textContent = paramObject.params.global_parameters.discard_chains;
    } else {
        discard_chainsDiv.textContent = "No discard chains provided";
    }

    document.getElementById("consider_elements").textContent = paramObject.params.comparison_parameters.consider_elements;

    const tmalign_referenceDiv = document.getElementById("tmalign_reference");
    if (paramObject.params.comparison_parameters.tmalign_reference != "None") {
        tmalign_referenceDiv.textContent = paramObject.params.comparison_parameters.tmalign_reference;
    } else {
        tmalign_referenceDiv.textContent = "No tmalign reference provided";
    }

}

function fillComparisonInfo() { 

    const comparisonInfoDiv = document.getElementById("comparisonInfoDiv");
    let name, data;

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