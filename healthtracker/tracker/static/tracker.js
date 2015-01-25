$(document).ready(function(){

    var width = 900,
        height = 100,
        margin = {top: 20, right: 20, bottom: 30, left: 50};

    var makeChart = function(el) {
        var chart = d3.select(el).append("svg:svg")
            .attr("width", width + margin.left + margin.right)
            .attr("height", height + margin.top + margin.bottom)
          .append("g")
            .attr("transform", "translate(" + margin.left + "," + margin.top + ")");
        return chart;
    }

    var createLineChart = function(el) {
        var $el = $(el);

        var answers = $el.find($(".answers")).data("answers").answers,
            qmax = parseInt($el.find(".answers").data("qmax")),
            qmin = parseInt($el.find(".answers").data("qmin"));

        if(answers.length < 5){
            console.log('not enough info for this one');
            return false;
        }

        var chart = makeChart(el);

        var x = d3.time.scale().range([0, width]),
            y = d3.scale.linear().domain([qmax,qmin]).range([0, height]),
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

  var createBinaryYearChart = function(el) {
    var $el = $(el);

    var chart = makeChart(el);

    var cellSize = 15;

    var day = d3.time.format("%w"),
        week = d3.time.format("%U"),
        percent = d3.format(".1%"),
        format = d3.time.format("%d-%m-%Y");

    var color = d3.scale.quantize()
        .domain([0, 1])
        .range(d3.range(11).map(function(d) { return "q" + d + "-11"; }));

    var answers = $el.find($(".answers")).data("answers").answers;

    var rect = chart.selectAll(".day")
        .data(d3.time.days(new Date(2014, 0, 1), new Date(2015, 0, 1)))
      .enter().append("rect")
        .attr("class", "day")
        .attr("width", cellSize)
        .attr("height", cellSize)
        .attr("x", function(d) { return week(d) * cellSize; })
        .attr("y", function(d) { return day(d) * cellSize; })
      .datum(format);

    var parseDate = d3.time.format("%d-%m-%Y %H:%M").parse;
    var yesses = answers.filter(function(a) {
      if (!a.value) {
        return a;
      }
      return false;
    }).map(function(a) {
      //var d = parseDate(a.date);
      //return new Date(d.getFullYear(), d.getMonth(), d.getDate());
      return a.date.split(' ')[0];
    });

    window.a = yesses;

    var parseDate2 = d3.time.format("%d-%m-%Y").parse;
    rect.filter(function(d) {
      var isYes = yesses.indexOf(d) >= 0;
      return isYes;
    })
      .attr("class", function(d) { return "day yes"; })
      .style('fill', 'rgb(153, 55, 19)');

    chart.selectAll(".month")
        .data(d3.time.months(new Date(2014, 0, 1), new Date(2015, 0, 1)))
      .enter().append("path")
        .attr("class", "month")
        .attr("d", monthPath);

    function monthPath(t0) {
      var t1 = new Date(t0.getFullYear(), t0.getMonth() + 1, 0),
          d0 = +day(t0), w0 = +week(t0),
          d1 = +day(t1), w1 = +week(t1);
      return "M" + (w0 + 1) * cellSize + "," + d0 * cellSize
        + "H" + w0 * cellSize + "V" + 7 * cellSize
        + "H" + w1 * cellSize + "V" + (d1 + 1) * cellSize
        + "H" + (w1 + 1) * cellSize + "V" + 0
        + "H" + (w0 + 1) * cellSize + "Z";
    }

    chart.selectAll(".month")
        .data(function(d) { return d3.time.months(new Date(d, 0, 1), new Date(d + 1, 0, 1)); })
      .enter().append("path")
        .attr("class", "month")
      .style('color', 'white')
        .attr("d", monthPath);
  }


var createYesNoChart = function(el) {
    var $el = $(el);

    var chart = makeChart(el);

    var answers = $el.find($(".answers")).data("answers").answers,
        qmax = parseInt($el.find(".answers").data("qmax")),
        qmin = parseInt($el.find(".answers").data("qmin"));

    if(answers.length < 5){
        console.log('not enough info for this one');
        return false;
    }

    var parseDate = d3.time.format("%d-%m-%Y %H:%M").parse;

    $.each(answers, function(i,d) {
        d.date = parseDate(d.date);
        d.value = +d.value;
    });

    var lastAnswer = answers[answers.length - 1];
    var x = d3.time.scale()
        .domain(d3.extent(answers, function(d) { return d.date; }))
        .range([0, width]);

    var y = d3.scale.ordinal().range(['steelblue', 'darkorchid']).domain([0, 1]),
        bisectDate = d3.bisector(function(d) { return d.date; }).left;

    chart.selectAll("rect").data(answers).enter()
      .append("rect")
        .style("fill", function (d)     { return y(d.value); } )
        .attr("x",     function(d, i)   { return x(d.date); } )
        .attr("y", 0)
        .attr("height", height)
        .attr("width", ((width-margin.left)/answers.length));


         ///////////////////////////
        /// AXES //////////////////
       ///////////////////////////
        var xAxis = d3.svg.axis()
            .scale(x)
            .ticks(d3.time.months, 1)
            .tickSize(0)
            .orient("bottom");

        chart.append("g")
            .attr("class", "x axis")
            .attr("transform", "translate(0," + height + ")")
            .call(xAxis);



    /// info text

        var focusText = chart.append("g")
            .attr("class", "focusText")
            .attr("display", null);

        focusText.append("text")
            .attr("x", 0)
            .attr("dy", "-.4em")
            .style("font", "12px sans-serif");

        chart.append("rect")
            .attr("class", "overlay")
            .attr("width", width+margin.right)
            .attr("height", height)
            .on("mouseover", function() { focusText.style("display", null); })
            .on("mouseout", function()  { focusText.style("display", "none"); })
            .on("mousemove", mousemove);

        f = d3.time.format("%a, %b %-d %Y");

        function mousemove() {
            var x0 = x.invert(d3.mouse(this)[0]),
                i = bisectDate(answers, x0, 1),
                d = answers[i],
                dname = (d.value == 0) ? 'yes' : 'no';
            focusText.select("text").text("You reported a " + dname + " on " + f(d.date));
        }
    }

    $('.status-report').each(function(i, el){
        if($(el).hasClass('yesno')) createBinaryYearChart(el);
        else if(!createLineChart(el)) $(el).hide();
//        if(!createLineChart(el)) $(el).hide();
    });
});
