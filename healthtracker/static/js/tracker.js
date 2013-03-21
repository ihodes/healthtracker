$(document).ready(function(){
    
    statuses = $(".statuses").data("statuses");

    // create an SVG element inside the #graph div that fills 100% of the div
    var graph = d3.select(".statuses").append("svg:svg").attr("width", "100%").attr("height", "50px");

    var x = d3.scale.linear().domain([0, 10]).range([0, 500]);
    var y = d3.scale.linear().domain([0, 5]).range([0, 20]);

    var line = d3.svg.line()
        .x(function(d,i) { return x(i); })
        .y(function(d) { return y(d); })
    
    graph.append("svg:path").attr("d", line(statuses));
});
