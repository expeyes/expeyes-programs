// ----------DOM MANIPULATION
function makeSVG(tag, attrs) {
            var el= document.createElementNS('http://www.w3.org/2000/svg', tag);
            for (var k in attrs)
                el.setAttribute(k, attrs[k]);
			result = document.createTextNode("-");
			textElements["res"] = result;
			el.appendChild(result);
            return el;
        }



/* --------------- Get Voltage ------------ */



Blockly.Blocks['get_voltage'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read Voltage")
        .appendField(new Blockly.FieldImage("media/transparent.png", 3, 30,  "*"))
        .appendField(new Blockly.FieldDropdown([["A1","A1"], ["A2","A2"], ["A3","A3"]]), "CHANNEL");
    this.setOutput(true, "Number");
    this.setColour(330);

	this.txt= makeSVG('text', {x: 20, y: 35, fill: 'white',text:'0V'});
    this.getSvgRoot().appendChild(this.txt);
    textElements["get_voltage"] = this.txt;

 this.setTooltip("Read Voltage from selected channel");
 this.setHelpUrl("");
  }
};

function  GetVoltageCodeWrapper(dropdown_channel, res){
	console.log(textElements);
	textElements[res].childNodes[0].textContent =  "sada";//v.toFixed(2);
	textElements["res"].textContent = "asdsa";
	v = MyJavascriptInterface.get_voltage(dropdown_channel)+10;
	return v;
}
Blockly.JavaScript['get_voltage'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = "MyJavascriptInterface.get_voltage('"+dropdown_channel+"')";
  //var code = "GetVoltageCodeWrapper('"+dropdown_channel+"','get_voltage')";
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_voltage'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble Python into code variable.
  var code = 'get_voltage(\''+dropdown_channel+'\')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

/*---------------------- SET PV1 / PV2---------------*/

Blockly.Blocks['set_voltage'] = {
  init: function() {
    this.appendValueInput("VOLTAGE")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SET VOLTAGE")
        .appendField(new Blockly.FieldDropdown([["PV1","PV1"], ["PV2","PV2"], ["option","OPTIONNAME"]]), "CHANNEL");
    this.setInputsInline(false);
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("Set Voltage of PV1");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_voltage'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_voltage = Blockly.JavaScript.valueToCode(block, 'VOLTAGE', Blockly.JavaScript.ORDER_NONE);
  //var code = eval(MyJavascriptInterface.set_voltage(dropdown_channel,value_voltage));
  var code = 'MyJavascriptInterface.set_voltage(\''+dropdown_channel+'\','+value_voltage+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['set_voltage'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_voltage = Blockly.Python.valueToCode(block, 'VOLTAGE', Blockly.Python.ORDER_NONE);
  // TODO: Assemble Python into code variable.
  var code = 'set_voltage(\''+dropdown_channel+'\','+value_voltage+')';
  return [code, Blockly.Python.ORDER_NONE];
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
  var value_frequency = Blockly.JavaScript.valueToCode(block, 'FREQUENCY', Blockly.JavaScript.ORDER_ATOMIC);
  var code = 'MyJavascriptInterface.set_frequency(\''+dropdown_channel+'\','+value_frequency+')';
  return code;
};


Blockly.Python['set_frequency'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var value_frequency = Blockly.Python.valueToCode(block, 'FREQUENCY', Blockly.Python.ORDER_NONE);
  if(dropdown_channel === "WG")
	var code = 'set_sine('+value_frequency+')';
  else if(dropdown_channel === "SQ1")
	var code = 'set_sq1('+value_frequency+',50)';
  else if(dropdown_channel === "SQ2")
	var code = 'set_sq2('+value_frequency+',50)';

  return code;
};


/*------- GET FREQUENCY -----------*/



Blockly.Blocks['get_frequency'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Read Frequency")
        .appendField(new Blockly.FieldImage("media/ttl.png", 20, 20,  "*", this.collapse,'SS'))
        .appendField(new Blockly.FieldDropdown([["IN2","IN2"], ["SEN","SEN"]]), "CHANNEL");
    this.setInputsInline(false);
    this.setOutput(true, "Number");
    this.setColour(230);
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
  var code = MyJavascriptInterface.get_frequency(dropdown_channel);
  var code = 'MyJavascriptInterface.get_frequency(\''+dropdown_channel+'\')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_frequency'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_frequency(\''+dropdown_channel+'\')';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

/*---------- Get Sensor --------------*/

//---------BMP280

Blockly.Blocks['read_BMP280'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read BMP280")
        .appendField(new Blockly.FieldDropdown([["TEMPERATURE","0"], ["PRESSURE","1"], ["HUMIDITY","2"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/BMP280.png", 40, 40, { alt: "*", flipRtl: "FALSE" }));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_BMP280'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'MyJavascriptInterface.get_sensor(\'BMP280\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_BMP280'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'BMP280\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
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
  var code = 'MyJavascriptInterface.get_sensor(\'MPU6050\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_MPU6050'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MPU6050\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
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
  var code = 'MyJavascriptInterface.get_sensor(\'VL53L0X\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_VL53L0X'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'VL53L0X\',\''+dropdown_channel+'\')';
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
  var code = 'MyJavascriptInterface.get_sensor(\'ML8511\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_ML8511'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'ML8511\',\''+dropdown_channel+'\')';
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
  var code = 'MyJavascriptInterface.get_sensor(\'VOLTS\',\''+dropdown_channel+'\')';
  //var code = 'alert(MyJavascriptInterface)';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_VOLTS'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'VOLTS\',\''+dropdown_channel+'\')';
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
  var code = 'MyJavascriptInterface.get_sensor(\'HMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_HMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'HMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
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
    this.setColour('#FF0000');
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['set_state'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_state = block.getFieldValue('STATE');
  block.setColour('#0ec244');//Make block green
  var state = true;
  if(dropdown_state === 'OFF' ){
	  state = "false"; 
	  block.setColour('#eb091c');//Make block red
  }  
  var code = MyJavascriptInterface.set_state(dropdown_channel,state);
  return code;
};

Blockly.Python['set_state'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var dropdown_state = block.getFieldValue('STATE');
  // TODO: Assemble Python into code variable.
  var state = 'true';
  if(dropdown_state === 'OFF' ) state = "false"; 
  var code = 'set_state(\''+dropdown_channel+'\',' + state+  ')';
  return code;
};


/**
 * @license
 * Copyright 2017 Google LLC
 * SPDX-License-Identifier: Apache-2.0
 */

/**
 * @fileoverview Example "wait" block that will pause the interpreter for a
 * number of seconds. Because wait is a blocking behavior, such blocks will
 * only work in interpreted environments.
 *
 * See https://neil.fraser.name/software/JS-Interpreter/docs.html
 */
Blockly.defineBlocksWithJsonArray([{
  "type": "wait_seconds",
  "message0": " wait %1 seconds",
  "args0": [{
    "type": "field_number",
    "name": "SECONDS",
    "min": 0,
    "max": 600,
    "value": 1
  }],
  "previousStatement": null,
  "nextStatement": null,
  "colour": "%{BKY_LOOPS_HUE}"
}]);

/**
 * Generator for wait block creates call to new method
 * <code>waitForSeconds()</code>.
 */
Blockly.JavaScript['wait_seconds'] = function(block) {
  var seconds = Number(block.getFieldValue('SECONDS'));
  var code = 'waitForSeconds(' + seconds + ');\n';
  return code;
};

Blockly.Python['wait_seconds'] = function(block) {
  var seconds = Number(block.getFieldValue('SECONDS'));
  var code = 'time.sleep(' + seconds + ')';
  return code;
};


//-------------------- API ------------------------



	function initApi(interpreter, scope) {
			/*Patch it
		  patchInterpreter(Interpreter);			
		  InterfaceDictionary={'get_voltage':'MyJavascriptInterface.get_voltage'};		  
		  interpreter.setProperty(scope, 'MyJavascriptInterface', interpreter.createConnectedObject(MyJavascriptInterface), interpreter.READONLY_DESCRIPTOR);
		  //interpreter.setProperty(scope,'MyJavascriptInterface', MyJavascriptInterface);
		  */

		  // Add an API function for highlighting blocks.
		  var wrapper = function(id) {
			return workspacePlayground.highlightBlock(id);
		  };
		  interpreter.setProperty(scope, 'highlightBlock',
			  interpreter.createNativeFunction(wrapper));

		  // Add an API function for the alert() block.
		  var wrapper = function(text) {
			return alert(arguments.length ? text : '');
		  };
		  interpreter.setProperty(scope, 'alert',
			  interpreter.createNativeFunction(wrapper));


		  // Add an API function for the prompt() block.
		  var wrapper = function(text) {
			text = text ? text.toString() : '';
			return interpreter.createPrimitive(prompt(text));
		  };

		  interpreter.setProperty(scope, 'prompt',
			  interpreter.createNativeFunction(wrapper));



		  // Add an API for the wait block.  See wait_block.js
		  Blockly.JavaScript.addReservedWords('waitForSeconds');
		  var wrapper = interpreter.createAsyncFunction(
			function(timeInSeconds, callback) {
			  // Delay the call to the callback.
			  setTimeout(callback, timeInSeconds * 1000);
			});
		  interpreter.setProperty(scope, 'waitForSeconds', wrapper);

		  // Add an API function for highlighting blocks.
		  var wrapper = function(id) {
			id = id ? id.toString() : '';
			return interpreter.createPrimitive(highlightBlock(id));
		  };
		  interpreter.setProperty(scope, 'highlightBlock',
			  interpreter.createNativeFunction(wrapper));

	}



