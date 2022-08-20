
$(document).ready(function(){

                $('.launchsvg').bind('click', function(){
                  var link= $(this).attr('href');
				  MyJavascriptInterface.openSVG(link);
                });

                $('.launchxml').bind('click', function(){
                  var link= $(this).attr('href');
				  MyJavascriptInterface.openXML(link);
                });


        }); 

