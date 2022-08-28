
//-------------------- API ------------------------

function initApi(interpreter, scope) {

		  // Add an API function for highlighting blocks.
		  var wrapper = function(id) {
			return workspacePlayground.highlightBlock(id);
		  };
		  interpreter.setProperty(scope, 'highlightBlock',
			  interpreter.createNativeFunction(wrapper));

		  // Add an API function for the (alert) print() block.
		  var wrapper = function(text) {
			return results.html(results.html()+text+"<br>");
			//return document.getElementById("resulttext").innerHTML+=text+"<br>";
		  };
		  interpreter.setProperty(scope, 'alert',
			  interpreter.createNativeFunction(wrapper));
		  interpreter.setProperty(scope, 'print',
			  interpreter.createNativeFunction(wrapper));

		  // Add an API function for the prompt() block.
		  var wrapper = function(text) {
			text = text ? text.toString() : '';
			return interpreter.createPrimitive(prompt(text));
		  };

		  interpreter.setProperty(scope, 'prompt',
			  interpreter.createNativeFunction(wrapper));



		  // Add an API for the wait block.  See wait_block.js
		  var wrapper = interpreter.createAsyncFunction(
			function(timeInSeconds, callback) {
			  // Delay the call to the callback.
			  setTimeout(callback, timeInSeconds * 1000);
			});
		  interpreter.setProperty(scope, 'waitForSeconds', wrapper);
		  interpreter.setProperty(scope, 'sleep', wrapper);

		  // Add an API function for highlighting blocks.
		  var wrapper = function(id) {
			id = id ? id.toString() : '';
			return interpreter.createPrimitive(highlightBlock(id));
		  };
		  interpreter.setProperty(scope, 'highlightBlock',
			  interpreter.createNativeFunction(wrapper));

			// PLOT CALLS
		  // Add an API for the plot call
		  interpreter.setProperty(scope, 'plot', interpreter.createNativeFunction(
				function( value) {
				  return addDataPoint(value);
				})
			);

		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_xy', interpreter.createNativeFunction(
				function( vx,vy) {
				  return addDataPointXY(vx,vy);
				})
			);


		  // Add an API for the XY array plot call
		  interpreter.setProperty(scope, 'plot_xyarray', interpreter.createNativeFunction(
				function( mydata) {
				  return plotArraysXY(mydata);
				})
			);

		  // Add an API for the XY plot call
		  interpreter.setProperty(scope, 'plot_xarray_yarray', interpreter.createNativeFunction(
				function( X,Y) {
				  return plotXArrayYArray(X,Y);
				})
			);


		  // Add an API for the XYY array plot call
		  interpreter.setProperty(scope, 'plot_xyyarray', interpreter.createNativeFunction(
				function( mydata) {
				  return plotArraysXYY(mydata);
				})
			);

		  // Add an API for the Polar plot call
		  interpreter.setProperty(scope, 'plot_radar', interpreter.createNativeFunction(
				function( angle,radius, maxrad) {
				  return addDataPointPolar(angle,radius, maxrad);
				})
			);



			// File writing calls
		  // Add an API for the writeToFile call
		  interpreter.setProperty(scope, 'write_to_file', interpreter.createNativeFunction(
				function(fname, txt, newline) {
					if(newline){txt+='\n';}
			  return MyJavascriptInterface.writeToFile(fname,txt);
				})
			);

          // EXPEYES API CALLS

		  // Add an API for the get_sensor call
		  interpreter.setProperty(scope, 'get_sensor', interpreter.createAsyncFunction(
				function(sensor,param, callback) {
				  return MyJavascriptInterface.get_sensor(sensor,param, callback);
				})
			);

		  // Add an API for the set_PCA9685 call
		  interpreter.setProperty(scope, 'set_PCA9685', interpreter.createNativeFunction(
				function(channel, value) {
				  return MyJavascriptInterface.set_PCA9685(channel,value);
				})
			);

		  // Add an API for the set_servo call
		  interpreter.setProperty(scope, 'set_servo', interpreter.createNativeFunction(
				function(channel, value) {
				  return MyJavascriptInterface.set_servo(channel,value);
				})
			);






	}



