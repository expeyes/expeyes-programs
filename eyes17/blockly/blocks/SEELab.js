

/* --------------- Get Voltage ------------ */



Blockly.Blocks['get_voltage'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read Voltage")
        .appendField(new Blockly.FieldDropdown([["A1","A1"],["A2","A2"],["A3","A3"],["SEN","SEN"],["IN1","IN1"],["CCS","CCS"]]), "CHANNEL");
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
  var code = 'p.get_voltage(\''+dropdown_channel+'\')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

/*---------------------- SET PV1 / PV2---------------*/

Blockly.Blocks['set_voltage'] = {
  init: function() {
    this.appendValueInput("VOLTAGE")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SET VOLTAGE")
        .appendField(new Blockly.FieldDropdown([["PV1","PV1"], ["PV2","PV2"]]), "CHANNEL");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
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
  // TODO: Assemble Python into code variable.

  if(dropdown_channel === "PV1")
	var code = 'p.set_pv1('+value_voltage+')\n';
  else if(dropdown_channel === "PV1")
	var code = 'p.set_pv2('+value_voltage+')\n';

  return code;
};



/* --------------- Get Voltage ------------ */

Blockly.Blocks['get_resistance'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("READ RESISTANCE");
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
  var code = 'p.get_resistance())';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Blocks['get_capacitance'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("READ CAPACITANCE(IN1)");
    this.appendDummyInput()
        .appendField(new Blockly.FieldImage("media/capacitor.svg", 150, 25,  "*"))
    this.setOutput(true, "Number");
    this.setColour(330);
 this.setTooltip("Read capacitance b/w IN1 and GND");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['get_capacitance'] = function(block) {
  var code = "get_capacitance()";
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_capacitance'] = function(block) {
  var code = 'p.get_capacitance())';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

/*---------------------- Select voltage range---------------*/


Blockly.Blocks['select_range'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Select ")
        .appendField(new Blockly.FieldDropdown([["A1","A1"], ["A2","A2"]]), "CHANNEL");
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Range: ")
        .appendField(new Blockly.FieldDropdown([["16 V","16"], ["8 V","8"], ["4 V","4"], ["2.5 V","2.5"], ["1.5 V","1.5"], ["1 V","1"], ["0.5 V","0.5"], ["0.25 V","0.25"]]), "RANGE");
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

/*------- select sine amplitude ---*/

Blockly.Blocks['set_sine_amp'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Sine(WG) Amplitude ")
        .appendField(new Blockly.FieldDropdown([["3V","2"], ["1V","1"], ["80mV","0"]]), "RANGE");
    this.setInputsInline(true);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("Set WG Voltage Range");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_sine_amp'] = function(block) {
  var range = block.getFieldValue('RANGE');
  var code = 'set_sine_amp(' + range+  ');\n';
  return code;
};


Blockly.Python['set_sine_amp'] = function(block) {
  var range = block.getFieldValue('RANGE');
  var code = 'p.set_sine_amp(' + range+  ')\n';
  return code;
};




/*---------------------- SET WG / SQ1 / SQ2---------------*/



Blockly.Blocks['set_frequency'] = {
  init: function() {
    this.appendValueInput("FREQUENCY")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SET FREQUENCY")
        .appendField(new Blockly.FieldDropdown([["WG","WG"], ["SQ1","SQ1"], ["SQ2","SQ2"]]), "CHANNEL");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Set FREQUENCY of WG/SQ1/SQ2");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_frequency'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_frequency = Blockly.JavaScript.valueToCode(block, 'FREQUENCY', Blockly.JavaScript.ORDER_NONE);
  //var code = 'set_frequency(\''+dropdown_channel+'\',' + value_frequency+  ');\n';

  if(dropdown_channel === "WG")
	var code = 'set_sine('+value_frequency+')\n';
  else if(dropdown_channel === "SQ1")
	var code = 'set_sqr1('+value_frequency+',50)\n';
  else if(dropdown_channel === "SQ2")
	var code = 'set_sqr2('+value_frequency+',50)\n';


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

/*------- select sine amplitude ---*/

Blockly.Blocks['select_sine_amp'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Sine(WG) Amplitude ")
        .appendField(new Blockly.FieldDropdown([["3V","2"], ["1V","1"], ["80mV","0"]]), "RANGE");
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
  var code = 'set_sine_amp(' + range+  ');\n';
  return code;
};


Blockly.Python['select_sine_amp'] = function(block) {
  var range = block.getFieldValue('RANGE');
  var code = 'p.set_sine_amp(' + range+  ')\n';
  return code;
};




/*------- GET FREQUENCY -----------*/


Blockly.Blocks['get_freq'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Read Frequency")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.surprise,'SS'))
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"]]), "CHANNEL");
    this.appendDummyInput()
        .appendField("Timeout:")
        .appendField(new Blockly.FieldDropdown([["0.1","0.1"], ["1","1"], ["2","2"], ["4","4"], ["10","10"]]), "TIMEOUT");
    this.setInputsInline(false);
    this.setOutput(true, "Number");
    this.setColour(230);
 this.setTooltip("Get FREQUENCY from IN2/SEN");
 this.setHelpUrl("");
  },
    surprise: function() {
		alert('Read frequency from the IN2/SEN inputs!');
	},
	collapse: function(){
		this.getSourceBlock().setCollapsed(true);
	}

};


Blockly.JavaScript['get_freq'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_timeout = block.getFieldValue('TIMEOUT');
  var code = "get_freq('"+dropdown_channel+"',"+dropdown_timeout+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_freq'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_timeout = block.getFieldValue('TIMEOUT');
  var code = "p.get_freq('"+dropdown_channel+"',"+dropdown_timeout+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};


/*------- multi_r2r -----------*/



Blockly.Blocks['multi_r2r'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Rising Edge Timer")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.collapse,'SS'))
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"]]), "CHANNEL");
    this.appendDummyInput()
        .appendField("Edges:")
        .appendField(new Blockly.FieldDropdown([["2","2"], ["3","3"], ["4","4"], ["8","8"], ["12","12"], ["16","16"], ["32","32"], ["48","48"]]), "EDGES")
        .appendField("Timeout:")
        .appendField(new Blockly.FieldDropdown([["1","1"], ["2","2"], ["3","3"], ["5","5"], ["5","5"]]), "TIMEOUT");
    this.setInputsInline(false);
    this.setOutput(true, "Number");
    this.setColour(230);
 this.setTooltip("Measure time between multiple rising edges from IN2/SEN");
 this.setHelpUrl("");
  },

};


Blockly.JavaScript['multi_r2r'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_edges = block.getFieldValue('EDGES');
  var dropdown_timeout = block.getFieldValue('TIMEOUT');
  var code = 'multi_r2r(\''+dropdown_channel+'\','+dropdown_edges+','+dropdown_timeout+')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['multi_r2r'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_edges = block.getFieldValue('EDGES');
  var dropdown_timeout = block.getFieldValue('TIMEOUT');
  var code = 'p.multi_r2rtime(\''+dropdown_channel+'\','+dropdown_edges+','+dropdown_timeout+')';
  return [code,Blockly.Python.ORDER_NONE];
};

Blockly.Blocks['singlePinEdges'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Digital Timer")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.collapse,'SS'))
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"]]), "CHANNEL")
        .appendField(new Blockly.FieldDropdown([["rising","rising"], ["falling","falling"],["4 rising","4xrising"],["16 rising","16xrising"]]), "TYPE");
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
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.collapse,'SS'));
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
        .appendField(new Blockly.FieldDropdown([["A1","A1"], ["A2","A2"], ["A3","A3"], ["SEN","SEN"], ["IN1","IN1"], ["MIC","MIC"]]), "CHANNEL");
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

  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');

  var code = timevar+','+datavar+' = p.capture1(\''+dropdown_channel+'\','+number_samples+','+number_timegap+')\n';
  return code;
};


/*----------Capture routine. Capture 2---------*/

Blockly.Blocks['capture2'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Capture 2, ")
        .appendField(new Blockly.FieldDropdown([["Chan 1: A1","A1"], ["Chan 1: A2","A2"], ["Chan 1: A3","A3"], ["Chan 1: SEN","SEN"], ["Chan 1: IN1","IN1"], ["Chan 1: MIC","MIC"]]), "CHANNEL")
        .appendField("Chan 2: A2");
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

  var code = "var jsondata = capture2('"+dropdown_channel+"',"+number_samples+","+number_timegap+");\ntmpjson=JSON.parse(jsondata);"+timevar+"=tmpjson[0];"+datavar1+"=tmpjson[1];"+datavar2+"=tmpjson[2];\n";
  return code;
};

Blockly.Python['capture2'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');

  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar1 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');
  var datavar2 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA2'), 'VARIABLE');

  var code = timevar+','+datavar1+','+datavar2+'  = p.capture2('+number_samples+','+number_timegap+',\''+dropdown_channel+'\')\n';
  return code;
};

/*----------Capture routine. Capture 4---------*/

Blockly.Blocks['capture4'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Capture 4 |")
        .appendField(new Blockly.FieldDropdown([["Chan 1: A1","A1"], ["Chan 1: A2","A2"], ["Chan 1: A3","A3"], ["Chan 1: SEN","SEN"], ["Chan 1: IN1","IN1"], ["Chan 1: MIC","MIC"]]), "CHANNEL")
        .appendField(", Chan 2: A2");
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

  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar1 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');
  var datavar2 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA2'), 'VARIABLE');
  var datavar3 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA3'), 'VARIABLE');
  var datavar4 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA4'), 'VARIABLE');

  var code = timevar+','+datavar1+','+datavar2+','+datavar2+','+datavar2+'  = p.capture4('+number_samples+','+number_timegap+',\''+dropdown_channel+'\')\n';
  return code;
};


/*---------------TRIGGER -----------------*/



Blockly.Blocks['scope_trigger'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Oscilloscope Trigger")
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
  var code = 'configure_trigger('+dropdown_channel+',\'A1\',' + level +');\n';
  return code;
};


Blockly.Python['scope_trigger'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var level = block.getFieldValue('LEVEL');
  var state = block.getFieldValue('STATE');
  var code = 'p.configure_trigger('+dropdown_channel+',\'A1\',' + level +')\n';

  return code;
};

/*-------------- CAPTURE PLOT ------------------*/

Blockly.Blocks['capture_plot'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Capture And Plot")
        .appendField(new Blockly.FieldDropdown([["Chan 1: A1","A1"], ["Chan 1: A2","A2"], ["Chan 1: A3","A3"], ["Chan 1: SEN","SEN"], ["Chan 1: IN1","IN1"], ["Chan 1: MIC","MIC"]]), "CHANNEL");
    this.appendDummyInput()
        .appendField("Chan 2: A2")
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
  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar1 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');
  var datavar2 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA2'), 'VARIABLE');

  var code = "configure_trigger(0,'" + dropdown_channel+ "',0);\n";
  code += "var jsondata = capture2('"+dropdown_channel+"',400,5);\nvar tmpjson=JSON.parse(jsondata);"+timevar+"=tmpjson[0];"+datavar1+"=tmpjson[1];"+datavar2+"=tmpjson[2];\n";
  code += 'sleep(0.01);\n'+'plot_xyyarray('+timevar+','+datavar1+','+datavar2+');\n';
  return code;
};

Blockly.Python['capture_plot'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('TIMESTAMPS'), 'VARIABLE');
  var datavar1 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA1'), 'VARIABLE');
  var datavar2 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('DATA2'), 'VARIABLE');

  var code = "p.configure_trigger(0,'" + dropdown_channel+ "',0)\n";
  code = timevar+', '+datavar1+', '+datavar2+ " = p.capture2('"+dropdown_channel+"',400,5)\n";
  code += 'sleep(0.001);\n'+'plot_xyyarray('+timevar+','+datavar1+','+datavar2+')\n';
  return code;
};


/*---------- CAPTURE ACTION --------*/



Blockly.Blocks['capture_action_plot'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Set OD1 ")
        .appendField(new Blockly.FieldDropdown([["ON(5V)","HIGH"], ["OFF","LOW"]]), "ACTION")
        .appendField(", Capture")
        .appendField(new Blockly.FieldDropdown([["A1","A1"], ["A2","A2"], ["A3","A3"], ["SEN","SEN"], ["IN1","IN1"], ["MIC","MIC"]]), "CHANNEL");
    this.appendDummyInput()
        .appendField("SAMPLES:")
        .appendField(new Blockly.FieldNumber(0, 10, 5000, 1), "SAMPLES")
        .appendField(" TIMEGAP(uS):")
        .appendField(new Blockly.FieldNumber(0, 1, 2000, 1), "TIMEGAP");
    this.appendDummyInput()
        .appendField("Plot :")
        .appendField(new Blockly.FieldVariable("timestamps"), "TIMESTAMPS")
        .appendField(new Blockly.FieldVariable("data1", null, ['Number','String'], 'Number'), "DATA1");
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
  var code = "var jsondata = capture_action('"+dropdown_channel+"',"+number_samples+","+number_timegap+",'"+action+"');\ntmpjson = JSON.parse(jsondata);"+timevar+"=tmpjson[0];"+datavar+"=tmpjson[1];\n";
  code += 'sleep(0.01);\n'+'plot_xyarray('+timevar+','+datavar+');\n';
  return code;
};

Blockly.Python['capture_action_plot'] = function(block) {
  var action = block.getFieldValue('ACTION');
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var code = 'timestamps,data1 = capture_action(\''+dropdown_channel+'\','+number_samples+','+number_timegap+',\''+action+'\')\n';
  code += 'sleep(0.01);\n'+'plot_xyarray(timestamps,data1);\n';
  return code;
};



/*-------GENERIC 2 input timing calls----_*/

Blockly.Blocks['measure_timing'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Measure Timing")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.collapse,'SS'))
        .appendField(new Blockly.FieldDropdown([["Rise to Rise","r2r"], ["Fall to Fall","f2f"], ["Rise to Fall","r2f"], ["Fall to Rise","f2r"]]), "COMMAND")
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"],["SQR1_READ","SQR1_READ"],["OD1_READ","OD1_READ"]]), "CHANNEL1")
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"],["SQR1_READ","SQR1_READ"],["OD1_READ","OD1_READ"]]), "CHANNEL2")
        .appendField("Timeout(S):")
        .appendField(new Blockly.FieldDropdown([["1","1"], ["2","2"], ["3","3"], ["5","5"], ["5","5"]]), "TIMEOUT");
    this.setInputsInline(false);
    this.setOutput(true, "Number");
    this.setColour(230);
 this.setTooltip("Measure time between multiple rising edges from IN2/SEN");
 this.setHelpUrl("");
  },

};


Blockly.JavaScript['measure_timing'] = function(block) {
  var cmd = block.getFieldValue('COMMAND');
  var src = block.getFieldValue('CHANNEL1');
  var dst = block.getFieldValue('CHANNEL2');
  var tmt = block.getFieldValue('TIMEOUT');
  var code = "measure_timing('"+cmd+"','"+src+"','"+dst+"',"+tmt+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['measure_timing'] = function(block) {
  var cmd = block.getFieldValue('COMMAND');
  var src = block.getFieldValue('CHANNEL1');
  var dst = block.getFieldValue('CHANNEL2');
  var tmt = block.getFieldValue('TIMEOUT');
  var code = "p.DoublePinEdges('"+cmd+"','"+src+"','"+dst+"',"+tmt+")";
  return [code,Blockly.Python.ORDER_NONE];
};




Blockly.Blocks['action_timing'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Action Timing")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.collapse,'SS'))
        .appendField(new Blockly.FieldDropdown([["Set to Rise","s2r"], ["Set to Fall","s2f"], ["Clear to Fall","c2f"], ["Clear to Rise","c2r"]]), "COMMAND")
        .appendField(new Blockly.FieldDropdown([["OD1","OD1"], ["SQR1","SQR1"],["SQR2","SQR2"],["CCS","CCS"]]), "CHANNEL1")
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"],["SQR1_READ","SQR1_READ"],["OD1_READ","OD1_READ"]]), "CHANNEL2")
        .appendField("Timeout(S):")
        .appendField(new Blockly.FieldDropdown([["1","1"], ["2","2"], ["3","3"], ["5","5"], ["5","5"]]), "TIMEOUT");
    this.setInputsInline(false);
    this.setOutput(true, "Number");
    this.setColour(230);
 this.setTooltip("Measure time between setting/clearing an output and an edge on a digital input");
 this.setHelpUrl("");
  },

};


Blockly.JavaScript['action_timing'] = function(block) {
  var cmd = block.getFieldValue('COMMAND');
  var src = block.getFieldValue('CHANNEL1');
  var dst = block.getFieldValue('CHANNEL2');
  var tmt = block.getFieldValue('TIMEOUT');
  var code = "action_timing('"+cmd+"','"+src+"','"+dst+"',"+tmt+")";
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['action_timing'] = function(block) {
  var cmd = block.getFieldValue('COMMAND');
  var src = block.getFieldValue('CHANNEL1');
  var dst = block.getFieldValue('CHANNEL2');
  var tmt = block.getFieldValue('TIMEOUT');
  up = ['s2r','c2r'];
  if(up.indexOf(cmd)>-1){edge = 'rising';}
  else {edge = 'falling';}

  var code = "p.SinglePinEdges('"+dst+"','"+edge+"',1,"+tmt+","+src+"=1)";
  if(cmd[0] == 'c')
	code = "p.SinglePinEdges('"+dst+"','"+edge+"',1,"+tmt+","+src+"=0)";
  
  return [code,Blockly.Python.ORDER_NONE];
};



/*---------- Get Sensor --------------*/


Blockly.Blocks['scanI2C'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Scan I2C port, and get a")
    this.appendDummyInput()
        .appendField("list of detected sensors")
    this.setColour(330);
    this.setOutput(true, null);
    this.setTooltip("Scan I2C");
    this.setHelpUrl("");
  },

};


Blockly.JavaScript['scanI2C'] = function(block) {
  var code = 'JSON.parse(scanI2C())';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['scanI2C'] = function(block) {
  var code = 'p.I2C.scan()';
  return [code,Blockly.Python.ORDER_NONE];
};




Blockly.Blocks['scanI2CString'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Scan I2C port, and get detected")
    this.appendDummyInput()
        .appendField("sensors in a comma separated string")
    this.setColour(330);
    this.setOutput(true, null);
    this.setTooltip("Scan I2C");
    this.setHelpUrl("");
  },

};


Blockly.JavaScript['scanI2CString'] = function(block) {
  var code = 'scanI2CString()';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['scanI2CString'] = function(block) {
  var code = 'str(p.I2C.scan())';
  return [code,Blockly.Python.ORDER_NONE];
};



Blockly.Blocks['read_I2C_sensor'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read I2C Sensor:")
        .appendField(new Blockly.FieldDropdown([["BMP280","BMP280"], ["HMC5883L","HMC5883L"], ["TSL2561","TSL2561"], ["QMC5883L","QMC5883L"], ["MPU6050","MPU6050"],["MAX30100","MAX30100"],["VL53L0X","VL53L0X"]]), "NAME");
    this.appendDummyInput()
        .appendField("Address:")
        .appendField(new Blockly.FieldNumber(13, 1, 127, 1), "ADDR");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_I2C_sensor'] = function(block) {
  var name = block.getFieldValue('NAME');
  var addr = block.getFieldValue('ADDR');
  var code = 'JSON.parse(get_generic_sensor(\''+name+'\','+addr+'))';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_I2C_sensor'] = function(block) {
  var name = block.getFieldValue('NAME');
  var addr = block.getFieldValue('ADDR');
  var code = 'p.get_generic_sensor(\''+name+'\','+addr+')';
  return [code, Blockly.Python.ORDER_NONE];
};



//----------------SR04_distance

Blockly.Blocks['read_SR04'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read SR04 Distance(cm)");
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


//---------BMP280

Blockly.Blocks['read_BMP280'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read BMP280")
        .appendField(new Blockly.FieldDropdown([["TEMPERATURE","0"], ["PRESSURE","1"], ["HUMIDITY","2"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/BMP280.png", 30, 30, { alt: "*", flipRtl: "FALSE" }));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_BMP280'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'BMP280\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_BMP280'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.get_sensor(\'BMP280\','+dropdown_channel+')';
  return [code, Blockly.Python.ORDER_NONE];
};


//---------MAX30100

Blockly.Blocks['read_MAX30100'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read MAX30100")
        .appendField(new Blockly.FieldDropdown([["RED LED","0"], ["IR LED","1"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/pulse.png", 30, 30, { alt: "*", flipRtl: "FALSE" }));
    this.appendDummyInput()
        .appendField("Heart Rate");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_MAX30100'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MAX30100\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_MAX30100'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.get_sensor(\'MAX30100\','+dropdown_channel+')';
  return [code, Blockly.Python.ORDER_NONE];
};

//MAX6675

Blockly.Blocks['read_MAX6675'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read Temperature from")
        .appendField(new Blockly.FieldImage("media/THERMOMETER.png", 30, 30));
    this.appendDummyInput()
        .appendField("MAX6675 Module on")
        .appendField(new Blockly.FieldDropdown([["CS1","1"], ["CS2","2"], ["CS3","3"], ["CS4","4"]]), "CHANNEL")
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_MAX6675'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'MAX6675('+dropdown_channel+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_MAX6675'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'p.get_sensor(\'MAX6675\','+dropdown_channel+')';
  return [code, Blockly.Python.ORDER_NONE];
};


//---------TSL2561

Blockly.Blocks['read_TSL2561'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read TSL2561(lum)")
        .appendField(new Blockly.FieldDropdown([["LUMINOSITY(total)","0"], ["Infrared","1"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_TSL2561'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'TSL2561\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_TSL2561'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.get_sensor(\'TSL2561\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

//----------------HMC5883L

Blockly.Blocks['read_QMC5883L'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read QMC5883L")
        .appendField(new Blockly.FieldImage("media/MAGNETOMETER.png", 20, 20, { alt: "*", flipRtl: "FALSE" }))
        .appendField(new Blockly.FieldDropdown([["Hx","0"], ["Hy","1"], ["Hz","2"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_QMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'QMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_QMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.get_sensor(\'QMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

// AD9833 Sine Wave generator module

Blockly.Blocks['set_AD9833'] = {
  init: function() {
    this.appendValueInput("FREQ")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Set AD9833  ")
        .appendField(new Blockly.FieldDropdown([["CS1","1"], ["CS2","2"]]), "CHANNEL")
        .appendField("Frequency ");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Set dual AD9833 module frequency");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_AD9833'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var freq = Blockly.JavaScript.valueToCode(block, 'FREQ', Blockly.JavaScript.ORDER_NONE);
  var code = 'set_dual_AD9833('+dropdown_channel+',' + freq+  ');\n';
  return code;
};


Blockly.Python['set_AD9833'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var freq = Blockly.JavaScript.valueToCode(block, 'FREQ', Blockly.Python.ORDER_NONE);
  var code = 'p.set_dual_AD9833('+dropdown_channel+',' + freq+  ')\n';

  return code;
};



//----------------MPU6050

Blockly.Blocks['read_MPU6050'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read MPU6050")
        .appendField(new Blockly.FieldDropdown([["Ax","0"], ["Ay","1"], ["Az","2"], ["Gx","4"], ["Gy","5"], ["Gz","6"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/MPU6050.png", 20, 20, { alt: "*", flipRtl: "FALSE" }));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_MPU6050'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MPU6050\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_MPU6050'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.get_sensor(\'MPU6050\','+dropdown_channel+')';
  return [code, Blockly.Python.ORDER_NONE];
};

//----------------VL53L0X

Blockly.Blocks['read_VL53L0X'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read VL53L0X")
        .appendField(new Blockly.FieldDropdown([["Distance(mm)","0"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_VL53L0X'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'VL53L0X\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_VL53L0X'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.get_sensor(\'VL53L0X\','+dropdown_channel+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

//----------------ML8511

Blockly.Blocks['read_ML8511'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read ML8511")
        .appendField(new Blockly.FieldDropdown([["UV Light mW/cm^2","0"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_ML8511'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'ML8511\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_ML8511'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.get_sensor(\'ML8511\','+dropdown_channel+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

//----------------VOLTS

Blockly.Blocks['read_VOLTS'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read VOLTS")
        .appendField(new Blockly.FieldDropdown([["A1","0"],["A2","1"],["A3","2"],["SEN","3"],["IN1","4"],["CCS","5"]]), "CHANNEL");
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
  var code = 'p.get_voltage(\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


//----------------HMC5883L

Blockly.Blocks['read_HMC5883L'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read HMC5883L")
        .appendField(new Blockly.FieldImage("media/MAGNETOMETER.png", 20, 20, { alt: "*", flipRtl: "FALSE" }))
        .appendField(new Blockly.FieldDropdown([["Hx","0"], ["Hy","1"], ["Hz","2"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_HMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'HMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_HMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.get_sensor(\'HMC5883L\','+dropdown_channel+')';
  return [code, Blockly.Python.ORDER_NONE];
};






/*-------------------- SET STATE inline --------------*/


Blockly.Blocks['set_state'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Turn")
        .appendField(new Blockly.FieldDropdown([["OD1","OD1"], ["SQ1","SQ1"], ["SQ2","SQ2"]]), "CHANNEL")
        .appendField(new Blockly.FieldDropdown([["ON","ON"], ["OFF","OFF"]]), "STATE");
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
  block.setColour('#0ec244');//Make block green
  var state = true;
  if(dropdown_state === 'OFF' )state = false; 
  var code = 'set_state(\''+dropdown_channel+'\',' + state+  ');\n';
  return code;
};

Blockly.Python['set_state'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_state = block.getFieldValue('STATE');
  // TODO: Assemble Python into code variable.
  var state = 'true';
  if(dropdown_state === 'OFF' ) state = "false"; 
  var code = 'p.set_state(\''+dropdown_channel+'\',' + state+  ')';
  return code;
};



/*---------------------- SET PCA9685 for Servo Motors---------------*/


Blockly.Blocks['set_PCA9685'] = {
  init: function() {
    this.appendValueInput("ANGLE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SERVO(PCA9685) ")
        .appendField(new Blockly.FieldDropdown([["1 Angle","1"], ["2 Angle","2"], ["3 Angle","3"], ["4 Angle","4"], ["5 Angle","5"], ["6 Angle","6"]]), "CHANNEL");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Set Angle on servo motor via PCA9685 module");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_PCA9685'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_angle = Blockly.JavaScript.valueToCode(block, 'ANGLE', Blockly.JavaScript.ORDER_NONE);
  var code = 'set_PCA9685(\''+dropdown_channel+'\',' + value_angle+  ');\n';
  return code;
};


Blockly.Python['set_PCA9685'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_angle = Blockly.JavaScript.valueToCode(block, 'ANGLE', Blockly.Python.ORDER_NONE);
  var code = 'set_PCA9685(\''+dropdown_channel+'\',' + value_angle+  ')\n';

  return code;
};


/*---------------------- SET SQ1/SQ2 for Servo Motors---------------*/


Blockly.Blocks['set_servo'] = {
  init: function() {
    this.appendValueInput("ANGLE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SERVO ")
        .appendField(new Blockly.FieldDropdown([["SQ1 Angle","SQ1"], ["SQ2 Angle","SQ2"]]), "CHANNEL");
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

  if(dropdown_channel === "SQ1")
	var code = 'dc=9.8*'+value_angle+'/180+3.7\np.set_sqr1(50,dc)\n';
  else if(dropdown_channel === "SQ2")
	var code = 'dc=9.8*'+value_angle+'/180+3.7\np.set_sqr2(50,dc)\n';

  return code;
};


/*--------------- EVENT DRIVEN CALLS -------------*/


/*---timer----*/
Blockly.Blocks['cs_start_timer'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("CREATE TIMER")
        .appendField(new Blockly.FieldImage("media/clock.svg", 25, 25,  "*"));
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Create Timer");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['cs_start_timer'] = function(block) {
  var code = 'var mytimer = new Date();\n';
  return code;
};

Blockly.Python['cs_start_timer'] = function(block) {
  var txt = Blockly.Python.valueToCode(block, 'TEXT', Blockly.Python.ORDER_NONE);
  var code = 'mytimer = time.time()\n';
  return code;
};

Blockly.Blocks['cs_get_timer'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("READ TIMER(mS)")
        .appendField(new Blockly.FieldImage("media/clock.svg", 25, 25,  "*"));
    this.setOutput(true, "Number");
    this.setColour(230);
 this.setTooltip("Create Timer");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['cs_get_timer'] = function(block) {
  var code = 'new Date()-mytimer';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['cs_get_timer'] = function(block) {
  var code = 'time.time()-mytimer';
  return [code, Blockly.Python.ORDER_NONE];
};

/*--------------- EVENT DRIVEN CALLS -------------*/
Blockly.Blocks['generic_slider'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("New Slider")
        .appendField(new Blockly.FieldTextInput("myvar"), "NAME");
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
        .appendField(new Blockly.FieldTextInput("myvar"), "NAME");

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


Blockly.Blocks['set_frequency_slider'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("FREQUENCY Slider")
        .appendField(new Blockly.FieldDropdown([["WG","WG"], ["SQ1","SQ1"], ["SQ2","SQ2"]]), "CHANNEL");
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
  var code = 'add_slider(\''+dropdown_channel+'\');\n';
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
        .appendField(new Blockly.FieldDropdown([["PV1","PV1"], ["PV2","PV2"]]), "CHANNEL");
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
  var code = 'add_slider(\''+dropdown_channel+'\');\n';
  return code;
};


Blockly.Python['set_voltage_slider'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = '# Add Event driven slider to adjust voltage of '+dropdown_channel+' \n';
  return code;
};

oninput = function(oninputsuffix,label) {
if(typeof oninputsuffix != 'undefined'){
	return ` oninput="this.nextElementSibling.value = '${label} ' + this.value + ' ${oninputsuffix}' " `
	}
else{ return ''; }
}



sldr = (label,opts,oninputsuffix) => `
	<div class = "ui row">
		<input type="range" ${opts} class="compactslider" widget="${label}" style="width:70%" ${ oninput(oninputsuffix,label) } >
		<output>${label}</output>
	</div>
`

function addSlider(value){
    var opts = ''
    if(value === 'WG' || value === 'SQ1' || value === 'SQ2'){
        if(value === 'WG')opts = " min=\"4\" max=\"5000\" ";
        else if(value === 'SQ1' || value === 'SQ2')opts = " min=\"4\" max=\"10000\" ";
        var sld = sldr(value,opts,' Hz')
        results.append(sld);
        //mygrid.transition('show');
        results.find('.compactslider').on("input",function(){
                if(typeof HWBridge != 'undefined')
                    HWBridge.set_frequency($(this).attr("widget"), this.value);

            });
    }else if(value === 'PV1' || value === 'PV2'){
        if(value === 'PV1')opts = " min=\"-5\" max=\"5\"  step=\"0.1\" ";
        else if(value === 'PV2')opts = " min=\"-3\" max=\"3\"  step=\"0.1\" ";

        var sld = sldr(value,opts,' V')
        results.append(sld);
        //mygrid.transition('show');
        results.find('.compactslider').on("input",function(){
                if(typeof HWBridge != 'undefined')
                    HWBridge.set_voltage($(this).attr("widget"), this.value);

            });
    }


}





Blockly.JavaScript.addReservedWords('set_frequency');
Blockly.JavaScript.addReservedWords('get_freq');
Blockly.JavaScript.addReservedWords('set_state');
Blockly.JavaScript.addReservedWords('multi_r2r');
Blockly.JavaScript.addReservedWords('measure_timing');
  Blockly.JavaScript.addReservedWords('capture_analysis');
  Blockly.JavaScript.addReservedWords('capture_analysis_dual');
  Blockly.JavaScript.addReservedWords('get_voltage');
  Blockly.JavaScript.addReservedWords('set_voltage');
  Blockly.JavaScript.addReservedWords('capture1');
  Blockly.JavaScript.addReservedWords('capture2');
  Blockly.JavaScript.addReservedWords('configure_trigger');


//-------------------- API ------------------------

function initSEELab(interpreter, scope) {





		  // Add an API for the get_voltage call
		  interpreter.setProperty(scope, 'get_voltage', interpreter.createAsyncFunction(
				function(channel, callback) {
				  return HWBridge.get_voltage(channel, callback);
				})
			);


		  // Add an API for the set_voltage call
		  interpreter.setProperty(scope, 'set_voltage', interpreter.createAsyncFunction(
				function(channel, value, callback) {
				  return HWBridge.set_voltage(channel,value, callback);
				})
			);

		  // Add an API for the capture block.  copied from wait_block. Async attempt
		  var wrapper = function capture1(channel, ns, tg, callback){
				HWBridge.capture1(channel , ns ,tg, callback);
		  };
		  interpreter.setProperty(scope, 'capture1', interpreter.createAsyncFunction(wrapper));

		  // Add an API for the capture block.  copied from wait_block. Async attempt
		  var wrapper = function capture2(channel, ns, tg, callback) {
			  HWBridge.capture2(channel , ns ,tg, callback);
		  };
		  interpreter.setProperty(scope, 'capture2', interpreter.createAsyncFunction(wrapper));

		  // Add an API for the trigger block.  
		  var wrapper = function configure_trigger(channel, name,level, callback) {
			  return HWBridge.configure_trigger(channel ,name, level,  callback);
		  };
		  interpreter.setProperty(scope, 'configure_trigger', interpreter.createAsyncFunction(wrapper));


		  interpreter.setProperty(scope, 'get_resistance', interpreter.createAsyncFunction(
				function(callback) {
				  return HWBridge.get_resistance(callback);
				})
			);
		  interpreter.setProperty(scope, 'get_capacitance', interpreter.createAsyncFunction(
				function(callback) {
				  return HWBridge.get_capacitance(callback);
				})
			);

		  // Add an API for the select_range call
		  interpreter.setProperty(scope, 'select_range', interpreter.createAsyncFunction(
				function(channel, value, callback) {
				  return HWBridge.select_range(channel,value, callback);
				})
			);

		  // Add an API for the sine_amplitude call
		  interpreter.setProperty(scope, 'set_sine_amp', interpreter.createAsyncFunction(
				function(value, callback) {
				  return HWBridge.set_sine_amp(value, callback);
				})
			);



		  var wrapper = function capture4(channel, ns, tg, callback) {
			  callback(HWBridge.capture4(channel , ns ,tg));
		  };
		  interpreter.setProperty(scope, 'capture4', interpreter.createAsyncFunction(wrapper));






		  // Add an API for the get_freq call
		  interpreter.setProperty(scope, 'get_freq', interpreter.createAsyncFunction(
				function(channel,timeout, callback) {
				  return HWBridge.get_freq(channel, timeout,callback);
				})
			);

		  // Add an API for the set_frequency call
		  interpreter.setProperty(scope, 'set_frequency', interpreter.createAsyncFunction(
				function(channel, value, callback) {
				  return HWBridge.set_frequency(channel,value, callback);
				})
			);


		  // Add an API for the set_frequency call
		  interpreter.setProperty(scope, 'set_sine', interpreter.createAsyncFunction(
				function(value, callback) {
				  return HWBridge.set_sine(value, callback);
				})
			);
		  interpreter.setProperty(scope, 'set_sqr1', interpreter.createAsyncFunction(
				function(value, dc, callback) {
				  return HWBridge.set_sqr1(value,dc,  callback);
				})
			);
		  interpreter.setProperty(scope, 'set_sqr2', interpreter.createAsyncFunction(
				function(value,dc, callback) {
				  return HWBridge.set_sqr2(value,dc, callback);
				})
			);


		  // Add an API for the sine_amplitude call
		  interpreter.setProperty(scope, 'set_sine_amp', interpreter.createAsyncFunction(
				function(value, callback) {
				  return HWBridge.set_sine_amp(value, callback);
				})
			);

		  // Add an API for the set_state call
		  interpreter.setProperty(scope, 'set_state', interpreter.createAsyncFunction(
				function(channel, value, callback) {
				  return HWBridge.set_state(channel,value, callback);
				})
			);



		  // Add an API for the multi_r2r call
		  interpreter.setProperty(scope, 'multi_r2r', interpreter.createAsyncFunction(
				function(channel,edges,timeout, callback) {
				  return HWBridge.multi_r2r(channel,edges,timeout, callback);
				})
			);


		  // Add an API for the measure_timing call
		  interpreter.setProperty(scope, 'measure_timing', interpreter.createAsyncFunction(
				function(cmd, src, dst,timeout, callback) {
				  return HWBridge.DoublePinEdges(cmd,src,dst,timeout, callback);
				})
			);






		  // Add an API for the capture_action block.
		  var wrapper = function capture_action(channel, ns, tg, action, callback) {
                return HWBridge.capture_action(channel , ns ,tg, action,10, callback);
		  };
		  interpreter.setProperty(scope, 'capture_action', interpreter.createAsyncFunction(wrapper));




		  // Add an API for the get_sensor call
		  interpreter.setProperty(scope, 'get_sensor', interpreter.createAsyncFunction(
				function(sensor,param, callback) {
				  return HWBridge.get_sensor(sensor,param, callback);
				})
			);
		  // Add an API for the get_sr04 call
		  interpreter.setProperty(scope, 'get_sr04', interpreter.createNativeFunction(
				function() {
				  return HWBridge.get_sr04();
				})
			);

		  // Add an API for the set_PCA9685 call
		  interpreter.setProperty(scope, 'set_PCA9685', interpreter.createNativeFunction(
				function(channel, value) {
				  return HWBridge.set_PCA9685(channel,value);
				})
			);

		  // Add an API for the set_servo call
		  interpreter.setProperty(scope, 'set_servo', interpreter.createNativeFunction(
				function(channel, value) {
				  return HWBridge.set_servo(channel,value);
				})
			);

		  interpreter.setProperty(scope, 'add_slider', interpreter.createNativeFunction(
				function( value) {
				  return addSlider(value);
				})
			);


	}



