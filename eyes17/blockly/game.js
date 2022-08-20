
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


