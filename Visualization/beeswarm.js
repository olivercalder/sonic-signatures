var width = 960;
var height = 200;
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
        }
    }

/*    var ZscoreWindow = d3.select("#ZscoreWindow");
    for (var k=0; k<phonemes.length; k++) {
        var svg = ZscoreWindow.append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("id", function(d) { return "Chart_" + data[k].phoneme; })
                .data(data[k].data)
                .enter().append("circle");
    }
*/

    var ZscoreWindow = d3.select("#ZscoreWindow");
    var svgs = ZscoreWindow.selectAll("svg")
        .data(data)
        .enter().append("svg")
            .attr("width", width)
            .attr("height", height)
            .attr("id", function(d) { return "Chart_" + d.phoneme; })
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
});
