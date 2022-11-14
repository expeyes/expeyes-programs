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
  var code = 'I2C.scan()';
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
  var code = 'I2C.scan()';
  return [code,Blockly.Python.ORDER_NONE];
};



Blockly.Blocks['scanI2Cselector'] = {

  init: function() {
    this.appendDummyInput()
        .appendField("Scan and select sensor")
    this.setColour(330);
    this.setOutput(true, null);
    this.setTooltip("Scan I2C");
    this.setHelpUrl("");
  },

};


Blockly.JavaScript['scanI2Cselector'] = function(block) {
  var code = 'scanI2Cselector()';
  return [code,Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['scanI2Cselector'] = function(block) {
  var code = 'I2C.scan()[0]';
  return [code,Blockly.Python.ORDER_NONE];
};



// Flexible I2C read

Blockly.Blocks['read_I2C_sensor'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read I2C Sensor:")
        .appendField(new Blockly.FieldDropdown([["BMP280","BMP280"],["MS5611","MS5611"],["INA219","INA219"],["ADS1115","ADS1115"], ["HMC5883L","HMC5883L"], ["TCS34725","TCS34725"], ["TSL2561","TSL2561"], ["MAX44009","MAX44009"], ["AHT10","AHT10"], ["QMC5883L","QMC5883L"], ["MPU6050","MPU6050"], ["AK8963","AK8963"],["MAX30100","MAX30100"],["VL53L0X","VL53L0X"]]), "NAME");
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
  var code = 'get_generic_sensor(\''+name+'\','+addr+')';
  return [code, Blockly.Python.ORDER_NONE];
};

// Super Flexible I2C read
Blockly.Blocks['read_i2c_sensor_flexible'] = {
  init: function() {
    this.appendValueInput("NAME")
        .setCheck(null)
        .appendField("Read I2C Sensor");
    this.appendDummyInput()
        .appendField("Parameter:")
        .appendField(new Blockly.FieldDropdown([["1","0"], ["2","1"], ["3","2"], ["4","3"], ["5","4"]]), "PARAM");
    this.setInputsInline(false);
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_i2c_sensor_flexible'] = function(block) {
  var value_name = Blockly.JavaScript.valueToCode(block, 'NAME', Blockly.JavaScript.ORDER_ATOMIC);
  var dropdown_param = block.getFieldValue('PARAM');
  var code = 'parseAndReadSensor('+value_name+','+dropdown_param+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_i2c_sensor_flexible'] = function(block) {
  var value_name = Blockly.Python.valueToCode(block, 'NAME', Blockly.Python.ORDER_ATOMIC);
  var dropdown_param = block.getFieldValue('PARAM');
  var code = '';
  return [code, Blockly.Python.ORDER_NONE];
};



// Super Duper Flexible  dynamic I2C read
Blockly.Blocks['read_i2c_sensor_flexible_dynamic'] = {

  init: function() {

    this.appendDummyInput()
        .appendField(new Blockly.FieldImage("media/i2cscan.png", 100, 30,  "*", this.scan.bind(this),'SS'))
        .appendField(new Blockly.FieldDropdown(this.generateNameOptions.bind(this),this.validateName.bind(this)), "NAME")
        .appendField(new Blockly.FieldImage("media/BMP280.png", 60, 60),'IMAGE');
    this.appendDummyInput()
        .appendField("Parameter")
        .appendField(new Blockly.FieldDropdown(this.generateParameterOptions.bind(this)), 'PARAM');
    this.appendDummyInput()
        .appendField("Configure")
        .appendField(new Blockly.FieldDropdown(this.generateConfigOptions.bind(this),this.validateConfiguration.bind(this)), 'CONFIG')
        .appendField(new Blockly.FieldDropdown(this.generateConfigSettings.bind(this),this.validateSettings.bind(this)), 'SETTING');
    this.setInputsInline(false);
    this.setOutput(true);
    this.setColour(330);
    this.setTooltip("");
    this.setHelpUrl("");
  },

  generateNameOptions: function() {

    if(typeof(this.availableSensors) === 'undefined'){
        var channels={};
        this.configParams = {};
        this.activeConfigurations = {};
        if(typeof(HWBridge) !== 'undefined'){channels = ["[65]INA219","[72]ADS1115","[104]MPU6050","[41]TCS34725/VL53L0X","[74]MAX44009","[12]AK8963","[13]QMC5883L","[83]ADXL345","[118]BMP280","[87]MAX30100","[119]MS5611","[56]AHT10","[57]TSL2561","[30]HMC5883L"];}
        else{channels = ["[129]ADCSENS"];}
        this.availableSensors = [];
        for(i=0;i<channels.length;i++){
            this.availableSensors.push(channels[i]);
        }
        if(this.availableSensors.length==0)this.currentValue = "No Sensor Found";
        else {
          if(this.availableSensors[0].search('/') != -1){ // 2 sensor options. more than that unsupported.
                this.currentValue = this.availableSensors[0].split('/')[0];
          }else{ // only one sensor
                this.currentValue = this.availableSensors[0];
          }
        }
    }

    ////console.log(this.id+'populate name dropdown:'+this.availableSensors);
    chans=[];
    for(i=0;i<this.availableSensors.length;i++){
      s = this.availableSensors[i];
      if(s.search('/') != -1){ // 2 sensor options. more than that unsupported.
          addr = s.split(']')[0].substring(1);
          sensor1 = s.split(']')[1].split('/')[0];
          sensor2 = s.split(']')[1].split('/')[1];
          chans.push([sensor1,'['+addr+']'+sensor1]);
          chans.push([sensor2,'['+addr+']'+sensor2]);
      }else{ // only one sensor
            var name = (s.search(']') == -1)?s : s.split(']')[1];
            chans.push([name,s]);
      }
    }
    if(chans.length>0)
        return chans;
    else
        return [["No Sensor Found","No Sensor Found"]];
  },

  validateName: function(newValue) {
    this.currentValue = newValue;
    var paramsDropdown = this.getField('PARAM');
    var opts = paramsDropdown.getOptions(false); // This regenerates the options for the parameters dropdown
    paramsDropdown.setValue(opts[0][1]);

    var configDropdown = this.getField('CONFIG');

    var opts = configDropdown.getOptions(false); // This regenerates the options for the options dropdown
    configDropdown.setValue(opts[0][1]);
    var image = this.getField('IMAGE');
    //console.log(image);
    //console.log("media/"+newValue.split(']')[1]+".jpeg");
    image.setValue("media/"+newValue.split(']')[1]+".jpeg");

  },

  generateParameterOptions: function() {
    if(typeof(this.currentValue) === 'undefined')return [["",""]];
    // this now refers to the block when it's called on the field dropdown because this was bound in init to the block
    try{
        if(!this.currentValue.startsWith("["))return [["",""]];
        var otherVal = this.currentValue;
        if(otherVal.search(']') != -1)otherVal = otherVal.split(']')[1];
        var channels=[];
        //if(typeof(HWBridge) !== 'undefined'){channels = JSON.parse(HWBridge.getSensorParameters(otherVal));}
        //else{channels = ["A1","A2","A3"];}
        //console.log("Generate Parameter options:"+otherVal+" = "+channels);
        channels = ["A1","A2","A3"];


        chans=[];
        for(i=0;i<channels.length;i++){
            chans.push([channels[i],String(i)]);
        }
        //console.log(otherVal+":"+chans+channels);
        return chans;
    }catch(e){
        return [["",""]];
    }
  },

  generateConfigOptions: function() {
    if(typeof(this.currentValue) === 'undefined')return [["",""]];
    // this now refers to the block when it's called on the field dropdown because this was bound in init to the block
    if(!this.currentValue.startsWith("["))return [["No Sensor Found","No Sensor Found"]];
    var otherVal = this.currentValue;
    //console.log(otherVal);
    if(otherVal.search(']') != -1)otherVal = otherVal.split(']')[1];
    var params = {};
    //if(typeof(HWBridge) !== 'undefined'){params = JSON.parse(JSON.parse(HWBridge.getSensorOptions(otherVal)));}
    //else{params = {"TIMING":["1x","16x"]};}
    params = {"TIMING":["1x","16x"]};
    this.configParams = params;
    //this.activeConfigurations = {};

    console.log('generate configuration options:'+params+','+otherVal);
    chans=[];
    for(key in params){
        if(key.length>1){
            if(!(key in  this.activeConfigurations)) this.activeConfigurations[key]=params[key][0];
            chans.push([key,key]);
        }

    }

    if(chans.length==0){
            chans  = [["",""]];
            try{
                var settingsDropdown = this.getField('SETTING');
                var opts = settingsDropdown.getOptions(false); // This regenerates the options for the parameters dropdown
                settingsDropdown.setValue(opts[0][1]);
            }catch(e){}
        } // try block because SETTING is not created for the first run. will be null.
    return chans;
  },

  validateConfiguration: function(newValue) {
    this.currentConfig = newValue;
    var settingsDropdown = this.getField('SETTING');
    var opts = settingsDropdown.getOptions(false); // This regenerates the options for the parameters dropdown
    //console.log('settings dropdown to '+opts[0][1]+'|'+opts);
    //settingsDropdown.setValue(opts[0][1]);
    //console.log(this.activeConfigurations[newValue]+' | '+ newValue + ' len:' + opts.length);
    if(!(typeof(this.activeConfigurations[newValue]) == 'undefined'))settingsDropdown.setValue(this.activeConfigurations[newValue]);
  },

  generateConfigSettings: function() {
    if(typeof(this.currentConfig) === 'undefined' || typeof(this.configParams) === 'undefined')return [["",""]];
    if(!(this.currentConfig in this.configParams))return [["",""]];

    chans=[];
    for(i=0;i<this.configParams[this.currentConfig].length;i++){
        chans.push([this.configParams[this.currentConfig][i],this.configParams[this.currentConfig][i]]);
    }
    if(chans.length==0)chans  = [["",""]];
    console.log("Config Settings Generated:"+chans);
    return chans;
  },

  validateSettings:function(value){
      var name = this.getFieldValue('NAME');
      //var conf = this.getFieldValue('CONFIG');
      var conf = this.currentConfig;

      if(typeof(name) === 'undefined' || typeof(conf) === 'undefined')return;
      if(conf in this.configParams){
          //console.log(conf+'is in '+this.configParams);
          if(!this.configParams[conf].includes(value)){
            //console.log(value+'is not in '+this.configParams[conf]);
            return;
          }
          try{
              addr = name.split(']')[0].substring(1);
              sensor = name.split(']')[1].split('/')[0];
              if(sensor === "unsupported")return;
              this.activeConfigurations[conf]=value;
              //if(typeof(HWBridge) !== 'undefined')HWBridge.configure_sensor(sensor,parseInt(addr),conf,value);
          }catch(e){
              //console.log(e);
          }
      }
  },


  scan: function() {
    //console.log('pre scan:'+this.availableSensors);
    var nameDropdown = this.getField('NAME');
    //var channels = JSON.parse(HWBridge.scanI2C());
    this.availableSensors = [];
    for(i=0;i<channels.length;i++){
        this.availableSensors.push(channels[i]);
    }
    ////console.log('Scanned:'+this.availableSensors);
    var opts = nameDropdown.getOptions(false); // This regenerates the options for the name dropdown
    nameDropdown.setValue(opts[0][1]);
  }

};

Blockly.JavaScript['read_i2c_sensor_flexible_dynamic'] = function(block) {
  var value_name = block.getFieldValue('NAME');
  var dropdown_param = block.getFieldValue('PARAM');
  var code = 'parseAndReadSensor(\''+value_name+'\','+dropdown_param+')';
  //console.log(code);
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_i2c_sensor_flexible_dynamic'] = function(block) {
  var code = '';
  return [code, Blockly.Python.ORDER_NONE];
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
  var code = 'get_sensor(\'BMP280\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};


//---------MS5611

Blockly.Blocks['read_MS5611'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read MS5611")
        .appendField(new Blockly.FieldDropdown([["PRESSURE","0"], ["TEMPERATURE","1"]]), "CHANNEL")
        .appendField(new Blockly.FieldImage("media/BMP280.png", 30, 30, { alt: "*", flipRtl: "FALSE" }));
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_MS5611'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MS5611\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_MS5611'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'MS5611\',\''+dropdown_channel+'\')';
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
  var code = 'get_sensor(\'TSL2561\',\''+dropdown_channel+'\')';
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
  var code = 'get_sensor(\'MAX30100\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};


//---------MAX30100

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
  var code = 'read_MAX6675('+dropdown_channel+')';
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
  var code = 'get_sensor(\'MPU6050\',\''+dropdown_channel+'\')';
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
  var code = 'get_sensor(\'ML8511\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_ML8511'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  // TODO: Assemble JavaScript into code variable.
  var code = 'get_sensor(\'ML8511\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};



//----------------TCS34725

Blockly.Blocks['read_TCS34725'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read TCS34725(RGB)")
        .appendField(new Blockly.FieldDropdown([["Luminance","0"],["InfraRed","1"],["Red","2"], ["Green","3"], ["Blue","4"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_TCS34725'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'TCS34725\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_TCS34725'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'TCS34725\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

//----------------INA219

Blockly.Blocks['read_INA219'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read INA219")
        .appendField(new Blockly.FieldDropdown([["Current","0"], ["Shunt Voltage","1"], ["Bus Voltage","2"], ["Power","3"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_INA219'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'INA219\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_INA219'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'INA219\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};
//----------------ADS1115

Blockly.Blocks['read_ADS1115'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read ADS1115 (+/-0.25V)")
        .appendField(new Blockly.FieldDropdown([["Voltage","0"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_ADS1115'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'ADS1115\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_ADS1115'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'ADS1115\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
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
  var code = 'get_sensor(\'HMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_HMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'HMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.Python.ORDER_NONE];
};

//----------------QMC5883L

Blockly.Blocks['read_QMC5883L'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Read QMC5883L")
        .appendField(new Blockly.FieldImage("media/MAGNETOMETER.png", 20, 20, { alt: "*", flipRtl: "FALSE" }))
        .appendField(new Blockly.FieldDropdown([["Hx","0"], ["Hy","1"], ["Hz","2"], ["Abs","3"]]), "CHANNEL");
    this.setOutput(true, null);
    this.setColour(230);
 this.setTooltip("");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['read_QMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'QMC5883L\',\''+dropdown_channel+'\')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};

Blockly.Python['read_QMC5883L'] = function(block) {
  var dropdown_channel = block.getFieldValue('CHANNEL');
  var code = 'get_sensor(\'QMC5883L\',\''+dropdown_channel+'\')';
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
  var code = 'set_dual_AD9833('+dropdown_channel+',' + freq+  ')\n';

  return code;
};



var I2CSelectionCallback;
function getSensorSelection(callback){
    I2CSelectionCallback = callback;
    //var sensors = JSON.parse(HWBridge.scanI2C());
    if(sensors.length>0){
        var senslist = $('<div class="ui mini teal buttons i2clist"></div>');
        sensors.forEach((s, i) => {
              if(i>0) senslist.append('<div class="or"></div>');
              if(s.search('/') != -1){ // 2 sensor options. more than that unsupported.
                  addr = s.split(']')[0].substring(1);
                  sensor1 = s.split(']')[1].split('/')[0];
                  sensor2 = s.split(']')[1].split('/')[1];
                  senslist.append(`<button class="ui button" onclick="var t = this.textContent; this.parentElement.remove(); I2CSelectionCallback(t);">[${addr}]${sensor1}</button>`);
                  senslist.append('<div class="or"></div>');
                  senslist.append(`<button class="ui button" onclick="var t = this.textContent; this.parentElement.remove(); I2CSelectionCallback(t);">[${addr}]${sensor2}</button>`);
              }else{ // only one sensor
                  senslist.append(`<a class="ui button" onclick="var t = this.textContent; this.parentElement.remove(); I2CSelectionCallback(t);">${s}</a>`);
              }


        } );
        results.append(senslist);
    }else{
      results.append('<span>No sensors found. default to voltmeter</span>');
      callback('[0]ADCSENS'); // default to voltmeter
    }
}

//-------------------- API ------------------------

function initSensors(interpreter, scope) {


		  // Add an API for the set_state call
		  interpreter.setProperty(scope, 'set_dual_AD9833', interpreter.createAsyncFunction(
				function(channel, value,callback) {
                    HWBridge.set_dual_AD9833(channel,value,callback);
				})
			);


		  // Add an API for the get_sensor call
		  interpreter.setProperty(scope, 'get_sensor', interpreter.createAsyncFunction(
				function(sensor,param,callback) {
                    HWBridge.get_sensor(sensor,param,callback);
				})
			);
		  // Add an API for the get_generic_sensor call
		  interpreter.setProperty(scope, 'get_generic_sensor', interpreter.createAsyncFunction(
				function(sensor,addr,callback) {
                    HWBridge.get_generic_sensor(sensor,addr,callback);
				})
			);
		  // Add an API for the parseAndReadSensor call
		  interpreter.setProperty(scope, 'parseAndReadSensor', interpreter.createAsyncFunction(
				function(descriptor,param,callback) {
                  addr = descriptor.split(']')[0].substring(1);
                  sensor = descriptor.split(']')[1].split('/')[0];
                  HWBridge.get_generic_sensor(sensor,parseInt(addr),(vals)=>{callback(JSON.parse(vals)[param])});
				})
			);


		  // Add an API for the get_generic_sensor call
		  interpreter.setProperty(scope, 'get_generic_sensor_param', interpreter.createAsyncFunction(
				function(sensor,addr, param,callback) {
				  HWBridge.get_generic_sensor_param(sensor,addr, param,callback);
				})
			);
		  // Add an API for the get_sensor call
		  interpreter.setProperty(scope, 'scanI2C', interpreter.createAsyncFunction(
				function(callback) {
                    HWBridge.scanI2C(callback);
				})
			);
		  // Add an API for the get_sensor call
		  interpreter.setProperty(scope, 'scanI2CString', interpreter.createAsyncFunction(
				function(callback) {
                    HWBridge.scanI2CString(callback);
				})
			);

		  // Add an API for the I2C Selector block.
		  var wrapper = function scanI2Cselector(callback) {
			  getSensorSelection(callback);
		  };
		  interpreter.setProperty(scope, 'scanI2Cselector', interpreter.createAsyncFunction(wrapper));


		  // Add an API for the get_max6675 call
		  interpreter.setProperty(scope, 'MAX6675', interpreter.createAsyncFunction(
				function(cs,callback) {
				  HWBridge.MAX6675(cs,(e)=>{
					  val = e&0xFFFF;
					  if(val&0x4){throw {name:"ReadError",message:"Measure Temperature(MAX6675)",stack:"Out of Range. Is the sensor connected properly?"}; }
					  callback( ((val>>3)&0xFFF)*0.25 );
					  
					  });
				})
			);

		  // Add an API for the set_PCA9685 call
		  interpreter.setProperty(scope, 'set_PCA9685', interpreter.createAsyncFunction(
				function(channel, value,callback) {
				  HWBridge.set_PCA9685(channel,value,callback);
				})
			);

	}



