$(document).ready(function(){
    
    statuses = $(".statuses").data("statuses");
    console.log(statuses);
    var width = 900;
    var height = 80;
    var barWidth = 50;

    var chart = d3.select(".statuses").append("svg:svg").attr("width", width).attr("height", height);

    var x = d3.scale.linear().domain([0, statuses.length]).range([0, width]);
    var y = d3.scale.linear().domain([0, 5]).range([0, height]);

    chart.selectAll("rect")
        .data(statuses)
        .enter().append("rect")
        .attr("x", function(d, i) { return x(i) - .5; })
        .attr("y", function(d) { return height - y(d) - .5; })
        .attr("width", barWidth)
        .attr("height", function(d) { return y(d); });

    chart.selectAll("text")
        .data(statuses)
        .enter().append("text")
        .text(function(d) { return d; })
        .attr("x", function(d, i) { return x(i) + barWidth/2; })
        .attr("y", function(d) { return height - 6; })
        .attr("text-anchor", "middle")
        .attr("font-family", "sans-serif")
        .attr("font-size", "14px")
        .attr("fill", "black");

});
