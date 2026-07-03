function openDB() {
    return new Promise((resolve, reject) => {
        const request = indexedDB.open("UserKey", 1);

        request.onupgradeneeded = (event) => {
            const db = event.target.result;

            db.createObjectStore("cache");
        };

        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

async function saveCache(key, data) {
    const db = await openDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction("cache", "readwrite");
        const store = tx.objectStore("cache");

        store.put({
            data: data,
            timestamp: Date.now()
        }, key);

        tx.oncomplete = () => resolve();
        tx.onerror = () => reject(tx.error);
    });
}

async function getCache(key) {
    const db = await openDB();

    return new Promise((resolve, reject) => {
        const tx = db.transaction("cache", "readonly");
        const store = tx.objectStore("cache");

        const request = store.get(key);

        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error);
    });
}

function saveUserKey(userKey) {
    saveCache("userKey", userKey);
}

function getUserKey() {

    const userKey = getCache("userKey");

    if (userKey) {
        return userKey;
    }
    return null;
}