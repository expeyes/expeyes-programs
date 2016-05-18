<!--
Responsive web interface for expEYES Junior connected to server
Copyright 2016,  Authors : Rakesh K M(rakeshkm2203@gmail.com), Manoj.S.Nair(manojsnair007@gmail.com), Jishnu R(jishnu47@gmail.com) [Amrita School of Engineering, Amritapuri Campus, Kollam 690525, Kerala]
License : GNU GPL version 3
-->
<!DOCTYPE html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <!-- The above 3 meta tags *must* come first in the head; any other head content must come *after* these tags -->
    <meta name="description" content="expEYES Web Interface by JARMS">
    <meta name="author" content="JARMS 2016">
    <link rel="icon" href="images/favicon.ico">
    <title>expEYES | Control Panel</title>
    <!-- Bootstrap core CSS -->
    <link href="css/bootstrap.custom.css" rel="stylesheet">
    <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
    <link href="css/ie10-viewport-bug-workaround.css" rel="stylesheet">
    <!-- Custom styles for this page -->
    <link href="css/jumbotron-narrow.css" rel="stylesheet">
    <script src="js/jquery.min.js"></script>
    <script src="js/bootstrap.min.js"></script>
    <script src="js/ie-emulation-modes-warning.js"></script>
    <!-- CDN Files-->
    <!--<link rel="stylesheet" href="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/css/bootstrap.min.css">
    <script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.0/jquery.min.js"></script>
    <script src="http://maxcdn.bootstrapcdn.com/bootstrap/3.3.6/js/bootstrap.min.js"></script>-->
    <!-- HTML5 shim and Respond.js for IE8 support of HTML5 elements and media queries -->
    <!--[if lt IE 9]>
    <script src="https://oss.maxcdn.com/html5shiv/3.7.2/html5shiv.min.js"></script>
    <script src="https://oss.maxcdn.com/respond/1.4.2/respond.min.js"></script>
    <![endif]-->
  </head>
  <body>
    <script type="text/javascript">
    $(document).ready(function(){
    $("#start").click(function(){
    dataType: 'json';
    $.post('/cgi-bin/expeyes_status.cgi',
    function(data){
    if (isNaN(data.a1)||isNaN(data.a2)||isNaN(data.in1)||isNaN(data.in2)){
    alert(data.a2)
    }
    $('.A1').text(data.a1);
    $('.A2').text(data.a2);
    $('.IN1').text(data.in1);
    $('.IN2').text(data.in2);
    $('#status').text("expEYES : Connected");
    });
    });
    });
    $(document).ready(function(){
    $("#submit").click(function(){
    $.post('/cgi-bin/expeyes_setoutput.cgi',
    {pvs: $('#pvs').val(),
    od1: $('#od1').val(),
    sqr1: $('#sqr1').val(),
    sqr2: $('#sqr2').val()
    } );
    });
    });
    </script>
    <div class="container">
      <!-- Nav Menu -->
      <div class="header clearfix">
        <nav>
          <ul class="nav nav-pills pull-right">
            <li role="presentation"><a href="http://www.amrita.edu">Home</a></li>
            <li role="presentation" class="active"><a href="#">Experiments</a></li>
            <li role="presentation"><a href="#">Account</a></li>
            <li role="presentation"><a href="#">Logout</a></li>
          </ul>
        </nav>
        <!-- Page Heading -->
        <h3 class="page-header"><strong>Amrita AutoDAQ 2016</strong></h3>
      </div>
      <!-- Experiment Section -->
      <div class="exp_info">
        <h2 class="text-center">expEYES Junior</br>
        <small class="text-center">Experiments for Young Engineers and Scientists</small></h2></br>
        <p class="text-center"> This is a dashboard for controlling expEYES connected to the server.</p>
      </div>
      <div class="jumbotron">
        <div class="container">
          <!-- Video Feed Section -->
          <div class="row">
            <div class="col-md-6">
              <div class="row">
                <div class="panel-heading"><h4 id="status">expEYES : Disconnected</h4></div>
                <div id="expeyes_pic" class="col-md-12" style="width:auto">
                  <img src="images/expeyes.png" alt="expeyes" class="img-rounded col-md-12 col-sd-12 col-xs-12 center-block">
                </div>
              </div>
              </br>
              <div class="col-md-12">
                <div class="row center-block">
                  <button id="start" class="btn center-block btn-success">Request Status</button>
                </div>
              </div>
            </div>
            </br>
            <!-- Experiment Control Panel -->
            <div class="col-md-6">
              <div class="row">
                <div class="panel panel-default">
                  <div class="panel-heading"><h4>Input Pins : Status</h4></div>
                  <div class="panel-body" style="text-align:center">
                    <div class="col-md-12"><small><strong>A1 : </strong></small><span class="A1">0.0000</span> V</div>
                    <div class="col-md-12"><small><strong>A2 : </strong></small><span class="A2">0.0000</span> V</div>
                    <div class="col-md-12"><small><strong>IN1 : </strong></small><span class="IN1">0.0000</span> V</div>
                    <div class="col-md-12"><small><strong>IN2 : </strong></small><span class="IN2">0.0000</span> V</div>
                  </div>
                </div>
              </div>
            </div>
            <div class="col-md-6">
              <div class="row">
                <div class="panel panel-default">
                  <div class="panel-heading">
                    <div class="panel-title">
                      <h4>Set Output Pins</h4>
                    </div>
                  </div>
                  <div class="panel-body">
                    <div class="form form-vertical">
                      <div class="control-group col-md-6">
                        <label>PVS</label>
                        <div class="controls">
                          <input type="text" id="pvs" class="form-control" placeholder="0 to +5V">
                        </div>
                      </div>
                      <div class="control-group col-md-6">
                        <label>OD1</label>
                        <div class="controls">
                          <select id="od1" class="form-control"><option>0</option><option>1</option></select>
                        </div>
                      </div>
                      <div class="control-group col-md-6">
                        <label>SQR1</label>
                        <div class="controls">
                          <input type="text" id="sqr1" class="form-control" placeholder="0.7-100k Hz" style="padding:6px 10px">
                        </div>
                      </div>
                      <div class="control-group col-md-6">
                        <label>SQR2</label>
                        <div class="controls">
                          <input type="text" id="sqr2" class="form-control" placeholder="0.7-100k Hz" style="padding:6px 10px">
                        </div>
                      </div>
                      <div class="control-group">
                        <label>&nbsp;</label>
                        <div class="controls">
                          <button type="submit" id="submit" class="btn btn-primary">
                          Submit
                          </button>
                        </div>
                      </div>
                    </div>
                    </div><!--/panel content-->
                  </div>
                  </div><!--/panel-->
                </div>
              </div>
            </div>
          </div>
          <!-- About Us Modal content-->
          <div id="about_us" class="modal fade" role="dialog">
            <div class="modal-dialog modal-lg">
              <div class="modal-content">
                <div class="modal-header">
                  <button type="button" class="close" data-dismiss="modal">&times;</button>
                  <h4 class="modal-title text-center">Amrita AutoDAQ 2016</h4>
                </div>
                <div class="modal-body col-md-12">
                  <h4 class="text-center"><strong>Team</strong></h4>
                  <div class="col-md-6">
                    <p class="text-center">Abhijith</p>
                    <p class="text-center">Jishnu</p>
                    <p class="text-center">Manoj</p>
                    <p class="text-center">Rakesh</p>
                    <p class="text-center">Sucheth</p>
                    <p class="text-center">Gayathri Narayanan</p>
                  </div>
                  <div class="col-md-6">
                    <p class="text-center">Anand Ramachandran</p>
                    <p class="text-center">Ullas Ramanadhan</p>
                  </div>
                  <div class="col-md-12">
                    <div class="col-md-6">
                      <p class="text-center" style="font-size:12px">
                      <strong>Department of Electronics and Communication Engineering.</strong></p>
                    </div>
                    <div class="col-md-6">
                      <p class="text-center" style="font-size:12px">
                      <strong>Amrita Center for Wireless Networks and Applications.</strong></p>
                    </div>
                    <div class="col-md-12" style="font-size:14px">
                      <p class="text-center"><strong>Amrita Vishwa Vidyapeetham</br>Amritapuri Campus</strong></p>
                      <p class="text-center">Contact : <a href="mailto:amrita-autodaq@googlegroups.com">amrita-autodaq@googlegroups.com</a></p>
                    </div>
                  </div>
                </div>
                <!-- Footer content-->
                <div class="modal-footer">
                  <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
                </div>
              </div>
            </div>
          </div>
          <footer class="footer">
            <p data-toggle="modal" data-target="#about_us">Made with love by JARMS | Amrita Vishwa Vidyapeetham<span class=pull-right><?php echo 'Server :'.$_SERVER{'SERVER_NAME'}.' | '.'Client :'.$_SERVER['REMOTE_ADDR'];?><span></p>
          </footer>
        </div>
        <!-- container -->
        <!-- IE10 viewport hack for Surface/desktop Windows 8 bug -->
        <script src="js/ie10-viewport-bug-workaround.js"></script>
      </body>
    </html>