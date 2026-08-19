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

    console.log("userKey", userKey);

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