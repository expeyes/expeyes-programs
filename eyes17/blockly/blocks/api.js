var audioReadyCallback  = ()=>{};

var startRecord = function(callback){
    audioReadyCallback = callback;
    if(typeof JSBridge != 'undefined'){
        if(!JSBridge.isAudioAvailable()){
            console.log('record permission not granted. wait.');
            JSBridge.getAudioPermission();
            return;
            }
    }
    audioReadyCallback();
}



var storageReadyCallback  = ()=>{};

var startStorage = function(callback){
    storageReadyCallback = callback;
    if(typeof JSBridge != 'undefined'){
        if(!JSBridge.isStorageAvailable()){
            console.log('storage permission not granted. wait.');
            JSBridge.getStoragePermission();
            return;
            }
    }
    storageReadyCallback();
}



/*---Audio Broadcast----*/
Blockly.Blocks['cs_start_audio'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldCheckbox("TRUE"), "STATE")
        .appendField("BROADCAST MIC");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Broadcast Audio");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['cs_start_audio'] = function(block) {
  var state = (block.getFieldValue('STATE') == "TRUE")?true:false;
  var code = 'audioBroadcast('+state+');\n';
  return code;
};

Blockly.Python['cs_start_audio'] = function(block) {
  var txt = Blockly.Python.valueToCode(block, 'TEXT', Blockly.Python.ORDER_NONE);
  var code = '\n';
  return code;
};
/*---Audio Broadcast----*/
Blockly.Blocks['cs_start_audio_listen'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldCheckbox("TRUE"), "STATE")
        .appendField("LISTEN BROADCAST");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Broadcast Audio");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['cs_start_audio_listen'] = function(block) {
  var state = (block.getFieldValue('STATE') == "TRUE")?true:false;
  var code = 'listenAudioBroadcast('+state+');\n';
  return code;
};

Blockly.Python['cs_start_audio_listen'] = function(block) {
  var code = '\n';
  return code;
};
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



/*--------------- Phone Sensors ----------------------*/

//----------------ACCELEROMETER (GRAVITY)

Blockly.Blocks['get_phone_accel'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Gravity")
        .appendField(new Blockly.FieldDropdown([["X","0"],["Y","1"],["Z","2"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['get_phone_accel'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_phone_sensor(\'GRAVITY\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_phone_accel'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'GRAVITY\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};




//----------------ROTATION (ACCELEROMETER+GYRO+COMPASS fusion sensor)

Blockly.Blocks['get_phone_rotation'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Phone's Rotation")
        .appendField(new Blockly.FieldDropdown([["X","0"],["Y","1"],["Z","2"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("Measure phone's angle of rotation ");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['get_phone_rotation'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_phone_sensor(\'ROTATION\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_phone_rotation'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_phone_sensor(\'ROTATION\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};



//----------------Luminosity (Inbuilt lux meter of phone)

Blockly.Blocks['get_phone_light'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Phone's sensor")
        .appendField(new Blockly.FieldDropdown([["LUMINOSITY","0"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("Measure phone's angle of rotation ");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['get_phone_light'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_phone_sensor(\'LUMINOSITY\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['get_phone_light'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_phone_sensor(\'LUMINOSITY\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};




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
  var code = 'sleep(' + seconds + ');\n';
  return code;
};

Blockly.Python['wait_seconds'] = function(block) {
  var seconds = Number(block.getFieldValue('SECONDS'));
  var code = 'time.sleep(' + seconds + ')\n';
  return code;
};


/*-------- Write to File ---------*/

Blockly.Blocks['write_to_file'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Print to File | Newline?")
        .appendField(new Blockly.FieldCheckbox("TRUE"), "NEWLINE");
    this.appendValueInput("TEXT")
        .setCheck(null)
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(new Blockly.FieldTextInput("exp.txt"), "FNAME")
        .appendField(", Text:");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(330);
 this.setTooltip("Save Content To a File");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['write_to_file'] = function(block) {
  var text_fname = block.getFieldValue('FNAME');
  var value_text = Blockly.JavaScript.valueToCode(block, 'TEXT', Blockly.JavaScript.ORDER_NONE);
  var nl = block.getFieldValue('NEWLINE') === 'TRUE';
  var code = 'write_to_file(\''+text_fname+'\','+value_text+','+nl+');\n';
  return code;
};

Blockly.Python['write_to_file'] = function(block) {
  var text_fname = block.getFieldValue('FNAME');
  var value_text = Blockly.Python.valueToCode(block, 'TEXT', Blockly.Python.ORDER_NONE);
  var code = 'write_to_file(\''+text_fname+'\','+value_text+')\n';
  return code;
};




/*---------------------- Analyse Captured Data ---------------*/



Blockly.Blocks['average_array'] = {
  init: function() {
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("AVERAGE of X[]:")
    this.setInputsInline(false);
    this.setOutput(true,null);
    this.setColour(230);
 this.setTooltip("Average array");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['average_array'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var code = 'average('+X+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['average_array'] = function(block) {
  var X = Blockly.Python.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var code = 'sum('+X+')/len('+X+')';
  return [code, Blockly.Python.ORDER_NONE];
};

Blockly.Blocks['sum_array'] = {
  init: function() {
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("SUM of X[]:")
    this.setInputsInline(false);
    this.setOutput(true,null);
    this.setColour(230);
 this.setTooltip("Average array");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['sum_array'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var code = 'sum('+X+')';
  console.log(code);
  return [code, Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['sum_array'] = function(block) {
  var X = Blockly.Python.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var code = 'sum('+X+')';

  return [code, Blockly.Python.ORDER_NONE];
};


Blockly.Blocks['sine_fit_arrays'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["Amplitude","0"], ["Frequency","1"], ["Phase (Deg)","2"]]), "PARAMETER");
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ANALYZE ARRAY X[]:")
    this.appendValueInput("Y")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y[]:")
    this.setInputsInline(false);
    this.setOutput(true,null);
    this.setColour(230);
 this.setTooltip("Fit X, Y arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['sine_fit_arrays'] = function(block) {
  var dropdown_parameter = block.getFieldValue('PARAMETER');
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var code = 'sine_fit_arrays('+X+','+Y+','+dropdown_parameter+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['sine_fit_arrays'] = function(block) {
  var dropdown_parameter = block.getFieldValue('PARAMETER');
  var X = Blockly.Python.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var Y = Blockly.Python.valueToCode(block, 'Y', Blockly.Python.ORDER_NONE);
  var code = 'sine_fit_arrays('+X+','+Y+','+dropdown_parameter+')';

  return [code, Blockly.Python.ORDER_NONE];
};







Blockly.Blocks['sine_fit_two_arrays'] = {
  init: function() {
    this.appendDummyInput()
        .appendField(new Blockly.FieldDropdown([["Amplitude Ratio[Gain]","0"], ["Frequency Ratio","1"], ["Phase Diff (Deg)","2"]]), "PARAMETER");
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ANALYZE ARRAY X[]:")
    this.appendValueInput("Y")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y[]:")
    this.appendValueInput("X2")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ANALYZE ARRAY X2[]:")
    this.appendValueInput("Y2")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("ARRAY Y2[]:")
    this.setInputsInline(false);
    this.setOutput(true,null);
    this.setColour(230);
 this.setTooltip("Fit X, Y arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['sine_fit_two_arrays'] = function(block) {
  var dropdown_parameter = block.getFieldValue('PARAMETER');
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var X2 = Blockly.JavaScript.valueToCode(block, 'X2', Blockly.JavaScript.ORDER_NONE);
  var Y2 = Blockly.JavaScript.valueToCode(block, 'Y2', Blockly.JavaScript.ORDER_NONE);
  var code = 'sine_fit_two_arrays('+X+','+Y+','+X2+','+Y2+','+dropdown_parameter+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['sine_fit_two_arrays'] = function(block) {
  var dropdown_parameter = block.getFieldValue('PARAMETER');
  var X = Blockly.Python.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var Y = Blockly.Python.valueToCode(block, 'Y', Blockly.Python.ORDER_NONE);
  var X2 = Blockly.Python.valueToCode(block, 'X2', Blockly.Python.ORDER_NONE);
  var Y2 = Blockly.Python.valueToCode(block, 'Y2', Blockly.Python.ORDER_NONE);
  var code = 'sine_fit_two_arrays('+X+','+Y+','+X2+','+Y2+','+dropdown_parameter+')';

  return [code, Blockly.Python.ORDER_NONE];
};





Blockly.Blocks['fourier_transform'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Fourier Transform");
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Time Array X[]:")
    this.appendValueInput("Y")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Amplitude ARRAY Y[]:")
    this.appendDummyInput()
        .appendField(new Blockly.FieldVariable("fftx"), "FFTX")
        .appendField(new Blockly.FieldVariable("ffty"), "FFTY");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("FFT of X, Y arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['fourier_transform'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);

  var xvar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('FFTX'), 'VARIABLE');
  var yvar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('FFTY'), 'VARIABLE');
  var code = "var jsondata = fourier_transform("+X+","+Y+");\ntmpjson = JSON.parse(jsondata);"+xvar+"=tmpjson[0];"+yvar+"=tmpjson[1];\n";
  return code;

};


Blockly.Python['fourier_transform'] = function(block) {
  var X = Blockly.Python.valueToCode(block, 'X', Blockly.Python.ORDER_NONE);
  var Y = Blockly.Python.valueToCode(block, 'Y', Blockly.Python.ORDER_NONE);
  var code = 'fft('+X+','+Y+')';

  return [code, Blockly.Python.ORDER_NONE];
};








/*
  Blockly.JavaScript.addReservedWords('sleep');
  Blockly.JavaScript.addReservedWords('waitForSeconds');
  Blockly.JavaScript.addReservedWords('plot');
  Blockly.JavaScript.addReservedWords('capture_analysis');
  Blockly.JavaScript.addReservedWords('capture_analysis_dual');
  Blockly.JavaScript.addReservedWords('plot_xy');
  Blockly.JavaScript.addReservedWords('plot_xyarray');
  Blockly.JavaScript.addReservedWords('plot_xyyarray');
  Blockly.JavaScript.addReservedWords('plot_radar');
  Blockly.JavaScript.addReservedWords('write_to_file');
  Blockly.JavaScript.addReservedWords('get_voltage');
  Blockly.JavaScript.addReservedWords('set_voltage');
  Blockly.JavaScript.addReservedWords('get_frequency');
  Blockly.JavaScript.addReservedWords('multi_r2r');
  Blockly.JavaScript.addReservedWords('capture1');
  Blockly.JavaScript.addReservedWords('capture2');
  Blockly.JavaScript.addReservedWords('scope_trigger');
  Blockly.JavaScript.addReservedWords('set_frequency');
  Blockly.JavaScript.addReservedWords('set_state');
  Blockly.JavaScript.addReservedWords('get_sensor');
  Blockly.JavaScript.addReservedWords('set_PCA9685');
  Blockly.JavaScript.addReservedWords('set_servo');
  Blockly.JavaScript.addReservedWords('get_phone_sensor');
*/


//-------------------- API ------------------------

function initApi(interpreter, scope) {
			/*Patch it
			 * // Desperate attempt at infiltrating the sandbox. Didn't work
		  patchInterpreter(Interpreter);			
		  InterfaceDictionary={'get_voltage':'JSBridge.get_voltage'};
		  interpreter.setProperty(scope, 'JSBridge', interpreter.createConnectedObject(JSBridge), interpreter.READONLY_DESCRIPTOR);
		  //interpreter.setProperty(scope,'JSBridge', JSBridge);
		  */


		  // Add an API for the wait block.
		  interpreter.setProperty(scope, 'waitForSeconds', interpreter.createAsyncFunction(
                                                           			function(timeInSeconds, callback) {
                                                           			  // Delay the call to the callback.
                                                           			  setTimeout(callback, timeInSeconds * 1000);
                                                           			}));
		  interpreter.setProperty(scope, 'sleep', interpreter.createAsyncFunction(
                                                  			function(timeInSeconds, callback) {
                                                  			  // Delay the call to the callback.
                                                  			  setTimeout(callback, timeInSeconds * 1000);
                                                  			}));

		  // Add an API function for highlighting blocks.
		  var wrapper = function(id) {
			id = id ? id.toString() : '';
			return interpreter.createPrimitive(highlightBlock(id));
		  };
		  interpreter.setProperty(scope, 'highlightBlock',
			  interpreter.createNativeFunction(wrapper));


		  // Add an API for the console.log call
		  interpreter.setProperty(scope, 'log', interpreter.createNativeFunction(
				function( value) {
				  return console.log(value);
				})
			);

		  // Add an API for the JSON.parse call
		  interpreter.setProperty(scope, 'myparse', interpreter.createNativeFunction(
				function( value) {
				  return JSON.parse(value);
				})
			);



		  // Add APIs for the average analysis calls. pass entire data to native java for processing.
		  interpreter.setProperty(scope, 'average', interpreter.createNativeFunction(
				function(xin) {
				  x = myInterpreter.pseudoToNative(xin);
				  return x.reduce((a, b) => parseInt(a) + parseInt(b), 0) / x.length || 0;
				})
			);
		  interpreter.setProperty(scope, 'sum', interpreter.createNativeFunction(
				function(xin) {
				  x = myInterpreter.pseudoToNative(xin);
				  return x.reduce((a, b) => parseInt(a) + parseInt(b), 0) ;
				})
			);
		  // Add APIs for the program starting block.
		  interpreter.setProperty(scope, 'programStarting', interpreter.createAsyncFunction(
				function(callback) {
				            if(typeof HWBridge != 'undefined')
                                    HWBridge.programStarting(callback);
				})
			);

		  // Add APIs for the sine fit analysis calls. pass entire data to native java for processing.
		  interpreter.setProperty(scope, 'sine_fit_arrays', interpreter.createAsyncFunction(
				async function(x,y,param, callback) {
				  val = await JSBridge.sine_fit_arrays(JSON.stringify(Object.values(x.a)),JSON.stringify(Object.values(y.a)),param);
				  callback( val.toFixed(3) );
				})
			);
		  interpreter.setProperty(scope, 'sine_fit_two_arrays', interpreter.createAsyncFunction(
				async function(x,y,x2,y2,param,callback) {
				  val =  await JSBridge.sine_fit_two_arrays(JSON.stringify(Object.values(x.a)),JSON.stringify(Object.values(y.a)),JSON.stringify(Object.values(x2.a)),JSON.stringify(Object.values(y2.a)),param);
				  callback(val.toFixed(3));
				})
			);
		  // Add an API for the FFT block.  copied from wait_block. Async attempt
		  interpreter.setProperty(scope, 'fourier_transform', interpreter.createAsyncFunction(
				function fourier_transform(x,y,callback) {
                                JSBridge.fourier_transform(JSON.stringify(Object.values(x.a)),JSON.stringify(Object.values(y.a)),callback);
                		  })
			);


			// File writing calls
		  // Add an API for the writeToFile call
		  interpreter.setProperty(scope, 'write_to_file', interpreter.createAsyncFunction(
				function(fname, txt, newline,callback) {
					if(newline){txt+='\n';}
			        return JSBridge.writeToFile(fname,txt,callback);
				})
			);






	}



