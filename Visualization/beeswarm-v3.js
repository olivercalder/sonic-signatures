var width = 1200;
var height = 400;
var xMargin = 100;
var yMargin = 60;
var classifiers = {
    "role":   ["protag", "antag",   "fool",  "other"],
    "gender": ["m",      "f"],
    "genre":  ["comedy", "tragedy", "history"]
};
var colors =  ["blue",   "red",     "green", "yellow"]

var classifier = "role";
var characteristics = new Array()

function getColor(d, classifier, characteristics) {
    name = d.character;
    charInfo = characteristics.find(item => item.character === name);
    classification = charInfo[classifier];
    colorIndex = classifiers[classifier].indexOf(classification);
    return colors[colorIndex];
};

function colorCircles() {
    d3.selectAll("circle")
        .style("fill", function(d) { return getColor(d, classifier, characteristics) })
        .style("stroke", function(d) { return getColor(d, classifier, characteristics) });
};

function handleMouseOver(d, i) {
    let circ = d3.select(this)  // circle element being modified
        .style("fill", "white")
        .style("stroke", "black");

    let charName = circ.attr("character");
    let score = parseFloat(circ.attr("score")).toFixed(3);

    let graph = d3.select(this.parentNode)  // g element containing circles

    let chart = d3.select(this.parentNode.parentNode)  // svg element containing everything

    let chartID = chart.attr("id");
    let phonIndex = chartID.indexOf("_");
    let phon = chartID.slice(phonIndex + 1);

    let labelID = phon + "_" + charName.replace(".", "-") + "_label";

    circLabel = graph.append("text")
        .attr("id", labelID)
        .attr("x", function() { return circ.attr("cx") - 50 })
        .attr("y", function() { return circ.attr("cy") - 15 })
        .text(function() { return charName + ": " + score; });
}

function handleMouseOut(d, i) {
    circ = d3.select(this)
        .style("fill", function() { return getColor(d, classifier, characteristics) })
        .style("stroke", function() { return getColor(d, classifier, characteristics) });

    let graph = d3.select(this.parentNode)  // g element containing circles

    let chart = d3.select(this.parentNode.parentNode)  // svg element containing everything

    let chartID = chart.attr("id");
    let phonIndex = chartID.indexOf("_");
    let phon = chartID.slice(phonIndex + 1);
    let charName = circ.attr("character");

    let labelID = phon + "_" + charName.replace(".", "-") + "_label";

    d3.select("#" + labelID).remove();
}


//d3.json("../Archive/Vowels-Only-No-Others/percentages_Z-scores.json", function(rawData) { 
//d3.json("percentages_Z-scores.json", function(rawData) { 
//       https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Archive/Vowels-Only-All/percentages_Z-scores.json
d3.json("https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Archive/Vowels-Only-No-Others/percentages_Z-scores.json", function(rawData) { 
    d3.csv("https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Reference/characteristics.csv", function(c) {
        characteristics = c;

        var characters = Object.keys(rawData);
        var phonemes = Object.keys(rawData[characters[0]]);
        var data = new Array();
        for (let i=0; i<phonemes.length; i++) {
            phoneme = phonemes[i];
            var phonData = new Array();
            data.push({"phoneme": phoneme, "data": phonData});
            for (let j=0; j<characters.length; j++) {
                var charName = characters[j];
                var Zscore = rawData[charName][phoneme];
                phonData.push({"score": Zscore, "character": charName});
            };
        };
        // This creates data with structure:
        //      data = [{"phoneme": phoneme, "data": phonData}, ...]
        //      where phonData = [{"score": Zscore, "character": charName}, ...]

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

            xScale = d3.scale.linear()
                .domain(d3.extent(chartData, function(d) { return d.score; }))
                .range([10, width - xMargin - 10]);

            var xAxis = d3.svg.axis()
                .orient("bottom")
                .scale(xScale);

            var axis = d3.select(this).append("g")  // Element to contain axis
                .attr("class", "axis")
                .attr("transform", "translate(" + xMargin + "," + (height - (yMargin / 2)) + ")")
                .attr("width", width - xMargin)
                .attr("height", yMargin)
                .call(xAxis);

            var g = d3.select(this).append("g")  // Element to contain circles
                .attr("class", "graph")
                .attr("transform", "translate(" + xMargin + "," + yMargin + ")")
                .attr("width", width - xMargin)
                .attr("height", height - yMargin);

            var circles = g.selectAll("circle")
                    .data(chartData)
                .enter().append("circle")
                    .attr("r", 4)
                    .attr("cx", function(d) { return xScale(d.score); })
                    .attr("cy", (height / 2) - yMargin)
                    .attr("character", function(d) { return d.character; })
                    .attr("score", function(d) { return d.score; })
                    .attr("title", function(d) { return d.character + ": " + parseFloat(d.score).toFixed(3); })
                    .on("mouseover", handleMouseOver)
                    .on("mouseout", handleMouseOut);

            var force = d3.layout.force()
                .nodes(circles)
                .charge(-30)
                .chargeDistance(10);

            force.start();
            for (let n=0; n<10; n++) { force.tick(); };
            force.stop();

            colorCircles();
        });
    });
});