var navbarHeight = 96;

var width;  // of bar graph, set by multiplying barWidth by number of phonemes, in update()
var height = 300;  // of bar graph
var barWidth = 30;  // of individual bars

var xMargin = 30;  // on either side of the bar graph
var yMargin = 60;  // on either side of the bar graph
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


var shortDur = 250; // shorter duration of animations
var stdDur = 500;  // standard duration of animations
var longDur = 1000; //  longer duration of animations


var avgStrokeWidth = 3;  // Stroke width of average bars


var classifiers = {
    "role":   ["protag", "antag",   "fool",  "other"],
    "gender": ["m",      "f"],
    "genre":  ["comedy", "tragedy", "history"]
}
var colors =  ["blue",   "red",     "green", "yellow"];

var data;  // Will be modified by initial d3.json call
    // data is of the form:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
var fullData;  // Full data from the last loadData() call, without sorting or filtering
var characteristics;  // Classes of each character for each classifier
var averagesData;  // Average Z-score for each phoneme for each class
    // averageData of the form:
    //     averageData = {<phon1>: {<class1>: Zscore, <class2>: Zscore, ...}, <phon2>: {...}, ... }

var renderBuffer = 2;  // The number of rows beyond those visible that will be rendered
var triggerBuffer = 1; // The number of rows beyond those visible that will trigger the next render
var visible = new Map();
var startVisible;
var startIndex;
var endVisible;
var endIndex;


// Checkbox to toggle displaying average bars
var averageToggle = d3.select("#averageToggle")
    .on("change", update);

// Dropdown to select classifier
var classSelect = d3.select("#classSelect")
    .on("change", update);

classSelect.selectAll("option")
        .data(Object.keys(classifiers)).enter()
    .append("option")
        .text(d => d);

// Returns the currently selected classifier
function getClassifier() {
    return d3.select("#classSelect").property("value");
}

function getClasses() {
    let classifier = getClassifier();
    return classifiers[classifier].sort();
}

// Dropdown to select sorting
var sortSelect = d3.select("#sortSelect")
    .on("change", update);

// Dropdown to select characters
var characterSelect = d3.select("#characterSelect")
    .on("change", updateLoad);

// Dropdown to select calculation
var calculationSelect = d3.select("#calculationSelect")
    .on("change", updateLoad);

// Checkbox to toggle Emphasis
var emphasisToggle = d3.select("#emphasisToggle")
    .on("change", updateLoad);

// Checkbox to toggle Vowels-Only
var vowelsToggle = d3.select("#vowelsToggle")
    .on("change", updateLoad);


var yScale = d3.scaleLinear()
    .range([height - 10, 10])
    // .domain() must be set independently


function getColor(d) {
    let classifier = getClassifier();
    let classification = d[classifier];
    let colorIndex = classifiers[classifier].indexOf(classification);
    return colors[colorIndex];
}


function getCharacters(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    let characters = new Array();
    newData.forEach(entry => characters.push(entry.character));
    return characters;
}


function getPhonemes(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    let phonemes = new Array();
    (newData[0]["data"]).forEach(d => phonemes.push(d.phoneme));
    return phonemes;
}


function getZscores(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    let Zscores = new Array();
    newData.forEach(function(entry) {
        entry["data"].forEach(bar => Zscores.push(bar["Zscore"]))
    });
    return Zscores;
}


function getArrayMin(arr) {
    let min = arr.reduce(function(a, b) {
        return Math.min(a, b);
    });
    return min;
}


function getArrayMax(arr) {
    let max = arr.reduce(function(a, b) {
        return Math.max(a, b);
    });
    return max;
}


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
}


function getXPos(index, gWidth = gridWidth, tWidth = totalWidth) {
    return (index % gWidth) * tWidth;
}


function getYPos(index, gWidth = gridWidth, tHeight = totalHeight) {
    return Math.floor(index / gWidth) * tHeight + navbarHeight;
}


function getIndex(character, d = data) {
    // d should have the structure:
    //     data = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    let index = 0;
    if (d) {
        while (index < d.length && d[index]["character"] != character) {
            index += 1;
        }
        if (index == d.length) {
            index = false;
        }
    } else {
        index = false;
    }
    return index;
}


function updateAvgBars(selection, animate) {
    if (d3.select("#averageToggle").property("checked")) {
        avgRect = selection.select("rect.average");
        if (avgRect.size() == 0) {
            selection.append("rect")
                .attr("class", d => d[getClassifier()] + " average " + d.phoneme)
                .attr("x", Math.floor((avgStrokeWidth + 1) / 2))
                .attr("width", barWidth - avgStrokeWidth - 1)
                .attr("y", yScale(0))
                .attr("height", 0)
                .style("fill", "white")
                .style("fill-opacity", 0)
                .style("stroke", "black")
                .style("stroke-width", avgStrokeWidth)
                .transition()
                .duration((animate) ? stdDur : 0)
                .attr("y", function(d) {
                    avg = averagesData[d[getClassifier()]][d.phoneme]
                    if (avg > 0) {
                        return yScale(avg);
                    } else {
                        return yScale(0);
                    }
                })
                .attr("height", d => Math.abs(yScale(averagesData[d[getClassifier()]][d.phoneme]) - yScale(0)));
        } else {
            avgRect
                .transition()
                .duration((animate) ? stdDur : 0)
                .attr("y", function(d) {
                    avg = averagesData[d[getClassifier()]][d.phoneme]
                    if (avg > 0) {
                        return yScale(avg);
                    } else {
                        return yScale(0);
                    }
                })
                .attr("height", d => Math.abs(yScale(averagesData[d[getClassifier()]][d.phoneme]) - yScale(0)));
        }
    } else {
        selection.select("rect.average")
            .transition()
            .duration((animate) ? stdDur : 0)
            .attr("y", yScale(0))
            .attr("height", 0)
            .remove();
    }

}


function removeBars(selection, animate = false, dur = stdDur) {
    selection.selectAll("rect")
        .transition()
        .duration((animate) ? dur : 0)
        .attr("y", yScale(0))
        .attr("height", 0)
        .remove();
    selection.selectAll("text")
        .transition()
        .duration((animate) ? dur : 0)
        .style("font-size", "0px")
        .remove();
    selection
        .transition()
        .duration(dur)
        .remove();
}


function drawBars(selection, animate = false) {
    selection.append("rect")
        .attr("class", d => d.phoneme + " id_" + d.character.replace(/\./g, "-"))
        .attr("x", 1)
        .attr("width", barWidth - 2)
        .attr("y", yScale(0))
        .attr("height", 0)
        .style("fill", d => getColor(d))
        .style("stroke", d => getColor(d))
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
    selection.call(updateAvgBars, animate);
}


function updateBars(selection, animate = false) {
    let charID = ""
    if (selection.size() > 0) {
        charID = selection.datum().character.replace(/\./g, "-");
    }
    selection.select("rect.id_" + charID)
        .transition()
        .duration((animate) ? stdDur : 0)
        .attr("y", d => d.Zscore > 0 ? yScale(d.Zscore) : yScale(0))
        .attr("height", d => Math.abs(yScale(d.Zscore) - yScale(0)))
        .style("fill", d => getColor(d))
        .style("stroke", d => getColor(d));
    selection.select("text")
        .transition()
        .duration((animate) ? stdDur : 0)
        .attr("x", barWidth / 2 + 4)
        .attr("y", d => (d.Zscore >= 0) ? yScale(d.Zscore) - 5 : yScale(d.Zscore) + 5)
        .attr("transform", d => "rotate(270," + (barWidth / 2 + 4) + "," + ((d.Zscore >= 0) ? yScale(d.Zscore) - 5 : yScale(d.Zscore) + 5) + ")")
        .style("text-anchor", d => (d.Zscore >= 0) ? "start" : "end")
        .style("font-size", "10px")
        .text(d => d.phoneme + ": " + d.Zscore.toFixed(3));
    selection.call(updateAvgBars, animate);
}


function updateChart(entry, index, animate = false, svg = d3.select("#ZscoreWindow"), xPos = false, yPos = false) {
    if (!xPos || !yPos) {
        xPos = getXPos(index);
        yPos = getYPos(index);
    }

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
    }

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
    }

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
    }

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
    }


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
    }

    // Binds data to bar elements containing rectangles and labels
    let bars = d3.select("g.graph.id_" + character.replace(/\./g, "-")).selectAll("g.bar")
            .data(chartData, d => d.phoneme);
    
    // Removes unneeded bars
    bars.exit().call(removeBars, animate);

    // Modifies existing bar elements
    bars
        .attr("class", d => "id_" + character.replace(/\./g, "-") + " bar " + d.phoneme)
        .call(updateBars, animate)
        .transition()
        .duration(stdDur)
        .attr("width", barWidth)
        .attr("height", height)
        .attr("transform", (d, i) => "translate(" + (barWidth * i) + ", 0)");

    // Creates new bar elements for new data
    bars.enter().append("g")
        .attr("class", d => "id_" + character.replace(/\./g, "-") + " bar " + d.phoneme)
        .attr("width", barWidth)
        .attr("height", height)
        .attr("transform", (d, i) => "translate(" + (barWidth * i) + ", 0)")
        .call(drawBars, animate);
}


// Animates the removal of a chart, first by shrinking the 
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
        let chart = d3.select("g.chart.id_" + character.replace(/\./g, "-"))
        chart.selectAll(".bar")
            .call(removeBars, true, shortDur)
        chart
            .transition()
            .duration(shortDur)
            .remove();
    }
}


// Returns the indices of the first and last charts visible onscreen, not including the buffer
//     Excludes buffer so that this can be used to compare current position with buffer indices
function getVisibleIndices(callbackFunction = false) {
    let winTop = $(window).scrollTop();
    let winBot = winTop + $(window).height();
    startVisible = Math.floor(winTop / totalHeight) * gridWidth;
    endVisible = Math.floor(winBot / totalHeight) * gridWidth - 1;
    if (callbackFunction) { callbackFunction(startVisible, endVisible); }
    return [startVisible, endVisible];
}


// Checks whether the window has scrolled enough to require refresh,
//     and if so, calls refreshVisible()
function checkVisible() {
    getVisibleIndices(function(startVisible, endVisible) {
        if (startVisible - triggerBuffer <= startIndex || endVisible + triggerBuffer >= endIndex) {
            refreshVisible(data, false, false);
        }
    });
}


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
            }
        }
        visible.forEach(function(entry) {
            if (!newVisible.has(entry.character)) {
                removeChart(entry.character, newData)
            }
        });
        visible = newVisible;
        if (callbackFunction) { callbackFunction() }
    });
}


// Uses current dimensions of the window to calculate the grid size,
//     and then resizes the svg and calls the callback function
function refreshSize(newData = data, callbackFunction = false) {
    svgWidth = Math.max($(window).width(), totalWidth);

    oldGridWidth = gridWidth;
    gridWidth = Math.floor(svgWidth / totalWidth);

    gridHeight = Math.floor((newData.length - 1) / gridWidth) + 1;
    
    svgHeight = totalHeight * gridHeight + navbarHeight + yBuffer;
    d3.select("#ZscoreWindow")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
    if (callbackFunction) { callbackFunction(); }
}


// Gets the average Z-scores of each phoneme for each class, and returns it as a dictionary
function getAvgsData(sortedData = data) {
    // sortedData should have the following structure:
    //     sortedData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    let phonemes = getPhonemes(sortedData);
    let classifier = getClassifier();
    let classes = getClasses();
    let sums = new Object();
    let counts = new Object();
    classes.forEach(function(c) {
        sums[c] = new Object();
        counts[c] = new Object();
        phonemes.forEach(function(phon) {
            sums[c][phon] = 0;
            counts[c][phon] = 0;
        });
    });
    sortedData.forEach(function(entry) {
        entry.data.forEach(function(d) {
            sums[d[classifier]][d.phoneme] += d.Zscore;
            counts[d[classifier]][d.phoneme] += 1;
        });
    });
    let avgsData = new Object();
    classes.forEach(function(c) {
        avgsData[c] = new Object();
        phonemes.forEach(function(phon) {
            avgsData[c][phon] = sums[c][phon] / counts[c][phon];
        });
    });
    // avgsData is of the form:
    //     avgsData = {<class1>: {<phon1>: <avg1>, <phon2>: <avg2>, ... }, <class2>: { ... }, ... }
    return avgsData;
}


// Sorts the given data array and returns it
function sortDataAlpha(dataArr) {
    // dataArr should have the following structure:
    //     dataArr = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    sortedArr = dataArr.sort(function(a, b) {
        if (a.character < b.character) {
            return -1;
        } else if (a.character > b.character) {
            return 1;
        } else {
            return 0;
        }
    });
    return sortedArr;
}


// Sorts data by either name or class
function sortData(newData) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]
    let newSort = d3.select("#sortSelect").property("value")
    let sortedData;
    if (newSort == "Play" || newSort == "Character") {
        sortedData = sortDataAlpha(newData);
    }
    else if (newSort == "Class") {
        let classifier = getClassifier();
        let classes = getClasses();
        sortedClasses = new Object();
        classes.forEach(function(c) {
            sortedClasses[c] = new Array();
        });
        newData.forEach(function(entry) {
            classification = entry[classifier];
            sortedClasses[classification].push(entry);
        });
        sortedData = new Array();
        classes.forEach(function(c) {
            sortedData = sortedData.concat(sortDataAlpha(sortedClasses[c]));
        });
    }
    return sortedData;
}


// General purpose update function which refreshes onscreen charts and modifies
//     global variables, grid size, etc. according to the given data and the 
//     current selections in the control panel
function update(newData = data) {
    // newData should have the following structure:
    //     newData = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]

    let sortedData = sortData(newData);

    averagesData = getAvgsData(sortedData);

    let phonemes = getPhonemes(sortedData);

    width = barWidth * phonemes.length;

    oldTotalWidth = totalWidth;
    totalWidth = width + (2 * xMargin);
    oldTotalWidth = (oldTotalWidth) ? oldTotalWidth : totalWidth;

    let newScale = updateScale(sortedData);

    refreshSize(sortedData, function() {
        refreshVisible(sortedData, true, true, function() {
            data = sortedData;
            oldTotalWidth = totalWidth;
            oldGridWidth = gridWidth;
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
        checkVisible(data);
    });
}


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
            fullData = newData;
            callbackFunction(newData);
        });
    });
}


/*
 * Template for doing other things with new data:
 *
 * loadData(path, function(newData) {
 *     // do thing with newData
 * }
 *
 * For example, set global data to newData:
 *
 * loadData(path, function(newData) {
 *     data = newData;
 * }
 */


// Loads the Z-score file corresponding to the current state of selections in the
//     control panel, and calls update() on the new data once it is loaded and
//     parsed
function updateLoad() {
    let loadString = "../Archive/";
    let newEmphasis = d3.select("#emphasisToggle").property("checked");
    loadString = (newEmphasis == true) ? loadString + "Emphasis-" : loadString;
    let newVowels = d3.select("#vowelsToggle").property("checked");
    loadString = (newVowels == true) ? loadString + "Vowels-Only-" : loadString;
    let newCharacters = d3.select("#characterSelect").property("value");
    switch (newCharacters) {
        case "No Others":
            loadString = loadString + "No-Others";
            break;
        case ">2500 words":
            loadString = loadString + "Min-2500";
            break;
        case ">1000 words":
            loadString = loadString + "Min-1000";
            break;
        case ">500 words":
            loadString = loadString + "Min-500";
            break;
        case ">250 words":
            loadString = loadString + "Min-250";
            break;
        case ">100 words":
            loadString = loadString + "Min-100";
            break;
        case "All":
            loadString = loadString + "All";
    }
    let newCalculation = d3.select("#calculationSelect").property("value");
    if (newCalculation == "Counts") {
        loadString = loadString + "/counts_Z-scores.json";
    } else if (newCalculation == "Percentages") {
        loadString = loadString + "/percentages_Z-scores.json";
    }
    loadData(loadString, function(newData) { update(newData); });
}


// Initial function call which renders the page
updateLoad();
