var width = 960;
var height = 300;
var xMargin = 60;
var yMargin = 60;
var classifiers = {
    "role":   ["protag", "antag",   "fool",  "other"],
    "gender": ["m",      "f"],
    "genre":  ["comedy", "tragedy", "history"]
};
var colors =  ["blue",   "red",     "green", "yellow"]

function getColor(d, classifier, characteristics) {
    name = d.character;
    charInfo = characteristics.find(item => item.character === name);
    classification = charInfo[classifier];
    colorIndex = classifiers[classifier].indexOf(classification);
    return colors[colorIndex];
};

//d3.json("../Archive/Vowels-Only-No-Others/percentages_Z-scores.json", function(rawData) { 
//d3.json("percentages_Z-scores.json", function(rawData) { 
d3.json("https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Archive/Vowels-Only-No-Others/percentages_Z-scores.json", function(rawData) { 
    var characters = Object.keys(rawData);
    var phonemes = Object.keys(rawData[characters[0]]);
    var data = new Array();
    for (var i=0; i<phonemes.length; i++) {
        phoneme = phonemes[i];
        var phonData = new Array();
        data.push({"phoneme": phoneme, "data": phonData});
        for (var j=0; j<characters.length; j++) {
            var charName = characters[j];
            var Zscore = rawData[charName][phoneme];
            phonData.push({"score": Zscore, "character": charName});
        };
    };

    var ZscoreWindow = d3.select("#ZscoreWindow");
    var svgs = ZscoreWindow.selectAll("svg")
            .data(data);

    var svg = svgs.enter().append("svg")
        .attr("width", width)
        .attr("height", height)
        .attr("id", function(d) { return "Chart_" + d.phoneme; });

    var axis = svg.append("g")  // Element to contain axis
        .attr("transform", "translate(" + xMargin + "," + (height - (yMargin / 2)) + ")")
        .attr("class", "axis")
        .attr("width", width - xMargin)
        .attr("height", yMargin);

    axis.each(function(chartEntry) {
        chartData = chartEntry.data;
        axisScale = d3.scale.linear()
            .domain(d3.extent(chartData, function(d) { return d.score; }))
            .range([10, width - xMargin - 10]);

        var xAxis = d3.svg.axis()
            .orient("bottom")
            .scale(axisScale);

        axis.call(xAxis);
    });

    var g = svg.append("g")  // Element to contain circles
        .attr("transform", "translate(" + xMargin + "," + yMargin + ")")
        .attr("width", width - xMargin)
        .attr("height", height - yMargin);
        // Add line to place label on left of SVG at this stage

    g.each(function(chartEntry) {
        chartData = chartEntry.data;

        xScale = d3.scale.linear()
            .domain(d3.extent(chartData, function(d) { return d.score; }))
            .range([10, width - xMargin - 10]);

        var circles = d3.select(this).selectAll("circle")
                .data(chartData);
        circles.enter().append("circle")
            .attr("r", 4)
            .attr("cx", function(d) { return xScale(d.score); })
            .attr("cy", (height / 2) - yMargin)
            .attr("character", function(d) { return d.character; })
            .attr("score", function(d) { return d.score; });
    });

    d3.csv("https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Reference/characteristics.csv", function(characteristics) {
        classifier = "role"

        var legend = svg.append("g")  // Element to contain legend for classes
            .attr("transform", "translate(" + xMargin + ", 0)")
            .attr("class", "legend")
            .attr("width", width - xMargin)
            .attr("height", height - yMargin);

        var circles = d3.selectAll("circle")
            .style("fill", function(d) { return getColor(d, classifier, characteristics) })
            .style("stroke", function(d) { return getColor(d, classifier, characteristics) });
    });


/*
                //.data(function(d) { return d.data; })
                //.enter().append("circle")
    for (var n=0; n<phonemes.length; n++) {
        var id = "#Chart_" + phonemes[n];
        var chartData = data[n].data;
        xScale = d3.scale.linear()
            .domain([d3.min(chartData, function(d) { return d.score; }),
                     d3.max(chartData, function(d) { return d.score; })])
            .range([0, width]);
        var svg = d3.select(id)
            .selectAll("circle")
                    .data(data[n].data)
                .enter().append("circle")
                    .attr("r", 3)
                    .attr("cx", function(d) { return xScale(d.score); })
                    .attr("cy", 100)
                
    }
*/

});
