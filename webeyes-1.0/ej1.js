/**
 * adds two sizes in px
 * @param a a string terminated by "px"
 * @param b a string terminated by "px"
 * @return the sum of both values, as an integer
 **/
function pxAdd(a,b){
    var result=0;
    var pat= /(\S+)px/;
    var ar=a.match(pat);
    if (ar != null){
	result += parseFloat(ar[1]);
    }
    var br=b.match(pat);
    if (br != null){
	result += parseFloat(br[1]);
    }
    return result;
}

var leftButtons=[
    {id: "A1",  c: 0, l: 0,  f: "black", b: "wheat"},
    {id: "A2",  c: 0, l: 1,  f: "black", b: "wheat"},
    {id: "IN1", c: 0, l: 2,  f: "black", b: "wheat"},
    {id: "IN2", c: 0, l: 3,  f: "black", b: "wheat"},
    {id: "SEN", c: 0, l: 4,  f: "black", b: "wheat"},
    {id: "SQ1", c: 0, l: 5,  f: "black", b: "wheat"},
    {id: "SQ2", c: 0, l: 6,  f: "black", b: "wheat"},
    {id: "OD1", c: 0, l: 7,  f: "blue",  b: "beige"},
    {id: "CCS", c: 0, l: 8,  f: "blue",  b: "beige"},
    {id: "NML", c: 0, l: 9,  f: "black", b: "khaki"},
    {id: "FTR", c: 0, l: 10, f: "black", b: "khaki"},
    {id: "FIT", c: 0, l: 11, f: "black", b: "khaki"},
    {id: "DEL", c: 0, l: 12, f: "black", b: "khaki"},

    {id: "ATR", c: 1, l: 0,  f: "black",   b: "wheat"},
    {id: "WHI", c: 1, l: 1,  f: "black",   b: "wheat"},
    {id: "WLO", c: 1, l: 2,  f: "black",   b: "wheat"},
    {id: "WRE", c: 1, l: 3,  f: "black",   b: "wheat"},
    {id: "WFE", c: 1, l: 4,  f: "black",   b: "wheat"},
    {id: "SHI", c: 1, l: 5,  f: "blue",    b: "beige"},
    {id: "SLO", c: 1, l: 6,  f: "blue",    b: "beige"},
    {id: "HTP", c: 1, l: 7,  f: "blue",    b: "beige"},
    {id: "LTP", c: 1, l: 8,  f: "blue",    b: "beige"},
    {id: "CH1", c: 1, l: 9,  f: "black",   b: "khaki"},
    {id: "CH2", c: 1, l: 10, f: "red",     b: "khaki"},
    {id: "CH3", c: 1, l: 11, f: "blue",    b: "khaki"},
    {id: "CH4", c: 1, l: 12, f: "magenta", b: "khaki"},
];

var leftSliders=[
    {id:"timeScale", min: 1, max: 10, value: 1, title: "ms/div"},
    {id:"voltScale", min: 1, max: 10, value: 1, title: "V/div"},
    {id:"trigScale", min: 1, max: 10, value: 5, title: "trigger"},
];

var rightSliders=[
    {id:"CH1", min: 0, max: 100, value: 50, color: "black"},
    {id:"CH2", min: 0, max: 100, value: 50, color: "red"},
    {id:"CH3", min: 0, max: 100, value: 50, color: "blue"},
    {id:"CH4", min: 0, max: 100, value: 50, color: "magenta"},
];

$(function () {
    // this function is launched when the page is downloaded
    for (i=0; i<leftButtons.length; i++){
	//adds draggable buttons inside "#leftButtons"
	var b = leftButtons[i]
	var div = $("<div id=drag-"+b.id+"/>");
	div.addClass("drag-item");
	var x = 2 + 40 * b.c;
	var y = 0 + 25 * b.l + 6*Math.floor(b.l/9)
	div.css("top",y+"px");
	div.css("left",x+"px");
	div.css("color",b.f);
	div.css("background-color",b.b);
        div.css('z-index', '100');
	div.text(b.id);
	$("#leftButtons").append(div);
    }
    // makes some buttons in "#leftButtons" draggable
    $("#leftButtons div[id^='drag']").draggable({
        containment: "parent",
        stack: ".drag",
	opacity: 0.8,
	revert: true,
	scroll: false,
	start: function() {
	    // lifts the button when drag starts
            $(this).effect("highlight", {}, 1000);
	    $(this).css( "cursor","move" );
            $(this).css('z-index', '110');
	},
	stop: function(event,ui) {
	    // lowers the button when drag stops
            $(this).css("cursor","default");
            $(this).css('z-index', '100');
        }
    }).droppable({
	accept: ".drag-item",
	tolerance: "intersect",
	drop: function(event,ui){
	    alert(event.originalEvent.target.id+" dropped on "+event.target.id);
	}
    });
    // add the left sliders
    for (i=0; i<leftSliders.length; i++){
	//adds draggable buttons inside "#leftButtons"
	var s = leftSliders[i]
	var div0 = $("<div id=title-slider-"+s.id+"/>");
	div0.text(s.title)
	$("#leftSliders").append(div0);
	var div1 = $("<div id=slider-"+s.id+"/>");
	div1.addClass("left-slider");
	div1.min=s.min;
	div1.max=s.max;
	div1.value=s.value;
	div1.slider({
	    min: s.min,
	    max: s.max,
	    value: s.value,
	    step: 1,
	    change: function(event,ui){
		alert(event.target.id+" = "+ui.value);
	    },
	});
	$("#leftSliders").append(div1);
    }
    // add a canvas for the CRO's screen
    var canvas = document.getElementById("cro-canvas");
    var ctx = canvas.getContext('2d');
    ctx.strokeStyle = "grey";
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(canvas.width / 2, 0);
    ctx.lineTo(canvas.width / 2, canvas.height);
    ctx.moveTo(0, canvas.height / 2);
    ctx.lineTo(canvas.width, canvas.height / 2);
    ctx.stroke();

    ctx.strokeStyle = "black";
    ctx.strokeRect(0, 0, canvas.width, canvas.height)

    ctx.strokeStyle = "grey";
    if ( ctx.setLineDash !== undefined )   ctx.setLineDash([1,4]);
    if ( ctx.mozDash !== undefined )       ctx.mozDash = [1,4];
    ctx.beginPath();
    for (var i=1; i< 10; i++){
	ctx.moveTo(canvas.width / 10 * i, 0);
	ctx.lineTo(canvas.width / 10 * i, canvas.height);
    }
    for (var i=1; i< 10; i++){
	ctx.moveTo(0, canvas.height / 10 * i);
	ctx.lineTo(canvas.width, canvas.height / 10 * i);
    }
    ctx.stroke();

    // add the right sliders
    for (i=0; i<rightSliders.length; i++){
	//adds draggable buttons inside "#leftButtons"
	var s = rightSliders[i]
	var div1 = $("<div id=slider-"+s.id+"/>");
	div1.addClass("right-slider");
	div1.min=s.min;
	div1.max=s.max;
	div1.value=s.value;
	div1.slider({
	    orientation: "vertical",
	    min: s.min,
	    max: s.max,
	    value: s.value,
	    step: 1,
	    change: function(event,ui){
		alert(event.target.id+" = "+ui.value);
	    },
	});
	div1.children(".ui-slider-handle").css("background", s.color);
	$("#rightSliders").append(div1);
    }

});

