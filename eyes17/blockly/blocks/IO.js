
/*---print statememt----*/
Blockly.Blocks['cs_print'] = {
  init: function() {
    this.appendValueInput("TEXT")
        .setCheck(null)
        .appendField("Print");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Print to screen");
 this.setHelpUrl("");
  }
};



Blockly.JavaScript['cs_print'] = function(block) {
  var txt = Blockly.JavaScript.valueToCode(block, 'TEXT', Blockly.JavaScript.ORDER_NONE);
  var code = 'print('+txt+');\n';
  return code;
};


Blockly.Python['cs_print'] = function(block) {
  var txt = Blockly.Python.valueToCode(block, 'TEXT', Blockly.Python.ORDER_NONE);
  var code = 'print('+txt+')\n';
  return code;
};


/*------ Fixed label in Registers area -----*/

/*---print statememt----*/
Blockly.Blocks['cs_sticker'] = {
  init: function() {
    this.appendValueInput("LABEL")
        .setCheck(null)
        .appendField("Label:");
    this.appendValueInput("TEXT")
        .setCheck(null)
        .appendField("Print:");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Print to screen");
 this.setHelpUrl("");
  }
};



Blockly.JavaScript['cs_sticker'] = function(block) {
  var label = Blockly.JavaScript.valueToCode(block, 'LABEL', Blockly.JavaScript.ORDER_NONE);
  var txt = Blockly.JavaScript.valueToCode(block, 'TEXT', Blockly.JavaScript.ORDER_NONE);
  var code = 'sticker('+label+','+txt+');\n';
  return code;
};


Blockly.Python['cs_sticker'] = function(block) {
  var label = Blockly.Python.valueToCode(block, 'LABEL', Blockly.Python.ORDER_NONE);
  var txt = Blockly.Python.valueToCode(block, 'TEXT', Blockly.Python.ORDER_NONE);
  var code = 'print('+label+','+txt+')\n';
  return code;
};



//-------------------- API ------------------------

function initIO(interpreter, scope) {

		  // Add an API function for the (alert) print() block.
		  var wrapper = function(text) {
			return results.html(results.html()+text+"<br>");
			//return document.getElementById("resulttext").innerHTML+=text+"<br>";
		  };
		  interpreter.setProperty(scope, 'alert',
			  interpreter.createNativeFunction(wrapper));
		  interpreter.setProperty(scope, 'print',
			  interpreter.createNativeFunction(wrapper));

		  // Add an API function for the sticker() block.
		  var wrapper = function(label, text) {
			return showReg(label, text);
		  };
		  interpreter.setProperty(scope, 'sticker',
			  interpreter.createNativeFunction(wrapper));

		  // Add an API function for the prompt() block.
		  var wrapper = function(text) {
			text = text ? text.toString() : '';
			return interpreter.createPrimitive(prompt(text));
		  };

		  interpreter.setProperty(scope, 'prompt',
			  interpreter.createNativeFunction(wrapper));


	}



