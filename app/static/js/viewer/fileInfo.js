document.addEventListener('DOMContentLoaded', () => {
    const dataElement = document.getElementById('file-info-data');
    if (!dataElement) {
        console.error('File info data element not found');
        return;
    }

    const { fileContent, pdbId, techUsed } = JSON.parse(dataElement.textContent);

    const container = document.getElementById('container-frame');
    const buttonDiv = document.getElementById('buttonDiv3DMol');
    const threeDMolButton = document.getElementById('3DMolButton');
    const molStarButton = document.getElementById('molStarButton');
    const jsMolButton = document.getElementById('jsMolButton');

    function load3DMol() {
        const config = { backgroundColor: 'white' };
        const viewer = $3Dmol.createViewer(container, config);
        viewer.addModel(fileContent, 'pdb');
        viewer.setStyle({}, { cartoon: { color: 'spectrum' } });
        viewer.zoomTo();
        viewer.render();
        viewer.zoom(1.2, 1000);

        document.querySelectorAll('input[id^="style_"]').forEach(button => {
            button.addEventListener('click', () => {
                const style = button.id.replace('style_', '');
                viewer.setStyle({}, { [style]: { color: 'spectrum' } });
                viewer.render();
            });
        });
    }

    function loadJSMol() {
        const pdbUrl = `/pdb_content/${pdbId}`;

        const width = container.width || 600;
        const height = container.height || 400;

        const info = {
            width: width,
            height: height,
            j2sPath: 'https://chemapps.stolaf.edu/jmol/jsmol/j2s',
            use: 'HTML5',
            debug: false
        };

        const applet = Jmol.getApplet('applet0', info);
        container.innerHTML = Jmol.getAppletHtml(applet);

        try {
            Jmol.script(applet, 'load ' + pdbUrl);
        } catch (error) {
            console.error('JSmol load error:', error);
        }

        const appletInfo = document.getElementById('applet0_appletinfotablediv');
        if (!appletInfo) {
            return;
        }

        container.appendChild(appletInfo);
        appletInfo.style.width = '100%';
        appletInfo.style.height = '100%';
    }

    function loadMolStar() {
        molstar.Viewer.create('container-frame', {
            layoutIsExpanded: false,
            layoutShowControls: false
        })
            .then(viewer => {
                const pdbUrl = `/pdb_content/${pdbId}`;
                return viewer.loadStructureFromUrl(pdbUrl, 'pdb');
            })
            .catch(error => {
                console.error('Erreur lors du chargement:', error);
                container.innerHTML = '<p class="text-danger">Erreur : ' + error.message + '</p>';
            });
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
        window.location.href = `/fileInfo/${pdbId}/Mol*`;
    });

    jsMolButton.addEventListener('click', () => {
        window.location.href = `/fileInfo/${pdbId}/JSmol`;
    });

    threeDMolButton.addEventListener('click', () => {
        window.location.href = `/fileInfo/${pdbId}/3DMol`;
    });
});