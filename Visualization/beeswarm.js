var width = 1000;  // of circle graph
var height = 280;  // of circle graph
var xMargin = 100;  // on either side of circle graph
var yMargin = 60;  // on either side of circle graph
var totalWidth = width + (2 * xMargin);  // of each svg element
var totalHeight = height + (2 * yMargin);  // of each svg element
var middle = height / 2;  // of circle graph

var slowTrans = 1000;  // Transition time for slow transitions, in milliseconds
var fastTrans = 150;  // Transition time for fast transitions, in milliseconds

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
var characteristics;  // Will be modified by the initial csv load


// Checkbox to toggle displaying average circles
var averageToggle = d3.select("#controlPanel");

averageToggle.append("input")
    .attr("type", "checkbox")
    .attr("class", "checkbox")
    .attr("id", "averageToggle")
    .on("change", function() {
        averages = d3.select("#averageToggle").property("checked");
        updateAverages();
    });

averageToggle.append("label")
    .text("Draw Averages    ");


// Draw or hide average circles, depending on whether var averages is true or false
function updateAverages() {
    if (averages) {
        drawAverages(); 
    } else if (!averages) {
        hideAverages();
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
    updateAverages();
    colorCircles();
}


// Gets the color for a given character's data according to the current classifier
function getColor(charData) {
    classification = charData[classifier];
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
        .style("stroke", d => getColor(d));
};


// Click handler that locks circles from being modified by mouseover or mouseout
function handleClick(d) {
    let circ = d3.select(this);  //circle element triggering event

    let newPersist = (parseInt(circ.attr("persist")) + 1) % 2;

    d3.selectAll(".id_" + d.identity.replace(/\./g, "-"))  // all circle elements for the same character
        .attr("persist", function() { return newPersist; });
};


// Selects circle that was moused over, as well as all circles of the same identity, 
//     and enlarges and labels them
function handleMouseOver(d) {
    let circ = d3.select(this);  // circle element triggering event
    if (circ.attr("persist") == 0) {

        d3.selectAll("circle.id_" + d.identity.replace(/\./g, "-"))  // all circle elements for the same character
            .transition()
            .duration(fastTrans)
            .attr("r", function() { return (circ.classed("average") ? sizeScale(d.count, d.total) + radius : 2 * radius); })
            .style("stroke", "black")
            .each(function() {
                let currentCirc = d3.select(this);
                let phon = currentCirc.datum()["phoneme"];

                let graph = d3.select(this.parentNode);  // g element containing circles for each circle

                circPopup = graph.append("text")
                    .attr("class", function() { return "id_" + d.identity.replace(/\./g, "-") + ((d.average) ? " average" : "") + " popup"; })  
                        // Need average class to be included in popup in case average circles are redrawn while popup is still in existence
                    .attr("x", function() { return currentCirc.attr("cx");})
                    .attr("y", function() { let cy = parseFloat(currentCirc.attr("cy"));
                        return ((cy < middle) ? cy - 30 : cy + 40); })
                    .style("text-anchor", "middle")
                    .style("font-weight", "bold")
                    //.style("stroke", "white")
                    .style("fill", "black")
                    .style("font-size", "16px")
                    .text(function() { return d.identity + ": " + parseFloat(currentCirc.datum()["Zscore"]).toFixed(3); });
            });
    };
};


// Selects circle that was moused out, as well as all circles of the same identity,
//     and returns them to their default size and removes their labels
function handleMouseOut(d) {
    let circ = d3.select(this);  // circle element triggering event

    if (circ.attr("persist") == 0) {

        d3.selectAll("circle.id_" + d.identity.replace(/\./g, "-"))  // all circle elements for the same character
            .transition()
            .duration(fastTrans)
            .attr("r", function() { return (circ.classed("average") ? sizeScale(d.count, d.total) : radius); })
            .style("stroke", function() { return getColor(d) });

        d3.selectAll("text.id_" + d.identity.replace(/\./g, "-") + ".popup").remove();
    };
};


/*
function truncScore(Zscore) {
    if (Zscore > 3) {
        return 4;
    } else if (Zscore < -3) {
        return -4;
    } else {
        return Zscore;
    };
}

xScale = d3.scaleLinear()
    .domain(d3.extent(chartData, function(d) { return truncScore(d.Zscore); }))
    .domain([-4, 4])
    .range([10, width - xMargin - 10]);
*/


// Scale used for placing circles as well as generating axes
var xScale = d3.scaleLinear()
    .range([10, width - 10]);
    // .domain() must be set independently, such as by updateScale()


// Returns a list of Z-scores from a given dataset
function getZscores(newData) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    Zscores = new Array();
    for (let i = 0; i < newData.length; i++) {
        let phonData = newData[i].data;
        for (let j = 0; j < phonData.length; j++) {
            Zscores.push(phonData[j].Zscore);
        };
    };
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


// Returns the minimum Z-score from a given dataset
function getZscoreMin(newData) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let Zscores = getZscores(newData);
    let ZscoreMin = getArrayMin(Zscores);
    return ZscoreMin;
}

// Returns the minimum Z-score from a given dataset
function getZscoreMax(newData) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    let Zscores = getZscores(newData);
    let ZscoreMax = getArrayMax(Zscores);
    return ZscoreMax;
}


// Updates xScale according to specified data
function updateScale(newData) {
    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
    ZscoreMin = getZscoreMin(newData);
    ZscoreMax = getZscoreMax(newData);

    xScale.domain([ZscoreMin, ZscoreMax]);
    return xScale;
}  // Returns xScale so that the scaling can be done by the output of this function, to avoid race conditions


var sizeScaleHelper = d3.scaleLinear()
    .range([20, (height / 2) - 20]);

// Scales the size of average circles given the number of characters in 
//     the class and the total number of characters
function sizeScale(classCount, totalCount) {
    sizeScaleHelper.domain([0, totalCount]);
    return sizeScaleHelper(classCount);
}


// Returns data of averages of each class for each phoneme, used by drawAverages()
function getAvgsData() {
    let avgsData = new Object();

    d3.selectAll("g.graph").each(function(entry) {
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
        let classData = new Array();

        for (let i = 0; i < classes.length; i++) {
            classData.push({
                "identity": classes[i],
                "average": true,
                "count": classCounts[classes[i]],
                "total": entryData.length,
                "Zscore": classSums[classes[i]] / classCounts[classes[i]],
                "role": ((classifier == "role") ? classes[i] : undefined),
                "gender": ((classifier == "gender") ? classes[i] : undefined),
                "genre": ((classifier == "genre") ? classes[i] : undefined)
            })
        }

        let xForceAvg = d3.forceX(d => xScale(d.Zscore))  // force to pull circle towards its specified x value
            .strength(1);
        let yForceAvg = d3.forceY(middle)
            .strength(0.1);
        let collisionAvg = d3.forceCollide()  // applied to every node
            .radius(d => sizeScale(d.count, d.total) + 1)
            .strength(0.9)
            .iterations(10);

        let simulationAvg = d3.forceSimulation(classData)  // Initializes a simulation with each datum as a node
            .force("xForce", xForceAvg)
            .force("yForce", yForceAvg)
            .force("collision", collisionAvg)
            .stop();

        for (let i = 0; i < 120; i++) { simulationAvg.tick(); };

        avgsData[phoneme] = classData;
    });
    return avgsData;
    // avgsData is of the form:
    //     avgsData = {"AA": classData, "AE": classData, ...}
    //     where classData = [{"identity": <class>, "average": true, "Zscore": <avgZscore>, ...}, ...]
};


// Draws average circles onto graphs based on the data bound to those graphs
function drawAverages() {
    let avgsData = getAvgsData();

    d3.selectAll("g.graph").each(function(entry) {
        let phoneme = entry.phoneme;
        let classData = avgsData[phoneme];

        // Binds averages data to average circles
        let avgCircles = d3.select(this).selectAll("circle.average")
            .data(classData, d => d.identity);

        // Removes all average circle popup labels
        d3.select(this).selectAll(".average.popup").remove()

        // Removes old circles gracefully
        avgCircles.exit()
            .transition()
            .duration(slowTrans)
            .attr("fill-opacity", 0.0)
            .style("stroke", "white")
            .attr("r", 0)
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
            .attr("persist", 0)
            .on("mouseover", handleMouseOver)
            .on("mouseout", handleMouseOut)
            .on("click", handleClick)
            .attr("fill-opacity", 0.5)
            .transition()
            .duration(slowTrans)
            .attr("r", d => sizeScale(d.count, d.total))
            .style("fill", d => getColor(d))
            .style("stroke", d => getColor(d));

        // Modify existing average circles
        avgCircles
            .attr("class", function(d) {
                    let classList = new Array();
                    classList.push(phoneme);
                    classList.push("average");
                    classList.push("id_" + d.identity);
                    return classList.join(" ");
            })
            .attr("persist", 0)
            .on("mouseover", handleMouseOver)
            .on("mouseout", handleMouseOut)
            .on("click", handleClick)
            .transition()
            .duration(slowTrans)
            .attr("r", d => sizeScale(d.count, d.total))
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            .attr("fill-opacity", 0.5)
            .style("fill", d => getColor(d))
            .style("stroke", d => getColor(d));
    });
    // The code after avgCircles.enter() and avgCircles is very similar, but separated so as to avoid race conditions

    d3.selectAll("circle").filter(d => (d.average ? false : true))  // Make all other non-average circles opacity 0.5
        .transition()
        .duration(slowTrans)
        .attr("fill-opacity", 0.5)
};


// Removes average circles from each graph and returns other circles to opacity 1
function hideAverages() {
    d3.selectAll("circle").filter(d => (d.average ? false : true))
        .transition()
        .duration(slowTrans)
        .attr("fill-opacity", 1.0)

    d3.selectAll(".average")
        .transition()
        .duration(slowTrans)
        .attr("fill-opacity", 0.0)
        .style("stroke", "white")
        .attr("r", 0)
        .remove();
}


function initializeSVG(entry) {
    let phoneme = entry.phoneme;
    let chartData = entry.data;

    // Creates element to contain phoneme label
    let label = d3.select("svg." + phoneme).append("g")
        .attr("class", function() { return phoneme + " label"; })
        .attr("width", xMargin)
        .attr("height", totalHeight);

    // Creates text within the label element
    label.append("text")
        .attr("x", xMargin / 2)
        .attr("y", totalHeight / 2)
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

    // Creates actual d3 axis object
    var xAxis = d3.axisBottom(xScale);

    // Creates element to contain the axis, then creates the axis itself
    d3.select("svg." + phoneme).append("g")
        .attr("class", function() { return phoneme + " axis"; })
        .attr("transform", "translate(" + xMargin + "," + (height + (yMargin * 1.5)) + ")")
        .attr("width", width)
        .attr("height", yMargin)
        .call(xAxis);

    // Creates force to pull circle towards the x coordinate corresponding to its Z-score
    var xForce = d3.forceX(d => xScale(d.Zscore))
        .strength(1);

    // Creates force to pull each circle towards the horizontal center line
    var yForce = d3.forceY(middle)
        .strength(0.1);

    // Creates collision force between each circle
    var collision = d3.forceCollide()
        .radius(radius + 1)
        .strength(0.9)
        .iterations(10);

    // Initializes a simulation to calculate x and y coordinates of each circle
    var simulation = d3.forceSimulation(chartData)
        .force("xForce", xForce)
        .force("yForce", yForce)
        .force("collision", collision)
        .stop();

    // Performs 120 ticks of calculation
    for (let i = 0; i < 120; i++) { simulation.tick(); };

    // Creates element to contain circles
    var g = d3.select("svg." + phoneme).append("g")
        .attr("class", function() { return phoneme + " graph"; })
        .attr("transform", "translate(" + xMargin + "," + yMargin + ")")
        .attr("width", width)
        .attr("height", height);

    // Gets a list of all classifiers
    let classifier_keys = Object.keys(classifiers);

    // Binds data to circles, then creates new ones as needed, deletes old ones, and updates existing ones
    var circles = g.selectAll("circle")
            .data(chartData, d => d.identity);

    circles.enter().append("circle")
        .attr("r", 0)
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .attr("persist", 0)
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
        .duration(slowTrans)
        .attr("r", radius)
        .style("fill", d => getColor(d))
        .style("stroke", d => getColor(d));
    
}


// Draws label, axis, legend, and circles onto the svg element corresponding to the given data entry
//     Where entry = {"phoneme": phoneme, "data": phonData}
//         Where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
function updateSVG(entry, scale = xScale) {
    let phoneme = entry.phoneme;
    let chartData = entry.data;

    // Re-creates actual d3 axis object
    let xAxis = d3.axisBottom(scale);

    // Re-calls new axis in existing axis element
    d3.select("g.axis." + phoneme)
        .call(xAxis);

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
    for (let i = 0; i < 120; i++) { simulation.tick(); };

    // Gets a list of all classifiers
    let classifier_keys = Object.keys(classifiers);

    // Binds data to circles, then creates new ones as needed, deletes old ones, and updates existing ones
    let circles = d3.select("g.graph." + phoneme).selectAll("circle")
            .data(chartData, d => d.identity);

    // Remove all popup labels
    d3.select("g.graph." + phoneme).selectAll(".popup")
        .remove()

    // Remove old circles gracefully
    circles.exit()
        .transition()
        .duration(slowTrans)
        .attr("r", 0)
        .attr("fill-opacity", 0)
        .style("stroke", "white")
        .remove();

    // Creates new circles and formats them properly
    circles.enter().append("circle")
        .attr("r", 0)
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .attr("persist", 0)
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
        .duration(slowTrans)
        .attr("r", radius)
        .style("fill", d => getColor(d))
        .style("stroke", d => getColor(d));

    // Modify existing circles
    circles
        .attr("persist", 0)
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
        .duration(slowTrans)
        .attr("r", radius)
        .attr("cx", d => d.x)
        .attr("cy", d => d.y)
        .style("fill", d => getColor(d))
        .style("stroke", d => getColor(d));
};


// Update svg elements and the circles they contain with new data
function update(newData) {
    // newData must be explicitly passed data to avoid race conditions

    // newData should have the following structure:
    //     newData = [{"phoneme": phoneme, "data": phonData}, ...]
    //     where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]

    updateScale(newData);

    let ZscoreWindow = d3.select("#ZscoreWindow");

    // Bind data to svg elements, pairing by phoneme
    let svgs = ZscoreWindow.selectAll("svg")
        .data(newData, d => d.phoneme);

    // Remove unneeded svg elements
    svgs.exit().remove();

    // Add svg elements for new data
    svgs.enter().append("svg")
        .attr("width", totalWidth)
        .attr("height", totalHeight)
        .attr("id", d => "Chart_" + d.phoneme)
        .attr("class", d => d.phoneme)
        // Update the elements in new svg elements
        .each(entry => initializeSVG(entry));

    // Update the elements in existing svg elements
    svgs.each(entry => updateSVG(entry, updateScale(newData)));

    updateAverages();
};


function rescaleGraphs(scale = xScale, phon = "") {
    d3.selectAll("svg" + ((phon == "") ? "" : "." + phon)).each(function(entry) {
        phoneme = entry.phoneme;
        chartData = entry.data;

        // Re-creates actual d3 axis object with new scale
        let xAxis = d3.axisBottom(scale);

        // Re-calls new axis in existing axis element
        d3.select(this).selectAll("g.axis")
            .call(xAxis);

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
        for (let i = 0; i < 120; i++) { simulation.tick(); };

        d3.select(this).selectAll("circle")
            .transition()
            .duration(slowTrans)
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            .style("fill", d => getColor(d))
            .style("stroke", d => getColor(d));

        avgsData = getAvgsData()[phoneme];

        // Creates collision force between each circle
        let avgsCollision = d3.forceCollide()
            .radius(d => sizeScale(avgsData.count, avgsData.total) + 1)
            .strength(0.9)
            .iterations(10);

        // Initializes a simulation to calculate x and y coordinates for average circles
        let avgsSimulation = d3.forceSimulation(avgsData)
            .force("xForce", xForce)
            .force("yForce", yForce)
            .force("collision", avgsCollision)
            .stop();

        // Performs 120 ticks of calculation
        for (let i = 0; i < 120; i++) { simulation.tick(); };
        
        d3.select(this).selectAll("circle.average").data(avgsData)
            .transition()
            .duration(slowTrans)
            .attr("cx", d => d.x)
            .attr("cy", d => d.y)
            .style("fill", d => getColor(d))
            .style("stroke", d => getColor(d));
    });
};


//d3.json("../Archive/Vowels-Only-No-Others/percentages_Z-scores.json", function(rawData) { 
//d3.json("percentages_Z-scores.json", function(rawData) { 
//       https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Archive/Vowels-Only-All/percentages_Z-scores.json
d3.json("https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Archive/Vowels-Only-Min-2500/percentages_Z-scores.json", function(rawData) { 
    d3.csv("https://raw.githubusercontent.com/olivercalder/sonic-signatures/master/Reference/characteristics.csv", function(c) {

        data = new Array();
        characteristics = new Object();

        for (let i = 0; i < c.length; i++) {
            let entry = c[i];
            characteristics[entry["character"]] = entry;
        }

        let characters = Object.keys(rawData);
        let phonemes = Object.keys(rawData[characters[0]]);
        for (let i = 0; i < phonemes.length; i++) {
            phoneme = phonemes[i];
            let phonData = new Array();
            data.push({"phoneme": phoneme, "data": phonData});
            for (let j = 0; j < characters.length; j++) {
                let charName = characters[j];
                let Zscore = rawData[charName][phoneme];
                phonData.push({
                    "Zscore": parseFloat(Zscore),
                    "identity": charName,
                    "role": characteristics[charName]["role"],
                    "gender": characteristics[charName]["gender"],
                    "genre": characteristics[charName]["genre"],
                });
            };
        };
        // This creates data with structure:
        //      data = [{"phoneme": phoneme, "data": phonData}, ...]
        //      where phonData = [{"Zscore": Zscore, "identity": charName, ...}, ...]
        
        update(data);
    });
});

