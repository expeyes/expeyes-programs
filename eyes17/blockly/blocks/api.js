
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

		  // Add APIs for the sine fit analysis calls
		  interpreter.setProperty(scope, 'capture_analysis', interpreter.createNativeFunction(
				function(param) {
				  return MyJavascriptInterface.capture_analysis(param);
				})
			);

		  // Add APIs for the sine fit analysis calls
		  interpreter.setProperty(scope, 'capture_analysis_dual', interpreter.createNativeFunction(
				function(param) {
				  return MyJavascriptInterface.capture_analysis_dual(param);
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

		  // Add an API for the get_voltage call
		  interpreter.setProperty(scope, 'get_voltage', interpreter.createAsyncFunction(
				function(channel, callback) {
				  return MyJavascriptInterface.get_voltage(channel, callback);
				})
			);


		  // Add an API for the set_voltage call
		  interpreter.setProperty(scope, 'set_voltage', interpreter.createAsyncFunction(
				function(channel, value, callback) {
				  return MyJavascriptInterface.set_voltage(channel,value, callback);
				})
			);

		  // Add an API for the get_frequency call
		  interpreter.setProperty(scope, 'get_frequency', interpreter.createAsyncFunction(
				function(channel, callback) {
				  return MyJavascriptInterface.get_frequency(channel, callback);
				})
			);

		  // Add an API for the set_frequency call
		  interpreter.setProperty(scope, 'set_frequency', interpreter.createAsyncFunction(
				function(channel, value, callback) {
				  return MyJavascriptInterface.set_frequency(channel,value, callback);
				})
			);

		  // Add an API for the set_state call
		  interpreter.setProperty(scope, 'set_state', interpreter.createAsyncFunction(
				function(channel, value, callback) {
				  return MyJavascriptInterface.set_state(channel,value, callback);
				})
			);



		  // Add an API for the multi_r2r call
		  interpreter.setProperty(scope, 'multi_r2r', interpreter.createAsyncFunction(
				function(channel,edges,timeout, callback) {
				  return MyJavascriptInterface.multi_r2r(channel,edges,timeout, callback);
				})
			);



		  // Add an API for the capture block.  copied from wait_block. Async attempt
		  var wrapper = function capture1(channel, ns, tg, callback) {
			  MyJavascriptInterface.capture1(channel , ns ,tg, callback);
		  };
		  interpreter.setProperty(scope, 'capture1', interpreter.createAsyncFunction(wrapper));

		  // Add an API for the capture block.  copied from wait_block. Async attempt
		  var wrapper = function capture2(channel, ns, tg, callback) {
			  MyJavascriptInterface.capture2(channel , ns ,tg, callback);
		  };
		  interpreter.setProperty(scope, 'capture2', interpreter.createAsyncFunction(wrapper));

		  // Add an API for the trigger block.  
		  var wrapper = function scope_trigger(channel, level, state, callback) {
			  return MyJavascriptInterface.scope_trigger(channel ,level, state, callback);
		  };
		  interpreter.setProperty(scope, 'scope_trigger', interpreter.createAsyncFunction(wrapper));



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





	}



