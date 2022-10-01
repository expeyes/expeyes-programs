

Blockly.Blocks['lists_push'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Append To ")
        .appendField(new Blockly.FieldVariable("list"), "list")
        .appendField(", Value:");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#745ba5");
 this.setTooltip("Fit X, Y arrays");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['lists_push'] = function(block) {
  var datavar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('list'), 'VARIABLE');
  var X = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  code = datavar+'.push('+X+');log('+datavar+')\n'
  return code;
};


Blockly.Python['lists_push'] = function(block) {
  var datavar = Blockly.Python.nameDB_.getName(block.getFieldValue('list'), 'VARIABLE');
  var X = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  code = datavar+'.append('+X+')\n'
  return code;
};


Blockly.Blocks['lists_push_time'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Append To ")
        .appendField(new Blockly.FieldVariable("list"), "list")
        .appendField(", Value:");
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Timestamps ")
        .appendField(new Blockly.FieldVariable("timevals"), "timevals")
        .appendField(new Blockly.FieldVariable("clock"), "clock");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#745ba5");
 this.setTooltip("");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['lists_push_time'] = function(block) {
  var datavar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('list'), 'VARIABLE');
  var timevar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('timevals'), 'VARIABLE');
  var clockvar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('clock'), 'VARIABLE');
  var X = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  code = 'if(typeof '+datavar+' == \'undefined\'){'+datavar+'=[];'+timevar+'=[];'+clockvar+'=initTime();}\n';
  code += datavar+'.push('+X+');\n';
  code += timevar+'.push(getTime('+clockvar+'));\n';
  return code;
};


Blockly.Python['lists_push_time'] = function(block) {
  var datavar = Blockly.Python.nameDB_.getName(block.getFieldValue('list'), 'VARIABLE');
  var timevar = Blockly.Python.nameDB_.getName(block.getFieldValue('timevals'), 'VARIABLE');
  var X = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  code = 'if(typeof '+datavar+' == \'undefined\'):'+datavar+'=[];'+timevar+'=[];initTime()\n'
  code += datavar+'.push('+X+')\n'
  code += timevar+'.push(getTime())\n'
  return code;
};


Blockly.Blocks['lists_new'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("New List ")
        .appendField(new Blockly.FieldVariable("list"), "list");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#745ba5");
 this.setTooltip("Create empty list");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['lists_new'] = function(block) {
  var datavar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('list'), 'VARIABLE');
  code = datavar+' = [];\n'
  return code;
};


Blockly.Python['lists_new'] = function(block) {
  var datavar = Blockly.Python.nameDB_.getName(block.getFieldValue('list'), 'VARIABLE');
  code = datavar+'=[]\n'
  return code;
};




Blockly.Blocks['lists_subtract'] = {
  init: function() {
    this.appendValueInput("VALUE")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("From List ")
        .appendField(new Blockly.FieldVariable("list"), "list")
        .appendField(", Subtract");
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#745ba5");
 this.setTooltip("Subtract Y from X . modify X with new value");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['lists_subtract'] = function(block) {
  var datavar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('list'), 'VARIABLE');
  var X = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  code = datavar+'=subtract_lists('+datavar+','+X+');\n'
  return code;
};


Blockly.Python['lists_subtract'] = function(block) {
  var datavar = Blockly.Python.nameDB_.getName(block.getFieldValue('list'), 'VARIABLE');
  var X = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  code = datavar+'= '+datavar+'-'+X+'\n'
  return code;
};



Blockly.Blocks['lists_subtract_return'] = {
  init: function() {
    this.appendDummyInput()
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(new Blockly.FieldVariable("list"), "list")
        .appendField(" - ")
        .appendField(new Blockly.FieldVariable("list2"), "list2");
    this.setOutput(true);
    this.setColour("#745ba5");
 this.setTooltip("Subtract Y from X and return");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['lists_subtract_return'] = function(block) {
  var datavar = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('list'), 'VARIABLE');
  var datavar2 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('list2'), 'VARIABLE');
  code = 'subtract_lists('+datavar+','+datavar2+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['lists_subtract_return'] = function(block) {
  var datavar = Blockly.Python.nameDB_.getName(block.getFieldValue('list'), 'VARIABLE');
  var datavar2 = Blockly.JavaScript.nameDB_.getName(block.getFieldValue('list2'), 'VARIABLE');
  code = 'subtract_lists('+datavar+','+datavar2+')';
  return [code, Blockly.Python.ORDER_NONE];
};


/*---------------------- Save Lists ---------------*/



Blockly.Blocks['save_lists'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Save Arrays to File")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField(new Blockly.FieldTextInput("data.csv"), "FNAME")
    this.appendValueInput("COL1")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Column1 []:")
    this.appendValueInput("COL2")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Column2 []:")
    this.appendValueInput("COL3")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Column3 []:")
    this.appendValueInput("COL4")
        .setAlign(Blockly.ALIGN_RIGHT)
        .appendField("Column4 []:")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour("#745ba5");
 this.setTooltip("Save arrays to file");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['save_lists'] = function(block) {
  var fname = block.getFieldValue('FNAME');
  var COL1 = Blockly.JavaScript.valueToCode(block, 'COL1', Blockly.JavaScript.ORDER_NONE);
  var COL2 = Blockly.JavaScript.valueToCode(block, 'COL2', Blockly.JavaScript.ORDER_NONE);
  var COL3 = Blockly.JavaScript.valueToCode(block, 'COL3', Blockly.JavaScript.ORDER_NONE);
  var COL4 = Blockly.JavaScript.valueToCode(block, 'COL4', Blockly.JavaScript.ORDER_NONE);
  var code = "save_lists('"+fname+"'";
  if(COL1.length>2)code += ","+COL1;
  else code += ",[]";
  if(COL2.length>2)   code += ","+COL2;
  else code += ",[]";
  if(COL3.length>3)   code += ","+COL3;
  else code += ",[]";
  if(COL4.length>4)   code += ","+COL4;
  else code += ",[]";
  code+= ');\n';

  return code;
};


Blockly.Python['save_lists'] = function(block) {
  var fname = block.getFieldValue('FNAME');
  var COL1 = Blockly.Python.valueToCode(block, 'COL1', Blockly.Python.ORDER_NONE);
  var COL2 = Blockly.Python.valueToCode(block, 'COL2', Blockly.Python.ORDER_NONE);
  var COL3 = Blockly.Python.valueToCode(block, 'COL3', Blockly.Python.ORDER_NONE);
  var COL4 = Blockly.Python.valueToCode(block, 'COL4', Blockly.Python.ORDER_NONE);
  var code = "save_lists('"+fname+"'";
  if(COL1.length>2)code += ","+COL1;
  else code += ",[]";
  if(COL2.length>2)   code += ","+COL2;
  else code += ",[]";
  if(COL3.length>3)   code += ","+COL3;
  else code += ",[]";
  if(COL4.length>4)   code += ","+COL4;
  else code += ",[]";
  code+= ')\n';
  return code;
};



function initLists(interpreter, scope) {

		  interpreter.setProperty(scope, 'subtract_lists', interpreter.createNativeFunction(
				function(x,y) {
				  c = [];
				  a = Object.values(x.a);
				  b = Object.values(y.a);
				  if(a.length == b.length){
				          for(var i=0;i<a.length;i++)c.push(a[i]-b[i]);
				          return interpreter.nativeToPseudo(c);
    				  }
				})
			);

		  // Add an API for the XYY array plot call
		  interpreter.setProperty(scope, 'save_lists', interpreter.createNativeFunction(
				function( fname,x,y1, y2, y3) {
				  return JSBridge.save_lists(fname,JSON.stringify(Object.values(x.a)),JSON.stringify(Object.values(y1.a)),JSON.stringify(Object.values(y2.a)),JSON.stringify(Object.values(y3.a)));
				})
			);

		  interpreter.setProperty(scope, 'initTime', interpreter.createNativeFunction(
				function() {
				    return new Date();
				})
			);
		  interpreter.setProperty(scope, 'getTime', interpreter.createNativeFunction(
				function( start_time) {
				  return new Date() - start_time;
				})
			);


	}



