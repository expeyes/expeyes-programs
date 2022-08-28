

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


/*---------- Get Sensor --------------*/



//----------------SR04_distance

Blockly.Blocks['read_SR04'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read SR04")
        .appendField(new Blockly.FieldDropdown([["Distance(cm)","0"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_SR04'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'SR04\',\''+dropdown_channel+'\')';
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
  var code = 'p.get_sensor(\'BMP280\',\''+dropdown_channel+'\')';
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
  var code = 'p.get_sensor(\'MAX30100\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
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
  var code = 'p.get_sensor(\'MPU6050\',\''+dropdown_channel+'\')';
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
  var code = 'p.get_sensor(\'VL53L0X\',\''+dropdown_channel+'\')';
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
  var code = 'p.get_sensor(\'ML8511\',\''+dropdown_channel+'\')';
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
  var code = 'p.get_sensor(\'HMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
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
    this.setColour(230);
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
  var code = 'set_servo(\''+dropdown_channel+'\',' + value_angle+  ')\n'; // TODO: Change to set_sq1(frequency, duty cycle) or set_sq2

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

/*---------------------- Plot against Time ---------------*/


Blockly.Blocks['plot_datapoint'] = {
  init: function() {
    this.appendValueInput("YAXIS")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Y-Label:")
    this.appendValueInput("VALUE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT VALUE:")
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



/*---------------------- Plot plot_xyarray ---------------*/


Blockly.Blocks['plot_xyarray'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT ARRAY [X[],Y[]]:")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xyarray'] = function(block) {
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_xyarray('+value+')\n';
  
  return code;
};


Blockly.Python['plot_xyarray'] = function(block) {
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  var code = 'plot_xyarray('+value+')\n';

  return code;
};

/*---------------------- Plot plot_xarray_yarray ---------------*/


Blockly.Blocks['plot_xarray_yarray'] = {
  init: function() {
    this.appendValueInput("X")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT ARRAY X[]:")
    this.appendValueInput("Y")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT ARRAY Y[]:")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xarray_yarray'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_xarray_yarray('+X+','+Y+')\n';
  
  return code;
};


Blockly.Python['plot_xarray_yarray'] = function(block) {
  var X = Blockly.JavaScript.valueToCode(block, 'X', Blockly.JavaScript.ORDER_NONE);
  var Y = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_xarray_yarray('+X+','+Y+')\n';

  return code;
};



/*---------------------- Plot plot_xyyarray ---------------*/


Blockly.Blocks['plot_xyyarray'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("PLOT ARRAY [X[],Y1[], Y2[]]:")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Plot X, Y , Y2 arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['plot_xyyarray'] = function(block) {
  var value = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  var code = 'sleep(0.001);\n'+'plot_xyyarray('+value+')\n';
  
  return code;
};


Blockly.Python['plot_xyyarray'] = function(block) {
  var value = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  var code = 'plot_xyyarray('+value+')\n';

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

  Blockly.JavaScript.addReservedWords('sleep');
  Blockly.JavaScript.addReservedWords('waitForSeconds');
  Blockly.JavaScript.addReservedWords('plot');
  Blockly.JavaScript.addReservedWords('plot_xy');
  Blockly.JavaScript.addReservedWords('plot_xyarray');
  Blockly.JavaScript.addReservedWords('plot_xyyarray');
  Blockly.JavaScript.addReservedWords('plot_radar');
  Blockly.JavaScript.addReservedWords('write_to_file');
  Blockly.JavaScript.addReservedWords('get_sensor');
  Blockly.JavaScript.addReservedWords('set_PCA9685');
  Blockly.JavaScript.addReservedWords('set_servo');
  Blockly.JavaScript.addReservedWords('get_phone_sensor');




