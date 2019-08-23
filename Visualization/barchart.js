var width;  // of bar graph, set by multiplying barWidth by number of phonemes, in update()
var height = 300;  // of bar graph
var barWidth = 30;  // of individual bars

var xMargin = 30;  // on either side of the bar graph
var yMargin = 30;  // on either side of the bar graph
var totalWidth = width + (2 * xMargin);  // of graph and margins
var totalHeight = height + (2 * yMargin);  // of graph and margins

var oldTotalWidth;  // total width before the last change in data or size

var gridWidth;  // total number of charts which fit on a single row
var gridHeight; // total number of rows of charts

var oldGridWidth;  // grid width before the last change in data or size

var xBuffer = 20;  // on either side of the row of graphs
var yBuffer = 20;  // above and below the columns of graphs

var svgHeight;  // of the svg element
var svgWidth;  // of the svg element


var stdDur = 500;  // standard duration of animations
var longDur = 1000; // longer duration of animations


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


// Checkbox to toggle displaying average bars
var averageToggle = d3.select("controlPanel");

averageToggle.append("input")
    .attr("type", "checkbox")
    .attr("class", "checkbox")
    .attr("id", "averageToggle")
    .on("change", function() {
        averages = d3.select("#averageToggle").property("checked");
        visible.forEach(entry => updateAverages(entry, true));
    });


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


function getXPos(index, gWidth = gridWidth, tWidth = totalWidth) {
    return (index % gWidth) * tWidth;
};


function getYPos(index, gWidth = gridWidth, tHeight = totalHeight) {
    return Math.floor(index / gWidth) * tHeight;
};


function getIndex(character, d = data) {
    // d should have the structure:
    //     data = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    let index = 0;
    if (d) {
        while (d[index]["character"] != character) {
            index += 1;
        }
        if (index == d.length) {
            index = false;
        };
    } else {
        index = false;
    };
    return index;
};


function removeBars(selection, animate = false) {
    selection.selectAll("rect")
        .transition()
        .duration((animate) ? stdDur : 0)
        .attr("y", yScale(0))
        .attr("height", 0)
        .remove()
    selection.selectAll("text")
        .transition()
        .duration((animate) ? stdDur : 0)
        .style("font-size", "0px")
        .remove()
};


function drawBars(selection, animate = false) {
    selection.append("rect")
        .attr("class", d => "id_" + d.character.replace(/\./g, "-") + " rect " + d.phoneme)
        .attr("x", 1)
        .attr("width", barWidth - 2)
        .attr("y", yScale(0))
        .attr("height", 0)
        .transition()
        .duration((animate) ? stdDur : 0)
        .attr("y", d => d.Zscore > 0 ? yScale(d.Zscore) : yScale(0))
        .attr("height", d => Math.abs(yScale(d.Zscore) - yScale(0)));
    selection.append("text")
        .attr("class", d => "id_" + d.character.replace(/\./g, "-") + " phoneme label " + d.phoneme)
        .attr("font-size", "0px")
        .attr("x", barWidth / 2 + 4)
        .attr("y", d => (d.Zscore >= 0) ? yScale(d.Zscore) - 5 : yScale(d.Zscore) + 5)
        .attr("transform", d => "rotate(270," + (barWidth / 2 + 4) + "," + ((d.Zscore >= 0) ? yScale(d.Zscore) - 5 : yScale(d.Zscore) + 5) + ")")
        .text(d => d.phoneme + ": " + d.Zscore.toFixed(3))
        .transition()
        .duration((animate) ? stdDur : 0)
        .style("text-anchor", d => (d.Zscore >= 0) ? "start" : "end")
        .style("font-size", "10px")
};


function updateBars(selection, animate = false) {
    selection.select("rect")
        .transition()
        .duration((animate) ? stdDur : 0)
        .attr("y", d => d.Zscore > 0 ? yScale(d.Zscore) : yScale(0))
        .attr("height", d => Math.abs(yScale(d.Zscore) - yScale(0)));
    selection.select("text")
        .transition()
        .duration((animate) ? stdDur : 0)
        .attr("x", barWidth / 2 + 4)
        .attr("y", d => (d.Zscore >= 0) ? yScale(d.Zscore) - 5 : yScale(d.Zscore) + 5)
        .attr("transform", d => "rotate(270," + (barWidth / 2 + 4) + "," + ((d.Zscore >= 0) ? yScale(d.Zscore) - 5 : yScale(d.Zscore) + 5) + ")")
        .style("text-anchor", d => (d.Zscore >= 0) ? "start" : "end")
        .style("font-size", "10px")
        .text(d => d.phoneme + ": " + d.Zscore.toFixed(3));
};


function updateChart(entry, index, animate = false, svg = d3.select("#ZscoreWindow", xPos = false, yPos = false)) {
    if (!xPos || !yPos) {
        xPos = getXPos(index);
        yPos = getYPos(index);
    };

    let character = entry.character;
    let chartData = entry.data;

    // Checks whether chart element already exists
    let chart = svg.select("g.chart.id_" + character.replace(/\./g, "-"));
    if (chart.size() == 0) {
        // Creates chart element and positions it in primary svg
        let oldIndex = getIndex(character, data);
        oldIndex = (oldIndex) ? oldIndex : index;
        let oldXPos = getXPos(oldIndex, oldGridWidth, oldTotalWidth);
        let oldYPos = getYPos(oldIndex, oldGridWidth, totalHeight);
        chart = svg.append("g");
        chart
            .attr("class", "id_" + character.replace(/\./g, "-") + " chart")
            .attr("transform", "translate(" + oldXPos + ", " + oldYPos + ")")
            .attr("width", totalWidth)
            .attr("height", totalHeight)
            .transition()
            .duration(stdDur)
            .attr("transform", "translate(" + xPos + ", " + yPos + ")");
    } else {
        // Modifies the existing chart element
        chart
            .attr("width", totalWidth)
            .attr("height", totalHeight)
            .transition()
            .duration(stdDur)
            .attr("transform", "translate(" + xPos + ", " + yPos + ")");
    };

    // Checks whether title element already exists
    let title = chart.select("g.title");
    if (title.size() == 0) {
        // Creates element to contain character title
        title = chart.append("g")
            .attr("class", "id_" + character.replace(/\./g, "-") + " title")
            .attr("transform", "translate(" + xMargin + ", 0)")
            .attr("width", width)
            .attr("height", height)
    } else {
        // Modifies existing title element
        title
            .attr("class", "id_" + character.replace(/\./g, "-") + " title")
            .attr("width", width)
            .attr("height", height)
            .transition()
            .duration(stdDur)
            .attr("transform", "translate(" + xMargin + ", 0)")
    };

    // Checks whether title text already exists
    titleText = title.select("text");
    if (titleText.size() == 0) {
        // Writes character name within the title element
        titleText = title.append("text")
            .attr("x", width / 2)
            .attr("y", yMargin / 2)
            .attr("class", "id_" + character.replace(/\./g, "-") + " title")
            .style("text-anchor", "middle")
            .style("fill", "black")
            .style("stroke", "black")
            .style("font-size", "16px")
            .text(character);
    } else {
        // Modifies existing text in the title element
        titleText
            .attr("class", "id_" + character.replace(/\./g, "-") + " title")
            .transition()
            .duration(stdDur)
            .attr("x", width / 2)
            .attr("y", yMargin / 2)
            .style("text-anchor", "middle")
            .style("fill", "black")
            .style("stroke", "black")
            .style("font-size", "16px")
            .text(character);
    };

    let yAxis = d3.axisLeft(yScale);

    // Checks whether axis element already exists
    let axis = chart.select("g.axis");
    if (axis.size() == 0) {
        // Creates element to contain axis
        axis = chart.append("g")
            .attr("class", "id_" + character.replace(/\./g, "-") + " axis")
            .attr("transform", "translate(" + (xMargin) + ", " + yMargin + ")")
            .attr("width", xMargin / 2)
            .attr("height", height)
            .call(yAxis);
    } else {
        // Modify existing axis element
        axis
            .attr("class", "id_" + character.replace(/\./g, "-") + " axis")
            .attr("width", xMargin / 2)
            .attr("height", height)
            .transition()
            .duration(stdDur)
            .attr("transform", "translate(" + (xMargin) + ", " + yMargin + ")")
            .call(yAxis);
    };


    // Checks whether graph element already exists
    let graph = chart.select("g.graph");
    if (graph.size() == 0) {
        // Creates element to contain bars and phoneme labels
        graph = chart.append("g")
            .attr("class", "id_" + character.replace(/\./g, "-") + " graph")
            .attr("transform", "translate(" + xMargin + ", " + yMargin + ")")
            .attr("width", width)
            .attr("height", height);
    } else {
        // Modifies existing element containing bars and phoneme labels
        graph
            .attr("class", "id_" + character.replace(/\./g, "-") + " graph")
            .attr("width", width)
            .attr("height", height)
            .transition()
            .duration(stdDur)
            .attr("transform", "translate(" + xMargin + ", " + yMargin + ")")
    };

    // Binds data to bar elements containing rectangles and labels
    let bars = d3.select("g.graph.id_" + character.replace(/\./g, "-")).selectAll("g.bar")
            .data(chartData, d => d.phoneme);
    
    // Removes unneeded bars
    bars.exit().call(removeBars, animate);

    // Modifies existing bar elements
    bars
        .attr("class", d => "id_" + character.replace(/\./g, "-") + " bar " + d.phoneme)
        .transition()
        .duration(stdDur)
        .attr("width", barWidth)
        .attr("height", height)
        .attr("transform", (d, i) => "translate(" + (barWidth * i) + ", 0)")
        .call(updateBars, animate);

    // Creates new bar elements for new data
    bars.enter().append("g")
        .attr("class", d => "id_" + character.replace(/\./g, "-") + " bar " + d.phoneme)
        .attr("transform", (d, i) => "translate(" + (barWidth * i) + ", 0)")
        .attr("width", barWidth)
        .attr("height", height)
        .call(drawBars, animate);
};


function removeChart(character, d = data) {
    let newIndex = getIndex(character, d);
    if (newIndex !== false) {
        let newXPos = getXPos(newIndex);
        let newYPos = getYPos(newIndex);
        d3.select("g.chart.id_" + character.replace(/\./g, "-"))
            .transition()
            .duration(stdDur)
            .attr("transform", "translate(" + newXPos + "," + newYPos + ")")
            .remove();
    } else {
        d3.select("g.chart.id_" + character.replace(/\./g, "-"))
            .remove();
    };
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
            refreshVisible(data, false, false);
        };
    });
};


// Recalculates which graphs are visible and populates visible ones,
//     removing those that are no longer visible
function refreshVisible(newData = data, fullRefresh = false, animate = false, callbackFunction = false) {
    getVisibleIndices(function(startVisible, endVisible) {
        startIndex = Math.max(0, startVisible - (renderBuffer * gridWidth));
        endIndex = Math.min(newData.length - 1, endVisible + (renderBuffer * gridWidth));
        let newVisible = new Map();
        for (let i = startIndex; i <= endIndex; i++) {
            let entry = newData[i];
            let character = entry.character;
            newVisible.set(character, entry);
            if (!visible.has(character) || fullRefresh) {
                updateChart(entry, i, animate)
            };
        };
        visible.forEach(function(entry) {
            if (!newVisible.has(entry.character)) {
                removeChart(entry.character, newData)
            };
        });
        visible = newVisible;
        if (callbackFunction) { callbackFunction() };
    });
};


function refreshSize(newData = data, callbackFunction = false) {
    svgWidth = $(window).width();

    oldGridWidth = gridWidth;
    gridWidth = Math.floor(svgWidth / totalWidth);

    gridHeight = Math.floor((newData.length - 1) / gridWidth) + 1;
    
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

    oldTotalWidth = totalWidth;
    totalWidth = width + (2 * xMargin);
    oldTotalWidth = (oldTotalWidth) ? oldTotalWidth : totalWidth;

    let newScale = updateScale(newData);

    refreshSize(newData, function() {
        refreshVisible(newData, true, true, function() {
            data = newData;
            oldTotalWidth = totalWidth;
        });
    });

    var timeout;
    $(window).on("resize", function() {
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            refreshSize(newData, function() {
                refreshVisible(data, true, false, function() {
                    oldGridWidth = gridWidth;
                });
            });
        }, 250);
    });
    $(window).on("scroll", function() {
        checkVisible(newData);
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
            // This creates newData with the structure:
            //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
            //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
            callbackFunction(newData);
        });
    });
};

// Initializes call to data files and calls update() on the data
loadData("../Archive/Vowels-Only-No-Others/percentages_Z-scores.json", function(newData) {
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
