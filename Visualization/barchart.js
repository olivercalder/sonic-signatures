var width;  // of bar graph, set by multiplying barWidth by number of phonemes, in update()
var height = 300;  // of bar graph
var barWidth = 30;  // of individual bars

var xMargin = 60;  // on either side of the bar graph
var yMargin = 60;  // on either side of the bar graph
var totalWidth = width + (2 * xMargin);  // of graph and margins
var totalHeight = height + (2 * yMargin);  // of graph and margins

var gridWidth;  // total number of charts which fit on a single row
var gridHeight;  // total number of rows of charts

var xBuffer = 20;  // on either side of the row of graphs
var yBuffer = 20;  // above and below the columns of graphs

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
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
var characteristics;

var renderBuffer = 2;  // The number of rows beyond those visible that will be rendered
var triggerBuffer = 1; // The number of rows beyond those visible that will trigger the next render
var visible = new Map();
var startVisible;
var startIndex;
var endVisible;
var endIndex;



var yScale = d3.scaleLinear()
    .range([height - 10, 10])
    // .domain() must be set independently


function getCharacters(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    let characters = new Array();
    newData.forEach(entry => characters.push(entry.character));
    return characters;
};


function getPhonemes(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    let phonemes = new Array();
    (newData[0]["data"]).forEach(d => phonemes.push(d.phoneme));
    return phonemes;
};


function getZscores(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
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
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    let Zscores = getZscores(newData);
    let ZscoreMin = getArrayMin(Zscores);
    let ZscoreMax = getArrayMax(Zscores);

    yScale.domain([ZscoreMin, ZscoreMax]);
    return yScale;
};


function getXPos(index) {
    return (index % gridWidth) * totalWidth;
};


function getYPos(index) {
    return Math.floor(index / gridWidth) * totalHeight;
};


function drawChart(entry, index, scale = yScale, xPos = false, yPos = false, svg = d3.select("#ZscoreWindow")) {
    if (!xPos || !yPos) {
        xPos = getXPos(index);
        yPos = getYPos(index);
    };

    let character = entry.character;
    let chartData = entry.data;

    // Creates chart element and positions it in primary svg
    let chart = svg.append("g")
        .attr("class", "id_" + character.replace(/\./g, "-") + " chart")
        .attr("transform", "translate(" + xPos + ", " + yPos + ")")
        .attr("width", totalWidth)
        .attr("height", totalHeight);

    // Creates element to contain character title
    let label = chart.append("g")
        .attr("class", "id_" + character.replace(/\./g, "-") + " title")
        .attr("transform", "translate(" + xMargin + ", 0)")
        .attr("width", width)
        .attr("height", height)

    // Writes character name within the label element
    label.append("text")
        .attr("x", width / 2)
        .attr("y", yMargin / 2)
        .attr("class", "id_" + character.replace(/\./g, "-") + " title")
        .style("text-anchor", "middle")
        .style("fill", "black")
        .style("stroke", "black")
        .style("font-size", "16px")
        .text(character);

    let yAxis = d3.axisLeft(scale);

    // Creates element to contain axis
    chart.append("g")
        .attr("class", "id_" + character.replace(/\./g, "-") + " axis")
        .attr("transform", "translate(" + (xMargin / 2) + ", " + yMargin + ")")
        .attr("width", xMargin / 2)
        .attr("height", height)
        .call(yAxis);

    // Creates element to contain bars and phoneme labels
    let graph = chart.append("g")
        .attr("class", "id_" + character.replace(/\./g, "-") + " graph")
        .attr("transform", "translate(" + xMargin + ", " + yMargin + ")")
        .attr("width", width)
        .attr("height", height);

    // Creates bar containers within graph container and binds data to them
    let bars = d3.select("g.graph.id_" + character.replace(/\./g, "-")).selectAll("g.bar")
            .data(entry)
        .enter().append("g")
            .attr("class", d => "id_" + character.replace(/\./g, "-") + " bar " + d.phoneme)
            .attr("transform", (d, i) => "translate(" + (barWidth * i) + ", 0)")
            .attr("width", barWidth)
            .attr("height", height);
    
    // Creates rectangles in bar containers
    bars.append("rect")
        .attr("x", 1)
        .attr("y", d => d.Zscore > 0 ? scale(d.Zscore) : scale(0))
        .attr("width", barWidth - 1)
        .attr("height", d => Math.abs(scale(d.Zscore) - scale(0)));

    // Creates phoneme label above/below bar
    bars.append("text")
        .attr("class", d => "id_" + character.replace(/\./g, "-") + " phoneme label " + d.phoneme)
        .attr("x", barWidth / 2)
        .attr("y", d => (d.Zscore >= 0) ? scale(d.Zscore) - 12 : scale(d.Zscore) + 18)
        .style("text-anchor", "middle")
        .style("font-size", "10px")
        .text(d => d.phoneme + ": " + d.Zscore.toFixed(3));
};


// Returns the indices of the first and last charts visible onscreen, not including the buffer
//     Excludes buffer so that this can be used to compare current position with buffer indices
function getVisibleIndices(callbackFunction = false) {
    let winTop = $(window).scrollTop();
    let winBot = winTop + $(window).height();
    startVisible = Math.floor(winTop / totalHeight) * gridWidth;
    endVisible = Math.floor(winBot / totalHeight) * gridWidth;
    if (callbackFunction) { callbackFunction(startVisible, endVisible); };
    return [startVisible, endVisible];
};


// Checks whether the window has scrolled enough to require refresh,
//     and if so, calls refreshVisible()
function checkVisible() {
    getVisibleIndices(function(startVisible, endVisible) {
        if (startVisible - triggerBuffer <= startIndex || endVisible + triggerBuffer >= endIndex) {
            refreshVisible(data, yScale, false);
        };
    });
};


// Recalculates which graphs are visible and populates visible ones,
//     removing those that are no longer visible
function refreshVisible(newData = data, scale = yScale, fullRefresh = false) {
    getVisibleIndices(function(startVisible, endVisible) {
        startIndex = Math.max(0, startVisible - (renderBuffer * gridWidth));
        endIndex = Math.min(newData.length - 1, endVisible + (renderBuffer * gridWidth));
        let newVisible = new Map();
        for (let i = startIndex; i <= endIndex; i++) {
            let entry = newData[i];
            let character = entry.character;
            newVisible.set(character, entry);
            if (!visible.has(character) || fullRefresh) {
                drawChart(entry, i, scale)
            };
        };
        visible.forEach(function(entry) {
            if (!newVisible.has(entry.character)) {
                d3.select("g.chart.id_" + entry.character.replace(/\./g, "-")).remove()
            };
        });
        visible = newVisible;
    });
};


function refreshSize(callbackFunction = false) {
    svgWidth = $(window).width();
    //gridWidth = ((svgWidth - xBuffer) / (totalWidth + xBuffer));
    gridWidth = Math.floor(svgWidth / totalWidth);
    gridHeight = Math.floor(data.length / gridWidth) + 1;
    //svgHeight = (totalHeight + yBuffer) * gridHeight + yBuffer;
    svgHeight = totalHeight * gridHeight;
    d3.select("#ZscoreWindow")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
    if (callbackFunction) { callbackFunction(); };
};


function update(newData, sortBy = "name") {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    
    let characters = getCharacters(newData);
    let phonemes = getPhonemes(newData);
    width = barWidth * phonemes.length;
    totalWidth = width + (2 * xMargin);

    let newScale = updateScale(newData);

    /*
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
        .attr("class", d => "id_" + d.character.replace(/\./g, "-"))
        .each(entry => initializeSVG(entry, newScale));
    */

    refreshSize();
    $(window).on("resize", function() {
        refreshSize(refreshVisible);
    });

    refreshVisible(newData, newScale);
    $(window).on("scroll", function() {
        checkVisible(newData, newScale);
    });
};


// Loads Z-scores from specified file path, then processes it and executes callback function on the data
function loadData(ZscorePath, callbackFunction) {
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
                let barData = new Array();
                phonemes.forEach(function(phoneme) {
                    let phonData = new Object();
                    phonData["phoneme"] = phoneme;
                    phonData["Zscore"] = parseFloat(rawData[character][phoneme]);
                    phonData["character"] = character;
                    Object.keys(classifiers).forEach(classifier => phonData[classifier] = characteristics[character][classifier]);
                    barData.push(phonData);
                });
                charData["data"] = barData;
                newData.push(charData);
            });
            // This creates data with the structure:
            //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
            //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
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
