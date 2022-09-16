
//---------GAME

Blockly.Blocks['add_game'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Add Game")
        .appendField(new Blockly.FieldImage("media/bird.png", 30, 30, { alt: "*", flipRtl: "FALSE" }));
    this.setColour(135);
 this.setTooltip("Add a bird game");
 this.setInputsInline(false);
 this.setPreviousStatement(true, null);
 this.setNextStatement(true, null);
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['add_game'] = function(block) {
  var code = 'addGame();\nsleep(0.1);\n';
  return code;
};


Blockly.Python['add_game'] = function(block) {
  var code = 'addGame()\n';
  return code;
};

Blockly.Blocks['stop_game'] = {
  init: function() {
    this.appendDummyInput()
        .appendField("Stop Game")
        .appendField(new Blockly.FieldImage("media/bird.png", 30, 30, { alt: "*", flipRtl: "FALSE" }));
    this.setColour(230);
 this.setTooltip("Stop the bird game");
 this.setInputsInline(false);
 this.setPreviousStatement(true, null);
 this.setNextStatement(true, null);
 this.setHelpUrl("");
  }
};

Blockly.JavaScript['stop_game'] = function(block) {
  var code = 'stopGame();\n';
  return code;
};


Blockly.Python['stop_game'] = function(block) {
  var code = 'stopGame()\n';
  return code;
};



Blockly.Blocks['set_bird_y'] = {
  init: function() {
    this.appendValueInput("Y")
        .setAlign(Blockly.ALIGN_LEFT)
        .appendField("Bird's Altitude (0 to 1000): ")
    this.setInputsInline(false);
    this.setPreviousStatement(true, null);
    this.setNextStatement(true, null);
    this.setColour(230);
 this.setTooltip("Set Bird's Height");
 this.setHelpUrl("");
  }
};


Blockly.JavaScript['set_bird_y'] = function(block) {
  var alt = Blockly.JavaScript.valueToCode(block, 'Y', Blockly.JavaScript.ORDER_NONE);
  var code = 'setBirdY(' + alt +  ');\nsleep(0.001);\n';
  return code;
};


Blockly.Python['set_bird_y'] = function(block) {
  var alt = Blockly.Python.valueToCode(block, 'Y', Blockly.Python.ORDER_NONE);
  var code = 'setBirdY(' + alt +  ')\n';
  return code;
};



/* --- Credit https://raw.githubusercontent.com/danba340/tiny-flappy-bird/master/index.html --*/

var birdX = score = bestScore = 0;
var birdSize = pipeWidth = topPipeBottomY = 24;
var interval = 40;
var birdY = pipeGap = 200;
var intervalID;

var context;
const bird = new Image();

var blit = function() {
	context.fillStyle = "skyblue";
	context.fillRect(0,0,canvasSize,canvasSize); // Draw sky
	context.drawImage(bird, birdX, birdY, birdSize * (524/374), birdSize); // Draw bird
	context.fillStyle = "green";
	context.fillRect(pipeX, 0, pipeWidth, topPipeBottomY); // Draw top pipe
	context.fillRect(pipeX, topPipeBottomY + pipeGap, pipeWidth, canvasSize); // Draw bottom pipe
	context.fillStyle = "blue";
	context.fillText(score++, 9, 25); // Increase and draw score
	context.fillText(`Best: ${bestScore}`, 9, 50); // Draw best score
}

var updateBird = function() {
	blit();
	pipeX -= 4; // Move pipe
	pipeX < -pipeWidth && // Pipe off screen?
	((pipeX = canvasSize), (topPipeBottomY = pipeGap * Math.random())); // Reset pipe and randomize gap.
	bestScore = bestScore < score ? score : bestScore; // New best score?
	if(((birdY < topPipeBottomY || birdY > topPipeBottomY + pipeGap) && pipeX < birdSize * (524/374)) ){// bird hit the pipe
	      context.fillStyle = "red";
	      context.fillRect(0,0,canvasSize,canvasSize); // Draw RED sky
	      birdY = 200;
	      pipeX = canvasSize;
	      score = 0; // Bird died
	     }
}

var addGame = function(){
	canvasSize = pipeX = resultplots.width()<400?400:resultplots.width();
        resplotarea.show();
	resultplots.append(
	`
	<div style="height: 400px; background: #111; text-align: center;touch-action: manipulation;">
	  <canvas id="c" width="$(pipeX)" height="400"></canvas>
	</div>
	`
	);
	context = c.getContext("2d");


	bird.src = "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABUAAAAOCAYAAADABlfOAAAA/0lEQVQ4y72TQWrDMBBF38gCqwtvC120YOgFegL3DrlFeppSanqc5iAlPUCgCy+kQOLJJkrkWE4TKBXMRuK/+fojwX8t773b1wzQXHnvn6b0ktt0ggIEe0v9+jU4W84rVBURIYRgnHN6qrcZpt69dxRs2J4cRyAQwX3OnElh+2I5r36NSERQ1dhEc041OkhFFCX12+rqmcgUNIXXbZeNYGAgicBe66JuuwgZzSKC7bGZDNwerp+4jE77RZltaJq1AqOWB+pj+5Odfr8oMc36bJx2KuOc4v4jYJoK/RynJs+b848foEjAD0kEaizfLzdjwfbIkwvno5f8xNzj/7O1A51fZ+BxD7C5AAAAAElFTkSuQmCC";


    //c.onclick = () => (birdDY = 9) ;


    intervalID = setInterval(updateBird, interval)


}


function setBirdY(val){ // 0-1000. scaled to 0-400
	birdY = 400 - val/2.5;
	blit();
}

function stopGame(){
  if(intervalID != null)clearInterval(intervalID);
}




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









//-------------------- API ------------------------

function initGames(interpreter, scope) {

		  // Add an API for the Add Game call
		  interpreter.setProperty(scope, 'addGame', interpreter.createNativeFunction(
				function() {
				  return addGame();
				})
			);
		  // Add an API for the Add Game call
		  interpreter.setProperty(scope, 'stopGame', interpreter.createNativeFunction(
				function() {
				  return stopGame();
				})
			);
		  // Add an API for the Add Game call
		  interpreter.setProperty(scope, 'setBirdY', interpreter.createNativeFunction(
				function(y) {
				  return setBirdY(y);
				})
			);

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



