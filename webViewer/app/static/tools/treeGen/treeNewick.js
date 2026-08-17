function drawTree(root, container) {

    const width = Math.max(container.clientWidth, 600);
    const rowHeight = 50;

    function countLeaves(node) {
        if (!node.children || node.children.length === 0) {
            return 1;
        }

        return node.children.reduce(
            (sum, child) => sum + countLeaves(child),
            0
        );
    }

    const leafCount = countLeaves(root);

    const height = Math.max(
        200,
        leafCount * rowHeight + 80
    );

    const margin = {
        top: 40,
        right: 180,
        bottom: 40,
        left: 40
    };

    const hierarchy = d3.hierarchy(
        root,
        node => node.children
    );

    const treeLayout = d3.tree()
        .size([
            height - margin.top - margin.bottom,
            width - margin.left - margin.right
        ]);

    treeLayout(hierarchy);

    const svg = d3.select(container)
        .append("svg")
        .attr("width", "100%")
        .attr("height", height)
        .attr("viewBox", `0 0 ${width} ${height}`)
        .style("overflow", "hidden");

    const zoomGroup = svg
        .append("g");

    // ==================================================
    // BRANCHES
    // ==================================================

    zoomGroup
        .selectAll(".tree-link")
        .data(hierarchy.links())
        .enter()
        .append("path")
        .attr("class", "tree-link")
        .attr("fill", "none")
        .attr("stroke", "#555")
        .attr("stroke-width", 1.5)
        .attr(
            "d",
            d => {

                const source = d.source;
                const target = d.target;

                return `
                    M ${source.y} ${source.x}
                    H ${(source.y + target.y) / 2}
                    V ${target.x}
                    H ${target.y}
                `;
            }
        );

    // ==================================================
    // DISTANCE LABELS
    // ==================================================

    zoomGroup
        .selectAll(".branch-length")
        .data(hierarchy.links())
        .enter()
        .append("text")
        .attr("class", "branch-length")
        .attr(
            "x",
            d => (d.source.y + d.target.y) / 2
        )
        .attr(
            "y",
            d => (d.source.x + d.target.x) / 2 - 5
        )
        .attr("text-anchor", "middle")
        .style("font-family", "Arial, sans-serif")
        .style("font-size", "11px")
        .style("fill", "#777")
        .text(
            d => {

                const length = d.target.data.length;

                if (
                    length === undefined ||
                    length === null
                ) {
                    return "";
                }

                return Number(length).toFixed(5);
            }
        );

    // ==================================================
    // NODES
    // ==================================================

    const nodes = zoomGroup
        .selectAll(".tree-node")
        .data(hierarchy.descendants())
        .enter()
        .append("g")
        .attr("class", "tree-node")
        .attr(
            "transform",
            d => `translate(${d.y},${d.x})`
        );

    nodes
        .append("circle")
        .attr("r", 4)
        .attr("fill", "#333");

    // ==================================================
    // NAMES
    // ==================================================

    nodes
        .filter(d => d.data.name)
        .append("text")
        .attr("dy", "0.32em")
        .attr(
            "x",
            d => d.children ? -8 : 8
        )
        .attr(
            "text-anchor",
            d => d.children ? "end" : "start"
        )
        .style("font-family", "Arial, sans-serif")
        .style("font-size", "14px")
        .style("fill", "#222")
        .text(d => d.data.name);

    // ==================================================
    // ZOOM
    // ==================================================

    const zoom = d3.zoom()
        .scaleExtent([0.2, 5])
        .on("zoom", event => {
            zoomGroup.attr(
                "transform",
                event.transform
            );
        });

    svg.call(zoom);

    svg.call(
        zoom.transform,
        d3.zoomIdentity
            .translate(margin.left, margin.top)
    );
}

function parseNewick(newick) {

    // Supprime espaces, retours à la ligne et ; final
    newick = newick
        .trim()
        .replace(/\s+/g, "")
        .replace(/;$/, "");

    let index = 0;

    function parseNode() {

        const node = {
            name: "",
            length: 0,
            children: []
        };

        // --------------------------------------------------
        // Node interne
        // --------------------------------------------------

        if (newick[index] === "(") {

            index++; // saute '('

            while (index < newick.length) {

                node.children.push(parseNode());

                if (newick[index] === ",") {
                    index++;
                    continue;
                }

                if (newick[index] === ")") {
                    index++;
                    break;
                }

                break;
            }
        }

        // --------------------------------------------------
        // Nom du node
        // --------------------------------------------------

        let name = "";

        while (
            index < newick.length &&
            !["(", ")", ",", ":"].includes(newick[index])
        ) {
            name += newick[index];
            index++;
        }

        node.name = name;

        // --------------------------------------------------
        // Longueur de branche
        // --------------------------------------------------

        if (newick[index] === ":") {

            index++;

            let length = "";

            while (
                index < newick.length &&
                !["(", ")", ",", ":"].includes(newick[index])
            ) {
                length += newick[index];
                index++;
            }

            const parsedLength = parseFloat(length);

            if (!isNaN(parsedLength)) {
                node.length = parsedLength;
            }
        }

        return node;
    }

    return parseNode();
}