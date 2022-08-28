
/* --------------- Get Voltage ------------ */



Blockly.Blocks['get_voltage'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read Voltage")
        .appendField(new Blockly.FieldDropdown([["A1","A1"], ["A2","A2"], ["A3","A3"]]), "CHANNEL");
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
  var code = 'p.set_voltage(\''+dropdown_channel+'\','+value_voltage+')\n';

  if(dropdown_channel === "PV1")
	var code = 'p.set_pv1('+value_voltage+')\n';
  else if(dropdown_channel === "PV1")
	var code = 'p.set_pv2('+value_voltage+')\n';

  return code;
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
    this.setOutput(true, null);
    this.setColour(150);
 this.setTooltip("Record traces using the  Oscilloscope");
 this.setHelpUrl("");
	}
}

Blockly.JavaScript['capture1'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var code = 'capture1(\''+dropdown_channel+'\','+number_samples+','+number_timegap+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['capture1'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var code = 'capture1(\''+dropdown_channel+'\','+number_samples+','+number_timegap+')';
  return [code, Blockly.Python.ORDER_NONE];
};


/*----------Capture routine. Capture 2---------*/


Blockly.Blocks['capture2'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Capture 2 |")
        .appendField(new Blockly.FieldDropdown([["Chan 1: A1","A1"], ["Chan 1: A2","A2"], ["Chan 1: A3","A3"], ["Chan 1: SEN","SEN"], ["Chan 1: IN1","IN1"], ["Chan 1: MIC","MIC"]]), "CHANNEL");
    this.appendDummyInput()
        .appendField("Chan 2: A2")
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SAMPLES")
        .appendField(new Blockly.FieldNumber(0, 10, 5000, 1), "SAMPLES");
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("TIMEGAP(uS)")
        .appendField(new Blockly.FieldNumber(0, 1, 2000, 1), "TIMEGAP");
    this.setOutput(true, null);
    this.setColour(150);
 this.setTooltip("Record traces using the  Oscilloscope");
 this.setHelpUrl("");
	}
}

Blockly.JavaScript['capture2'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var code = 'capture2(\''+dropdown_channel+'\','+number_samples+','+number_timegap+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['capture2'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var number_samples = block.getFieldValue('SAMPLES');
  var number_timegap = block.getFieldValue('TIMEGAP');
  var code = 'capture2('+number_samples+','+number_timegap+',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

/*---------------TRIGGER -----------------*/



Blockly.Blocks['scope_trigger'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Oscilloscope Trigger")
        .appendField(new Blockly.FieldCheckbox("TRUE"), "STATE");
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["Channel 1","0"], ["Channel 2","1"], ["Channel 3","2"], ["Channel 4","3"]]), "CHANNEL")
        .appendField(" Level:")
        .appendField(new Blockly.FieldNumber(512, 0, 1023, 1), "LEVEL");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(210);
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
  var code = 'scope_trigger(' + dropdown_channel+ ',' + (1023-level)+ ','+ state + ');\n';
  return code;
};


Blockly.Python['scope_trigger'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var level = block.getFieldValue('LEVEL');
  var state = block.getFieldValue('STATE');
  var code = 'scope_trigger('+dropdown_channel+',' + level+ ','+state +')\n';

  return code;
};




/*---------------------- Analyse Captured Data ---------------*/

Blockly.Blocks['capture_analysis'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Sine Fit Capture1 Data");
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["Amplitude","0"], ["Frequency","1"], ["Phase (Deg)","2"]]), "PARAMETER");
    this.setOutput(true, null);
    this.setColour(210);
 this.setTooltip("Analyse Captured Data");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['capture_analysis'] = function(block) {
  var dropdown_parameter = block.getFieldValue('PARAMETER');
  var code = 'capture_analysis('+dropdown_parameter+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['capture_analysis'] = function(block) {
  var dropdown_parameter = block.getFieldValue('PARAMETER');
  var code = 'capture_analysis('+dropdown_parameter+')';
  return [code, Blockly.Python.ORDER_NONE];
};



Blockly.Blocks['capture_analysis_dual'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Sine Fit Capture2 Data");
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["Amplitude Ratio","0"], ["Frequency Ratio","1"], ["Phase Difference (Deg)","2"]]), "PARAMETER");
    this.setOutput(true, null);
    this.setColour(210);
 this.setTooltip("Analyse Captured Data");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['capture_analysis_dual'] = function(block) {
  var dropdown_parameter = block.getFieldValue('PARAMETER');
  var code = 'capture_analysis_dual('+dropdown_parameter+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['capture_analysis_dual'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_parameter = block.getFieldValue('PARAMETER');
  var code = 'capture_analysis_dual('+dropdown_parameter+')';
  return [code, Blockly.Python.ORDER_NONE];
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
  var code = 'get_sensor(\'VOLTS\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_VOLTS'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'p.get_voltage(\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


  Blockly.JavaScript.addReservedWords('capture_analysis');
  Blockly.JavaScript.addReservedWords('capture_analysis_dual');
  Blockly.JavaScript.addReservedWords('get_voltage');
  Blockly.JavaScript.addReservedWords('set_voltage');
  Blockly.JavaScript.addReservedWords('capture1');
  Blockly.JavaScript.addReservedWords('capture2');
  Blockly.JavaScript.addReservedWords('scope_trigger');
  
//-------------------- API ------------------------

function initAnalog(interpreter, scope) {

		  // Add APIs for the sine fit analysis calls
		  interpreter.setProperty(scope, 'capture_analysis', interpreter.createNativeFunction(
				function(param) {
				  return MyJavascriptInterface.capture_analysis(param);
				})
			);

		  // Add APIs for the sine fit analysis calls
		  interpreter.setProperty(scope, 'capture_analysis_dual', interpreter.createNativeFunction(
				function(param) {
				  return MyJavascriptInterface.capture_analysis_dual(param);
				})
			);


		  // Add an API for the get_voltage call
		  interpreter.setProperty(scope, 'get_voltage', interpreter.createAsyncFunction(
				function(channel, callback) {
				  return MyJavascriptInterface.get_voltage(channel, callback);
				})
			);


		  // Add an API for the set_voltage call
		  interpreter.setProperty(scope, 'set_voltage', interpreter.createAsyncFunction(
				function(channel, value, callback) {
				  return MyJavascriptInterface.set_voltage(channel,value, callback);
				})
			);

		  // Add an API for the capture block.  copied from wait_block. Async attempt
		  var wrapper = function capture1(channel, ns, tg, callback) {
			  MyJavascriptInterface.capture1(channel , ns ,tg, callback);
		  };
		  interpreter.setProperty(scope, 'capture1', interpreter.createAsyncFunction(wrapper));

		  // Add an API for the capture block.  copied from wait_block. Async attempt
		  var wrapper = function capture2(channel, ns, tg, callback) {
			  MyJavascriptInterface.capture2(channel , ns ,tg, callback);
		  };
		  interpreter.setProperty(scope, 'capture2', interpreter.createAsyncFunction(wrapper));

		  // Add an API for the trigger block.  
		  var wrapper = function scope_trigger(channel, level, state, callback) {
			  return MyJavascriptInterface.scope_trigger(channel ,level, state, callback);
		  };
		  interpreter.setProperty(scope, 'scope_trigger', interpreter.createAsyncFunction(wrapper));


	}







