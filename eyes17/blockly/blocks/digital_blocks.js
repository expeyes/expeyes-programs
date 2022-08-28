
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
        .appendField("Read Frequency")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.surprise,'SS'))
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"]]), "CHANNEL");
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
  var code = 'p.multi_r2r(\''+dropdown_channel+'\','+dropdown_edges+','+dropdown_timeout+')';
  return [code,Blockly.Python.ORDER_NONE];
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
  if(dropdown_state === 'OFF' )
	  state = false; 
  var code = 'set_state(\''+dropdown_channel+'\',' + state+  ')';
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

Blockly.JavaScript.addReservedWords('set_frequency');
Blockly.JavaScript.addReservedWords('get_frequency');
Blockly.JavaScript.addReservedWords('set_state');
Blockly.JavaScript.addReservedWords('multi_r2r');


function initDigital(interpreter, scope) {

		  // Add an API for the get_frequency call
		  interpreter.setProperty(scope, 'get_frequency', interpreter.createAsyncFunction(
				function(channel, callback) {
				  return MyJavascriptInterface.get_frequency(channel, callback);
				})
			);

		  // Add an API for the set_frequency call
		  interpreter.setProperty(scope, 'set_frequency', interpreter.createAsyncFunction(
				function(channel, value, callback) {
				  return MyJavascriptInterface.set_frequency(channel,value, callback);
				})
			);

		  // Add an API for the set_state call
		  interpreter.setProperty(scope, 'set_state', interpreter.createAsyncFunction(
				function(channel, value, callback) {
				  return MyJavascriptInterface.set_state(channel,value, callback);
				})
			);



		  // Add an API for the multi_r2r call
		  interpreter.setProperty(scope, 'multi_r2r', interpreter.createAsyncFunction(
				function(channel,edges,timeout, callback) {
				  return MyJavascriptInterface.multi_r2r(channel,edges,timeout, callback);
				})
			);




}
