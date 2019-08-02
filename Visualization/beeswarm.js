var width = 1200;
var height = 400;
var xMargin = 100;
var yMargin = 60;

var radius = 4;

var classifiers = {
    "role":   ["protag", "antag",   "fool",  "other"],
    "gender": ["m",      "f"],
    "genre":  ["comedy", "tragedy", "history"]
};
var colors =  ["blue",   "red",     "green", "yellow"]

var classifier = "role";
var characteristics = new Object();

function getColor(d, classifier) {
    classification = d[classifier];
    colorIndex = classifiers[classifier].indexOf(classification);
    return colors[colorIndex];
};

function colorCircles() {
    d3.selectAll("circle")
        .style("fill", function(d) { return getColor(d, classifier) })
        .style("stroke", function(d) { return getColor(d, classifier) });
};

function handleMouseOver(d, i) {
    // d3.selectAll("." + d.character);
    let circ = d3.select(this)  // circle element being modified
        .style("fill", "white")
        .style("stroke", "black");

    let charName = d.character;
    let Zscore = d.Zscore.toFixed(3);

    let graph = d3.select(this.parentNode)  // g element containing circles

    let chart = d3.select(this.parentNode.parentNode)  // svg element containing everything

    let chartID = chart.attr("id");
    let phonIndex = chartID.indexOf("_");
    let phon = chartID.slice(phonIndex + 1);

    let labelID = phon + "_" + charName.replace(/\./g, "-") + "_label";

    circLabel = graph.append("text")
        .attr("id", labelID)
        .attr("x", function() { return circ.attr("cx") - 50 })
        .attr("y", function() { return circ.attr("cy") - 15 })
        .text(function() { return charName + ": " + Zscore; });
}

function handleMouseOut(d, i) {
    circ = d3.select(this)
        .style("fill", function() { return getColor(d, classifier) })
        .style("stroke", function() { return getColor(d, classifier) });

    let graph = d3.select(this.parentNode)  // g element containing circles

    let chart = d3.select(this.parentNode.parentNode)  // svg element containing everything

    let chartID = chart.attr("id");
    let phonIndex = chartID.indexOf("_");
    let phon = chartID.slice(phonIndex + 1);
    let charName = circ.attr("character");

    let labelID = phon + "_" + charName.replace(/\./g, "-") + "_label";

    d3.select("#" + labelID).remove();
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
            .attr("width", width)
            .attr("height", height)
            .attr("id", function(d) { return "Chart_" + d.phoneme; });

        svg.each(function(chartEntry) {
            phoneme = chartEntry.phoneme;
            chartData = chartEntry.data;

            var label = d3.select(this).append("g")  // Element to contain phoneme label
                .attr("class", "label")
                .attr("width", xMargin)
                .attr("height", height);

            label.append("text")  // Text within the Label element
                .attr("x", xMargin / 2)
                .attr("y", height / 2)
                .style("text-anchor", "middle")
                .style("fill", "#999999")
                .style("stroke", "black")
                .style("font-size", "48px")
                .text(phoneme);

            var legend = d3.select(this).append("g")  // Element to contain legend for classes
                .attr("class", "legend")
                .attr("transform", "translate(" + xMargin + ", 0)")
                .attr("width", width - xMargin)
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
                .range([10, width - xMargin - 10]);               

            var xAxis = d3.axisBottom(xScale);

            var axis = d3.select(this).append("g")  // Element to contain axis
                .attr("class", "axis")
                .attr("transform", "translate(" + xMargin + "," + (height - (yMargin / 2)) + ")")
                .attr("width", width - xMargin)
                .attr("height", yMargin)
                .call(xAxis);

            var middle = (height / 2) - yMargin;

            var xForce = d3.forceX(function(d) { return xScale(d.Zscore); })  // force to pull circle towards its specified x value
                .strength(0.9);
            var yForce = d3.forceY(middle)
                .strength(0.1);
            var collision = d3.forceCollide()  // applied to every node
                .radius(radius + 1)
                .strength(0.7)
                .iterations(10);

            var simulation = d3.forceSimulation(chartData)  // Initializes a simulation with each circle as a node
                .force("xForce", xForce)
                .force("yForce", yForce)
                .force("collision", collision)
                .stop();

            for (let i = 0; i < 120; i++) { simulation.tick(); };

            var g = d3.select(this).append("g")  // Element to contain circles
                .attr("class", "graph")
                .attr("transform", "translate(" + xMargin + "," + yMargin + ")")
                .attr("width", width - xMargin)
                .attr("height", height - yMargin);

            var circles = g.selectAll("circle")
                    .data(chartData);
            circle = circles.enter().append("circle")
                .attr("r", function(d) { return radius; })
                .attr("cx", function(d) { return d.x; })  //truncScore(d.Zscore)); })
                .attr("cy", function(d) { return d.y; })
                .attr("character", function(d) { return d.character; })
                .attr("Zscore", function(d) { return d.Zscore; })
                .attr("title", function(d) { return d.character + ": " + d.Zscore.toFixed(3); })
                .on("mouseover", handleMouseOver)
                .on("mouseout", handleMouseOut);

            let classifier_keys = Object.keys(classifiers);
            circle.attr("class", function(d) { 
                let class_list = new Array();
                for (let i = 0; i < classifier_keys.length; i++) {
                    class_list.push(d[classifier_keys[i]]);
                };
                return class_list.join(" ");
            });

            colorCircles();
        });
    });
});
