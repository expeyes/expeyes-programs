
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

var addPlot = function(plotType){
	
	saveButton = $('<button>').text('Save').click(dumpToDisc);
	resultplots.prepend(saveButton);
	

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
						label: 'Time',
						labelSize: 20,
					},
					{
						size: 40,
						label: 'Y Axis',
						labelSize: 12,
						stroke: "magenta",
					}
				]

	if(plotType == 'xy'){
		myaxes[0].label = 'X Data';
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
						auto: true,
					},
					y: {
						auto: true,
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
	
	
}



var polarPositions = []


var addPolarPlot = function(){
	polarPositions = [];

	saveButton = $('<button>').text('Save').click(dumpToDisc);
	resultplots.prepend(saveButton);

	//if(resultplots.width()<300)resultplots.width("300px");
	//if(resultplots.height()<300)resultplots.height("300px");

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

var dumpToDisc = function(){
	dat = ''
	for(i=0;i<lastPosition;i++){
		dat+=mydata[0][i]+','+mydata[1][i]+'\n';
	}
	MyJavascriptInterface.savePlotToDisc('plot data',dat);
}

var addDataPoint = function(x){
	mydata[0][lastPosition] = (new Date() - startTime)/1000.;
	mydata[1][lastPosition] = x;
	activePlot.setData([mydata[0].slice(0,lastPosition),mydata[1].slice(0,lastPosition)]);	
	lastPosition ++;
}

var plotArraysXY = function(data){
	x=JSON.parse(data);
	//alert(x[0]);
	//alert(x[1]);
	mydata[0] = x[0];
	mydata[1] = x[1];
	activePlot.setData([x[0],x[1]]);	

}
var plotXArrayYArray = function(X,Y){
for(var i=0;i<Math.min(X.a.length, Y.a.length);i++){
	addDataPointXY(X.a[i],Y.a[i]);
	}
}


var plotArraysXYY = function(data){
	x=JSON.parse(data);
	mydata[0] = x[0];
	mydata[1] = x[1];
	activePlot.setData([ x[0],x[1],x[2] ]);	

}


var addDataPointXY = function(x,y){
	mydata[0][lastPosition] = x
	mydata[1][lastPosition] = y;
	activePlot.setData([mydata[0].slice(0,lastPosition),mydata[1].slice(0,lastPosition)]);	
	lastPosition ++;
}

var addDataPointPolar = function(angle, radius, maxrad){
	console.log(angle+' '+radius+' '+maxrad);
	angle = angle%360;
	x = 100+100*radius*Math.cos(3.1415*angle/180)/maxrad;
	y = 100-100*radius*Math.sin(3.1415*angle/180)/maxrad;
	polarPositions[Math.round(angle)].setAttribute('cx',x)
	polarPositions[Math.round(angle)].setAttribute('cy',y)
	//mydata[0][lastPosition] = radius*Math.cos(3.1415*angle/180);
	//mydata[1][lastPosition] = radius*Math.sin(angle*3.1415/180);
	//activePlot.setData([mydata[0].slice(0,lastPosition),mydata[1].slice(0,lastPosition)]);	
	//console.log('angle:'+angle+' rad:'+radius+' maxrad:'+maxrad+' x:'+mydata[0][lastPosition]+' y:'+mydata[1][lastPosition]);
	//lastPosition ++;
}
