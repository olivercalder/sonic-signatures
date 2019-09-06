var navbarHeight;

var width;  // of circle graph, set based upon the number of characters, in update()
var height;  // of circle graph, set based upon the number of characters, in update()
var middle;  // of circle graph

var barWidth = 30;  // of individual bars
var barchartWidth;  // of barchart graph
var barchartHeight = 300;  // of barchart graph

var xMargin = 100;  // on either side of the beeswarm graph element
var yMargin = 60;  // above and below the beeswarm graph element
var totalWidth;  // of graph and margins, set by adding width + 2*xMargin, in update()
var totalHeight;  // of graph and margins, set by height + 2*yMargin, in update()

var oldTotalWidth;  // total width before the last change in data or size
var oldTotalHeight; // total height before the last change in data or size

var gridWidth;  // total number of beeswarm charts which fit on a single row
var gridHeight; // total number of rows of beeswarm charts

var oldGridWidth;  // grid width before the last change in data or size

var yBuffer = 20;  // above the top row and below the bottom row

var svgHeight;  // of the svg element
var svgWidth;  // of the svg element


var shortDur = 150; // shorter duration of animations
var stdDur = 500;  // standard duration of animations
var longDur = 1000; //  longer duration of animations

var simTicks = 60;  // Number of ticks calculated for each simulation

var radius = 4;  // Radius of character circles
var avgRadius = 32;  // Radius of average circles

var avgStrokeWidth = 3;  // Stroke width of average bars


var classifiers = {
    "role":   ["protag", "antag",   "fool",  "other"],
    "gender": ["m",      "f"],
    "genre":  ["comedy", "tragedy", "history"]
}
var colors =  ["blue",   "red",     "green", "yellow"];

var data;  // Will be modified by initial d3.json call
    // data is of the form:
    //     data = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
var fullData;  // Full data from the last loadData() call, without sorting or filtering
var characteristics;  // Classes of each character for each classifier
var averagesBarData;  // Average Z-score for each phoneme for each class
    // averageData of the form:
    //     averageData = {<phon1>: {<class1>: Zscore, <class2>: Zscore, ...}, <phon2>: {...}, ... }

var circleSims = new Map();  // Set of pre-simulated circle positions, reset by loadData()

var selected = new Set();
var persisted = new Set();

var renderBuffer = 2;  // The number of rows beyond those visible that will be rendered
var triggerBuffer = 1; // The number of rows beyond those visible that will trigger the next render
var visible = new Map();
var startVisible;
var startIndex;
var endVisible;
var endIndex;


// Makes changes to the averages checkbox cause visualization to update
var averageToggle = d3.select("#averageToggle")
    .on("change", update);

// Makes clicks on button container act as though they were clicks on the inner input element
var averageToggleButton = d3.select("#averageToggleButton")
    .on("click", function() {
        $("#averageToggle").click();
    });

// Returns true or false whether Averages checkbox is checked
function getAverageToggle() {
    return d3.select("#averageToggle").property("checked")
}


// Makes changes to the classifier dropdown cause visualization to update
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

// Returns the available classes for the current classifier
function getClasses() {
    let classifier = getClassifier();
    return classifiers[classifier];
}


// Makes changes to the select sort dropdown cause visualization to update
var filterSelect = d3.select("#filterSelect")
    .on("change", update);

// Returns the current filter selection
function getFilter() {
    return d3.select("#filterSelect").property("value")
}


// Makes changes to the select characters dropdown cause visualization to update load
var characterSelect = d3.select("#characterSelect")
    .on("change", updateLoad);

// Makes changes to the select calculation dropdown cause visualization to update load
var calculationSelect = d3.select("#calculationSelect")
    .on("change", updateLoad);


// Makes changes to the emphasis checkbox cause visualization to update load
var emphasisToggle = d3.select("#emphasisToggle")
    .on("change", updateLoad);

// Makes clicks on button container act as though they were clicks on the inner input element
var emphasisToggleButton = d3.select("#emphasisToggleButton")
    .on("click", function() {
        $("#emphasisToggle").click();
    });


// Makes changes to the vowels chackbox cause visualization to update load
var vowelsToggle = d3.select("#vowelsToggle")
    .on("change", updateLoad);

// Makes clicks on button container act as though they were clicks on the inner input element
var vowelsToggleButton = d3.select("#vowelsToggleButton")
    .on("click", function() {
        $("#vowelsToggle").click();
    });


// Returns the current value of the search box
function getSearch() {
    return d3.select("#searchBox").property("value");
}

// Search box for user to enter search
var searchBox = d3.select("#searchBox")
    .on("change", update);

// Search button to sumbit search
var searchButton = d3.select("#searchButton")
    .on("click", update);


// Scales x position of circles, and scales axis of beeswarm
var xScale = d3.scaleLinear();
    // .range() must be set based on the current width, in 
    // .domain() must be set independently, such as by updateScale()


// Scales height of bar charts
var yScale = d3.scaleLinear()
    .range([height - 10, 10])
    // .domain() must be set independently


// Returns fill opacity based on averages and filter
function getOpacity(d) {
    let opacity = 1;
    if (getAverageToggle()) {
        opacity = 0.5;
    }
    let search = getSearch();
    if (search) {
        let filter = getFilter();
        if (filter == "Name") {
            if (!d.identity.includes(search)) {
                opacity = 0;
            }
        } else if (filter == "Class") {
            let classifier = getClassifier();
            let charClass = d[classifier];
            if (!charClass.includes(search)) {
                opacity = 0;
            }
        }
    }
    return opacity;
}

// Returns radius based on selection status and average vs normal circle
function getRadius(d) {
    if (d.average == true) {
        var newRadius = sizeScale(d.count, d.total);
    } else {
        var newRadius = radius;
    }
    if (selected.has(d.identity)) {
        newRadius += radius;
    }
    return newRadius;
}


// Returns the stroke color of a circle, black if selected, otherwise getColor
function getStroke(d) {
    return (selected.has(d.identity) ? "black" : getColor(d))
}


// Returns the color corresponding to the class of the given datum
function getColor(d) {
    let classifier = getClassifier();
    let classification = d[classifier];
    let colorIndex = classifiers[classifier].indexOf(classification);
    return colors[colorIndex];
}


// Deprecated?
/*
// Colors character circles according to the current classifier
function colorCircles(optionalClass = "") {
    d3.selectAll(((optionalClass != "") ? "circle." + optionalClass : "circle"))
        .filter(d => ((d.average) ? false : true))  // Must not modify average circles for risk of interrupting them
        .transition()                               //     Also, their colors are inherent and do not change
        .duration(stdDur)
        .style("fill", d => getColor(d))
        .style("stroke", d => getStroke(d));
}
*/


// Function to move popups when graph is rescaled or otherwise modified
function updatePopups(circles) {
    circles.each(function(d) {
        let graph = d3.select("g.graph." + d.phoneme);
        if (selected.has(d.identity)) {
            let currPopup = graph.selectAll(".popup.id_" + d.identity.replace(/\./g, "-"))
            if (currPopup.size() > 0) {
                console.log("Updating existing popup for " + d.identity)
                currPopup.transition()
                    .duration(stdDur)
                    .attr("x", function() { return d.x; })
                    .attr("y", function() { let y = parseFloat(d.y);
                        return ((y < middle) ? y - 30 : y + 40); 
                    })
            } else {
                graph.append("text")
                    .attr("class", function() { 
                        let classList = new Array();
                        classList.push(d.phoneme);
                        ((d.average) ? classList.push("average") : true);
                        classList.push("popup");
                        classList.push("id_" + d.identity.replace(/\./g, "-"));
                        return classList.join(" ");
                    })
                        // Need average class to be included in popup in case average circles are redrawn while popup is still in existence
                    .attr("x", function() { return d.x; })
                    .attr("y", function() { let y = parseFloat(d.y);
                        return ((y < middle) ? y - 30 : y + 40); })
                    .style("text-anchor", "middle")
                    .style("font-weight", "bold")
                    //.style("stroke", "white")
                    .style("fill", "black")
                    .style("font-size", "16px")
                    .text(function() { return d.identity + ": " + parseFloat(d.Zscore).toFixed(3); });
            }
        } else {
            graph.selectAll("text.id_" + d.identity.replace(/\./g, "-") + ".popup").remove();
        }
    });
}


// Enlarges and labels all circles with identity matching that of given d
function selectCircles(d) {
    d3.selectAll("circle.id_" + d.identity.replace(/\./g, "-"))  // all circle elements for the same character
        .call(updatePopups)
        .transition()
        .duration(shortDur)
        .attr("r", getRadius(d))
        .style("stroke", "black");
}


// For all circles with identity matching that of given d, returns circles to default size and removes labels
function deselectCircles(d) {
    d3.selectAll("circle.id_" + d.identity.replace(/\./g, "-"))  // all circle elements for the same character
        .call(updatePopups)
        .transition()
        .duration(shortDur)
        .attr("r", getRadius(d))
        .style("stroke", getColor(d));
}


// When new circles are drawn on scroll, this method checks whether they should be enlarged and labeled
//     as a result of a circle with the same identity having been previously moused over or clicked
function updateSelected(selection) {
    selection.each(function(d) {
        if (selected.has(d.identity)) {
            selectCircles(d);
        } else {
            deselectCircles(d);
        }
    });
}


// Click handler that locks circles from being modified by mouseover or mouseout
function handleClick(d) {
    if (persisted.has(d.identity)) {
        persisted.delete(d.identity);
    } else {
        selected.add(d.identity);  // in case somehow persistence was triggered without mouseover triggering
        persisted.add(d.identity);
    }
}


// Selects circle that was moused over, as well as all circles of the same identity, 
//     and enlarges and labels them
function handleMouseOver(d) {
    selected.add(d.identity);
    if (!persisted.has(d.identity)) {  // If already selected and persisted, do not redraw repeatedly on subsequent mouseovers
        selectCircles(d);
    }
}


// Selects circle that was moused out, as well as all circles of the same identity,
//     and returns them to their default size and removes their labels
function handleMouseOut(d) {
    if (!persisted.has(d.identity)) {
        selected.delete(d.identity);
        deselectCircles(d);
    }
}


// Returns an array of all the characters in the data set
function getCharacters(newData) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let characters = new Array();
    newData[0]["data"].forEach(entry => characters.push(entry.identity));
    return characters;
}


// Returns an array of all the phonemes in the data set
function getPhonemes(newData) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let phonemes = new Array();
    newData.forEach(entry => phonemes.push(entry.phoneme));
    return phonemes;
}


// Returns an array of all the Z-scores in the given data set
function getZscores(newData) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let Zscores = new Array();
    newData.forEach(function(entry) {
        entry["data"].forEach(d => Zscores.push(d.Zscore))
    });
    return Zscores;
}


// Returns the minimum value of an array of numbers
function getArrayMin(arr) {
    let min = arr.reduce(function(a, b) {
        return Math.min(a, b);
    });
    return min;
}


// Returns the maximum value of an array of numbers
function getArrayMax(arr) {
    let max = arr.reduce(function(a, b) {
        return Math.max(a, b);
    });
    return max;
}


// Updates yScale according to specified data
function updateScale(newData) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let Zscores = getZscores(newData);
    let ZscoreMin = getArrayMin(Zscores);
    let ZscoreMax = getArrayMax(Zscores);

    xScale
        .domain([ZscoreMin, ZscoreMax])
        .range([10, width - 10]);
    yScale
        .domain([ZscoreMin, ZscoreMax]);
    sizeScaleHelper
        .range([20, (height / 2) - 20]);
    return xScale;
}


// Calculates the x position of the upper left corner of a beeswarm chart given its index
//     and total width, along with the grid width
function getXPos(index, gWidth = gridWidth, tWidth = totalWidth) {
    return (index % gWidth) * tWidth;
}


// Calculates the y position of the upper left corner of a beeswarm chart given its index
//     and total width, along with the grid width
function getYPos(index, gWidth = gridWidth, tHeight = totalHeight) {
    return Math.floor(index / gWidth) * tHeight + navbarHeight;
}


// Returns the index of the specified phoneme in the data set
function getIndex(phoneme, d = data) {
    // d should have the following structure:
    //     d = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let index = 0;
    if (d) {
        while (index < d.length && d[index]["phoneme"] != phoneme) {
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


/*
// If the averages toggle is checked, either draws or updates the average rects
//     overlay on the given bar selection, otherwise removes the average rects
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
                .style("stroke-width", 0)
                .transition()
                .duration((animate) ? stdDur : 0)
                .attr("y", function(d) {
                    avg = averagesBarData[d[getClassifier()]][d.phoneme]
                    if (avg > 0) {
                        return yScale(avg);
                    } else {
                        return yScale(0);
                    }
                })
                .attr("height", d => Math.abs(yScale(averagesBarData[d[getClassifier()]][d.phoneme]) - yScale(0)))
                .style("stroke-width", avgStrokeWidth);
        } else {
            avgRect
                .transition()
                .duration((animate) ? stdDur : 0)
                .attr("y", function(d) {
                    avg = averagesBarData[d[getClassifier()]][d.phoneme]
                    if (avg > 0) {
                        return yScale(avg);
                    } else {
                        return yScale(0);
                    }
                })
                .attr("height", d => Math.abs(yScale(averagesBarData[d[getClassifier()]][d.phoneme]) - yScale(0)));
        }
    } else {
        selection.select("rect.average")
            .transition()
            .duration((animate) ? stdDur : 0)
            .attr("y", yScale(0))
            .attr("height", 0)
            .style("stroke-width", 0)
            .remove();
    }
}


// Animates the removal of the rectangle(s) and text from the given bar
//     selection, then removes the g elements themselves
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


// Draws rectangles and text in the given selection of bars
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


// Updates the existing rectangles and texts in the given selection of bars
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
*/


sizeScaleHelper = d3.scaleLinear();
    // .range() must be set in update()

// Scales the size of average circles given the number of characters in 
//     the class and the total number of characters
function sizeScale(classCount, totalCount) {
    sizeScaleHelper.domain([0, totalCount]);
    return sizeScaleHelper(classCount);
}


// Returns data of averages of each class for the given entry, used by drawAverages()
function getAvgsData(entry) {
    let phoneme = entry.phoneme;
    let entryData = entry.data;

    let classifier = getClassifier();

    let classSums = new Object();
    let classCounts = new Object();
    for (let i = 0; i < entryData.length; i++) {
        let charClass = entryData[i][classifier];
        classSums[charClass] = (classSums[charClass] ? classSums[charClass] + entryData[i].Zscore : entryData[i].Zscore);
        classCounts[charClass] = (classCounts[charClass] ? classCounts[charClass] + 1 : 1);
    }

    let classes = Object.keys(classSums);
    let avgsData = new Array();

    for (let i = 0; i < classes.length; i++) {
        avgsData.push({
            "phoneme": phoneme,
            "identity": classes[i],
            "average": true,
            "count": classCounts[classes[i]],
            "total": entryData.length,
            "Zscore": classSums[classes[i]] / classCounts[classes[i]],
            "role": ((classifier == "role") ? classes[i] : undefined),
            "gender": ((classifier == "gender") ? classes[i] : undefined),
            "genre": ((classifier == "genre") ? classes[i] : undefined)
        });
    }

    let xForceAvg = d3.forceX(d => xScale(d.Zscore))  // force to pull circle towards its specified x value
        .strength(1);

    let yForceAvg = d3.forceY(middle)
        .strength(0.1);

    let collisionAvg = d3.forceCollide()  // applied to every node
        .radius(d => sizeScale(d.count, d.total) + 1)
        .strength(0.9)
        //.iterations(10);

    let simulationAvg = d3.forceSimulation(avgsData)  // Initializes a simulation with each datum as a node
        .force("xForce", xForceAvg)
        .force("yForce", yForceAvg)
        .force("collision", collisionAvg)
        .stop();

    // Performs 120 ticks of calculation
    for (let i = 0; i < simTicks; i++) { simulationAvg.tick(); }
    return avgsData;
    // avgsData is of the form:
    //     avgsData = [{"identity: <class>, "average": true, "Zscore": <avgZscore>, ...}, ...]
}


// Draws average circles onto graph corresponding to the given entry
function drawAverages(entry, animate = true) {
    let phoneme = entry.phoneme;
    let avgsData = getAvgsData(entry, xScale);
    console.log("Drawing Averages for " + phoneme + ": animate = " + animate)

    // Binds averages data to average circles
    let avgCircles = d3.select("g.graph." + phoneme).selectAll("circle.average")
        .data(avgsData, d => d.identity);

    // Removes old circles gracefully
    avgCircles.exit()
        .transition()
        .duration((animate == true) ? stdDur : 0)
        .attr("fill-opacity", 0.0)
        .style("stroke", "white")
        .attr("r", 0)
        .each(function(d) {
            d3.select("text.average.popup." + d.phoneme + ".id_" + d.identity.replace(/\./g, "-")).remove();
        })
        .remove();

    // Creates new average circles and format them properly
    avgCircles.enter().append("circle")
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .attr("class", function(d) {
            let classList = new Array();
            classList.push(phoneme);
            classList.push("average");
            classList.push("id_" + d.identity);
            return classList.join(" ");
        })
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut)
        .on("click", handleClick)
        .attr("fill-opacity", d => getOpacity(d))
        .transition()
        .duration((animate == true) ? stdDur : 0)
        .attr("r", d => getRadius(d))
        .style("fill", d => getColor(d))
        .style("stroke", d => getStroke(d))
        .call(updatePopups);

    // Modify existing average circles
    avgCircles
        .attr("class", function(d) {
            let classList = new Array();
            classList.push(phoneme);
            classList.push("average");
            classList.push("id_" + d.identity);
            return classList.join(" ");
        })
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut)
        .on("click", handleClick)
        .transition()
        .duration((animate == true) ? stdDur : 0)
        .attr("r", d => getRadius(d))
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .attr("fill-opacity", d => getOpacity(d))
        .style("fill", d => getColor(d))
        .style("stroke", d => getStroke(d))
        .call(updatePopups);
    
    // The code after avgCircles.enter() and avgCircles is very similar,
    //     but separated so as to avoid race conditions

    // Deprecated?
    /*
    // Make all other non-average circles opacity 0.5
    d3.selectAll("circle").filter(d => (d.average ? false : true))
        .transition()
        .duration((animate == true) ? stdDur : 0)
        .attr("fill-opacity", 0.5)
    */

}


// Removes average circles from each graph and returns other circles to opacity 1
function hideAverages(entry, animate = true) {
    let phoneme = entry.phoneme;

    // Deprecated?
    /*
    d3.selectAll("circle").filter(d => ((d.average ? false : true) && d.phoneme == phoneme))
        .transition()
        .duration((animate == true) ? stdDur : 0)
        .attr("fill-opacity", 1.0);
    */

    d3.selectAll("text.average.popup." + phoneme)
        .remove();

    d3.selectAll("circle.average." + phoneme)
        .transition()
        .duration((animate == true) ? stdDur : 0)
        .attr("fill-opacity", 0.0)
        .style("stroke", "white")
        .attr("r", 0)
        .remove();
}


// Draw or hide average circles, depending on whether the averages checkbox is checked
function updateAverages(entry, animate = true) {
    if (getAverageToggle()) {
        drawAverages(entry, animate);
        //visible.forEach(value => drawAverages(value));
    } else {
        hideAverages(entry, animate);
        //visible.forEach(value => hideAverages(value));
    }
}


// Fully updates the beeswarm chart of the given entry, placing it according to its index
//     (or given x and y positions) on the ZscoreWindow svg or the specified svg,
//     and updates the title, axis, and graph appropriately
function updateBeeswarm(entry, index, animate = false, svg = d3.select("#ZscoreWindow"), xPos = false, yPos = false) { 
    if (!xPos || !yPos) {
        xPos = getXPos(index);
        yPos = getYPos(index);
    }

    let phoneme = entry.phoneme;
    let chartData = entry.data;
    
    if (circleSims.has(phoneme)) {
        chartData = circleSims.get(phoneme);
    } else {
        // Creates force to pull circle towards the x coordinate corresponding to its Z-score
        let xForce = d3.forceX(d => xScale(d.Zscore))
            .strength(1);

        // Creates force to pull each circle towards the horizontal center line
        let yForce = d3.forceY(middle)
            .strength(0.1);

        // Creates collision force between each circle
        let collision = d3.forceCollide()
            .radius(radius + 1)
            .strength(1)
            //.iterations(10);

        // Initializes a simulation to calculate x and y coordinates of each circle
        let simulation = d3.forceSimulation(chartData)
            .force("xForce", xForce)
            .force("yForce", yForce)
            .force("collision", collision)
            .stop();

        // Performs number of ticks of calculation equal to simTicks
        for (let i = 0; i < simTicks; i++) { simulation.tick(); }

        circleSims.set(phoneme, chartData);
    }


    // Checks whether chart element already exists
    let chart = svg.select("g.chart." + phoneme);
    if (chart.size() == 0) {
        // Creates chart element and positions it in primary svg
        let oldIndex = getIndex(phoneme, data);
        oldIndex = (oldIndex) ? oldIndex : index;
        let oldXPos = getXPos(oldIndex, oldGridWidth, oldTotalWidth);
        let oldYPos = getYPos(oldIndex, oldGridWidth, oldTotalHeight);
        chart = svg.append("g");
        chart
            .attr("class", phoneme + " chart")
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
            .attr("class", phoneme + " title")
            .attr("width", xMargin)
            .attr("height", totalHeight);
    } else {
        // Modifies existing title element
        title
            .attr("class", phoneme + " title")
            .attr("width", xMargin)
            .attr("height", totalHeight)
    }

    // Checks whether title text already exists
    titleText = title.select("text");
    if (titleText.size() == 0) {
        // Writes character name within the title element
        titleText = title.append("text")
            .attr("x", xMargin / 2)
            .attr("y", totalHeight / 2)
            .attr("class", phoneme + " title")
            .style("text-anchor", "middle")
            .style("fill", "#999999")
            .style("stroke", "black")
            .style("font-size", "48px")
            .text(phoneme);
    } else {
        // Modifies existing text in the title element
        titleText
            .attr("class", phoneme + " title")
            .transition()
            .duration(stdDur)
            .attr("x", xMargin / 2)
            .attr("y", totalHeight / 2)
            .style("text-anchor", "middle")
            .style("fill", "#999999")
            .style("stroke", "black")
            .style("font-size", "48px")
            .text(phoneme);
    }

    let xAxis = d3.axisBottom(xScale);

    // Checks whether axis element already exists
    let axis = chart.select("g.axis");
    if (axis.size() == 0) {
        // Creates element to contain axis
        axis = chart.append("g")
            .attr("class", phoneme + " axis")
            .attr("transform", "translate(" + xMargin + ", " + (height + (yMargin * 1.5)) + ")")
            .attr("width", width)
            .attr("height", yMargin / 2)
            .call(xAxis);
    } else {
        // Modify existing axis element
        axis
            .attr("class", phoneme + " axis")
            .attr("width", width)
            .attr("height", yMargin / 2)
            .transition()
            .duration(stdDur)
            .attr("transform", "translate(" + xMargin + ", " + (height + (yMargin * 1.5)) + ")")
            .call(xAxis);
    }


    // Checks whether graph element already exists
    let graph = chart.select("g.graph");
    if (graph.size() == 0) {
        // Creates element to contain circles
        graph = chart.append("g")
            .attr("class", phoneme + " graph")
            .attr("transform", "translate(" + xMargin + ", " + yMargin + ")")
            .attr("width", width)
            .attr("height", height);
    } else {
        // Modifies existing element containing circles
        graph
            .attr("class", phoneme + " graph")
            .attr("width", width)
            .attr("height", height)
            .transition()
            .duration(stdDur)
            .attr("transform", "translate(" + xMargin + ", " + yMargin + ")")
    }


    // Get a list of all classifiers
    let classifierKeys = Object.keys(classifiers);


    // Binds data to circle elements
    let circles = graph.selectAll("circle")
            .data(chartData, d => d.identity);
    
    // Removes old circles gracefully
    circles.exit()
        .transition()
        .duration((animate) ? stdDur: 0)
        .attr("r", 0)
        .attr("fill-opacity", 0)
        .style("stroke", "white")
        .each(function(d) {
            d3.select("text.popup." + phoneme + ".id_" + d.identity.replace(/\./g, "-")).remove();
        })
        .remove();

    // Modifies existing circles
    circles
        .attr("class", function(d) {
            let classList = new Array();
            classList.push("id_" + d.identity.replace(/\./g, "-"));
            classList.push("p_" + d.identity.split("_")[0]);
            classList.push(phoneme);
            classifierKeys.forEach(key => classList.push(d[key]));
            return classList.join(" ");
        })
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut)
        .on("click", handleClick)
        .transition()
        .duration((animate) ? stdDur : 0)
        .attr("r", d => getRadius(d))
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .attr("fill-opacity", d => getOpacity(d))
        .style("fill", d => getColor(d))
        .style("stroke", d => getStroke(d))
        .call(updatePopups);

    // Creates new circle elements for new data
    circles.enter().append("circle")
        .attr("class", function(d) {
            let classList = new Array();
            classList.push("id_" + d.identity.replace(/\./g, "-"));
            classList.push("p_" + d.identity.split("_")[0]);
            classList.push(phoneme);
            classifierKeys.forEach(key => classList.push(d[key]));
            return classList.join(" ");
        })
        .attr("r", 0)
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut)
        .on("click", handleClick)
        .transition()
        .duration((animate) ? stdDur : 0)
        .attr("r", d => getRadius(d))
        .attr("fill-opacity", d => getOpacity(d))
        .style("fill", d => getColor(d))
        .style("stroke", d => getStroke(d))
        .call(updatePopups);

    // Draw average circles on the graph
    updateAverages(entry, animate);
}


// Animates the removal of a beeswarm chart, called when it is no longer going to
//     be visible.
// If the chart has a new index (the phoneme is still in the new data
//     set), animates the chart moving to the new index, then removes it.
// If the chart does not have a new index after the update (the phoneme
//     is not part of the new data set), the bars are shrunk and then
//     the chart is removed.
function removeBeeswarm(phoneme, d = data) {
    let newIndex = getIndex(phoneme, d);
    if (newIndex !== false) {
        let newXPos = getXPos(newIndex);
        let newYPos = getYPos(newIndex);
        d3.select("g.chart." + phoneme)
            .transition()
            .duration(stdDur)
            .attr("transform", "translate(" + newXPos + "," + newYPos + ")")
            .remove();
    } else {
        let chart = d3.select("g.chart." + phoneme)
        chart.selectAll("circle")
            .transition()
            .duration(shortDur)
            .attr("r", 0)
            .attr("fill-opacity", 0)
            .style("stroke", "white")
            .remove();
        chart
            .transition()
            .duration(shortDur)
            .remove();
    }
}


// Returns the indices of the first and last beeswarm charts visible onscreen, not including the buffer
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
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    getVisibleIndices(function(startVisible, endVisible) {
        startIndex = Math.max(0, startVisible - (renderBuffer * gridWidth));
        endIndex = Math.min(newData.length - 1, endVisible + (renderBuffer * gridWidth));
        let newVisible = new Map();
        for (let i = startIndex; i <= endIndex; i++) {
            let entry = newData[i];
            let phoneme = entry.phoneme;
            newVisible.set(phoneme, entry);
            if (!visible.has(phoneme) || fullRefresh) {
                updateBeeswarm(entry, i, animate)
            }
        }
        visible.forEach(function(entry) {
            if (!newVisible.has(entry.phoneme)) {
                removeBeeswarm(entry.phoneme, newData)
            }
        });
        visible = newVisible;
        if (callbackFunction) { callbackFunction() }
    });
}


// Uses current dimensions of the window to calculate the grid size,
//     and then resizes the svg and calls the callback function
function refreshSize(newData = data, callbackFunction = false) {
    navbarHeight = $("nav.navbar").height() + yBuffer;
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
function getAvgsBarData(newData = data) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let phonemes = getPhonemes(newData);
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
    newData.forEach(function(entry) {
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


/*
// Sorts the given data array and returns it
function sortDataAlpha(dataArr) {
    // dataArr should have the following structure:
    //     dataArr = [{"character": <character>, "data": <barData>, ...}, ...]
    //     where barData = [{"phoneme": <phoneme>, "Zscore": <Zscore>,  ...}, ...]

    //     dataArr = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
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

    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let newSort = d3.select("#sortSelect").property("value")
    let sortedData;
    if (newSort == "Play" || newSort == "Character") {
        sortedData = sortDataAlpha(newData);
    }
    else if (newSort == "Class") {
        let classifier = getClassifier();
        let classes = getClasses();
        sortedClassData = new Object();
        classes.forEach(function(c) {
            sortedClassData[c] = new Array();
        });
        newData.forEach(function(entry) {
            classification = entry[classifier];
            sortedClassData[classification].push(entry);
        });
        sortedData = new Array();
        classes.forEach(function(c) {
            sortedData = sortedData.concat(sortDataAlpha(sortedClassData[c]));
        });
    }
    return sortedData;
}
*/


/*
// Returns a new set of data containing only the characters whose identities
//     contain the search keyword
function filter(newData) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let search = getSearch();
    let filteredData = new Array();
    newData.forEach(function(entry) {
        let newEntry = new Object();
        newEntry.phoneme = entry.phoneme;
        newEntry.data = new Array();
        entry.data.forEach(function(d) {
            if (d.identity.includes(search)) {
                newEntry.data.push(d);
            }
        });
        filteredData.push(newEntry);
    });
    return filteredData;
}
*/


// General purpose update function which refreshes onscreen charts and modifies
//     global variables, grid size, etc. according to the given data and the 
//     current selections in the control panel
function update(newData = data) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]

    averagesBarData = getAvgsBarData(fullData);

//    let sortedData = sortData(filteredData);

    let phonemes = getPhonemes(fullData);
    let characters = getCharacters(fullData);

    width = 1000;
    height = Math.floor(Math.cbrt(characters.length)) * 25;
    middle = height / 2;

    barchartWidth = barWidth * phonemes.length;

    oldTotalWidth = totalWidth;
    totalWidth = width + (2 * xMargin);
    oldTotalWidth = (oldTotalWidth) ? oldTotalWidth : totalWidth;

    oldTotalHeight = totalHeight;
    totalHeight = height + (2 * yMargin);
    oldTotalHeight = (oldTotalHeight) ? oldTotalHeight : totalHeight;

    updateScale(fullData);

//    let filteredData = filter(newData);

    refreshSize(newData, function() {
        refreshVisible(newData, true, true, function() {
            data = newData;
            oldTotalWidth = totalWidth;
            oldTotalHeight = totalHeight;
            oldGridWidth = gridWidth;
        });
    });

    var timeout;
    $(window).on("resize", function() {
        clearTimeout(timeout);
        timeout = setTimeout(function() {
            refreshSize(data, function() {
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


/*
// Triggered by a search confirmation, calls update on the fullData dataset,
//     thus filter is not compounded upon existing filter
function searchFilter() {
    update(fullData);
}
*/


// Loads Z-scores from specified file path, then processes it and executes callback function on the data
function loadData(ZscorePath, callbackFunction) {
    let newData = new Array();
    characteristics = new Object();
    d3.json(ZscorePath, function(rawData) {
        d3.csv("../Reference/characteristics.csv", function(c) {
            c.forEach(entry => characteristics[entry["character"]] = entry);

            let characters = Object.keys(rawData);
            let phonemes = Object.keys(rawData[characters[0]]);
            phonemes.forEach(function(phoneme) {
                let phonData = new Array();
                characters.forEach(function(charName) {
                    let charData = new Object();
                    let Zscore = rawData[charName][phoneme];
                    charData["phoneme"] = phoneme;
                    charData["Zscore"] = parseFloat(Zscore);
                    charData["identity"] = charName;
                    Object.keys(classifiers).forEach(classifier => charData[classifier] = characteristics[charName][classifier]);
                    phonData.push(charData);
                });
                newData.push({"phoneme": phoneme, "data": phonData});
            });
            // This creates data with structure:
            //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
            //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
            fullData = newData;
            circleSims = new Map();
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
