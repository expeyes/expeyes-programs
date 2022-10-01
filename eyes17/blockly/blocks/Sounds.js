
/*---------------------- SET PV1 / PV2---------------*/

Blockly.Blocks['set_phone_frequency'] = {
  init: function() {
    this.appendValueInput("FREQUENCY")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SET PHONE BUZZER");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("Set Frequency from Phone");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_phone_frequency'] = function(block) {
  var value_voltage = Blockly.JavaScript.valueToCode(block, 'FREQUENCY', Blockly.JavaScript.ORDER_NONE);
  var code = 'set_phone_frequency('+value_voltage+');\n';
  return code;
};


Blockly.Python['set_phone_frequency'] = function(block) {
  var value_voltage = Blockly.Python.valueToCode(block, 'FREQUENCY', Blockly.Python.ORDER_NONE);
  var code = 'set_phone_frequency('+value_voltage+')\n';
  return code;
};


Blockly.Blocks['set_phone_frequency_stereo'] = {
  init: function() {
    this.appendValueInput("FREQUENCY1")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PHONE BUZZER (LEFT)");
    this.appendValueInput("FREQUENCY2")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("(RIGHT)");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("Set Frequency from Phone");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_phone_frequency_stereo'] = function(block) {
  var f1 = Blockly.JavaScript.valueToCode(block, 'FREQUENCY1', Blockly.JavaScript.ORDER_NONE);
  var f2 = Blockly.JavaScript.valueToCode(block, 'FREQUENCY2', Blockly.JavaScript.ORDER_NONE);
  var code = 'set_phone_frequency_stereo('+f1+','+f2+')\n';
  return code;
};


Blockly.Python['set_phone_frequency_stereo'] = function(block) {
  var f1 = Blockly.Python.valueToCode(block, 'FREQUENCY1', Blockly.Python.ORDER_NONE);
  var f2 = Blockly.Python.valueToCode(block, 'FREQUENCY2', Blockly.Python.ORDER_NONE);
  var code = 'set_phone_frequency_stereo('+f1+','+f2+')\n';
  return code;
};


Blockly.Blocks['stop_phone_frequency'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("STOP PHONE BUZZER");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("Stop Frequency from Phone");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['stop_phone_frequency'] = function(block) {
  var code = 'stop_phone_frequency();\n';
  return code;
};


Blockly.Python['stop_phone_frequency'] = function(block) {
  var value_voltage = Blockly.Python.valueToCode(block, 'FREQUENCY', Blockly.Python.ORDER_NONE);
  var code = 'stop_phone_frequency()\n';
  return code;
};



function initSounds(interpreter, scope) {
		  // Add an API for the set_voltage call
		  interpreter.setProperty(scope, 'stop_phone_frequency', interpreter.createNativeFunction(
				function() {
				  return JSBridge.stop_phone_frequency();
				})
			);
	  interpreter.setProperty(scope, 'set_phone_frequency', interpreter.createNativeFunction(
				function(val) {
				  return JSBridge.set_phone_frequency(val);
				})
			);

	  interpreter.setProperty(scope, 'set_phone_frequency_stereo', interpreter.createNativeFunction(
				function(val1, val2) {
				  return JSBridge.set_phone_frequency(val1, val2);
				})
			);

	}



