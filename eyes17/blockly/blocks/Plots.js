

var colors = ['red','orange','yellow','olive','green','teal','blue','violet','purple','pink','brown','grey','black'];
var recentcolor=0;
var activePlot;
var uPlotOptions;


function f(x) {
	return Math.random() - 0.5 + Math.sin(x * 0.00002) * 40 + Math.sin(x * 0.001) * 5 + Math.sin(x * 0.1) * 2;
}

function getData(fill,max) {
	const data = [
		Array(max),
		Array(max)
	];

	for (let x = 0; x < fill; x++) {
		data[0][x] = x/1000;
		data[1][x] = 0;
	}
	return data;
}


var mydata = getData(1000,1000);
var lastPosition = 0;
var startTime = new Date();
var activePlot=null;


var clearPlot = function(){
	 resultplots.empty();
}

var addPlot = function(plotType,autoScalingX,autoScalingY){

	myseries = [
					{
						label: "data",
					},
					{
						label: "Y",
						stroke: "magenta",
					}
				];

	myaxes = [
					{
					    size: 30,
						labelGap: 20,
						labelSize: 20,
					},
					{
						size: 40,
						labelSize: 12,
						stroke: "magenta",
					}
				]

	if(plotType == 'xy'){
		myaxes[0].label = 'X Data';
		myaxes[1].label = 'Y Data';
	}

	if(plotType == 'xyy'){
		myseries = [
						{
							label: "data",
						},
						{
							label: "Y",
							stroke: "magenta",
						},
						{
							label: "Y2",
							stroke: "green",
						}
					];


		myaxes = [
						{
							size: 20,
							label: 'Time(mS)',
							labelSize: 20,
						},
						{
							size: 25,
							label: 'Chan 1',
							labelGap: 10,
							labelSize: 12,
							stroke: "magenta",
						},
						{
							size: 25,
							label: 'Chan 2',
							labelGap: 10,
							labelSize: 12,
							stroke: "green",
						}
					];

	}
	if(plotType == 'xyyy'){
		myseries = [
						{
							label: "data",
						},
						{
							label: "Y1",
							stroke: "magenta",
						},
						{
							label: "Y2",
							stroke: "green",
						},
                        {
                            label: "Y3",
                            stroke: "blue",
                        }
					];


		myaxes = [
						{
							size: 20,
							label: 'Time(mS)',
							labelSize: 20,
						}
					];

	}


	uPlotOptions = {
				width: resultplots.width()<300?300:resultplots.width(),
				height: resultplots.height()<300?300:resultplots.height(),
 	paths: u => null,
 	points: {
 		space: 0,
 	},
 					legend:{
					show: false
				},

				cursor: {
					drag: {
						setScale: false,
					}
				},
				scales: {
					x: {
						time: false,
						auto: autoScalingX,
					},
					y: {
						auto: autoScalingY,
					},
				},
				series: myseries,
				axes: myaxes,
			};


	if(plotType == 'polar'){
			uPlotOptions['axes']= null;
		}

	lastPosition = 0;
	startTime = new Date();
	activePlot = new uPlot(uPlotOptions,[[],[],[],[]], resultplots[0]);
	console.log(uPlotOptions);


}



var polarPositions = []


var addPolarPlot = function(){
	polarPositions = [];

	resultplots.append(`
	<div id="polarplot" style="min-width:300px;width:100%;height:100%;position:relative;">
	<!-- Grey circle -->
	 <svg viewBox="0 0 200 200" class="circle" style="position:absolute;">
	     <circle cx="100" cy="100" r="100" fill="#9cb" />
	</svg>

	<!-- Pie -->
	 <svg class="polar" viewBox="-1 -1 2 2" style="transform: rotate(-90deg)">
	</svg>

	<!-- Slice borders -->
	<svg viewBox="0 0 200 200" style="transform: rotate(0deg)" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(60deg)" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(-60deg)" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(30deg)" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(-30deg)" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>

	<svg viewBox="0 0 200 200" style="transform: rotate(90deg)" xmlns="http://www.w3.org/2000/svg">
	  <line x1="0" y1="300" x2="0" y2="0" stroke-width="1" stroke="#ffffff33" transform="translate(100, 0)">
	</svg>


	<!-- Concentric circles -->
	<svg viewBox="0 0 200 200" class="polar circle">
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


var addDataPoint = function(x){
	mydata[0][lastPosition] = (new Date() - startTime)/1000.;
	mydata[1][lastPosition] = x;
	lastPosition ++;
	activePlot.setData([mydata[0].slice(0,lastPosition),mydata[1].slice(0,lastPosition)]);
}

var plotArraysXY = function(X,Y){
nx = Object.values(X.a)
ny = Object.values(Y.a)

mydata[0] = nx;
mydata[1] = ny;

activePlot.setData([nx,ny]);
}


var plotArraysXYY = function(x,y1, y2){
nx = Object.values(x.a)
ny1 = Object.values(y1.a)
ny2 = Object.values(y2.a)

mydata[0] = nx;
mydata[1] = ny1;

activePlot.setData([nx,ny1,ny2]);

}


var plotArraysXYYY = function(x,y1, y2, y3){
nx = Object.values(x.a)
ny1 = Object.values(y1.a)
ny2 = Object.values(y2.a)
ny3 = Object.values(y3.a)

mydata[0] = nx;
mydata[1] = ny1;

activePlot.setData([nx,ny1,ny2, ny3]);

}


var addDataPointXY = function(x,y){
	mydata[0][lastPosition] = x
	mydata[1][lastPosition] = y;
	lastPosition ++;
	activePlot.setData([mydata[0].slice(0,lastPosition),mydata[1].slice(0,lastPosition)]);
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
        .setAlign(Blockly.ALIGN_RIGHT)
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
  var code = 'sleep(0.001);\n'+'plot('+value+');\n';

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
        .appendField("Plot X Range, Min: ")
        .appendField(new Blockly.FieldNumber(0), "XMIN")
        .appendField("  Max: ")
        .appendField(new Blockly.FieldNumber(10), "XMAX");
    this.appendDummyInput()
        .appendField("Plot Y Range, Min: ")
        .appendField(new Blockly.FieldNumber(-5), "YMIN")
        .appendField("  Max: ")
        .appendField(new Blockly.FieldNumber(5), "YMAX");
    this.appendDummyInput()
        .appendField("Invoke after Plotting.");
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
  var code = 'plot_scale(\'x\','+xmin+','+xmax+');\nplot_scale(\'y\','+ymin+','+ymax+');\n';
  return code;
};


Blockly.Python['plot_scale'] = function(block) {
  var xmin = Number(block.getFieldValue('XMIN'));
  var xmax = Number(block.getFieldValue('XMAX'));
  var ymin = Number(block.getFieldValue('YMIN'));
  var ymax = Number(block.getFieldValue('YMAX'));
  var code = 'plot_scale(\'x\','+xmin+','+xmax+');\nplot_scale(\'y\','+ymin+','+ymax+');\n';
  return code;
};


Blockly.Blocks['plot_scale_x'] = {
  init: function() {
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
  var code = 'plot_scale(\'x\','+vmin+','+vmax+');\n';

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
  var code = 'plot_scale(\'y\','+vmin+','+vmax+');\n';

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
        .appendField("ARRAY Y[]:")
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
  var code = 'sleep(0.001);\n'+'plot_xyarray('+X+','+Y+');\n';

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
  var code = 'sleep(0.001);\n'+'plot_xyyarray('+X+','+Y1+','+Y2+');\n';

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
  var code = 'sleep(0.001);\n'+'plot_xyyyarray('+X+','+Y1+','+Y2+','+Y3+');\n';

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
  var vx = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var vy = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_xy('+vx+','+vy+')\n';

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


function getSize() {
    return {
        width: resultplots.width(),
        height: 300,
    }
}

window.addEventListener("resize", e => {
				if(activePlot != null)
					activePlot.setSize(getSize());
			});


//-------------------- API ------------------------

function initPlots(interpreter, scope) {
			// PLOT CALLS
		  // Add an API for the plot call
		  interpreter.setProperty(scope, 'plot', interpreter.createNativeFunction(
				function( value) {
				  return addDataPoint(value);
				})
			);



		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_scale', interpreter.createNativeFunction(
				function( axis, vmin,vmax) {
                    activePlot.setScale(axis, { min: vmin, max: vmax});
                    console.log(axis);
                    console.log({ min: vmin, max: vmax});
				})
			);
		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_xy', interpreter.createNativeFunction(
				function( vx,vy) {
				  return addDataPointXY(vx,vy);
				})
			);


		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_xyarray', interpreter.createNativeFunction(
				function( X,Y) {
				  return plotArraysXY(X,Y);
				})
			);


		  // Add an API for the XYY array plot call
		  interpreter.setProperty(scope, 'plot_xyyarray', interpreter.createNativeFunction(
				function( x,y1, y2) {
				  return plotArraysXYY(x,y1, y2);
				})
			);

		  // Add an API for the XYY array plot call
		  interpreter.setProperty(scope, 'plot_xyyyarray', interpreter.createNativeFunction(
				function( x,y1, y2, y3) {
				  return plotArraysXYYY(x,y1, y2, y3);
				})
			);

		  // Add an API for the Polar plot call
		  interpreter.setProperty(scope, 'plot_radar', interpreter.createNativeFunction(
				function( angle,radius, maxrad) {
				  return addDataPointPolar(angle,radius, maxrad);
				})
			);





	}



