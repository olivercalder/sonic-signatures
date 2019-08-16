var width = 1000;  // of circle graph
var height = 280;  // of circle graph
var xMargin = 100;  // on either side of circle graph
var yMargin = 60;  // on either side of circle graph
var svgWidth = width + (2 * xMargin);  // of each svg element
var svgHeight = height + (2 * yMargin);  // of each svg element
var middle = height / 2;  // of circle graph

var slowTrans = 500;  // Transition time for slow transitions, in milliseconds
var fastTrans = 150;  // Transition time for fast transitions, in milliseconds

var simTicks = 50;  // Number of ticks computed in forceSimulation

var radius = 4;  // Radius of character circles
var avgRadius = 32;  // Radius of average circles

var classifiers = {
    "role":   ["protag", "antag",   "fool",  "other"],
    "gender": ["m",      "f"],
    "genre":  ["comedy", "tragedy", "history"]
};
var colors =  ["blue",   "red",     "green", "yellow"];

var classifier = "role";  // Initial default classifier
var averages = false;  // Initial value for displaying averages

var data;  // Will be modified by the initial json load
    // data is of the form:
    //     data = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
var characteristics;  // Will be modified by the initial csv load


var selected = new Set();
var persisted = new Set();


var renderBuffer = 2;  // The number of SVG elements beyond those visible that will be rendered
var triggerBuffer = 1; // The number of SVG elements beyond those visible that will trigger the next render
var visible = new Map();
var startVisible;
var startIndex;
var endVisible;
var endIndex;


// Returns the indices of the first and last SVGs visible on screen, not including the buffer
//     Excludes buffer so that this can be used to compare current position with buffer indices
function getVisibleIndices() {
    let winTop = $(window).scrollTop();
    let winBot = winTop + $(window).height();
    startVisible = Math.floor(winTop / svgHeight);  // May be < 0
    endVisible = Math.floor(winBot / svgHeight);  // May be > data.length
    return [startVisible, endVisible];
};


// Checks whether window has scrolled enough to require refresh,
//     and if so, calls refreshVisible
function checkVisible() {
    getVisibleIndices();
    if (startVisible - triggerBuffer <= startIndex || endVisible + triggerBuffer >= endIndex) {
        refreshVisible(data, xScale, false);
    };
};


// Recalculates which graphs are visible and populates visible ones,
//     removing elements from ones that are no longer visible
function refreshVisible(newData = data, scale = xScale, fullRefresh = false) {
    getVisibleIndices();
    startIndex = Math.max(0, startVisible - renderBuffer);
    endIndex = Math.min(newData.length - 1, endVisible + renderBuffer);
    let newVisible = new Map();
    for (let i = startIndex; i <= endIndex; i++) {
        let entry = newData[i];
        let phoneme = entry.phoneme;
        newVisible.set(phoneme, entry);
        let refreshOnscreen = false;
        if (!visible.has(phoneme) || fullRefresh) {
            updateGraph(entry, scale, ((i >= startVisible || i <= endVisible) ? false : true));
        };
    };
    visible.forEach(function(entry) {
        if (!newVisible.has(entry.phoneme)) {
            d3.selectAll("circle." + entry.phoneme).remove();
            d3.selectAll("text.popup." + entry.phoneme).remove();
        };
    });
    visible = newVisible;
};


// Redraws circles onto graphs from saved data without recalculating
// Future function for use if simulations are run only on substantive change,
//     and otherwise merely recalled
function repopulateVisible(entry, scale = xScale, animate = true) {
    let phoneme = entry.phoneme;
    let chartData = entry.data;
    if (visible.has(phoneme)) {
        // recall saved data and rebind it to circles
    };
};


// Checkbox to toggle displaying average circles
var averageToggle = d3.select("#controlPanel");

averageToggle.append("input")
    .attr("type", "checkbox")
    .attr("class", "checkbox")
    .attr("id", "averageToggle")
    .on("change", function() {
        averages = d3.select("#averageToggle").property("checked");
        visible.forEach(entry => updateAverages(entry, xScale, true));
    });

averageToggle.append("label")
    .text("Draw Averages    ");


// Draw or hide average circles, depending on whether var averages is true or false
function updateAverages(entry, scale = xScale, animate = true) {
    if (averages) {
        drawAverages(entry, scale, animate);
        //visible.forEach(value => drawAverages(value));
    } else if (!averages) {
        hideAverages(entry, animate);
        //visible.forEach(value => hideAverages(value));
    };
};


// Dropdown options to change the current classifier
var classSelect = d3.select("#controlPanel")
    .append("select")
        .attr("class", "select")
        .attr("id", "classSelect")
        .on("change", redrawClasses);
    
classSelect.selectAll("option")
        .data(Object.keys(classifiers)).enter()
    .append("option")
        .text(d => d);


// Recolors circles based on the current classifier
// Also updates average circles according to new classifier
function redrawClasses() {
    newClassifier = d3.select("#classSelect").property("value");
    classifier = newClassifier;
    visible.forEach(entry => updateAverages(entry, xScale, true));
    colorCircles();
};


// Returns radius based on selection status and average vs normal circle
function getRadius(d) {
    if (d.average == true) {
        var newRadius = sizeScale(d.count, d.total);
    } else {
        var newRadius = radius;
    };
    if (selected.has(d.identity)) {
        newRadius += radius;
    };
    return newRadius;
};


// Returns the stroke color of a circle, black if selected, otherwise getColor
function getStroke(d) {
    return (selected.has(d.identity) ? "black" : getColor(d))
};


// Gets the color for a given character's data according to the current classifier
function getColor(d) {
    classification = d[classifier];
    colorIndex = classifiers[classifier].indexOf(classification);
    return colors[colorIndex];
};


// Colors character circles according to the current classifier
function colorCircles(optionalClass = "") {
    d3.selectAll(((optionalClass != "") ? "circle." + optionalClass : "circle"))
        .filter(d => ((d.average) ? false : true))  // Must not modify average circles for risk of interrupting them
        .transition()                               //     Also, their colors are inherent and do not change
        .duration(slowTrans)
        .style("fill", d => getColor(d))
        .style("stroke", d => getStroke(d));
};


// Function to move popups when graph is rescaled or otherwise modified
function updatePopups(circles) {
    circles.each(function(d) {
        let graph = d3.select("g.graph." + d.phoneme);
        if (selected.has(d.identity)) {
            let currPopup = graph.selectAll(".popup.id_" + d.identity.replace(/\./g, "-"))
            if (currPopup.size() > 0) {
                console.log("Updating existing popup for " + d.identity)
                currPopup.transition()
                    .duration(slowTrans)
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
            };
        } else {
            graph.selectAll("text.id_" + d.identity.replace(/\./g, "-") + ".popup").remove();
        };
    });
};


// Enlarges and labels all circles with identity matching that of given d
function selectCircles(d) {
    d3.selectAll("circle.id_" + d.identity.replace(/\./g, "-"))  // all circle elements for the same character
        .call(updatePopups)
        .transition()
        .duration(fastTrans)
        .attr("r", getRadius(d))
        .style("stroke", "black");
};


// For all circles with identity matching that of given d, returns circles to default size and removes labels
function deselectCircles(d) {
    d3.selectAll("circle.id_" + d.identity.replace(/\./g, "-"))  // all circle elements for the same character
        .call(updatePopups)
        .transition()
        .duration(fastTrans)
        .attr("r", getRadius(d))
        .style("stroke", getColor(d));
};


// When new circles are drawn on scroll, this method checks whether they should be enlarged and labeled
//     as a result of a circle with the same identity having been previously moused over or clicked
function updateSelected(selection) {
    selection.each(function(d) {
        if (selected.has(d.identity)) {
            selectCircles(d);
        } else {
            deselectCircles(d);
        };
    });
};


// Click handler that locks circles from being modified by mouseover or mouseout
function handleClick(d) {
    if (persisted.has(d.identity)) {
        persisted.delete(d.identity);
    } else {
        selected.add(d.identity);  // in case somehow persistence was triggered without mouseover triggering
        persisted.add(d.identity);
    };
};


// Selects circle that was moused over, as well as all circles of the same identity, 
//     and enlarges and labels them
function handleMouseOver(d) {
    selected.add(d.identity);
    if (!persisted.has(d.identity)) {  // If already selected and persisted, do not redraw repeatedly on subsequent mouseovers
        selectCircles(d);
    };
};


// Selects circle that was moused out, as well as all circles of the same identity,
//     and returns them to their default size and removes their labels
function handleMouseOut(d) {
    if (!persisted.has(d.identity)) {
        selected.delete(d.identity);
        deselectCircles(d);
    };
};


// Scale used for placing circles as well as generating axes
var xScale = d3.scaleLinear()
    .range([10, width - 10]);
    // .domain() must be set independently, such as by updateScale()


// Returns a list of Z-scores from a given dataset
function getZscores(newData) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let Zscores = new Array();
    newData.forEach(function(entry) {
        entry["data"].forEach(d => Zscores.push(d.Zscore));
    });
    return Zscores;
};


// Returns the minimum value of an array of numbers
function getArrayMin(arr) {
    let min = arr.reduce(function(a, b) {
        return Math.min(a, b);
    });
    return min;
};

// Returns the maximum value of an array of numbers
function getArrayMax(arr) {
    let max = arr.reduce(function(a, b) {
        return Math.max(a, b);
    });
    return max;
};


// Updates xScale according to specified data
function updateScale(newData = data) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let Zscores = getZscores(newData);
    let ZscoreMin = getArrayMin(Zscores);
    let ZscoreMax = getArrayMax(Zscores);

    xScale.domain([ZscoreMin, ZscoreMax]);
    return xScale;
};  // Returns xScale so that the scaling can be done by the output of this function, to avoid race conditions


var sizeScaleHelper = d3.scaleLinear()
    .range([20, (height / 2) - 20]);

// Scales the size of average circles given the number of characters in 
//     the class and the total number of characters
function sizeScale(classCount, totalCount) {
    sizeScaleHelper.domain([0, totalCount]);
    return sizeScaleHelper(classCount);
};


// Returns data of averages of each class for each phoneme, used by drawAverages()
function getAvgsData(entry, scale = xScale) {
    let phoneme = entry.phoneme;
    let entryData = entry.data;

    let classSums = new Object();
    let classCounts = new Object();
    for (let i = 0; i < entryData.length; i++) {
        let charClass = entryData[i][classifier];
        classSums[charClass] = (classSums[charClass] ? classSums[charClass] + entryData[i].Zscore : entryData[i].Zscore);
        classCounts[charClass] = (classCounts[charClass] ? classCounts[charClass] + 1 : 1);
    };

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
    };

    let xForceAvg = d3.forceX(d => scale(d.Zscore))  // force to pull circle towards its specified x value
        .strength(1);
    let yForceAvg = d3.forceY(middle)
        .strength(0.1);
    let collisionAvg = d3.forceCollide()  // applied to every node
        .radius(d => sizeScale(d.count, d.total) + 1)
        .strength(0.9)
        .iterations(10);

    let simulationAvg = d3.forceSimulation(avgsData)  // Initializes a simulation with each datum as a node
        .force("xForce", xForceAvg)
        .force("yForce", yForceAvg)
        .force("collision", collisionAvg)
        .stop();

    // Performs 120 ticks of calculation
    for (let i = 0; i < simTicks; i++) { simulationAvg.tick(); };
    return avgsData;
    // avgsData is of the form:
    //     avgsData = [{"identity: <class>, "average": true, "Zscore": <avgZscore>, ...}, ...]
};


// Draws average circles onto graph corresponding to the given entry
function drawAverages(entry, scale = xScale, animate = true) {
    let phoneme = entry.phoneme;
    let avgsData = getAvgsData(entry, scale);
    console.log("Drawing Averages for " + phoneme + ": animate = " + animate)

    // Binds averages data to average circles
    let avgCircles = d3.select("g.graph." + phoneme).selectAll("circle.average")
        .data(avgsData, d => d.identity);

    // Removes old circles gracefully
    avgCircles.exit()
        .transition()
        .duration((animate == true) ? slowTrans : 0)
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
        .attr("fill-opacity", 0.5)
        .transition()
        .duration((animate == true) ? slowTrans : 0)
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
        .duration((animate == true) ? slowTrans : 0)
        .attr("r", d => getRadius(d))
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .attr("fill-opacity", 0.5)
        .style("fill", d => getColor(d))
        .style("stroke", d => getStroke(d))
        .call(updatePopups);
    
    // The code after avgCircles.enter() and avgCircles is very similar,
    //     but separated so as to avoid race conditions

    // Make all other non-average circles opacity 0.5
    d3.selectAll("circle").filter(d => (d.average ? false : true))
        .transition()
        .duration((animate == true) ? slowTrans : 0)
        .attr("fill-opacity", 0.5)
};


// Removes average circles from each graph and returns other circles to opacity 1
function hideAverages(entry, animate = true) {
    let phoneme = entry.phoneme;
    d3.selectAll("circle").filter(d => ((d.average ? false : true) && d.phoneme == phoneme))
        .transition()
        .duration((animate == true) ? slowTrans : 0)
        .attr("fill-opacity", 1.0);

    d3.selectAll("text.average.popup." + phoneme)
        .remove();

    d3.selectAll("circle.average." + phoneme)
        .transition()
        .duration((animate == true) ? slowTrans : 0)
        .attr("fill-opacity", 0.0)
        .style("stroke", "white")
        .attr("r", 0)
        .remove();
};


// Recalculates scale and runs simulation, rebinding data to existing graph element
//     Where entry = {"phoneme": phoneme, "data": phonData}
//         Where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
function updateGraph(entry, scale = xScale, animate = true) {
    let phoneme = entry.phoneme;
    let chartData = entry.data;
    console.log("Updating " + phoneme);

    // Creates force to pull circle towards the x coordinate corresponding to its Z-score
    let xForce = d3.forceX(d => scale(d.Zscore))
        .strength(1);

    // Creates force to pull each circle towards the horizontal center line
    let yForce = d3.forceY(middle)
        .strength(0.1);

    // Creates collision force between each circle
    let collision = d3.forceCollide()
        .radius(radius + 1)
        .strength(0.9)
        .iterations(10);

    // Initializes a simulation to calculate x and y coordinates of each circle
    let simulation = d3.forceSimulation(chartData)
        .force("xForce", xForce)
        .force("yForce", yForce)
        .force("collision", collision)
        .stop();

    // Performs 120 ticks of calculation
    for (let i = 0; i < simTicks; i++) { simulation.tick(); };

    // Re-creates actual d3 axis object
    let xAxis = d3.axisBottom(scale);

    // Re-calls new axis in existing axis element
    d3.select("g.axis." + phoneme)
        .call(xAxis);

    // Binds data to circles, then creates new ones as needed, deletes old ones, and updates existing ones
    let circles = d3.select("g.graph." + phoneme).selectAll("circle").filter(d => (d.average) ? false : true)
            .data(chartData, d => d.identity);

    // Remove old circles gracefully
    circles.exit()
        .transition()
        .duration((animate) ? slowTrans : 0)
        .attr("r", 0)
        .attr("fill-opacity", 0)
        .style("stroke", "white")
        .remove();

    // Gets a list of all classifiers
    let classifier_keys = Object.keys(classifiers);

    // Creates new circles and formats them properly
    circles.enter().append("circle")
        .attr("r", 0)
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut)
        .on("click", handleClick)
        .attr("class", function(d) { 
            let classList = new Array();
            classList.push("id_" + d.identity.replace(/\./g, "-"));
            classList.push("p_" + d.identity.split("_")[0]);
            classList.push(phoneme);
            for (let i = 0; i < classifier_keys.length; i++) {
                classList.push(d[classifier_keys[i]]);
            };
            return classList.join(" ");
        })
        .transition()
        .duration((animate) ? slowTrans : 0)
        .attr("r", d => getRadius(d))
        .style("fill", d => getColor(d))
        .style("stroke", d => getStroke(d))
        .call(updatePopups);

    // Modify existing circles
    circles
        .on("mouseover", handleMouseOver)
        .on("mouseout", handleMouseOut)
        .on("click", handleClick)
        .attr("class", function(d) { 
            let classList = new Array();
            classList.push("id_" + d.identity.replace(/\./g, "-"));
            classList.push("p_" + d.identity.split("_")[0]);
            classList.push(phoneme);
            for (let i = 0; i < classifier_keys.length; i++) {
                classList.push(d[classifier_keys[i]]);
            };
            return classList.join(" ");
        })
        .transition()
        .duration((animate) ? slowTrans : 0)
        .attr("r", d => getRadius(d))
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .style("fill", d => getColor(d))
        .style("stroke", d => getStroke(d))
        .call(updatePopups);

    updateAverages(entry, scale, animate);
};


// Draws label, axis, legend, and circles onto the svg element corresponding to the given data entry
//     Where entry = {"phoneme": phoneme, "data": phonData}
//         Where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
function initializeSVG(entry, scale = xScale) {
    let phoneme = entry.phoneme;
    let chartData = entry.data;

    // Creates element to contain phoneme label
    let label = d3.select("svg." + phoneme).append("g")
        .attr("class", function() { return phoneme + " label"; })
        .attr("width", xMargin)
        .attr("height", svgHeight);

    // Creates text within the label element
    label.append("text")
        .attr("x", xMargin / 2)
        .attr("y", svgHeight / 2)
        .attr("class", function() { return phoneme + " label"; })
        .style("text-anchor", "middle")
        .style("fill", "#999999")
        .style("stroke", "black")
        .style("font-size", "48px")
        .text(phoneme);

    // Creates element to contain legend for classes
    let legend = d3.select("svg." + phoneme).append("g")
        .attr("class", function() { return phoneme + " legend"; })
        .attr("transform", "translate(" + xMargin + ", 0)")
        .attr("width", width)
        .attr("height", yMargin);

    // Creates element to contain the axis
    d3.select("svg." + phoneme).append("g")
        .attr("class", function() { return phoneme + " axis"; })
        .attr("transform", "translate(" + xMargin + "," + (height + (yMargin * 1.5)) + ")")
        .attr("width", width)
        .attr("height", yMargin / 2);

    // Creates element to contain circles
    var g = d3.select("svg." + phoneme).append("g")
        .attr("class", function() { return phoneme + " graph"; })
        .attr("transform", "translate(" + xMargin + "," + yMargin + ")")
        .attr("width", width)
        .attr("height", height);
};


// Update svg elements and the circles they contain with new data
function update(newData = data) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]

    let newScale = updateScale(newData);

    let ZscoreWindow = d3.select("#ZscoreWindow");

    // Bind data to svg elements, pairing by phoneme
    let svgs = ZscoreWindow.selectAll("svg")
        .data(newData, d => d.phoneme);

    // Remove unneeded svg elements
    svgs.exit().remove();

    // Add svg elements for new data
    svgs.enter().append("svg")
        .attr("width", svgWidth)
        .attr("height", svgHeight)
        .attr("id", d => "Chart_" + d.phoneme)
        .attr("class", d => d.phoneme)
        // Update the elements in new svg elements
        .each(entry => initializeSVG(entry, newScale));

    refreshVisible(newData, newScale);
    $(window).on("scroll", function() {
        checkVisible(newData, newScale);
    });
};


// Rescales circle and popup positions based on new scale
function rescaleGraphs(scale = xScale, phon = "") {
    xScale = scale;
    refreshVisible(data, scale, true);
};


// Loads Z-scores from specified file path, then processes it and executes callback function on the data
function loadData(ZscorePath, callbackFunction) {
    let newData = new Array();
    characteristics = new Object();
    d3.json(ZscorePath, function(rawData) { 
        d3.csv("../Reference/characteristics.csv", function(c) {
            for (let i = 0; i < c.length; i++) {
                let entry = c[i];
                characteristics[entry["character"]] = entry;
            };

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
