$(document).ready(function(){

    createLineChart = function(el){
        var $el = $(el);

        var answers = $el.find($(".answers")).data("answers").answers;
        if(answers.length < 5){
            console.log('not enough info for this one');
            return false;
        }

        var width = 600;
        var height = 100;
        var margin = {top: 20, right: 20, bottom: 30, left: 50}
        
        var chart = d3.select(".answers").append("svg:svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        
        var x = d3.time.scale().range([0, width]);
        var y = d3.scale.linear().domain([5,0]).range([0, height]);
        
        var parseDate = d3.time.format("%d-%m-%Y %H:%M").parse;
        
        var line = d3.svg.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y(d.value); })
            .interpolate("basis");
        
        var xAxis = d3.svg.axis()
            .scale(x)
            .ticks(d3.time.months, 1)
            .tickSize(0)
            .orient("bottom");
        
        var yAxis = d3.svg.axis()
            .scale(y)
            .ticks(1)
            .tickPadding(10)
            .orient("left");
        
        $.each(answers, function(i,d) {
            d.date = parseDate(d.date);
            d.value = +d.value;
        });
        
        
        x.domain(d3.extent(answers, function(d) { return d.date; }));
        
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
            .datum(answers)
            .attr("class", "line")
            .attr("d", line);

        return true;
    }

    $('.status-report').each(function(i, el){
        if(!createLineChart(el)) $(el).hide();
    });
});
