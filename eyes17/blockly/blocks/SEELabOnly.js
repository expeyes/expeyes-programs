var stepper_pos=0;
var set_stepper_pos = [], cursteppos=0;

var ap = 1;
var an = 4;
var bp = 2;
var bn = 8;

var step_positions=[ap + bp, an + bp, an + bn, ap + bn]; //# {AP+BP,AN+BP,AN+BN,AP+BN}; //full step sequence.

// ----------DOM MANIPULATION
const SVG_NS = "http://www.w3.org/2000/svg";
const SVG_XLINK = "http://www.w3.org/1999/xlink"
// an object to define the properties and text content of the text element

// a function to create a text element
function drawText(parent, props, textcontent) {
  // create a new text element
  let text = document.createElementNS(SVG_NS, "text");
  //set the attributes for the text
  for (var name in props) {
    if (props.hasOwnProperty(name)) {
      text.setAttributeNS(null, name, props[name]);
    }
  }
  text.textContent = textcontent;
  parent.appendChild(text);
  return text;
}


// a function to create an image
function drawImage(parent, props, url) {
  // create a new text element
  let img = document.createElementNS(SVG_NS, "image");
  //set the attributes for the text
  for (var name in props) {
    if (props.hasOwnProperty(name)) {
      img.setAttributeNS(null, name, props[name]);
    }
  }
  img.setAttributeNS(SVG_XLINK, 'xlink:href', url);
  //text.textContent = textcontent;
  parent.appendChild(img);
  return img;
}




/* --------------- Get Voltage ------------ */

Blockly.Blocks['get_voltage'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("READ VOLTAGE")
        .appendField(new Blockly.FieldDropdown([["A1","A1"],["A2","A2"],["A3","A3"],["SEN","SEN"],["IN1","IN1"],["CCS","CCS"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('get_voltage');},'SS'));
    this.setOutput(true, "Number");
    this.setColour(330);
 this.setTooltip("Read Voltage from selected channel");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['get_voltage'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = "get_voltage('"+dropdown_channel+"')";
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_voltage'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble Python into code variable.
  var code = 'p.get_voltage(\''+dropdown_channel+'\')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};


/* --------------- Get Resistance ------------ */

Blockly.Blocks['get_resistance'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("READ RESISTANCE")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('get_resistance');},'SS'));
    this.appendDummyInput()
        .appendField(new Blockly.FieldImage("media/resistor.svg", 150, 25,  "*"))
    this.setOutput(true, "Number");
    this.setColour(330);
 this.setTooltip("Read Resistance b/w Sen and GND");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['get_resistance'] = function(block) {
  var code = "get_resistance()";
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_resistance'] = function(block) {
  var code = 'p.get_resistance()';
  return [code,Blockly.JavaScript.ORDER_NONE];
};


Blockly.Blocks['get_capacitance'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("READ CAPACITANCE ")
        .appendField(new Blockly.FieldDropdown([["pF","0"],["uF","1"]]), "RANGE")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('get_capacitance');},'SS'));
    this.appendDummyInput()
        .appendField(new Blockly.FieldImage("media/capacitor.svg", 150, 25,  "*"))
    this.setOutput(true, "Number");
    this.setColour(330);
 this.setTooltip("Read capacitance b/w IN1 and GND");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['get_capacitance'] = function(block) {
  var r = block.getFieldValue('RANGE');
  if(r==0)
      var code = "get_capacitance("+r+",0)"; // pF range
  else if(r==1)
      var code = "get_capacitance("+r+",2)"; // uF range
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_capacitance'] = function(block) {
  var code = 'p.get_capacitance()';
  return [code,Blockly.JavaScript.ORDER_NONE];
};


/*---------------------- Select voltage range---------------*/


Blockly.Blocks['select_range'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Select ")
        .appendField(new Blockly.FieldDropdown([["A1","A1"], ["A2","A2"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('select_range');},'SS'));
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Range: ")
        .appendField(new Blockly.FieldDropdown([["16 V","0"], ["8 V","1"], ["4 V","2"], ["2.5 V","3"], ["1.5 V","4"], ["1 V","5"], ["0.5 V","6"], ["0.25 V","7"]]), "RANGE");
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(150);
 this.setTooltip("Set Input Voltage Range");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['select_range'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var range = block.getFieldValue('RANGE');
  var code = 'select_range(\''+dropdown_channel+'\',' + range+  ');\n';
  return code;
};


Blockly.Python['select_range'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var range = block.getFieldValue('RANGE');
  var code = 'p.select_range(\''+dropdown_channel+'\',' + range+  ')\n';
  return code;
};



/*---------------------- SET PV1 / PV2---------------*/

Blockly.Blocks['set_voltage'] = {
  init: function() {
    this.appendValueInput("VOLTAGE")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SET VOLTAGE")
        .appendField(new Blockly.FieldDropdown([["PV1","PV1"], ["PV2","PV2"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('set_voltage');},'SS'));
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("Set Voltage of PV1");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_voltage'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_voltage = Blockly.JavaScript.valueToCode(block, 'VOLTAGE', Blockly.JavaScript.ORDER_NONE);
  var code = 'set_voltage(\''+dropdown_channel+'\','+value_voltage+');\n';
  return code;
};


Blockly.Python['set_voltage'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_voltage = Blockly.Python.valueToCode(block, 'VOLTAGE', Blockly.Python.ORDER_NONE);
  var code = 'p.set_voltage(\''+dropdown_channel+'\','+value_voltage+')\n';
  return code;
};

/*------- select sine amplitude ---*/

Blockly.Blocks['select_sine_amp'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Sine(WG) Amplitude ")
        .appendField(new Blockly.FieldDropdown([["3V","2"], ["1V","1"], ["80mV","0"]]), "RANGE")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('select_sine_amp');},'SS'));
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("Set WG Voltage Range");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['select_sine_amp'] = function(block) {
  var range = block.getFieldValue('RANGE');
  var code = 'select_sine_amp(' + range+  ');\n';
  return code;
};


Blockly.Python['select_sine_amp'] = function(block) {
  var range = block.getFieldValue('RANGE');
  var code = 'p.select_sine_amp(' + range+  ')\n';
  return code;
};




/*---------------------- SET WG / SQ1 / SQ2---------------*/


Blockly.Blocks['set_frequency'] = {
  init: function() {
    this.appendValueInput("FREQUENCY")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SET FREQUENCY")
        .appendField(new Blockly.FieldDropdown([["WG","WG"], ["SQ1","SQ1"], ["SQ2","SQ2"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('set_frequency');},'SS'));
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("Set FREQUENCY of WG/SQ1/SQ2");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_frequency'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_frequency = Blockly.JavaScript.valueToCode(block, 'FREQUENCY', Blockly.JavaScript.ORDER_NONE);
  var code = 'set_frequency(\''+dropdown_channel+'\',' + value_frequency+  ');\n';
  return code;
};


Blockly.Python['set_frequency'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_frequency = Blockly.Python.valueToCode(block, 'FREQUENCY', Blockly.Python.ORDER_NONE);
  if(dropdown_channel === "WG")
	var code = 'p.set_sine('+value_frequency+')\n';
  else if(dropdown_channel === "SQ1")
	var code = 'p.set_sq1('+value_frequency+',50)\n';
  else if(dropdown_channel === "SQ2")
	var code = 'p.set_sq2('+value_frequency+',50)\n';

  return code;
};


/*------- GET FREQUENCY -----------*/



Blockly.Blocks['get_frequency'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("READ FREQUENCY")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.collapse,'SS'))
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('get_frequency');},'SS'));
    this.setInputsInline(false);
    this.setOutput(true, "Number");
    this.setColour(330);
 this.setTooltip("Get FREQUENCY from IN2/SEN");
 this.setHelpUrl("");
  },
    surprise: function() {
		alert('suprise!');
	},
	collapse: function(){
		this.getSourceBlock().setCollapsed(true);
	}

};

Blockly.JavaScript['get_frequency'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = "get_frequency('"+dropdown_channel+"')";
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_frequency'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'p.get_frequency(\''+dropdown_channel+'\')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};



/*------- multi_r2r -----------*/



Blockly.Blocks['multi_r2r'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Rising Edge Timer")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.collapse,'SS'))
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('multi_r2r');},'SS'));
    this.appendDummyInput()
        .appendField("Skip:")
        .appendField(new Blockly.FieldDropdown([["0","0"],["1","1"], ["2","2"], ["4","4"], ["8","8"], ["12","12"], ["16","16"], ["32","32"], ["48","48"]]), "SKIP")
        .appendField("Timeout:")
        .appendField(new Blockly.FieldDropdown([["1","1"], ["2","2"], ["3","3"], ["5","5"], ["10","10"], ["20","20"]]), "TIMEOUT");
    this.setInputsInline(false);
    this.setOutput(true, "Number");
    this.setColour(330);
 this.setTooltip("Measure time between multiple rising edges from IN2/SEN");
 this.setHelpUrl("");
  },

};


Blockly.JavaScript['multi_r2r'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var skip_edges = block.getFieldValue('SKIP');
  var dropdown_timeout = block.getFieldValue('TIMEOUT');
  var code = 'multi_r2r(\''+dropdown_channel+'\','+skip_edges+','+dropdown_timeout+')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['multi_r2r'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_edges = block.getFieldValue('SKIP');
  var dropdown_timeout = block.getFieldValue('TIMEOUT');
  var code = 'p.multi_r2r(\''+dropdown_channel+'\','+(dropdown_edges+2)+','+dropdown_timeout+')';
  return [code,Blockly.Python.ORDER_NONE];
};


Blockly.Blocks['singlePinEdges'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Digital Timer")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.collapse,'SS'))
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"]]), "CHANNEL")
        .appendField(new Blockly.FieldDropdown([["rising","rising"], ["falling","falling"],["4 rising","4xrising"],["16 rising","16xrising"]]), "TYPE")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('singlePinEdges');},'SS'));
    this.appendDummyInput()
        .appendField("Edges:")
        .appendField(new Blockly.FieldDropdown([["1","1"],["2","2"], ["3","3"], ["4","4"]]), "EDGES")
        .appendField("Timeout:")
        .appendField(new Blockly.FieldDropdown([["1","1"], ["2","2"], ["3","3"], ["5","5"], ["10","10"], ["20","20"]]), "TIMEOUT");
    this.appendDummyInput()
        .appendField("First edge starts the timer [t1=0]");
    this.setInputsInline(false);
    this.setOutput(true, "Number");
    this.setColour(330);
 this.setTooltip("Measure time between multiple edges from IN2/SEN");
 this.setHelpUrl("");
  },

};


Blockly.JavaScript['singlePinEdges'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var type = block.getFieldValue('TYPE');
  var edges = block.getFieldValue('EDGES');
  var dropdown_timeout = block.getFieldValue('TIMEOUT');
  var code = 'JSON.parse(singlePinEdges(\''+dropdown_channel+'\',\''+type+'\','+edges+','+dropdown_timeout+'))';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['singlePinEdges'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var type = block.getFieldValue('TYPE');
  var edges = block.getFieldValue('EDGES');
  var dropdown_timeout = block.getFieldValue('TIMEOUT');
  var code = 'p.singlePinEdges(\''+dropdown_channel+'\',\''+type+'\','+edges+','+dropdown_timeout+')';
  return [code,Blockly.Python.ORDER_NONE];
};




Blockly.Blocks['singlePinEdgesAction'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Digital Timer")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.collapse,'SS'))
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('singlePinEdgesAction');},'SS'));
    this.appendDummyInput()
        .appendField("SET ")
        .appendField(new Blockly.FieldDropdown([["OD1","OD1"], ["SQ1","SQ1"], ["SQ2","SQ2"]]), "OUTPUT")
        .appendField(new Blockly.FieldDropdown([["ON","ON"], ["OFF","OFF"]]), "STATE")
        .appendField("at t=0");
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"]]), "CHANNEL")
        .appendField(new Blockly.FieldDropdown([["rising","rising"], ["falling","falling"],["4 rising","4xrising"],["16 rising","16xrising"]]), "TYPE");
    this.appendDummyInput()
        .appendField("Edges:")
        .appendField(new Blockly.FieldDropdown([["1","1"],["2","2"], ["3","3"], ["4","4"]]), "EDGES")
        .appendField("Timeout:")
        .appendField(new Blockly.FieldDropdown([["1","1"], ["2","2"], ["3","3"], ["5","5"], ["10","10"], ["20","20"]]), "TIMEOUT");
    this.setInputsInline(false);
    this.setOutput(true, "Number");
    this.setColour(330);
 this.setTooltip("Measure time between multiple edges from IN2/SEN");
 this.setHelpUrl("");
  },

};


Blockly.JavaScript['singlePinEdgesAction'] = function(block) {
  var dropdown_output = block.getFieldValue('OUTPUT');
  var dropdown_state = block.getFieldValue('STATE');
  var state = true;
  block.setColour('#0ec244');//Make block green
  if(dropdown_state === 'OFF' ){
      block.setColour('#f33');//Make block red
	  state = false;
	  }

  var dropdown_channel = block.getFieldValue('CHANNEL');
  var type = block.getFieldValue('TYPE');
  var edges = block.getFieldValue('EDGES');
  var dropdown_timeout = block.getFieldValue('TIMEOUT');
  var code = 'JSON.parse(singlePinEdgesAction(\''+dropdown_channel+'\',\''+type+'\','+edges+',\''+dropdown_output+'\','+state+','+dropdown_timeout+'))';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['singlePinEdgesAction'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var type = block.getFieldValue('TYPE');
  var edges = block.getFieldValue('EDGES');
  var dropdown_timeout = block.getFieldValue('TIMEOUT');
  var code = 'p.singlePinEdgesAction(\''+dropdown_channel+'\',\''+type+'\','+edges+','+dropdown_timeout+')';
  return [code,Blockly.Python.ORDER_NONE];
};



/*----------Capture routine. Capture 1---------*/


Blockly.Blocks['capture1'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Capture 1 |")
        .appendField(new Blockly.FieldDropdown([["A1","A1"], ["A2","A2"], ["A3","A3"], ["SEN","SEN"], ["IN1","IN1"], ["MIC","MIC"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('capture1');},'SS'));
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SAMPLES")
        .appendField(new Blockly.FieldNumber(0, 10, 5000, 1), "SAMPLES");
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("TIMEGAP(uS)")
        .appendField(new Blockly.FieldNumber(0, 1, 2000, 1), "TIMEGAP");
    this.appendDummyInput()
        .appendField("Data in Variables:");
    this.appendDummyInput()
        .appendField(new Blockly.FieldVariable("timestamps"), "TIMESTAMPS")
        .appendField(new Blockly.FieldVariable("data1"), "DATA1");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(150);
 this.setTooltip("Record traces using the  Oscilloscope");
 this.setHelpUrl("");
	}
}

Blockly.JavaScript['capture1'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');
  //var code = "var jsondata = capture1('"+dropdown_channel+"',"+number_samples+","+number_timegap+");\ntmpjson=JSON.parse(jsondata);timestamps=tmpjson[0];data1=tmpjson[1];\n";
  var code = "var jsondata = capture1('"+dropdown_channel+"',"+number_samples+","+number_timegap+");\ntmpjson = JSON.parse(jsondata);"+timevar+"=tmpjson[0];"+datavar+"=tmpjson[1];\n";
  return code;
};

Blockly.Python['capture1'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var code = 'timestamps,data1 = p.capture1(\''+dropdown_channel+'\','+number_samples+','+number_timegap+')\n';
  return code;
};


/*----------Capture routine. Capture 2---------*/

Blockly.Blocks['capture2'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Capture 2, ")
        .appendField(new Blockly.FieldDropdown([["Chan 1: A1","A1"], ["Chan 1: A2","A2"], ["Chan 1: A3","A3"], ["Chan 1: SEN","SEN"], ["Chan 1: IN1","IN1"], ["Chan 1: MIC","MIC"]]), "CHANNEL")
        .appendField("Chan 2: A2")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('capture2');},'SS'));
    this.appendDummyInput()
        .appendField("SAMPLES")
        .appendField(new Blockly.FieldNumber(0, 10, 5000, 1), "SAMPLES")
        .appendField("TIMEGAP(uS)")
        .appendField(new Blockly.FieldNumber(0, 1, 2000, 1), "TIMEGAP");
    this.appendDummyInput()
        .appendField("Data in Variables:")
        .appendField(new Blockly.FieldVariable("timestamps"), "TIMESTAMPS");
    this.appendDummyInput()
        .appendField(new Blockly.FieldVariable("data1"), "DATA1")
        .appendField(new Blockly.FieldVariable("data2"), "DATA2");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(150);
 this.setTooltip("Record traces using the  Oscilloscope");
 this.setHelpUrl("");
	}
}

Blockly.JavaScript['capture2'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar1 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');
  var datavar2 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA2'), 'VARIABLE');

  var code = "var jsondata = capture2('"+dropdown_channel+"',"+number_samples+","+number_timegap+");\ntmpjson = JSON.parse(jsondata);"+timevar+"=tmpjson[0];"+datavar1+"=tmpjson[1];"+datavar2+"=tmpjson[2];\n";
  return code;
};

Blockly.Python['capture2'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var code = 'timestamps,data1,data2 = p.capture2('+number_samples+','+number_timegap+',\''+dropdown_channel+'\')\n';
  return code;
};

/*----------Capture routine. Capture 4---------*/

Blockly.Blocks['capture4'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Capture 4 |")
        .appendField(new Blockly.FieldDropdown([["Chan 1: A1","A1"], ["Chan 1: A2","A2"], ["Chan 1: A3","A3"], ["Chan 1: SEN","SEN"], ["Chan 1: IN1","IN1"], ["Chan 1: MIC","MIC"]]), "CHANNEL")
        .appendField(", Chan 2: A2")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('capture4');},'SS'));
    this.appendDummyInput()
        .appendField("SAMPLES")
        .appendField(new Blockly.FieldNumber(0, 10, 5000, 1), "SAMPLES")
        .appendField("TIMEGAP(uS)")
        .appendField(new Blockly.FieldNumber(0, 1, 2000, 1), "TIMEGAP");
    this.appendDummyInput()
        .appendField("Data Variables:")
        .appendField(new Blockly.FieldVariable("timestamps"), "TIMESTAMPS")
        .appendField(new Blockly.FieldVariable("data1"), "DATA1")
    this.appendDummyInput()
        .appendField(new Blockly.FieldVariable("data2"), "DATA2")
        .appendField(new Blockly.FieldVariable("data3"), "DATA3")
        .appendField(new Blockly.FieldVariable("data4"), "DATA4");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(150);
 this.setTooltip("Record traces using the  Oscilloscope");
 this.setHelpUrl("");
	}
}

Blockly.JavaScript['capture4'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar1 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');
  var datavar2 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA2'), 'VARIABLE');
  var datavar3 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA3'), 'VARIABLE');
  var datavar4 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA4'), 'VARIABLE');

  var code = "var jsondata = capture4('"+dropdown_channel+"',"+number_samples+","+number_timegap+");\ntmpjson=JSON.parse(jsondata);"+timevar+"=tmpjson[0];"+datavar1+"=tmpjson[1];"+datavar2+"=tmpjson[2];"+datavar3+"=tmpjson[3];"+datavar4+"=tmpjson[4];\n";
  return code;
};

Blockly.Python['capture4'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var code = 'timestamps,data1,data2, data3, data4 = p.capture4('+number_samples+','+number_timegap+',\''+dropdown_channel+'\')\n';
  return code;
};


/*---------------TRIGGER -----------------*/

Blockly.Blocks['scope_trigger'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Oscilloscope Trigger")
        .appendField(new Blockly.FieldCheckbox("TRUE"), "STATE")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('scope_trigger');},'SS'));
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["Channel 1","0"], ["Channel 2","1"], ["Channel 3","2"], ["Channel 4","3"]]), "CHANNEL")
        .appendField(" Level:")
        .appendField(new Blockly.FieldNumber(0, -5, 5, 0.1), "LEVEL");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(150);
 this.setTooltip("Set Scope Trigger level");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['scope_trigger'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var level = block.getFieldValue('LEVEL');
  var st = block.getFieldValue('STATE');
  var state = true;
  if(st == "FALSE")state = false;
  var code = 'scope_trigger(0,\'A1\',' + level + ');\n';
  return code;
};


Blockly.Python['scope_trigger'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var level = block.getFieldValue('LEVEL');
  var state = block.getFieldValue('STATE');
  var code = 'p.scope_trigger(0,\'A1\'' + level + ');\n';

  return code;
};

/*-------------- CAPTURE PLOT ------------------*/

Blockly.Blocks['capture_plot'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Capture And Plot")
        .appendField(new Blockly.FieldDropdown([["Chan 1: A1","A1"], ["Chan 1: A2","A2"], ["Chan 1: A3","A3"], ["Chan 1: SEN","SEN"], ["Chan 1: IN1","IN1"], ["Chan 1: MIC","MIC"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('capture_plot');},'SS'));
    this.appendDummyInput()
        .appendField("Chan 2: A2,")
        .appendField("SAMPLES:")
        .appendField(new Blockly.FieldNumber(200, 10, 5000, 1), "SAMPLES")
        .appendField(" TG(uS):")
        .appendField(new Blockly.FieldNumber(0, 2, 2000, 1), "TIMEGAP");
    this.appendDummyInput()
        .appendField(new Blockly.FieldVariable("timestamps"), "TIMESTAMPS")
        .appendField(new Blockly.FieldVariable("data1"), "DATA1")
        .appendField(new Blockly.FieldVariable("data2"), "DATA2");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(150);
 this.setTooltip("Record traces using the  Oscilloscope and plot them");
 this.setHelpUrl("");
	}
}

Blockly.JavaScript['capture_plot'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');

  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar1 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');
  var datavar2 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA2'), 'VARIABLE');

  //var code = 'scope_trigger(0,\'' + dropdown_channel+ '\',' + 0 + ');\n';
  var code = "var jsondata = capture2('"+dropdown_channel+"',"+number_samples+","+number_timegap+");\n";
  code += "var tmpjson=JSON.parse(jsondata);\n"+timevar+"=tmpjson[0];\n"+datavar1+"=tmpjson[1];\n"+datavar2+"=tmpjson[2];\n";
  code += 'sleep(0.01);\n'+'plot_xyyarray(\'captureplot2\','+timevar+','+datavar1+','+datavar2+');\n';
  return code;
};

Blockly.Python['capture_plot'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar1 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');
  var datavar2 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA2'), 'VARIABLE');

  var code = 'scope_trigger(0,\'' + dropdown_channel+ '\',' + 0 + ');\n';
  code += "var jsondata = await capture2('"+dropdown_channel+"',400,5)\ntmpjson=JSON.parse(jsondata);"+timevar+"=tmpjson[0];"+datavar1+"=tmpjson[1];"+datavar2+"=tmpjson[2]\n";
  code += 'sleep(0.001);\n'+'plot_xyyarray(\'captureplot2\','+timevar+','+datavar1+','+datavar2+')\n';
  return code;
};


/*---------- CAPTURE ACTION --------*/



Blockly.Blocks['capture_action_plot'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Set OD1 ")
        .appendField(new Blockly.FieldDropdown([["ON(5V)","HIGH"], ["OFF","LOW"]]), "ACTION")
        .appendField(", Capture")
        .appendField(new Blockly.FieldDropdown([["A1","A1"], ["A2","A2"], ["A3","A3"], ["SEN","SEN"], ["IN1","IN1"], ["MIC","MIC"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('capture_action_plot');},'SS'));
    this.appendDummyInput()
        .appendField("SAMPLES:")
        .appendField(new Blockly.FieldNumber(0, 10, 5000, 1), "SAMPLES")
        .appendField(" TIMEGAP(uS):")
        .appendField(new Blockly.FieldNumber(0, 1, 2000, 1), "TIMEGAP");
    this.appendDummyInput()
        .appendField("Plot :")
        .appendField(new Blockly.FieldVariable("timestamps"), "TIMESTAMPS")
        .appendField(new Blockly.FieldVariable("data1"), "DATA1");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(150);
 this.setTooltip("Record traces using the  Oscilloscope");
 this.setHelpUrl("");
	}
}

Blockly.JavaScript['capture_action_plot'] = function(block) {
  var action = block.getFieldValue('ACTION');
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');
  var code = "var jsondata = capture_action('"+dropdown_channel+"',"+number_samples+","+number_timegap+",'"+action+"');\ntmpjson = JSON.parse(jsondata);\n"+timevar+"=tmpjson[0];"+datavar+"=tmpjson[1];\n";
  code += 'sleep(0.01);\n'+'plot_xyarray(\'captureactionplot\','+timevar+','+datavar+');\n';
  return code;
};

Blockly.Python['capture_action_plot'] = function(block) {
  var action = block.getFieldValue('ACTION');
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var code = 'timestamps,data1 = p.capture_action(\''+dropdown_channel+'\','+number_samples+','+number_timegap+',\''+action+'\')\n';
  code += 'sleep(0.01);\n'+'plot_xyarray(timestamps,data1);\n';
  return code;
};



//----------------SR04_distance

Blockly.Blocks['read_SR04'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read SR04 Distance(cm)")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_SR04');},'SS'));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_SR04'] = function(block) {
  var code = 'get_sr04()';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_SR04'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.sr04_distance()';
  return [code, Blockly.JavaScript.ORDER_NONE];
};
//----------------HX711_load cell

Blockly.Blocks['read_HX711'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read HX711 LoadCell")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_HX711');},'SS'));
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["Chan A 128x","25"], ["Chan B 32x","26"], ["Chan A 64x","27"], ["OFF","0"], ["ON","1"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_HX711'] = function(block) {
  var chan = block.getFieldValue('CHANNEL');
  var code = 'get_hx711('+chan+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_HX711'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.hx711()';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

//----------------VOLTS

Blockly.Blocks['read_VOLTS'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read VOLTS")
        .appendField(new Blockly.FieldDropdown([["A1","0"],["A2","1"],["A3","2"],["SEN","3"],["IN1","4"],["CCS","5"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('read_VOLTS');},'SS'));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_VOLTS'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'ADCSENS\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_VOLTS'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.get_sensor(\'VOLTS\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


/*-------------------- SET STATE inline --------------*/


Blockly.Blocks['set_state'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("SET")
        .appendField(new Blockly.FieldDropdown([["OD1","OD1"], ["SQ1","SQ1"], ["SQ2","SQ2"]]), "CHANNEL")
        .appendField(new Blockly.FieldDropdown([["ON","ON"], ["OFF","OFF"]]), "STATE")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('set_state');},'SS'));
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['set_state'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_state = block.getFieldValue('STATE');
  var state = true;
  block.setColour('#0ec244');//Make block green
  if(dropdown_state === 'OFF' ){
      block.setColour('#f33');//Make block red
	  state = false;
	  }
  var code = 'set_state(\''+dropdown_channel+'\',' + state+  ');\n';
  return code;
};

Blockly.Python['set_state'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_state = block.getFieldValue('STATE');
  var state = 'true';
  if(dropdown_state === 'OFF' ) state = "false";
  var code = 'p.set_state(\''+dropdown_channel+'\',' + state+  ')';
  return code;
};


/*---------------------- SET SQ1/SQ2 for Servo Motors---------------*/


Blockly.Blocks['set_servo'] = {
  init: function() {
    this.appendValueInput("ANGLE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SERVO ")
        .appendField(new Blockly.FieldDropdown([["SQ1 Angle","SQ1"], ["SQ2 Angle","SQ2"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('set_servo');},'SS'));
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("Set Angle on servo motor via SQ1 or SQ2");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_servo'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_angle = Blockly.JavaScript.valueToCode(block, 'ANGLE', Blockly.JavaScript.ORDER_NONE);
  var code = 'set_servo(\''+dropdown_channel+'\',' + value_angle+  ');\n';
  return code;
};


Blockly.Python['set_servo'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_angle = Blockly.Python.valueToCode(block, 'ANGLE', Blockly.Python.ORDER_NONE);
  var code = 'p.set_servo(\''+dropdown_channel+'\',' + value_angle+  ')\n'; // TODO: Change to set_sq1(frequency, duty cycle) or set_sq2

  return code;
};



/*------------- SET STEPPER MOTOR via CS1-4 ----------*/

/*---------- STEPPER MOTORS ------------*/

Blockly.Blocks['init_stepper'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Init Stepper Motor[ CS1-4]");
    this.appendDummyInput()
        .appendField("CS1,CS2,CS3,CS4 are outputs. LOW.");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("init stepper");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['init_stepper'] = function(block) {
  stepper_pos=0;
  cursteppos = 4;
  return 'init_stepper();\n';
};


Blockly.Python['init_stepper'] = function(block) {
  return '#init stepper\n';
};



Blockly.Blocks['move_stepper'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Move Stepper:        ");
    this.appendDummyInput()
        .appendField(" ");
    this.appendValueInput("STEPS")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("STEPS: ");
    this.appendValueInput("DELAY")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("DELAY: ");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("move stepper motor");
 this.setHelpUrl("");

  props= {
   x: 135,
   y: 15,
   "fill": "lightgreen",
   "dominant-baseline": "middle",
   "text-anchor": "middle",
  };


  this.txt = drawText(this.getSvgRoot(),props,":");

  imgprops= {
   x: 0,
   y: 30,
   "dominant-baseline": "middle",
   "text-anchor": "middle",
   width: '80px',
   height: '80px'
  };
  this.imgbody = drawImage(this.getSvgRoot(),imgprops, "media/stepper_motor_body.png");
  this.imgshaft = drawImage(this.getSvgRoot(),imgprops, "media/stepper_motor_shaft.png");



  },
  set_stepper_display: function(val, angle) {
      this.txt.textContent = '['+val+']';
      this.imgshaft.setAttributeNS(null, "transform", `rotate(${angle} ${41} ${71})`);
  }

};


Blockly.JavaScript['move_stepper'] = function(block) {
  var code = '';
  var motor=1;

  var steps = Blockly.JavaScript.valueToCode(block, 'STEPS', Blockly.JavaScript.ORDER_NONE);
  var msdelay = Blockly.JavaScript.valueToCode(block, 'DELAY', Blockly.JavaScript.ORDER_NONE);
  set_stepper_pos.push(block);
  if( steps>0 ) // clockwise
      code = 'for(var i=0;i<'+steps+';i++){\nmove_stepper_cw();\nsleep('+msdelay*.001+');\n}\n';
  else
      code = 'for(var i=0;i<'+steps*-1+';i++){\nmove_stepper_ccw();\nsleep('+msdelay*.001+');\n}\n';
  return code;
};


Blockly.Python['move_stepper'] = function(block) {
  var code = '';
  var motor=1;

  var steps = Blockly.JavaScript.valueToCode(block, 'STEPS', Blockly.JavaScript.ORDER_NONE);
  var msdelay = Blockly.JavaScript.valueToCode(block, 'DELAY', Blockly.JavaScript.ORDER_NONE);
  set_stepper_pos.push(block);
  if( steps>0 ) // clockwise
      code = 'p.stepper_move('+steps+',True,'+msdelay*.001+')\n';
  else
      code = 'p.stepper_move('+steps*-1+',False,'+msdelay*.001+')\n';
  return code;
};



/*--------------- EVENT DRIVEN CALLS -------------*/
Blockly.Blocks['generic_slider'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("New Slider")
        .appendField(new Blockly.FieldTextInput("myvar"), "NAME")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('generic_slider');},'SS'));
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Min:")
        .appendField(new Blockly.FieldNumber(0, -1e9, 1e9, 1), "MIN")
        .appendField("Max:")
        .appendField(new Blockly.FieldNumber(100, -1e9, 1e9, 1), "MAX");

    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Add generic slider");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['generic_slider'] = function(block) {
  var name = block.getFieldValue('NAME');
  var mn = block.getFieldValue('MIN');
  var mx = block.getFieldValue('MAX');
  var code = 'add_slider(\''+name+'\','+mn+','+mx+');\n';
  return code;
};


Blockly.Python['generic_slider'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = '# Add Event driven slider \n';
  return code;
};

Blockly.Blocks['generic_slider_value'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Value of")
        .appendField(new Blockly.FieldTextInput("myvar"), "NAME")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('generic_slider_value');},'SS'));

    this.setInputsInline(false);
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("get generic slider value");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['generic_slider_value'] = function(block) {
  var name = block.getFieldValue('NAME');
  var code = 'get_slider_variable(\''+name+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['generic_slider_value'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = '# Add Event driven slider \n';
  return code;
};

//----------------------

Blockly.Blocks['set_frequency_slider'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("FREQUENCY Slider")
        .appendField(new Blockly.FieldDropdown([["WG","WG"], ["SQ1","SQ1"], ["SQ2","SQ2"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('set_frequency_slider');},'SS'));
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Min:")
        .appendField(new Blockly.FieldNumber(5, 1, 20000, 1), "MIN")
        .appendField("Max:")
        .appendField(new Blockly.FieldNumber(2000, 10, 20000, 1), "MAX");

    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Set FREQUENCY of WG/SQ1/SQ2");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_frequency_slider'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var mn = block.getFieldValue('MIN');
  var mx = block.getFieldValue('MAX');
  if(dropdown_channel === "WG" || dropdown_channel === "SQ2"){
    if(mn<4)mn = 4;
    else if(mn>4000)mn = 4000;
    if(mx<100)mx = 100;
    else if(mx>5000)mx = 5000;
  }

  var code = 'add_slider(\''+dropdown_channel+'\','+mn+','+mx+');\n';
  return code;
};


Blockly.Python['set_frequency_slider'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = '# Add Event driven slider to adjust frequency of '+dropdown_channel+' \n';
  return code;
};




oninput = function(oninputsuffix,label) {
if(typeof oninputsuffix != 'undefined'){
	return ` oninput="this.nextElementSibling.value = '${label} ' + this.value + ' ${oninputsuffix}' " `
	}
else{ return ''; }
}


Blockly.Blocks['set_voltage_slider'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("VOLTAGE Slider")
        .appendField(new Blockly.FieldDropdown([["PV1","PV1"], ["PV2","PV2"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/help.svg", 25, 25,  "*", ()=>{showBlockHelp('set_voltage_slider');},'SS'));
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Set VOLTAGE on PV1/PV2");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_voltage_slider'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  if(dropdown_channel === "PV1")
      var code = 'add_slider(\''+dropdown_channel+'\',-5,5);\n';
  else if(dropdown_channel ==="PV2")
      var code = 'add_slider(\''+dropdown_channel+'\',-3,3);\n';
  return code;
};


Blockly.Python['set_voltage_slider'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = '# Add Event driven slider to adjust voltage of '+dropdown_channel+' \n';
  return code;
};



oninput = function(oninputsuffix,label) {
if(typeof oninputsuffix != 'undefined'){
	return ` oninput="this.nextElementSibling.value = '${label} ' + this.value + ' ${oninputsuffix}'; sliderVariables['${label}']=parseFloat(this.value); " `
	}
else{ return ''; }
}

sldr = (label,opts,oninputsuffix) => `
	<div class = "ui row">
		<input type="range" ${opts} class="compactslider" widget="${label}" style="width:70%" ${ oninput(oninputsuffix,label) } >
		<output>${label}</output>
	</div>
`
var sliderVariables={}
function addSlider(value, mn, mx){
    var opts = ''
    if(value === 'WG' || value === 'SQ1' || value === 'SQ2'){
        opts = " min="+mn+" max="+mx;
        var sld = sldr(value,opts,' Hz')
        results.append(sld);
        setTimeout(()=>{
            results.find('.compactslider').on("input",function(){
                    if(typeof HWBridge != 'undefined')
                        HWBridge.set_frequency($(this).attr("widget"), this.value);
                });
            }, 200);
    }else if(value === 'PV1' || value === 'PV2'){
        opts = " min="+mn+" max="+mx+" step=0.01";
        var sld = sldr(value,opts,' V')
        results.append(sld);
        setTimeout(()=>{
            results.find('.compactslider').on("input",function(){
                    if(typeof HWBridge != 'undefined')
                        HWBridge.set_voltage($(this).attr("widget"), this.value);
                });
            }, 200);
    }else{
        sliderVariables[value] = mn;
        opts = " min="+mn+" max="+mx+" value="+mn;
        var sld = sldr(value,opts,'')
        results.append(sld);
    }


}


//-------------------- API ------------------------

function initSEELab(interpreter, scope) {

          // EXPEYES API CALLS
		  // Add an API for the get_voltage call
		  interpreter.setProperty(scope, 'get_voltage', interpreter.createAsyncFunction(
				function(channel,callback) {
				  return parseFloat(HWBridge.get_voltage(channel,callback)).toFixed(3);
				})
			);
		  interpreter.setProperty(scope, 'get_resistance', interpreter.createAsyncFunction(
				function(callback) {
				  return parseFloat(HWBridge.get_resistance(callback)).toFixed(1);
				})
			);
		  interpreter.setProperty(scope, 'get_capacitance', interpreter.createAsyncFunction(
				function(r,f,callback) {
				  return parseFloat(HWBridge.get_capacitance(r,callback)).toFixed(f);
				})
			);

		  // Add an API for the select_range call
		  interpreter.setProperty(scope, 'select_range', interpreter.createAsyncFunction(
				function(channel, value,callback) {
				  return HWBridge.select_range_raw(channel,value,callback);
				})
			);

		  // Add an API for the sine_amplitude call
		  interpreter.setProperty(scope, 'select_sine_amp', interpreter.createAsyncFunction(
				function(value,callback) {
				  return HWBridge.select_sine_amp(value,callback);
				})
			);

		  // Add an API for the set_voltage call
		  interpreter.setProperty(scope, 'set_voltage', interpreter.createAsyncFunction(
				function(channel, value,callback) {
				  return HWBridge.set_voltage(channel,value,callback);
				})
			);

		  // Add an API for the get_frequency call
		  interpreter.setProperty(scope, 'get_frequency', interpreter.createAsyncFunction(
				function(channel,callback) {
				  return parseFloat(HWBridge.get_frequency(channel,callback)).toFixed(3);
				})
			);

		  // Add an API for the multi_r2r call
		  interpreter.setProperty(scope, 'multi_r2r', interpreter.createAsyncFunction(
				function(channel,skip_edges,timeout,callback) {
				  return HWBridge.multi_r2r(channel,parseInt(skip_edges)+2,timeout,callback);
				})
			);
		  // Add an API for the singlePinEdges call
		  interpreter.setProperty(scope, 'singlePinEdges', interpreter.createAsyncFunction(
				function(channel,type, points,timeout,callback) {
				  return HWBridge.singlePinEdges(channel,type, points ,timeout,callback);
				})
			);

		  // Add an API for the singlePinEdges call
		  interpreter.setProperty(scope, 'singlePinEdgesAction', interpreter.createAsyncFunction(
				function(channel,type, points,output, state, timeout,callback) {
				  return HWBridge.singlePinEdgesAction(channel,type, points ,output, state, timeout,callback);
				})
			);



		  // Add an API for the capture block.  copied from wait_block. Async attempt
		  var wrapper = function capture1(channel, ns, tg,callback) {
                return HWBridge.capture1(channel , ns ,tg,callback);
                //return "[[1,2,3],[2,3,2]]";
		  };
		  interpreter.setProperty(scope, 'capture1', interpreter.createAsyncFunction(wrapper));

		  // Add an API for the capture block.  copied from wait_block. Async attempt
		  var wrapper = function capture2(channel, ns, tg, callback) {
			  HWBridge.capture2(channel , ns ,tg, callback);
		  };
		  interpreter.setProperty(scope, 'capture2', interpreter.createAsyncFunction(wrapper));

		  var wrapper = function capture4(channel, ns, tg, callback) {
				HWBridge.capture4(channel , ns ,tg,callback);
		  };
		  interpreter.setProperty(scope, 'capture4', interpreter.createAsyncFunction(wrapper));

		  // Add an API for the capture block.  copied from wait_block. Async attempt
		  interpreter.setProperty(scope, 'capture_data',
		    interpreter.createAsyncFunction(function capture_data(channel,callback) {
                        JSON.parse(HWBridge.capture_data(channel,(e)=>{callback(JSON.parse(e));}) );
                  }
          ));


		  // Add an API for the capture_action block.
		  var wrapper = function capture_action(channel, ns, tg, action,callback) {
                HWBridge.capture_action(channel , ns ,tg, action,10,callback);
		  };
		  interpreter.setProperty(scope, 'capture_action', interpreter.createAsyncFunction(wrapper));


		  // Add an API for the trigger block.
		  var wrapper = function scope_trigger(channel, name, voltage,callback) {
			  HWBridge.configure_trigger(channel ,name, voltage,callback);
		  };
		  interpreter.setProperty(scope, 'scope_trigger', interpreter.createAsyncFunction(wrapper));


		  // Add an API for the set_frequency call
		  interpreter.setProperty(scope, 'set_frequency', interpreter.createAsyncFunction(
				function(channel, value,callback) {
				  HWBridge.set_frequency(channel,value,callback);
				})
			);

		  // Add an API for the set_state call
		  interpreter.setProperty(scope, 'set_state', interpreter.createAsyncFunction(
				function(channel, value,callback) {
				  HWBridge.set_state(channel,value,callback);
				})
			);

		  // Add an API for the get_sr04 call
		  interpreter.setProperty(scope, 'get_sr04', interpreter.createAsyncFunction(
				function(callback) {
				  HWBridge.get_sr04(callback);
				})
			);
		  // Add an API for the get_hx711 call
		  interpreter.setProperty(scope, 'get_hx711', interpreter.createAsyncFunction(
				function(chan,callback,callback) {
                    HWBridge.get_hx711(chan,callback,callback);
				})
			);

		  // Add an API for the set_servo call
		  interpreter.setProperty(scope, 'set_servo', interpreter.createAsyncFunction(
				function(channel, value,callback) {
                    HWBridge.set_servo(channel,value,callback);
				})
			);



		  // Add an API for stepper
		  var wrapper = interpreter.createAsyncFunction(
				function(callback) {
				  HWBridge.set_multiplexer(0,callback);
				});
		  interpreter.setProperty(scope, 'init_stepper', wrapper);

		  var wrapper = interpreter.createAsyncFunction(
				function(motor, callback) {
                  stepper_pos+=1;
                  cursteppos+=1;
                  if(cursteppos>3)cursteppos=0;
				  HWBridge.set_multiplexer(step_positions[cursteppos], callback);
                  for(var i=0;i<set_stepper_pos.length;i++){
                    set_stepper_pos[i].set_stepper_display(stepper_pos, stepper_pos);
                  }
				});
		  interpreter.setProperty(scope, 'move_stepper_cw', wrapper);

		  var wrapper = interpreter.createAsyncFunction(
				function(motor, callback) {
                  stepper_pos-=1;
                  cursteppos-=1;
                  if(cursteppos<0)cursteppos=3;
				  HWBridge.set_multiplexer(step_positions[cursteppos], callback);
                  for(var i=0;i<set_stepper_pos.length;i++){
                    set_stepper_pos[i].set_stepper_display(stepper_pos, stepper_pos);
                  }
				});
		  interpreter.setProperty(scope, 'move_stepper_ccw', wrapper);


		  interpreter.setProperty(scope, 'add_slider', interpreter.createNativeFunction(
				function( value, mn, mx) {
				  return addSlider(value,mn,mx);
				})
			);

		  interpreter.setProperty(scope, 'get_slider_variable', interpreter.createAsyncFunction(
				function( value,callback) {
				  callback(sliderVariables[value]);
				})
			);


	}



