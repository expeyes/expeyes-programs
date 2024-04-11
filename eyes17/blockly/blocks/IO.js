var gauges = [];

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
  var code = 'sleep(0.0001);print('+txt+');\n';
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
  var code = 'sleep(0.0001);sticker('+label+','+txt+');\n';
  return code;
};


Blockly.Python['cs_sticker'] = function(block) {
  var label = Blockly.Python.valueToCode(block, 'LABEL', Blockly.Python.ORDER_NONE);
  var txt = Blockly.Python.valueToCode(block, 'TEXT', Blockly.Python.ORDER_NONE);
  var code = 'print('+label+','+txt+')\n';
  return code;
};


// -------------- Search string

/*---print statememt----*/
Blockly.Blocks['cs_search'] = {
  init: function() {
    this.appendValueInput("CHILD")
        .setAlign(Blockly.ALIGN_RIGHT)
        .setCheck(null)
        .appendField("Find position of");
    this.appendValueInput("PARENT")
        .setAlign(Blockly.ALIGN_RIGHT)
        .setCheck(null)
        .appendField("in a");
    this.appendDummyInput()
        .appendField("-1 if not found.")
    this.setOutput(true, null);
    this.setInputsInline(false);
    this.setColour(155);
 this.setTooltip("substring");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['cs_search'] = function(block) {
  var parent = Blockly.JavaScript.valueToCode(block, 'PARENT', Blockly.JavaScript.ORDER_NONE);
  var child = Blockly.JavaScript.valueToCode(block, 'CHILD', Blockly.JavaScript.ORDER_NONE);
  var code = parent+'.indexOf('+child+')';
  return [code, Blockly.JavaScript.ORDER_NONE];
};


Blockly.Python['cs_search'] = function(block) {
  var parent = Blockly.Python.valueToCode(block, 'PARENT', Blockly.Python.ORDER_NONE);
  var child = Blockly.Python.valueToCode(block, 'CHILD', Blockly.Python.ORDER_NONE);
  var code = parent+'.indexOf('+child+')';
  return [code, Blockly.Python.ORDER_NONE];
};


/*------ Fixed Gauge in Registers area -----

MIT License
Copyright (c) 2020 rotvalli
*/

Blockly.Blocks['cs_gauge'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Gauge Name:")
        .appendField(new Blockly.FieldTextInput("mygauge"), "ID");
    this.appendValueInput("VALUE")
        .setCheck(null)
        .appendField("Min:")
        .appendField(new Blockly.FieldNumber(0, -50000, 50000, 1), "MIN")
        .appendField("Max:")
        .appendField(new Blockly.FieldNumber(100, -50000, 50000, 1), "MAX")
        .appendField("Value:");
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Print to screen");
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['cs_gauge'] = function(block) {
  var label = block.getFieldValue('ID');
  var mn = block.getFieldValue('MIN');
  var mx = block.getFieldValue('MAX');
  var val = Blockly.JavaScript.valueToCode(block, 'VALUE', Blockly.JavaScript.ORDER_NONE);
  var code = 'sleep(0.0001);setGauge(\''+label+'\','+val+','+mn+','+mx+');\n';
  return code;
};


Blockly.Python['cs_gauge'] = function(block) {
  var label = block.getFieldValue('ID');
  var val = Blockly.Python.valueToCode(block, 'VALUE', Blockly.Python.ORDER_NONE);
  var code = 'print('+label+','+val+')\n';
  return code;
};

function addGauge(id){
        gaugearea.append(`
        <div class="item">
                <div id="${id}" class="gauge" style="
                --gauge-bg: #088478;
                --gauge-value:0;
                --gauge-display-value:0;">

                <div class="ticks">
                    <div class="tithe" style="--gauge-tithe-tick:1;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:2;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:3;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:4;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:6;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:7;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:8;"></div>
                    <div class="tithe" style="--gauge-tithe-tick:9;"></div>
                    <div class="min"></div>
                    <div class="mid"></div>
                    <div class="max"></div>
                </div>
                <div class="tick-circle"></div>

                <div class="needle">
                    <div class="needle-head"></div>
                </div>
                <div class="labels">
                    <div class="value-label"></div>
                </div>
            </div>
        </div>`);
        return true;
}
// Gauge
function updateGauge(id, value, min, max) {
    const newGaugeValue = Math.floor(((value - min) / (max - min)) * 100);
    document.getElementById(id).style.setProperty('--gauge-display-value', Math.floor(value));
    document.getElementById(id).style.setProperty('--gauge-value', newGaugeValue);
}


function savePNG(){
    var scaleFactor = 1;
    //Any modifications are executed on a deep copy of the element
    var cp = Blockly.mainWorkspace.svgBlockCanvas_.cloneNode(true);
    cp.removeAttribute("width");
    cp.removeAttribute("height");
    cp.removeAttribute("transform");

    var styleElem = document.createElementNS("http://www.w3.org/2000/svg", "style");
    //I've manually pasted codethemicrobit.com's CSS for blocks in here, but that can be removed as necessary
    styleElem.textContent = ".blocklyToolboxDiv {background: rgba(0, 0, 0, 0.05);}.blocklyMainBackground {stroke:none !important;}.blocklyTreeLabel, .blocklyText, .blocklyHtmlInput {font-family:'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'source-code-pro', monospace !important;}.blocklyText { font-size:1rem !important;}.rtl .blocklyText {text-align:right;} .blocklyTreeLabel { font-size:1.25rem !important;} .blocklyCheckbox {fill: #ff3030 !important;text-shadow: 0px 0px 6px #f00;font-size: 17pt !important;}";
    cp.insertBefore(styleElem, cp.firstChild);

    //Creates a complete SVG document with the correct bounds (it is necessary to get the viewbox right, in the case of negative offsets)
    var bbox = Blockly.mainWorkspace.svgBlockCanvas_.getBBox();
    var xml = new XMLSerializer().serializeToString(cp);
    xml = '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="'+bbox.width+'" height="'+bbox.height+'" viewBox="' + bbox.x + ' ' + bbox.y + ' '  + bbox.width + ' ' + bbox.height + '"><rect width="100%" height="100%" fill="white"></rect>'+xml+'</svg>';
    //If you just want the SVG then do console.log(xml)
    //Otherwise we render as an image and export to PNG
    var svgBase64 = "data:image/svg+xml;base64," + btoa(unescape(encodeURIComponent(xml)));
    var img = document.createElement('img');
    img.src = svgBase64;

    var canvas = document.createElement("canvas");
    canvas.width = Math.ceil(bbox.width) * scaleFactor;
    canvas.height = Math.ceil(bbox.height) * scaleFactor;
    var ctx = canvas.getContext('2d');
    ctx.scale(scaleFactor, scaleFactor);

    ctx.drawImage(img, 0, 0);
    //Opens the PNG image in a new tab for copying/saving
    window.open(canvas.toDataURL(), '_blank');
}



function initIO(interpreter, scope) {
        gauges = [];
        gaugearea.empty();

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


		  // Add an API function for the gauge() block.
		  var wrapper = function(label, val, min, max) {
		    if(!gauges.includes(label) ){
		        addGauge(label, val, min, max);
		        gauges.push(label);
                updateGauge(label, val, min, max);
		    }else{
                updateGauge(label, val, min, max);
			}
		  };
		  interpreter.setProperty(scope, 'setGauge',
			  interpreter.createNativeFunction(wrapper));

		  // Add an API function for the prompt() block.
		  var wrapper = function(text) {
			text = text ? text.toString() : '';
			return interpreter.createPrimitive(prompt(text));
		  };

		  interpreter.setProperty(scope, 'prompt',
			  interpreter.createNativeFunction(wrapper));


	}



