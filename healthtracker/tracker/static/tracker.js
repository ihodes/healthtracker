$(document).ready(function(){

    createLineChart = function(el){
        var $el = $(el);

        var answers = $el.find($(".answers")).data("answers").answers;

        if(answers.length < 5){
            console.log('not enough info for this one');
            return false;
        }

        var width = 600,
            height = 100,
            margin = {top: 20, right: 20, bottom: 30, left: 50};
        
        var chart = d3.select(el).append("svg:svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
            .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        
        var x = d3.time.scale().range([0, width]),
            y = d3.scale.linear().domain([5,0]).range([0, height]),
            bisectDate = d3.bisector(function(d) { return d.date; }).left;
        
        var parseDate = d3.time.format("%d-%m-%Y %H:%M").parse;

        $.each(answers, function(i,d) {
            d.date = parseDate(d.date);
            d.value = +d.value;
        });
        
        x.domain(d3.extent(answers, function(d) { return d.date; }));

        var line = d3.svg.line()
            .x(function(d) { return x(d.date); })
            .y(function(d) { return y(d.value); })
            .interpolate("monotone");
        
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

        var focus = chart.append("g")
            .attr("class", "focus")
            .style("display", "none");

        focus.append("circle")
            .attr("r", 2);

        var focusText = chart.append("g")
            .attr("class", "focusText")
            .attr("display", null);

        focusText.append("text")
            .attr("x", 0)
            .attr("dy", "-.4em")
            .style("font", "12px sans-serif");

        chart.append("rect")
            .attr("class", "overlay")
            .attr("width", width)
            .attr("height", height)
            .on("mouseover", function() { focus.style("display", null); focusText.style("display", null); })
            .on("mouseout", function() { focus.style("display", "none"); focusText.style("display", "none"); })
            .on("mousemove", mousemove);

        f = d3.time.format("%a, %b %-d %Y");

        function mousemove() {
            var x0 = x.invert(d3.mouse(this)[0]),
                i = bisectDate(answers, x0, 1),
                d0 = answers[i - 1],
                d1 = answers[i],
                d = x0 - d0.date > d1.date - x0 ? d1 : d0;
            focus.attr("transform", "translate(" + x(d.date) + "," + y(d.value) + ")");
            focusText.select("text").text("You reported a " + d.value + " on " + f(d.date));
        }

        return true;
    }

    $('.status-report').each(function(i, el){
        if(!createLineChart(el)) $(el).hide();
    });
});
