const container = document.getElementById('container-frame');
const buttonDiv = document.getElementById('buttonDiv3DMol');

function loadViewer(fileContent) {

    let fileContentCopy = fileContent; 

    load3DMol(fileContentCopy);
}

function load3DMol(fileContent ) {
    const modifiedContent = replaceBFactorByFitness(fileContent);
    const config = { id: "3DMol_viewer", backgroundColor: 'white' };
    const viewer = $3Dmol.createViewer(container, config);
    viewer.addModel(modifiedContent, 'cif');
    viewer.setStyle({}, { cartoon: { colorscheme: { prop: "b", gradient: new $3Dmol.Gradient.ROYGB(0, 1) } } });

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
            viewer.setStyle({}, { [style]: { colorscheme: { prop: "b", gradient: new $3Dmol.Gradient.ROYGB(0, 1) } } });
            viewer.render();
        });
    });

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


    const gradient = new $3Dmol.Gradient.ROYGB(0, 1);

    const legend = document.getElementById("gradientLegend");

    let stops = [];

    for (let i = 0; i <= 100; i++) {
        const t = i / 100;
        const color = gradient.valueToHex(t); // ou colorAt selon la version
        stops.push(`#${color.toString(16).padStart(6, "0")} ${i}%`);
    }

    legend.style.background = `linear-gradient(to right, ${stops.join(",")})`;
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

            if (cols[fitnessIndex] === ".") {
                cols[bIndex] = "0.0";
            } else {
                cols[bIndex] = cols[fitnessIndex];
            }

            lines[i] = cols.join(" ");
        }
    }

    return lines.join("\n");
}