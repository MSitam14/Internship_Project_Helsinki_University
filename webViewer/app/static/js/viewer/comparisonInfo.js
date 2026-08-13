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