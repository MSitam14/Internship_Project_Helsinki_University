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

let hotSpotsInViewer = {}; //{sybylType: {visible:true, level: {visible: true, model: model}}}

console.log("paramObject", paramObject);

function initPage(data) {
    dataResult = data.content;
    console.log("Data received:", dataResult);

    const fileName = String(paramObject.pdb.name).split('.')[0];
    if (dataResult[fileName][fileName + "_hotspot.cif"] === null) {
        hideLoading();
        showErrorPopup("Error during Cif file generation, retry with another parameters.");
    }

    hideLoading();

    fillFilesInfo();

    connectDownloadButton();

    loadViewer();
}

function fillFilesInfo() {
    const filesNameDiv = document.getElementById("fileName");
    filesNameDiv.textContent = paramObject.pdb.name;

    document.getElementById("grid_spacing").textContent = paramObject.params.global_parameters.grid_spacing;

    const pocketResNameDiv = document.getElementById("pocket_res_name");
    if (paramObject.params.global_parameters.pocket_res_name != "False") {
        pocketResNameDiv.textContent = paramObject.params.global_parameters.pocket_res_name;
    }else {
        pocketResNameDiv.textContent = "No pocket residue name provided";
    }  

    const pocket_res_idDiv = document.getElementById("pocket_res_id");
    if (paramObject.params.global_parameters.pocket_res_id != "") {
        pocket_res_idDiv.textContent = paramObject.params.global_parameters.pocket_res_id;
    }else {
        pocket_res_idDiv.textContent = "No pocket residue ID provided";
    }

    const lig_chainDiv = document.getElementById("lig_chain");
    if (paramObject.params.global_parameters.lig_chain != "False") {
        lig_chainDiv.textContent = paramObject.params.global_parameters.lig_chain;
    }else {
        lig_chainDiv.textContent = "No ligand chain provided";
    }

    document.getElementById("pocket_size").textContent = paramObject.params.global_parameters.pocket_size;
    document.getElementById("discard_hetatm").textContent = paramObject.params.global_parameters.discard_hetatm;
    document.getElementById("discard_hydrogen").textContent = paramObject.params.global_parameters.discard_hydrogen;
    document.getElementById("discard_water").textContent = paramObject.params.global_parameters.discard_water;
    
    const discard_chainsDiv = document.getElementById("discard_chains");
    if (paramObject.params.global_parameters.discard_chains != "") {
        discard_chainsDiv.textContent = paramObject.params.global_parameters.discard_chains;
    }else {
        discard_chainsDiv.textContent = "No discard chains provided";
    }

    document.getElementById("max_neighbor_number").textContent = paramObject.params.hotspot_parameters.max_neighbor_number;
    document.getElementById("tag_threshold").textContent = paramObject.params.hotspot_parameters.tag_threshold;
    document.getElementById("bad_score_threshold").textContent = paramObject.params.hotspot_parameters.bad_score_threshold;
    document.getElementById("good_score_threshold").textContent = paramObject.params.hotspot_parameters.good_score_threshold;
    document.getElementById("number_of_rounds").textContent = paramObject.params.hotspot_parameters.number_of_rounds;

}

// input: parsedCif, typeBox: "grid" or "pocket"
function extractBoxCornersFromCIF(parsedCif, typeBox) {

    const blockNames = Object.keys(parsedCif);

    if (blockNames.length === 0) {
        throw new Error("Aucun data block trouvé dans le CIF.");
    }

    const block = parsedCif[blockNames[0]];

    let boxCoordCif = null;

    if (typeBox === "grid") {
        boxCoordCif = block.grid_corner;
    }else if (typeBox === "pocket") {
        boxCoordCif = block.pocket_corner;
    }

    if (!boxCoordCif) {
        return null; // Return null if the specified box type is not found
    }

    let returnBoxCoord = [];

    for (let i = 0; i < 8; i++) {

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

function addBox(viewer, cifContent) {
    
    const pocketBoxCoord = extractBoxCornersFromCIF(cifContent, "pocket");

    if (pocketBoxCoord) {
        const pocketBoxParams = getBoxParameters(pocketBoxCoord);

        viewer.addBox({
            center: pocketBoxParams.center,
            dimensions: pocketBoxParams.dimensions,
            color: "red",
            opacity: 1,
            wireframe: true
        });

        viewer.setStyle(
            { resn: paramObject.params.global_parameters.pocket_res_name },
            {
                stick: {}
            }
        );
    }
    else {
        const boxCoord = extractBoxCornersFromCIF(cifContent, "grid"); // [[x1, y1, z1], [x2, y2, z2], ..., [x8, y8, z8]]
        const boxParams = getBoxParameters(boxCoord);

        viewer.addBox({
            center: boxParams.center,
            dimensions: boxParams.dimensions,
            color: "black",
            opacity: 1,
            wireframe: true
        });
    }
}

function extractHopSpotsFromCIF(parsedCif) {

    const blockNames = Object.keys(parsedCif);

    if (blockNames.length === 0) {
        throw new Error("Aucun data block trouvé dans le CIF.");
    }

    const block = parsedCif[blockNames[0]];

    const hotSpotsCif = block.hotspot;

    if (!hotSpotsCif) {
        return null;
    }

    // {
    //   "C.3": [ [lvl1], [lvl2], [lvl3] ],
    //   "O.2": [ [lvl1], [lvl2], [lvl3] ],
    //   ...
    // }
    const returnHotSpotsCoord = {};

    for (let i = 0; i < hotSpotsCif.Cartn_x.length; i++) {

        const level = Number(hotSpotsCif.tier[i]) - 1;
        const sybylType = hotSpotsCif.sybyl_type[i];

        if (!returnHotSpotsCoord[sybylType]) {
            returnHotSpotsCoord[sybylType] = [[], [], []];
        }

        returnHotSpotsCoord[sybylType][level].push([
            hotSpotsCif.Cartn_x[i],
            hotSpotsCif.Cartn_y[i],
            hotSpotsCif.Cartn_z[i],
            hotSpotsCif.type_symbol[i],
            hotSpotsCif.sybyl_type[i]
        ]);
    }

    return returnHotSpotsCoord;
}

function addHotSpots(viewer, cifContent) {

    const hotSpotsCoord = extractHopSpotsFromCIF(cifContent);

    if (!hotSpotsCoord) {
        console.warn("No hot spots found in the CIF.");
        return;
    }

    Object.entries(hotSpotsCoord).forEach(([sybylType, levels]) => {

        for (let level = 0; level < levels.length; level++) {

            const coords = levels[level];

            if (coords.length === 0) {
                continue;
            }

            const model = viewer.addModel();

            const radius =
                level === 0 ? 0.07 :
                    level === 1 ? 0.2 :
                        0.5;

            const atoms = [];

            for (let i = 0; i < coords.length; i++) {

                const coord = coords[i];

                atoms.push({
                    elem: coord[3],
                    x: parseFloat(coord[0]),
                    y: parseFloat(coord[1]),
                    z: parseFloat(coord[2])
                });
            }

            model.addAtoms(atoms);

            model.setStyle({}, {
                sphere: {
                    colorscheme: "Jmol",
                    radius: radius
                }
            });

            if (!hotSpotsInViewer[sybylType]) {
                hotSpotsInViewer[sybylType] = {};
                hotSpotsInViewer[sybylType]["visible"] = true;
            }
            hotSpotsInViewer[sybylType][level] = {};
            hotSpotsInViewer[sybylType][level]["visible"] = true;
            hotSpotsInViewer[sybylType][level]["model"] = model;
        }
    });

    viewer.render();
}



async function loadViewer() {
    const container = document.getElementById('container-frame');

    const config = { id: "3DMol_viewer", backgroundColor: 'white' };
    const viewer = $3Dmol.createViewer(container, config);

    const fileName = String(paramObject.pdb.name).split('.')[0];

    const parsedCif = await cif.loadCIF(atob(dataResult[fileName][fileName + "_hotspot.cif"].content), 1);


    // Load the model into the viewer
    viewer.addModel(atob(dataResult[fileName][fileName + "_hotspot.cif"].content), 'cif');

    viewer.setStyle({}, { cartoon: { colorscheme: "chain" } });

    viewer.zoomTo();
    viewer.zoom(1.2, 1000);

    // Set the viewer height to be the window height minus 200px
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

    // Add pocket box if it exists and connect the buttons
    
    addBox(viewer, parsedCif);
    addHotSpots(viewer, parsedCif);

    viewer.resize();
    viewer.render();

    connectButtonViewer(viewer);
}

function setModelVisibility(model, isVisible) {
    if (isVisible) {
        model.show();
    }
    else {
        model.hide();
    }
}

function connectButtonViewer(viewer) {

    const divButtonType = document.getElementById("buttonDiv3DMol-Types")

    for (const sybylType in hotSpotsInViewer) {
        const blockHtml = `
        <div class="form-check form-switch">
            <input class="form-check-input" type="checkbox" id="buttonType_${sybylType}" name="${sybylType}" checked>
            <label for="buttonType_${sybylType}" class="form-check-label"> ${sybylType} </label>
        </div>
        `;
        divButtonType.insertAdjacentHTML('beforeend', blockHtml);
    }

    document.querySelectorAll('input[id^="buttonType_"]').forEach(button => {

        button.addEventListener('click', () => {

            const sybylType = button.name;
            const isVisible = button.checked;

            hotSpotsInViewer[sybylType]["visible"] = isVisible;

            for (const level in hotSpotsInViewer[sybylType]) {
                if (level !== "visible") {
                    const model = hotSpotsInViewer[sybylType][level]["model"];
                    setModelVisibility(model, isVisible && hotSpotsInViewer[sybylType][level]["visible"]);
                }
            }

            viewer.render();
        });
    });

    const divButtonLevel = document.getElementById("buttonDiv3DMol-Tiers")

    for (let level = 0; level < 3; level++) {

        let buttonName = '';
        
        switch (level) {
            case 0:
                buttonName = 'Explored voxels';
                break;
            case 1:
                buttonName = 'Hotspots';
                break;
            case 2:
                buttonName = `Cleaned Hotspots 
                            <i class="bi bi-question-circle-fill" data-bs-toggle="tooltip" data-bs-placement="top" 
                                title = "Top scoring Hotspots with no overlap" >
                            </i>`;
                break;
        }


        const blockHtml = `
        <div class="form-check form-switch mb-3">
            <input class="form-check-input" type="checkbox" id="buttonLevel_${level}" name="${level}" checked>
            <label for="buttonLevel_${level}" class="form-check-label">${buttonName}</label>
        </div>
        `;
        divButtonLevel.insertAdjacentHTML('beforeend', blockHtml);
    }

    document.querySelectorAll('input[id^="buttonLevel_"]').forEach(button => {

        button.addEventListener('click', () => {
            const level = parseInt(button.name);
            const isVisible = button.checked;

            for (const sybylType in hotSpotsInViewer) {
                hotSpotsInViewer[sybylType][level]["visible"] = isVisible;
            }

            for (const sybylType in hotSpotsInViewer) {
                const model = hotSpotsInViewer[sybylType][level]["model"];
                setModelVisibility(model, isVisible && hotSpotsInViewer[sybylType]["visible"]);
            }

            viewer.render();
        });
    });
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

function saveDataInDB(userKey, params, data) {
    fetch(`/api-database-hotSpots/saveDataWithUserKey/${userKey}`, {
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
    fetch("/api-hot-comp/hotSpots", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(paramObject)
    })
        .then(response => response.json())
        .then(async data => {

            if (data.status !== "success") {
                throw new Error("Error from hot spots API: " + data.message);
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
            showErrorPopup("Error from hot spots. Please try again later.");
        });
}

function compareParams(params1, params2) {
    return JSON.stringify(params1) === JSON.stringify(params2);
}

onload = async function () {

    showLoading();

    userKey = await getUserKey();

    if (userKey) {
        fetch(`/api-database-hotSpots/getDataWhithUserKey/` + userKey, {
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