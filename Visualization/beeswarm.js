var width = 1000;  // of circle graph
var height = 280;  // of circle graph
var xMargin = 100;  // on either side of circle graph
var yMargin = 60;  // on either side of circle graph
var totalWidth = width + (2 * xMargin);  // of each svg element
var totalHeight = height + (2 * yMargin);  // of each svg element
var middle = height / 2;  // of circle graph

var radius = 4;
var avgRadius = 32;

var classifiers = {
    "role":   ["protag", "antag",   "fool",  "other"],
    "gender": ["m",      "f"],
    "genre":  ["comedy", "tragedy", "history"]
};
var colors =  ["blue",   "red",     "green", "yellow"];

var classifier = "role";
var characteristics = new Object();

var averageToggle = d3.select("#controlPanel")  // need html checkbox

var classSelect = d3.select("#controlPanel")
    .append("select")
        .attr("class", "select")
        .attr("id", "classSelect")
        .on("change", redrawClasses);
    
classSelect.selectAll("option")
        .data(Object.keys(classifiers)).enter()
    .append("option")
        .text(function(d) { return d; });

function redrawClasses() {
    newClassifier = d3.select("#classSelect").property("value");
    classifier = newClassifier;
    // need to regenerate averages data and bind it to existing circle.average before coloring
    colorCircles();
}

function getColor(d) {
    classification = d[classifier];
    colorIndex = classifiers[classifier].indexOf(classification);
    return colors[colorIndex];
};

function colorCircles(optionalClass = "") {
    d3.selectAll(((optionalClass != "") ? "circle." + optionalClass : "circle"))
        .transition()
        .duration(1000)
        .style("fill", function(d) { return getColor(d) })
        .style("stroke", function(d) { return getColor(d) });
};

function handleClick(d) {
    let circ = d3.select(this);  //circle element triggering event

    let newPersist = (parseInt(circ.attr("persist")) + 1) % 2;

    d3.selectAll(".c" + d.character.replace(/\./g, "-"))  // all circle elements for the same character
        .attr("persist", function() { return newPersist; });
};

function handleMouseOver(d) {
    let circ = d3.select(this);  // circle element triggering event
    if (circ.attr("persist") == 0) {

        d3.selectAll("circle.c" + d.character.replace(/\./g, "-"))  // all circle elements for the same character
            .transition()
            .duration(150)
            .attr("r", function() { return (circ.classed("average") ? sizeScale(d.count, d.total) + radius : 2 * radius); })
            .style("stroke", "black")
            .each(function(element) {
                let currentCirc = d3.select(this);
                let phon = currentCirc.attr("phoneme");

                let graph = d3.select(this.parentNode);  // g element containing circles for each circle

                circPopup = graph.append("text")
                    .attr("class", function() { return "c" + d.character.replace(/\./g, "-") + " popup"; })
                    .attr("x", function() { return currentCirc.attr("cx");})
                    .attr("y", function() { let cy = parseFloat(currentCirc.attr("cy"));
                        return ((cy < middle) ? cy - 30 : cy + 40); })
                    .style("text-anchor", "middle")
                    .style("font-weight", "bold")
                    //.style("stroke", "white")
                    .style("fill", "black")
                    .style("font-size", "16px")
                    .text(function() { return d.character + ": " + parseFloat(currentCirc.attr("Zscore")).toFixed(3); });
            });
    };
};

function handleMouseOut(d) {
    let circ = d3.select(this);  // circle element triggering event

    if (circ.attr("persist") == 0) {

        d3.selectAll("circle.c" + d.character.replace(/\./g, "-"))  // all circle elements for the same character
            .transition()
            .duration(150)
            .attr("r", function() { return (circ.classed("average") ? sizeScale(d.count, d.total) : radius); })
            .style("stroke", function() { return getColor(d) });

        let chart = d3.select(this.parentNode.parentNode);  // svg element containing everything

        d3.selectAll("text.c" + d.character.replace(/\./g, "-") + ".popup").remove();
    };
};

var sizeScaleHelper = d3.scaleLinear()
    .range([20, (height / 2) - 20]);

function sizeScale(classCount, totalCount) {
    sizeScaleHelper.domain([0, totalCount]);
    return sizeScaleHelper(classCount);
}

function drawAverages() {
    d3.selectAll("g.graph").each(function(entry) {
        let phoneme = entry.phoneme;
        let entryData = entry.data;

        classSums = new Object();
        classCounts = new Object();
        for (let i = 0; i < entryData.length; i++) {
            let charClass = entryData[i][classifier];
            classSums[charClass] = (classSums[charClass] ? classSums[charClass] += entryData[i].Zscore : entryData[i].Zscore);
            classCounts[charClass] = (classCounts[charClass] ? classCounts[charClass] += 1 : 1);
        };

        let classes = Object.keys(classSums);
        let classData = new Array();

        for (let i = 0; i < classes.length; i++) {
            classData.push({
                "character": classes[i],
                "average": true,
                "count": classCounts[classes[i]],
                "total": entryData.length,
                "Zscore": classSums[classes[i]] / classCounts[classes[i]],
                "role": ((classifier == "role") ? classes[i] : null),
                "gender": ((classifier == "gender") ? classes[i] : null),
                "genre": ((classifier == "genre") ? classes[i] : null)
            })
        }

        let xForceAvg = d3.forceX(function(d) { return xScale(d.Zscore); })  // force to pull circle towards its specified x value
            .strength(1);
        let yForceAvg = d3.forceY(middle)
            .strength(0.1);
        let collisionAvg = d3.forceCollide()  // applied to every node
            .radius(function(d) { return sizeScale(d.count, d.total) + 1; })
            .strength(0.9)
            .iterations(10);

        let simulationAvg = d3.forceSimulation(classData)  // Initializes a simulation with each circle as a node
            .force("xForce", xForceAvg)
            .force("yForce", yForceAvg)
            .force("collision", collisionAvg)
            .stop();

        for (let i = 0; i < 120; i++) { simulationAvg.tick(); };

        d3.select(this).selectAll("circle.average")
                .data(classData)
            .enter()
            .append("circle")
                .attr("class", function(d) {
                    let classList = new Array();
                    classList.push(phoneme);
                    classList.push("average");
                    classList.push("c" + d.character);
                    classList.push("p" + d.character.split(" ")[0]);
                    return classList.join(" ");
                })
                .attr("r", function(d) { return sizeScale(d.count, d.total); })
                .attr("cx", function(d) { return d.x; })
                .attr("cy", function(d) { return d.y; })
                .attr("phoneme", phoneme)
                .attr("character", function(d) { return d.character; })
                .attr("Zscore", function(d) { return d.Zscore; })
                .attr("title", function(d) { return d.character + ": " + d.Zscore.toFixed(3); })
                .attr("persist", 0)
                .attr("fill-opacity", 0.0)
                .style("stroke", "white")
                .style("fill", function(d) { return getColor(d, classifier) })
                .on("mouseover", handleMouseOver)
                .on("mouseout", handleMouseOut)
                .on("click", handleClick);
    });

    d3.selectAll("circle")
        .transition()
        .duration(1000)
        .attr("fill-opacity", 0.5)
        .style("stroke", function(d) { return getColor(d, classifier) });
};

function hideAverages() {
    d3.selectAll("circle").filter(function(d) { return (d.average ? false : true); })
        .transition()
        .duration(1000)
        .attr("fill-opacity", 1.0)

    d3.selectAll("circle.average")
        .transition()
        .duration(1000)
        .attr("fill-opacity", 0.0)
        .style("stroke", "white")
        .remove();
}


//d3.json("../Archive/Vowels-Only-No-Others/percentages_Z-scores.json", function(rawData) { 
//d3.json("percentages_Z-scores.json", function(rawData) { 
//       https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Archive/Vowels-Only-All/percentages_Z-scores.json
d3.json("https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Archive/Vowels-Only-No-Others/percentages_Z-scores.json", function(rawData) { 
    d3.csv("https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Reference/characteristics.csv", function(c) {
        for (let i = 0; i < c.length; i++) {
            entry = c[i];
            characteristics[entry["character"]] = entry;
        }

        var characters = Object.keys(rawData);
        var phonemes = Object.keys(rawData[characters[0]]);
        var data = new Array();
        var ZscoreMin = 0;
        var ZscoreMax = 0;
        for (let i = 0; i < phonemes.length; i++) {
            phoneme = phonemes[i];
            var phonData = new Array();
            data.push({"phoneme": phoneme, "data": phonData});
            for (let j = 0; j < characters.length; j++) {
                var charName = characters[j];
                var Zscore = rawData[charName][phoneme];
                ZscoreMin = Math.min(Zscore, ZscoreMin);
                ZscoreMax = Math.max(Zscore, ZscoreMax);
                phonData.push({
                    "Zscore": parseFloat(Zscore),
                    "character": charName,
                    "role": characteristics[charName]["role"],
                    "gender": characteristics[charName]["gender"],
                    "genre": characteristics[charName]["genre"],
                });
            };
        };
        // This creates data with structure:
        //      data = [{"phoneme": phoneme, "data": phonData}, ...]
        //      where phonData = [{"Zscore": Zscore, "character": charName, ...}, ...]

        var ZscoreWindow = d3.select("#ZscoreWindow");
        var svgs = ZscoreWindow.selectAll("svg")
            .data(data);

        var svg = svgs.enter().append("svg")
            .attr("width", totalWidth)
            .attr("height", totalHeight)
            .attr("id", function(d) { return "Chart_" + d.phoneme; })
            .attr("class", function(d) { return d.phoneme; });

        svg.each(function(entry) {
            phoneme = entry.phoneme;
            chartData = entry.data;

            var label = d3.select(this).append("g")  // Element to contain phoneme label
                .attr("class", function() { return phoneme; })
                .attr("width", xMargin)
                .attr("height", totalHeight);

            label.append("text")  // Text within the Label element
                .attr("x", xMargin / 2)
                .attr("y", totalHeight / 2)
                .attr("class", function() { return phoneme + " label"; })
                .style("text-anchor", "middle")
                .style("fill", "#999999")
                .style("stroke", "black")
                .style("font-size", "48px")
                .text(phoneme);

            var legend = d3.select(this).append("g")  // Element to contain legend for classes
                .attr("class", function() { return phoneme + " legend"; })
                .attr("transform", "translate(" + xMargin + ", 0)")
                .attr("width", width)
                .attr("height", yMargin);

/*            function truncScore(Zscore) {
                if (Zscore > 3) {
                    return 4;
                } else if (Zscore < -3) {
                    return -4;
                } else {
                    return Zscore;
                };
            }

            xScale = d3.scaleLinear()
//                .domain(d3.extent(chartData, function(d) { return truncScore(d.Zscore); }))
                .domain([-4, 4])
                .range([10, width - xMargin - 10]);
*/
            xScale = d3.scaleLinear()
                .domain([ZscoreMin, ZscoreMax])
                .range([10, width - 10]);

            var xAxis = d3.axisBottom(xScale);

            var axis = d3.select(this).append("g")  // Element to contain axis
                .attr("class", function() { return phoneme + " axis"; })
                .attr("transform", "translate(" + xMargin + "," + (height + (yMargin * 1.5)) + ")")
                .attr("width", width)
                .attr("height", yMargin)
                .call(xAxis);

            var xForce = d3.forceX(function(d) { return xScale(d.Zscore); })  // force to pull circle towards its specified x value
                .strength(1);
            var yForce = d3.forceY(middle)
                .strength(0.1);
            var collision = d3.forceCollide()  // applied to every node
                .radius(radius + 1)
                .strength(0.9)
                .iterations(10);

            var simulation = d3.forceSimulation(chartData)  // Initializes a simulation with each circle as a node
                .force("xForce", xForce)
                .force("yForce", yForce)
                .force("collision", collision)
                .stop();

            for (let i = 0; i < 120; i++) { simulation.tick(); };

            var g = d3.select(this).append("g")  // Element to contain circles
                .attr("class", function() { return phoneme + " graph"; })
                .attr("transform", "translate(" + xMargin + "," + yMargin + ")")
                .attr("width", width)
                .attr("height", height);

            var circles = g.selectAll("circle")
                    .data(chartData);
            circle = circles.enter().append("circle")
                .attr("r", function(d) { return radius; })
                .attr("cx", function(d) { return d.x; })  //truncScore(d.Zscore)); })
                .attr("cy", function(d) { return d.y; })
                .attr("phoneme", phoneme)
                .attr("character", function(d) { return d.character; })
                .attr("Zscore", function(d) { return d.Zscore; })
                .attr("title", function(d) { return d.character + ": " + d.Zscore.toFixed(3); })
                .attr("persist", 0)
                .on("mouseover", handleMouseOver)
                .on("mouseout", handleMouseOut)
                .on("click", handleClick);

            let classifier_keys = Object.keys(classifiers);
            circle.attr("class", function(d) { 
                let classList = new Array();
                classList.push("c" + d.character.replace(/\./g, "-"));
                classList.push("p" + d.character.split("_")[0]);
                classList.push(phoneme);
                for (let i = 0; i < classifier_keys.length; i++) {
                    classList.push(d[classifier_keys[i]]);
                };
                return classList.join(" ");
            });

        });
        colorCircles();
        drawAverages();
    });
});
