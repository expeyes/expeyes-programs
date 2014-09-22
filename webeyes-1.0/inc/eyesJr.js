/**
 * Javascript routines to support an interaction with expEYES-Jr
 **/

/**
 * Callback function for a widget which features a select element and
 * a neighboring div to display the result of a measurement
 * @param sel the select element (from the DOM tree)
 **/
function adcWjson(sel){
    var option=$(sel).find(":selected");
    var name=option.text();
    var val=option.val();
    console.log(name, val);
    $.getJSON(
	"/eyesJSON", {
	    fun: "allADC",
	    name: name,
	    val: val,
	}
    ).done(function(data){
	/* console.log("done:", data); */
	$(sel).next("div").text(data.name+": "+data.voltage+" V");
    }).fail(function(jqxhr, textStatus, error){
	var err = textStatus + ", " + error;
	/* console.log("Request Failed: " + err); */
	$(sel).next("div").text("Request Failed: " + err);
    });
}