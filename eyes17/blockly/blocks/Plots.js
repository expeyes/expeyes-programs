
var colors = ['red','orange','yellow','olive','green','teal','blue','violet','purple','pink','brown','grey','black'];
var recentcolor=0;

var mydata = {};
var startTime = new Date();
var activePlot=null;
var myplots = {}
var options = {}
var plotdatastack = {};

var clearPlot = function(){
    plotdatastack = {};
	 resultplots.empty();
	 myplots  = {};
	 options = {};
}

function createPlots(latestCode){
            mydata = {}; startTime = new Date();
            if(latestCode.indexOf('plot_radar(')>=0)
              addPolarPlot();
}


var polarPositions = [];

var addPolarPlot = function(){
	polarPositions = [];

	resultplots.append(`
	<div id="polarplot" style="min-width:300px;width:100%;height:100%;position:relative;">
	<!-- Grey circle -->
	 <svg viewBox="0 0 200 200" class="circle" style="position:absolute;">
	     <circle cx="100" cy="100" r="100" fill="#9cb" />
	</svg>

	<!-- Pie -->
	 <svg class="polar" viewBox="-1 -1 2 2" style="transform: rotate(-90deg);position: absolute;">
	</svg>

	<!-- Slice borders -->
	<svg viewBox="0 0 200 200" style="transform: rotate(0deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(60deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(-60deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(30deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(-30deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(90deg);position:absolute;" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>


	<!-- Concentric circles -->
	<svg viewBox="0 0 200 200" class="polar circle" style="position:absolute;">
	    <circle cx="100" cy="100" r="100" fill="none" stroke="white" stroke-width="1"  stroke-opacity=".5" />
	    <circle cx="100" cy="100" r="80" fill="none" stroke="white" stroke-width="1" stroke-opacity=".5"/>
	    <circle cx="100" cy="100" r="60" fill="none" stroke="white" stroke-width="1" stroke-opacity=".5"/>
	    <circle cx="100" cy="100" r="40" fill="none" stroke="white" stroke-width="1" stroke-opacity=".5"/>
	    <circle cx="100" cy="100" r="20" fill="none" stroke="white" stroke-width="1" stroke-opacity=".5"/>
	</svg>


	</div>
	`);



	plt = document.querySelector('.polar.circle');

	for(var i=0;i<361;i++){
		dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
		dot.setAttribute('cx',100);
		dot.setAttribute('cy',100);
		dot.setAttribute('r',2);
		dot.setAttribute('stroke','lightgreen');
		dot.setAttribute('fill','green');
		polarPositions.push(dot);
		plt.appendChild(dot);
	}

}

var makePlotIfUnavailable = function(plotname){
    if(!(plotname in myplots)){
        mydata[plotname] = [];
        var w = resultplots.width()<300?300:resultplots.width();
        var h = resultplots.height()<300 ? 300:resultplots.height();
        if(h>400)h=400;
        startTime = new Date();
        resultplots.append($('<div id="cs_'+plotname+'">').width(w).height(h));
        myplots[plotname] = 0;
        options[plotname] = {
                series: {
                    lines: {
                        show: true,
                        lineWidth: 2
                    },
                    points: {
                        show: true
                    }
                },
                xaxis: {
                    gridLines: true,
                    autoScaleMargin : 0.1,
                    autoScale: 'exact',
                    growOnly : true
                },
                yaxis: {
                    gridLines: true,
                    autoScaleMargin : 0.1,
                    autoScale: 'exact',
                    growOnly : true
                },

                legend: {
                    show: true,
                    noColumns: 1,
                    labelFormatter: null, // fn: string -> string
                    container: null, // container (as jQuery object) to put legend in, null means default on top of graph
                    position: 'ne', // position of default legend container within plot
                    margin: 5, // distance from grid edge to default legend container within plot
                    sorted: null // default to no legend sorting
                }
        };

    }
}
var addDataPoint = function(plotname, x){
    makePlotIfUnavailable(plotname);
    if(myplots[plotname]==0){
        	startTime = new Date();
        	mydata[plotname].push([0,x]);
    }else{
        	mydata[plotname].push([(new Date() - startTime)/1000.,x]);
	}
	myplots[plotname] ++;
	//if(myplots[plotname]>20)options[plotname].series.points.show = false;
	//else options[plotname].series.points.show = true;
	options[plotname].series.line.show = false;

    options[plotname].xaxes = [{ position: 'bottom', axisLabel: 'Time (S)', show: true }];
    $.plot("#cs_"+plotname, [{color: "red", lines: {show: true, lineWidth: 2}, data: mydata[plotname], label: "Y data"}], options[plotname]);
}
var addDataPointXY = function(plotname, x,y){
    makePlotIfUnavailable(plotname);
    mydata[plotname].push([x,y]);
	myplots[plotname] ++;
	//if(myplots[plotname]>200)options[plotname].series.points.show = false;
	//else options[plotname].series.points.show = true;
	options[plotname].series.line.show = false;
    $.plot("#cs_"+plotname, [ mydata[plotname] ], options[plotname]);
}


var plotArraysXYStack = function(plotname,X,Y, state){
    makePlotIfUnavailable(plotname);
    options[plotname].series.points.show = false;
    if(!(plotname in plotdatastack))plotdatastack[plotname] = [];

    if(state)plotdatastack[plotname] = [ {color: colors[plotdatastack[plotname].length % colors.length], lines: {show: true, lineWidth: 2}, data: [], label: "Chan "+plotdatastack[plotname].length} ];
    else plotdatastack[plotname].push( {color: colors[plotdatastack[plotname].length % colors.length], lines: {show: true, lineWidth: 2}, data: [], label: "Chan "+plotdatastack[plotname].length} );

    nx = Object.values(X.a)
    ny = Object.values(Y.a)
    dat = plotdatastack[plotname][plotdatastack[plotname].length - 1];
    for (i=0;i<nx.length;i++){
        dat.data.push([nx[i],ny[i]]);
    }

    $.plot("#cs_"+plotname, plotdatastack[plotname], options[plotname]);

}

var plotArraysXY = function(plotname,X,Y){
    makePlotIfUnavailable(plotname);
    options[plotname].series.points.show = false;
    mydata[plotname] = [
        {color: "red", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 1"},
    ];
    nx = Object.values(X.a)
    ny = Object.values(Y.a)
    for (i=0;i<nx.length;i++){
        mydata[plotname][0].data.push([nx[i],ny[i]]);
    }

    $.plot("#cs_"+plotname, mydata[plotname], options[plotname]);

}


var plotArraysXYY = function(plotname, X,Y1, Y2){
    makePlotIfUnavailable(plotname);
    options.series.points.show = false;
    mydata[plotname] = [
        {color: "red", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 1"},
        {color: "blue", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 2"},
    ];

    nx = Object.values(X.a)
    ny1 = Object.values(Y1.a)
    ny2 = Object.values(Y2.a)
    for (i=0;i<nx.length;i++){
        mydata[plotname][0].data.push([nx[i],ny1[i]]);
        mydata[plotname][1].data.push([nx[i],ny2[i]]);
    }

    $.plot("#cs_"+plotname, mydata[plotname] , options[plotname]);

}

var plotArraysXYYY = function(plotname, X,Y1, Y2, Y3){
    makePlotIfUnavailable(plotname);
    options[plotname].series.points.show = false;
    mydata[plotname] = [
        {color: "red", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 1"},
        {color: "blue", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 2"},
        {color: "forestgreen", lines: {show: true, lineWidth: 2}, data: [], label: "Chan 3"},
    ];

    nx = Object.values(X.a)
    ny1 = Object.values(Y1.a)
    ny2 = Object.values(Y2.a)
    ny3 = Object.values(Y3.a)
    for (i=0;i<nx.length;i++){
        mydata[plotname][0].data.push([nx[i],ny1[i]]);
        mydata[plotname][1].data.push([nx[i],ny2[i]]);
        mydata[plotname][2].data.push([nx[i],ny3[i]]);
    }

    $.plot("#cs_"+plotname, mydata[plotname] , options[plotname]);

}


var addDataPointPolar = function(angle, radius, maxrad){
	angle = angle%360;
	x = 100+100*radius*Math.cos(3.1415*angle/180)/maxrad;
	y = 100-100*radius*Math.sin(3.1415*angle/180)/maxrad;
	polarPositions[Math.round(angle)].setAttribute('cx',x)
	polarPositions[Math.round(angle)].setAttribute('cy',y)

}

/*---------------------- Plot against Time ---------------*/


Blockly.Blocks['plot_datapoint'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("PLOT X Vs Time:");
    this.appendValueInput("VALUE")
        .setAlign(Blockly.ALIGN_LEFT)
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME")
        .appendField("X :")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot datapoint against time");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_datapoint'] = function(block) {
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  var name = block.getFieldValue('PLOTNAME');
  var code = 'sleep(0.001);\n'+'plot(\''+name+'\','+value+');\n';

  return code;
};


Blockly.Python['plot_datapoint'] = function(block) {
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  var code = 'plot('+value+')\n';

  return code;
};


/*---------------------- Plot Scale ---------------*/
Blockly.Blocks['plot_scale'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME");
    this.appendDummyInput()
        .appendField(" : Set Range");
    this.appendDummyInput()
        .appendField("Plot X Range, Min: ")
        .appendField(new Blockly.FieldNumber(0), "XMIN")
        .appendField("  Max: ")
        .appendField(new Blockly.FieldNumber(10), "XMAX")
        .appendField(new Blockly.FieldDropdown([["fixed","none"], ["autoscale","exact"]]), "SCALEX")
    this.appendDummyInput()
        .appendField("Plot Y Range, Min: ")
        .appendField(new Blockly.FieldNumber(-5), "YMIN")
        .appendField("  Max: ")
        .appendField(new Blockly.FieldNumber(5), "YMAX")
        .appendField(new Blockly.FieldDropdown([["fixed","none"], ["autoscale","exact"]]), "SCALEY");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot Ranges");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_scale'] = function(block) {
  var xmin = Number(block.getFieldValue('XMIN'));
  var xmax = Number(block.getFieldValue('XMAX'));
  var ymin = Number(block.getFieldValue('YMIN'));
  var ymax = Number(block.getFieldValue('YMAX'));
  var scalex = block.getFieldValue('SCALEX');
  var scaley = block.getFieldValue('SCALEY');
  var name = block.getFieldValue('PLOTNAME');
  var code = 'plot_scale(\''+name+'\',\'x\','+xmin+','+xmax+',\''+scalex+'\');\n';
  code += 'plot_scale(\''+name+'\',\'y\','+ymin+','+ymax+',\''+scaley+'\');\n';

  return code;
};


Blockly.Python['plot_scale'] = function(block) {
  var xmin = Number(block.getFieldValue('XMIN'));
  var xmax = Number(block.getFieldValue('XMAX'));
  var ymin = Number(block.getFieldValue('YMIN'));
  var ymax = Number(block.getFieldValue('YMAX'));
  var name = block.getFieldValue('PLOTNAME');
  var code = 'plot_scale(\''+name+'\',\'x\','+xmin+','+xmax+')\n';
  code += 'plot_scale(\''+name+'\',\'y\','+ymin+','+ymax+')\n';
  return code;
};


Blockly.Blocks['plot_scale_x'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME");
    this.appendDummyInput()
        .appendField(" : Set X Range");
    this.appendDummyInput()
        .appendField("Plot X Range, Min: ")
        .appendField(new Blockly.FieldNumber(0), "XMIN");
    this.appendDummyInput()
        .appendField("  Max: ")
        .appendField(new Blockly.FieldNumber(0), "XMAX");
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X Axis Range");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_scale_x'] = function(block) {
  var vmin = Number(block.getFieldValue('XMIN'));
  var vmax = Number(block.getFieldValue('XMAX'));
  var name = block.getFieldValue('PLOTNAME');
  var code = 'plot_scale(\''+name+'\',\'x\','+vmin+','+vmax+');\n';

  return code;
};


Blockly.Python['plot_scale_x'] = function(block) {
  var vmin = Number(block.getFieldValue('XMIN'));
  var vmax = Number(block.getFieldValue('XMAX'));
  var code = 'plot_scale(\'x\','+vmin+','+vmax+')\n';
  return code;
};



Blockly.Blocks['plot_scale_y'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME");
    this.appendDummyInput()
        .appendField(" : Set Y Range");
    this.appendDummyInput()
        .appendField("Plot Y Range, Min: ")
        .appendField(new Blockly.FieldNumber(0), "YMIN");
    this.appendDummyInput()
        .appendField("  Max: ")
        .appendField(new Blockly.FieldNumber(0), "YMAX");
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot Y Axis Range");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_scale_y'] = function(block) {
  var vmin = Number(block.getFieldValue('YMIN'));
  var vmax = Number(block.getFieldValue('YMAX'));
  var name = block.getFieldValue('PLOTNAME');
  var code = 'plot_scale(\''+name+'\',\'y\','+vmin+','+vmax+');\n';

  return code;
};


Blockly.Python['plot_scale_y'] = function(block) {
  var vmin = Number(block.getFieldValue('YMIN'));
  var vmax = Number(block.getFieldValue('YMAX'));
  var code = 'plot_scale(\'y\','+vmin+','+vmax+')\n';
  return code;
};


/*---------------------- Plot plot_xarray_yarray ---------------*/


Blockly.Blocks['plot_xyarray'] = {
  init: function() {
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT ARRAY X[]:")
    this.appendValueInput("Y")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y[]:");
    this.appendDummyInput()
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME")
        .appendField(new Blockly.FieldCheckbox("TRUE"), "CLEAR")
        .appendField("Clear?");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xyarray'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var name = block.getFieldValue('PLOTNAME');
  var clr = block.getFieldValue('CLEAR');
  var state = (clr == "TRUE")?true:false;
  var code = 'sleep(0.001);\n'+'plot_xyarray(\''+name+'\','+X+','+Y+','+state+');\n';

  return code;
};


Blockly.Python['plot_xyarray'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_xyarray('+X+','+Y+')\n';

  return code;
};



/*---------------------- Plot plot_xyyarray ---------------*/



Blockly.Blocks['plot_xyyarray'] = {
  init: function() {
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT ARRAY X[]:")
    this.appendValueInput("Y1")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y1[]:")
    this.appendValueInput("Y2")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME")
        .appendField("ARRAY Y2[]:")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y1, Y2 arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xyyarray'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y1 = Blockly.JavaScript.valueToCode(block, 'Y1', Blockly.JavaScript.ORDER_NONE);
  var Y2 = Blockly.JavaScript.valueToCode(block, 'Y2', Blockly.JavaScript.ORDER_NONE);
  var name = block.getFieldValue('PLOTNAME');
  var code = 'sleep(0.001);\n'+'plot_xyyarray(\''+name+'\','+X+','+Y1+','+Y2+');\n';

  return code;
};


Blockly.Python['plot_xyyarray'] = function(block) {
  var X = Blockly.Python.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var Y1 = Blockly.Python.valueToCode(block, 'Y1', Blockly.Python.ORDER_NONE);
  var Y2 = Blockly.Python.valueToCode(block, 'Y2', Blockly.Python.ORDER_NONE);
  var code = 'plot_xyyarray('+X+','+Y1+','+Y2+')\n';
  return code;
};

/*---------------------- Plot plot_xyyyarray ---------------*/



Blockly.Blocks['plot_xyyyarray'] = {
  init: function() {
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT ARRAY X[]:")
    this.appendValueInput("Y1")
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y1[]:")
    this.appendValueInput("Y2")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y2[]:")
    this.appendValueInput("Y3")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y3[]:")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y1, Y2, Y3 arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xyyyarray'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y1 = Blockly.JavaScript.valueToCode(block, 'Y1', Blockly.JavaScript.ORDER_NONE);
  var Y2 = Blockly.JavaScript.valueToCode(block, 'Y2', Blockly.JavaScript.ORDER_NONE);
  var Y3 = Blockly.JavaScript.valueToCode(block, 'Y3', Blockly.JavaScript.ORDER_NONE);
  var name = block.getFieldValue('PLOTNAME');
  var code = 'sleep(0.001);\n'+'plot_xyyyarray(\''+name+'\','+X+','+Y1+','+Y2+','+Y3+');\n';

  return code;
};


Blockly.Python['plot_xyyyarray'] = function(block) {
  var X = Blockly.Python.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var Y1 = Blockly.Python.valueToCode(block, 'Y1', Blockly.Python.ORDER_NONE);
  var Y2 = Blockly.Python.valueToCode(block, 'Y2', Blockly.Python.ORDER_NONE);
  var Y3 = Blockly.Python.valueToCode(block, 'Y3', Blockly.Python.ORDER_NONE);
  var code = 'sleep(0.001)\n'+'plot_xyyyarray('+X+','+Y1+','+Y2+','+Y3+')\n';
  return code;
};

/*---------------------- Plot XY ---------------*/


Blockly.Blocks['plot_xy'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("PLOT X,Y")
    this.appendValueInput("X")
        .appendField(new Blockly.FieldTextInput("myplot"), "PLOTNAME")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("X:")
    this.appendValueInput("Y")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Y:")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xy'] = function(block) {
  var name = block.getFieldValue('PLOTNAME');
  var vx = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var vy = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_xy(\''+name+'\','+vx+','+vy+')\n';

  return code;
};


Blockly.Python['plot_xy'] = function(block) {
  var vx = Blockly.JavaScript.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var vy = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.Python.ORDER_NONE);
  var code = 'plot_xy('+vx+','+vy+')\n';

  return code;
};




/*---------------------- Polar Plot ---------------*/


Blockly.Blocks['plot_radar'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Polar Plot")
    this.appendValueInput("MAXRADIUS")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Maximum Radius:")
    this.appendValueInput("RADIUS")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("RADIUS:")
    this.appendValueInput("ANGLE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ANGLE(Deg):")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot R, Theta");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_radar'] = function(block) {
  var angle = Blockly.JavaScript.valueToCode(block, 'ANGLE', Blockly.JavaScript.ORDER_NONE);
  var radius = Blockly.JavaScript.valueToCode(block, 'RADIUS', Blockly.JavaScript.ORDER_NONE);
  var maxrad = Blockly.JavaScript.valueToCode(block, 'MAXRADIUS', Blockly.JavaScript.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_radar('+angle+','+radius+','+maxrad+');\n';

  return code;
};


Blockly.Python['plot_radar'] = function(block) {
  var angle = Blockly.Python.valueToCode(block, 'ANGLE', Blockly.Python.ORDER_NONE);
  var radius = Blockly.Python.valueToCode(block, 'RADIUS', Blockly.Python.ORDER_NONE);
  var maxrad = Blockly.Python.valueToCode(block, 'MAXRADIUS', Blockly.Python.ORDER_NONE);
  var code = 'plot_radar('+angle+','+radius+','+maxrad+')\n';

  return code;
};



//-------------------- API ------------------------

function initPlots(interpreter, scope) {
			// PLOT CALLS
		  // Add an API for the plot call
		  interpreter.setProperty(scope, 'plot', interpreter.createNativeFunction(
				function(plotname,  value) {
				  return addDataPoint(plotname, value);
				})
			);



		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_scale', interpreter.createNativeFunction(
				function( plotname, axis, vmin,vmax, scale) {
				    makePlotIfUnavailable(plotname);
				    if(axis === 'x'){options[plotname].xaxis.min = vmin; options[plotname].xaxis.max = vmax; options[plotname].xaxis.autoScale=scale;}
				    else if(axis === 'y'){options[plotname].yaxis.min = vmin; options[plotname].yaxis.max = vmax; options[plotname].yaxis.autoScale=scale;}
				})
			);
		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_xy', interpreter.createNativeFunction(
				function(plotname, vx,vy) {
				  return addDataPointXY(plotname, vx,vy);
				})
			);


		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_xyarray', interpreter.createNativeFunction(
				function(plotname,  X,Y, state) {
                  console.log(state);
    				  return plotArraysXYStack(plotname, X,Y, state);
				})
			);


		  // Add an API for the XYY array plot call
		  interpreter.setProperty(scope, 'plot_xyyarray', interpreter.createNativeFunction(
				function( plotname, x,y1, y2) {
				  return plotArraysXYY(plotname, x,y1, y2);
				})
			);

		  // Add an API for the XYY array plot call
		  interpreter.setProperty(scope, 'plot_xyyyarray', interpreter.createNativeFunction(
				function( plotname, x,y1, y2, y3) {
				  return plotArraysXYYY(plotname, x,y1, y2, y3);
				})
			);

		  // Add an API for the Polar plot call
		  interpreter.setProperty(scope, 'plot_radar', interpreter.createNativeFunction(
				function( angle,radius, maxrad) {
				  return addDataPointPolar(angle,radius, maxrad);
				})
			);





	}



