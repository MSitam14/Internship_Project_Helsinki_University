
const dataElement = document.getElementById('file-info-data');
if (!dataElement) {
    console.error('File info data element not found');
}

const { fileName, fileContent, pdbId, techUsed, userKey } = JSON.parse(dataElement.textContent);

const container = document.getElementById('container-frame');
const buttonDiv = document.getElementById('buttonDiv3DMol');
const threeDMolButton = document.getElementById('3DMolButton');
const molStarButton = document.getElementById('molStarButton');
const jsMolButton = document.getElementById('jsMolButton');

(function () {

    function loadJSMol() {
        const width = container.clientWidth || container.offsetWidth || 600;
        const height = container.clientHeight || container.offsetHeight || 400;

        const info = {
            width: width,
            height: height,
            j2sPath: 'https://chemapps.stolaf.edu/jmol/jsmol/j2s',
            use: 'HTML5',
            debug: false
        };

        const applet = Jmol.getApplet('applet0', info);
        container.innerHTML = Jmol.getAppletHtml(applet);

        const modifiedContent = replaceBFactorByFitness(fileContent);

        // load the structure after a short delay and poll for the applet info div
        setTimeout(() => {
            try {
                const escapedContent = modifiedContent
                    .replace(/\\/g, '\\\\')
                    .replace(/\r\n/g, '\n')
                    .replace(/\r/g, '\n');

                const script = `load DATA "mmcif"\n${escapedContent}\nEND "mmcif"; cartoon only; color structure; zoom 120;`;
                Jmol.script(applet, script);
            } catch (error) {
                console.error('JSmol script error:', error);
            }

            const start = Date.now();
            const maxWait = 5000; // ms
            const interval = 100;
            const poll = setInterval(() => {
                const appletInfo = document.getElementById('applet0_appletinfotablediv');
                if (appletInfo) {
                    clearInterval(poll);
                    if (!container.contains(appletInfo)) container.appendChild(appletInfo);
                    appletInfo.style.width = '100%';
                    appletInfo.style.height = '100%';
                    appletInfo.style.display = 'block';
                } else if (Date.now() - start > maxWait) {
                    clearInterval(poll);
                    console.warn('JSmol applet info div not found after wait');
                }
            }, interval);
        }, 100);
    }

    if (techUsed === '3DMol') {
        buttonDiv.style.display = 'block';
        threeDMolButton.style.display = 'none';
        load3DMol();
    } else if (techUsed === 'Mol*') {
        buttonDiv.style.display = 'none';
        molStarButton.style.display = 'none';
        loadMolStar();
    } else if (techUsed === 'JSmol') {
        buttonDiv.style.display = 'none';
        jsMolButton.style.display = 'none';
        loadJSMol();
    }

    molStarButton.addEventListener('click', () => {
        // window.location.href = `/fileInfo/${pdbId}/Mol*`;
        useOtherViewer("Mol*");
    });

    jsMolButton.addEventListener('click', () => {
        // window.location.href = `/fileInfo/${pdbId}/JSmol`;
        useOtherViewer("JSmol");
    });

    threeDMolButton.addEventListener('click', () => {
        // window.location.href = `/fileInfo/${pdbId}/3DMol`;
        useOtherViewer("3DMol");
    });

    document.getElementById('returnToInfoButton').addEventListener('click', () => {
        const form = document.createElement("form");
        form.method = "POST";
        form.action = "/pdbInfoUserKey";

        const input = document.createElement("input");
        input.type = "hidden";
        input.name = "userKey";
        input.value = userKey;

        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
    });

})();

function useOtherViewer(viewer) {

    const form = document.createElement("form");
    form.method = "POST";
    form.action = "/proteinViewer/" + viewer;

    const input = document.createElement("input");
    input.type = "hidden";
    input.name = "userKey";
    input.value = userKey;

    form.appendChild(input);
    document.body.appendChild(form);
    form.submit();
}

function load3DMol() {
    const modifiedContent = replaceBFactorByFitness(fileContent);
    const config = { backgroundColor: 'white' };
    const viewer = $3Dmol.createViewer(container, config);
    viewer.addModel(modifiedContent, 'mmcif');
    viewer.setStyle({}, { cartoon: { colorscheme: { prop: "b", gradient: new $3Dmol.Gradient.RWB(0, 1) } } });

    // viewer.addBox({
    //     center: { x: 0, y: 0, z: 0 },
    //     dimensions: { w: 30, h: 30, d: 30},
    //     color: "black",
    //     opacity: 0.5
    // });

    // viewer.addBox({
    //     center: { x: 10, y: 30, z: 0 },
    //     dimensions: { w: 30, h: 30, d: 30},
    //     color: "green",
    //     wireframe: true
    // });

    viewer.zoomTo();
    viewer.render();
    viewer.zoom(1.2, 1000);

    document.querySelectorAll('input[id^="style_"]').forEach(button => {
        button.addEventListener('click', () => {
            const style = button.id.replace('style_', '');
            viewer.setStyle({}, { [style]: { colorscheme: { prop: "b", gradient: new $3Dmol.Gradient.RWB(0, 1) } } });
            viewer.render();
        });
    });
}



function loadMolStar() {

    const modifiedContent = replaceBFactorByFitness(fileContent);

    const cifFileContent =

        molstar.Viewer.create('container-frame', {
            layoutIsExpanded: false,
            layoutShowControls: false
        })
            .then(viewer => {
                return viewer.loadStructureFromData(modifiedContent, 'mmcif');
            })
            .catch(error => {
                console.error('Erreur lors du chargement:', error);
                container.innerHTML = '<p class="text-danger">Erreur : ' + error.message + '</p>';
            });

    console.log(molstar.Viewer.plugin);
}

function replaceBFactorByFitness(cifContent) {

    const lines = cifContent.split("\n");

    let atomLoop = false;
    let readingHeaders = false;
    let headers = [];

    let bIndex = -1;
    let fitnessIndex = -1;

    for (let i = 0; i < lines.length; i++) {

        const line = lines[i].trim();

        if (line === "loop_") {
            atomLoop = false;
            readingHeaders = true;
            headers = [];
            continue;
        }

        if (readingHeaders && line.startsWith("_atom_site.")) {

            headers.push(line);

            if (line === "_atom_site.B_iso_or_equiv")
                bIndex = headers.length - 1;

            if (line === "_atom_site.pdbx_fitness_score")
                fitnessIndex = headers.length - 1;

            continue;
        }

        // Première ligne de données
        if (readingHeaders && headers.length > 0 && !line.startsWith("_")) {

            readingHeaders = false;

            // Ce n'est pas le bon loop
            if (bIndex === -1 || fitnessIndex === -1)
                break;

            atomLoop = true;
        }

        if (atomLoop) {

            if (line === "#" || line.startsWith("loop_"))
                break;

            const cols = lines[i].trim().split(/\s+/);

            cols[bIndex] = cols[fitnessIndex];

            lines[i] = cols.join(" ");
        }
    }

    return lines.join("\n");
}