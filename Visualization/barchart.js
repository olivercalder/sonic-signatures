var width = 300;  // of bar graph
var height = 300;  // of bar graph
var barWidth = 30;  // of individual bars

var xMargin = 60;  // on either side of the bar graph
var yMargin = 60;  // on either side of the bar graph
var totalWidth = width + (2 * xMargin);  // of graph and margins
var totalHeight = height + (2 * yMargin);  // of graph and margins

var gridWidth;  // total number of charts which fit on a single row
var gridHeight;  // total number of rows of charts

var xBuffer;  // on either side of the row of graphs
var yBuffer;  // above and below the columns of graphs

var svgHeight;  // of the svg element
var svgWidth;  // of the svg element


var classifiers = {
    "role":   ["protag", "antag",   "fool",  "other"],
    "gender": ["m",      "f"],
    "genre":  ["comedy", "tragedy", "history"]
};
var colors =  ["blue",   "red",     "green", "yellow"];

var data;  // Will be modified by initial d3.json call
    // data is of the form:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>, ...} ...]
var characteristics;


var yScale = d3.scaleLinear()
    .range(height - 10, 10)
    // .domain() must be set independently


function getCharacters(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>, ...} ...]
    let characters = new Array();
    newData.forEach(entry => characters.push(entry.character));
    return characters;
};


function getPhonemes(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>, ...} ...]
    let phonemes = new Array();
    newData[0]["data"].forEach(d => phonemes.push(d.phoneme));
    return phonemes;
};


function getZscores(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>, ...} ...]
    let Zscores = new Array();
    newData.forEach(function(entry) {
        entry["data"].forEach(bar => Zscores.push(bar["Zscore"]))
    });
    return Zscores;
};


function getArrayMin(arr) {
    let min = arr.reduce(function(a, b) {
        return Math.min(a, b);
    });
    return min;
};


function getArrayMax(arr) {
    let max = arr.reduce(function(a, b) {
        return Math.max(a, b);
    });
    return max;
};


// Updates yScale according to specified data
function updateScale(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>, ...} ...]
    let Zscores = getZscores(newData);
    let ZscoreMin = getArrayMin(Zscores);
    let ZscoreMax = getArrayMax(Zscores);

    yScale.domain([ZscoreMin, ZscoreMax]);
    return yScale;
};


function drawChart(entry, scale = yScale) {
    let character = entry.character;
    let chartData = entry.data;

    // Creates element to contain character title
    let label = d3.select("svg." + character).append("g")
        .attr("class", function() { return character + " title"; })
        .attr("transform", "translate(" + xMargin + ", 0)")
        .attr("width", width)
        .attr("height", height)

    // Writes character name within the label element
    label.append("text")
        .attr("x", width / 2)
        .attr("y", yMargin / 2)
        .attr("class", function() { return character + " title"; })
        .style("text-anchor", "middle")
        .style("fill", "black")
        .style("stroke", "black")
        .style("font-size", "16px")
        .text(character);

    // Creates element to contain axis
    d3.select("svg." + character).append("g")
        .attr("class", function() { return character + " axis"; })
        .attr("transform", "translate(" + (xMargin / 2) + ", " + yMargin + ")")
        .attr("width", xMargin / 2)
        .attr("height", height)
        .call(xAxis);


};


function refreshSize(callbackFunction) {
    svgWidth = $(window).width;
    gridWidth = ((svgWidth - xBuffer) / (totalWidth + xBuffer));
    gridHeight = Math.floor(data.length / gridWidth) + 1;
    svgHeight = (totalHeight + yBuffer) * gridHeight + yBuffer;
    d3.select("#ZscoreWindow")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
    if (callbackFunction) { callbackFunction(); };
};


function update(newData, sortBy = "name") {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>, ...} ...]
    
    let characters = getCharacters(newData);
    let phonemes = getPhonemes(newData);
    width = barWidth * phonemes.length;
    totalWidth = width + (2 * xMargin);

    gridWidth = ($(window).width / (totalWidth + )

    let newScale = updateScale(newData);

    let ZscoreWindow = d3.select("#ZscoreWindow")
        .attr("width", 

    // Do not bind data to elements beforehand
    /*
    // Bind data to svg elements, pairing by character
    let charts = ZscoreWindow.selectAll("g")
        .data(newData, d => d.character);
        
    // Remove unneeded svg elements
    charts.exit().remove();

    // Add g elements for new data
    charts.enter().append("g")
        .attr("width", totalWidth)
        .attr("height", totalHeight)
        .attr("id", d => "Chart_" + d.character)
        .attr("class", d => d.character)
        .each(entry => initializeSVG(entry, newScale));
    */

    refreshSize();
    $(window).on("resize", function() {
        refreshSize();
    });

    refreshVisible(newData, newScale);
    $(window).on("scroll", function() {
        checkVisible(newData, newScale);
    });
};


// Loads Z-scores from specified file path, then processes it and executes callback function on the data
function loadData(ZscorePath, callbackfunction) {
    let newData = new Array();
    characteristics = new Object();
    d3.json(ZscorePath, function(rawData) {
        d3.csv("../Reference/characteristics.csv", function(c) {
            c.forEach(entry => characteristics[entry["character"]] = entry);

            let characters = Object.keys(rawData);
            let phonemes = Object.keys(rawData[characters[0]]);
            characters.forEach(function(character) {
                let charData = new Object();
                charData["character"] = character;
                Object.keys(classifiers).forEach(classifier => charData[classifier] = characteristics[character][classifier]);
                charData["data"] = function(character) {
                    let barData = new Array();
                    phonemes.forEach(function(phoneme) {
                        let phoneData = new Object();
                        phonData["phoneme"] = phoneme;
                        phonData["Zscore"] = rawData[character][phoneme];
                        phonData["character"] = character;
                        Object.keys.forEach(classifier => phonData[classifier] = characteristics[character][classifier]);
                        barData.push(phonData);
                    });
                    return barData;
                };
                newData.push(charData);
            });
            // This creates data with the structure:
            //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
            //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>, ...} ...]
            callbackFunction(newData);
        });
    });
};

// Initializes call to data files and calls update() on the data
loadData("../Archive/Vowels-Only-No-Others/percentages_Z-scores.json", function(newData) {
    data = newData;
    update(newData);
});

/*
 * Template for doing other things with new data:
 *
 * loadData(path, function(newData) {
 *     // do thing with newData
 * }
 *
 * Set global data to newData:
 *
 * loadData(path, function(newData) {
 *     data = newData;
 * }
 */
