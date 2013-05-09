$(document).ready(function(){
    
    statuses = $(".statuses").data("statuses").statuses;
    var width = 300;
    var height = 80;
    var margin = {top: 20, right: 20, bottom: 30, left: 50}

    var chart = d3.select(".statuses").append("svg:svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", "translate(" + margin.left + "," + margin.top + ")");

    var x = d3.time.scale().range([0, width]);
    var y = d3.scale.linear().domain([5,0]).range([0, height]);

    var parseDate = d3.time.format("%d-%m-%Y").parse;

    var line = d3.svg.line()
        .x(function(d) { return x(d.date); })
        .y(function(d) { return y(d.value); });

    var xAxis = d3.svg.axis()
        .scale(x)
        .orient("bottom");

    var yAxis = d3.svg.axis()
        .scale(y)
        .orient("left");

    $.each(statuses, function(i,d) {
        d.date = parseDate(d.date);
        d.value = +d.value;
    });


    x.domain(d3.extent(statuses, function(d) { return d.date; }));

    chart.append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + height + ")")
        .call(xAxis);

    chart.append("g")
        .attr("class", "y axis")
        .call(yAxis)
        .append("text")
        .attr("transform", "rotate(-90)")
        .attr("y", 6)
        .attr("dy", ".71em")
        .style("text-anchor", "end");

    chart.append("path")
        .datum(statuses)
        .attr("class", "line")
        .attr("d", line);



    // chart.selectAll("rect")
    //     .data(statuses)
    //     .enter().append("rect")
    //     .attr("x", function(d, i) { return x(i); })
    //     .attr("y", function(d) { return height - y(d); })
    //     .attr("width", barWidth)
    //     .attr("height", function(d) { return y(d); });

    // chart.selectAll("text")
    //     .data(statuses)
    //     .enter().append("text")
    //     .text(function(d) { return d; })
    //     .attr("x", function(d, i) { return x(i) + barWidth/2; })
    //     .attr("y", function(d) { return height - 6; })
    //     .attr("text-anchor", "middle")
    //     .attr("font-family", "sans-serif")
    //     .attr("font-size", "14px")
    //     .attr("fill", "white");

});
