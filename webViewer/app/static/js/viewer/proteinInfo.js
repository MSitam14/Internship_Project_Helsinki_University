
const dataElement = document.getElementById('params-data');
if (!dataElement) {
    console.error('File info data element not found');
}

const paramObject = JSON.parse(dataElement.textContent);

console.log("Params object:", paramObject);

let dataResult = null;

function connectDownloadButtons() {

    const downloadCIFButton = document.getElementById("buttonDownloadCIF");
    const downloadCSVButton = document.getElementById("buttonDownloadCSV");

    downloadCIFButton.addEventListener("click", () => {
        const blob = new Blob([dataResult.content.cif_file.file_content], { type: 'chemical/x-mmcif' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${dataResult.content.cif_file.file_name}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

    downloadCSVButton.addEventListener("click", () => {
        const blob = new Blob([dataResult.content.csv_file.file_content], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${dataResult.content.csv_file.file_name}`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    });

}

function initScoreBar() {

    const scoreLine = dataResult.content.cif_file.file_content.split("\n").slice(0, 20);

    const proteinScore = scoreLine.find(line => line.includes("_pdbx_scoring_summary.score_protein")).replace(/\s+/g, " ").split(" ")[1];
    
    const totalScore = scoreLine.find(line => line.includes("_pdbx_scoring_summary.score_total")).replace(/\s+/g, " ").split(" ")[1];


    if (paramObject.params.water_env == true) {
        const waterScore = scoreLine.find(line => line.includes("_pdbx_scoring_summary.score_water")).replace(/\s+/g, " ").split(" ")[1];
        document.getElementById("progressbarWaterScore").style.width = `${waterScore * 100}%`;
        document.getElementById("progressbarWaterScore").setAttribute("aria-valuenow", waterScore * 100);
        document.getElementById("progressbarWaterScore").style.backgroundColor = colorScore(waterScore);
        document.getElementById("progressbarWaterScore").textContent = `${waterScore}`;
        document.getElementById("progressbarWaterScore").style.color = "black";
        document.getElementById("progressbarWaterScore").style.fontWeight = "bold";
    }
    else {
        document.getElementById("waterScoreDiv").style.display = "none";
    }

    document.getElementById("fileName").textContent = paramObject.pdb.name;

    // parameters
    document.getElementById("paramRun_frequencies").textContent = paramObject.params.run_frequencies;
    document.getElementById("paramWater_env").textContent = paramObject.params.water_env;
    document.getElementById("paramAtom_type").textContent = paramObject.params.atom_type;
    document.getElementById("paramEnvironment_size").textContent = paramObject.params.environment_size;
    document.getElementById("paramPocket_num").textContent = paramObject.params.pocket_num;
    document.getElementById("paramModel_num").textContent = paramObject.params.model_num;

    // score bars
    document.getElementById("progressbarProteinScore").style.width = `${proteinScore * 100}%`;
    document.getElementById("progressbarProteinScore").setAttribute("aria-valuenow", proteinScore * 100);
    document.getElementById("progressbarProteinScore").style.backgroundColor = colorScore(proteinScore);
    document.getElementById("progressbarProteinScore").textContent = `${proteinScore}`;
    document.getElementById("progressbarProteinScore").style.color = "black";
    document.getElementById("progressbarProteinScore").style.fontWeight = "bold";

    document.getElementById("progressbarTotalScore").style.width = `${totalScore * 100}%`;
    document.getElementById("progressbarTotalScore").setAttribute("aria-valuenow", totalScore * 100);
    document.getElementById("progressbarTotalScore").style.backgroundColor = colorScore(totalScore);
    document.getElementById("progressbarTotalScore").textContent = `${totalScore}`;
    document.getElementById("progressbarTotalScore").style.color = "black";
    document.getElementById("progressbarTotalScore").style.fontWeight = "bold";
}

function initViewerButton() {
    const viewerButton = document.getElementById("viwerButton");
    viewerButton.addEventListener("click", () => {

        const dataTemp = dataResult.content.cif_file;

        const form = document.createElement("form");
        form.method = "POST";
        form.action = "/proteinViewer/3DMol";

        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "json";
        input.value = JSON.stringify(dataTemp);

        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    });
}

function colorScore(score) {
    let red = 255;
    let green = 255;

    if (score > 0.5) {
        red = Math.round(255 * (1 - score) * 2);
        green = 255;
    }
    else {
        red = 255;
        green = Math.round(255 * score * 2);
    }

    return `rgb(${red}, ${green}, 0)`;
}

function initPage(data) {
    hideLoading();

    dataResult = data;
    console.log(data);

    initScoreBar();

    connectDownloadButtons();

    initViewerButton();
}

// spinner animation
const styleEl = document.createElement('style');
styleEl.textContent = '@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }';
document.head.appendChild(styleEl);

// show loading
const showLoading = () => document.getElementById('loading').style.display = 'flex';
const hideLoading = () => document.getElementById('loading').style.display = 'none';

function fetchData() {
    fetch("/api-score/score", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(paramObject)
    }).then(response => response.json())
        .then(data => {
            sessionStorage.setItem("lastDataLoadedParams", JSON.stringify(paramObject));
            saveDataInSession(JSON.stringify(data));
            initPage(data);
        })
        .catch(error => {
            console.error("Error:", error);
            hideLoading();
        });
}

function saveDataInSession(data) {
    const compressed = LZString.compressToUTF16(JSON.stringify(data));
    sessionStorage.setItem("lastDataLoadedResult", compressed);
}

function loadDataFromSession() {

    const compressed = sessionStorage.getItem("lastDataLoadedResult");
    if (!compressed) return null;
    const decompressed = JSON.parse(LZString.decompressFromUTF16(compressed));
    return JSON.parse(decompressed);
}

function compareParams(params1, params2) {
    return JSON.stringify(params1) === JSON.stringify(params2);
}


onload = () => {

    showLoading();

    let cachedParams = sessionStorage.getItem("lastDataLoadedParams");

    if (cachedParams) {
        cachedParams = JSON.parse(cachedParams);

        console.log("Cached params found:", cachedParams);
        console.log("Current params:", paramObject);

        if (compareParams(cachedParams, paramObject)) {
            console.log("Params match, loading cached data");

            const cachedData = loadDataFromSession();
            if (!cachedData) {
                console.log("No cached data found, fetching new data");
                fetchData();
                return;
            }
            initPage(cachedData);
        }
        else {
            console.log("Params do not match, fetching new data");
            fetchData();
        }
    }
    else {
        fetchData();
    }

};
