
const dataElement = document.getElementById('params-data');
if (!dataElement) {
    console.error('File info data element not found');
}

const paramObject = JSON.parse(dataElement.textContent);
let userKey = null;

// console.log("Params object:", paramObject);

let dataResult = null;

function connectDownloadButtons() {

    const downloadCIFButton = document.getElementById("buttonDownloadCIF");
    const downloadCSVButton = document.getElementById("buttonDownloadCSV"); 
    const downloadLOGButton = document.getElementById("buttonDownloadLog"); 

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

    console.log("dataResult.content.log_file:", dataResult.content.log_file);

    if (dataResult.content.log_file && dataResult.content.log_file.file_content) {
        downloadLOGButton.addEventListener("click", () => {
            const blob = new Blob([dataResult.content.log_file.file_content], { type: 'text/plain' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `${dataResult.content.log_file.file_name}`;
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    } else {
        downloadLOGButton.hidden = true;
    }

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

function initViewer() {

    loadViewer(dataResult.content.cif_file.file_content);
    
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

    initScoreBar();

    connectDownloadButtons();

    // initViewerButton();

    initViewer();

}

// spinner animation
const styleEl = document.createElement('style');
styleEl.textContent = '@keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }';
document.head.appendChild(styleEl);

// show loading
const showLoading = () => document.getElementById('loading').style.display = 'flex';
const hideLoading = () => document.getElementById('loading').style.display = 'none';

async function fetchData() {
    fetch("/api-score/score", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(paramObject)
    }).then(response => response.json())
        .then(async data => {

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
        });
}

function saveDataInDB(userKey, params, data) {
    fetch(`/api-database-score/saveDataWithUserKey/${userKey}`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({
            parameter: params,
            cif_file_name: data.content.cif_file.file_name,
            cif_file_content: data.content.cif_file.file_content,
            csv_file_name: data.content.csv_file.file_name,
            csv_file_content: data.content.csv_file.file_content,
            log_file_name: data.content.log_file.file_name,
            log_file_content: data.content.log_file.file_content
        })
    }).then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                console.log("Data saved successfully with userKey");
            }
            else {
                console.error("Error saving data with userKey:", data.message);
            }
        })
        .catch(error => {
            console.error("Error saving data with userKey:", error);
        });
}

function compareParams(params1, params2) {
    return JSON.stringify(params1) === JSON.stringify(params2);
}


onload = async () => {

    showLoading();

    userKey = await getUserKey();
    
    if (userKey) {

        fetch(`/api-database-score/getDataWhithUserKey/` + userKey, {
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

                        const formatData = {
                            content: {
                                cif_file: {
                                    file_name: data.cif_file_name,
                                    file_content: data.cif_file_content
                                },
                                csv_file: {
                                    file_name: data.csv_file_name,
                                    file_content: data.csv_file_content
                                },
                                log_file: {
                                    file_name: data.log_file_name,
                                    file_content: data.log_file_content
                                }
                            }
                        };

                        initPage(formatData);
                    }
                    else {
                        console.log("Params do not match, fetching new data");
                        fetchData();
                    }
                }
                else {
                    console.log("No data found for userKey, fetching new data");
                    fetchData();
                }
            })
            .catch(error => {
                console.error("Error:", error);
                hideLoading();
            });
    }
    else {
        console.log("No userKey found, fetching new data");
        fetchData();
    }
};
