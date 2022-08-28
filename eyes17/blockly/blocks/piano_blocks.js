
//---------GAME

Blockly.Blocks['add_piano'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Add Piano")
    this.setColour(135);
 this.setTooltip("Add a Piano");
 this.setInputsInline(false);
 this.setPreviousStatement(true, null);
 this.setNextStatement(true, null);
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['add_piano'] = function(block) {
  var code = 'addPiano();\nsleep(0.1);\n';
  return code;
};


Blockly.Python['add_piano'] = function(block) {
  var code = 'addPiano()\n';
  return code;
};



Blockly.Blocks['play_piano'] = {
  init: function() {
    this.appendValueInput("NOTE")
        .setAlign(Blockly.ALIGN_LEFT)
        .appendField("Play Piano:(A,A#, B, C...")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Play Piano Note");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['play_piano'] = function(block) {
  var alt = Blockly.JavaScript.valueToCode(block, 'NOTE', Blockly.JavaScript.ORDER_NONE);
  var code = 'playPiano(' + alt +  ');\n';
  return code;
};


Blockly.Python['play_piano'] = function(block) {
  var alt = Blockly.Python.valueToCode(block, 'NOTE', Blockly.Python.ORDER_NONE);
  var code = 'playPiano(' + alt +  ')\n';
  return code;
};





var note, hints;
var audios = {};
var mykeys = {};



var addPiano = function(){

	registers.append(`
		<section id="main" style="width:100%">
		  <div class="nowplaying"></div>
			  <div class="keys">

				<div data-key="65" class="key" data-note="C">
					<span class="hints">A</span>
					<span class="nhints">C</span>
				</div>
				<div data-key="87" class="key sharp" data-note="C#">
					<span class="hints">W</span>
					<span class="nhints">C#</span>
				</div>
				<div data-key="83" class="key" data-note="D">
					<span class="hints">S</span>
					<span class="nhints">D</span>
				</div>
				<div data-key="69" class="key sharp" data-note="D#">
					<span class="hints">E</span>
					<span class="nhints">D#</span>
				</div>
				<div data-key="68" class="key" data-note="E">
					<span class="hints">D</span>
					<span class="nhints">E</span>
				</div>
				<div data-key="70" class="key" data-note="F">
					<span class="hints">F</span>
					<span class="nhints">F</span>
				</div>
				<div data-key="84" class="key sharp" data-note="F#">
					<span class="hints">T</span>
					<span class="nhints">F#</span>
				</div>
				<div data-key="71" class="key" data-note="G">
					<span class="hints">G</span>
					<span class="nhints">G</span>
				</div>
				<div data-key="89" class="key sharp" data-note="G#">
					<span class="hints">Y</span>
					<span class="nhints">G#</span>
				</div>
				<div data-key="72" class="key" data-note="A">
					<span class="hints">H</span>
					<span class="nhints">A</span>
				</div>
				<div data-key="85" class="key sharp" data-note="A#">
					<span class="hints">U</span>
					<span class="nhints">A#</span>
				</div>
				<div data-key="74" class="key" data-note="B">
					<span class="hints">J</span>
					<span class="nhints">B</span>
				</div>
				<div data-key="75" class="key" data-note="2C">
					<span class="hints">K</span>
					<span class="nhints">2C</span>
				</div>
				<div data-key="79" class="key sharp" data-note="2C#">
					<span class="hints">O</span>
					<span class="nhints">2C#</span>
				</div>
				<div data-key="76" class="key" data-note="2D">
					<span class="hints">L</span>
					<span class="nhints">2D</span>
				</div>
				<div data-key="80" class="key sharp" data-note="2D#">
					<span class="hints">P</span>
					<span class="nhints">2D#</span>
				</div>
				<div data-key="186" class="key" data-note="2E">
					<span class="hints">;</span>
					<span class="nhints">2E</span>
				</div>


			  </div>

			  <audio data-note="C" src="sounds/040.wav"></audio>
			  <audio  data-note="C#" src="sounds/041.wav"></audio>
			  <audio  data-note="D" src="sounds/042.wav"></audio>
			  <audio  data-note="D#" src="sounds/043.wav"></audio>
			  <audio  data-note="E" src="sounds/044.wav"></audio>
			  <audio  data-note="F" src="sounds/045.wav"></audio>
			  <audio  data-note="F#" src="sounds/046.wav"></audio>
			  <audio  data-note="G" src="sounds/047.wav"></audio>
			  <audio  data-note="G#" src="sounds/048.wav"></audio>
			  <audio  data-note="A" src="sounds/049.wav"></audio>
			  <audio  data-note="A#" src="sounds/050.wav"></audio>
			  <audio  data-note="B" src="sounds/051.wav"></audio>
			  <audio  data-note="2C" src="sounds/052.wav"></audio>
			  <audio  data-note="2C#" src="sounds/053.wav"></audio>
			  <audio  data-note="2D" src="sounds/054.wav"></audio>
			  <audio  data-note="2D#" src="sounds/055.wav"></audio>
			  <audio  data-note="2E" src="sounds/056.wav"></audio>
		  </section>
	`


	);

	const keys = document.querySelectorAll(".key");
	note = document.querySelector(".nowplaying");

	keys.forEach(key => key.addEventListener("transitionend", removeTransition));
	keys.forEach(key => key.addEventListener("touchstart", clicked));
	for(const x of ['C','C#','D','D#','E','F','F#','G','G#','A','A#','B','2C','2C#','2D','2D#','2E' ]){
		audios[x] = document.querySelector(`audio[data-note="${x}"]`);
		mykeys[x] = document.querySelector(`.key[data-note="${x}"]`);
	}

	window.addEventListener("keydown", playNote);


}

function clicked(e) {
playPiano(this.getAttribute("data-note"));
	}

function playPiano(notename) {
	  const audio = audios[notename]; // document.querySelector(`audio[data-note="${notename}"]`),
	  key = mykeys[notename];//document.querySelector(`.key[data-note="${notename}"]`);
	  if (!key) return;
	  key.classList.add("playing");
	  note.innerHTML = notename;
	  audio.currentTime = 0;
	  audio.play();
	}


function playNote(e) {
  key = document.querySelector(`.key[data-key="${e.keyCode}"]`);
  if (!key) return;
  const keyNote = key.getAttribute("data-note");
  playPiano(keyNote);
}

function removeTransition(e) {
	  if (e.propertyName !== "transform") return;
	  this.classList.remove("playing");
	}









function initPiano(interpreter, scope) {


		  // Add an API for the Add Piano call
		  interpreter.setProperty(scope, 'addPiano', interpreter.createNativeFunction(
				function() {
				  return addPiano();
				})
			);
		  // Add an API for the Play Music call
		  interpreter.setProperty(scope, 'playPiano', interpreter.createNativeFunction(
				function(mynote) {
				  return playPiano(mynote);
				})
			);



}
