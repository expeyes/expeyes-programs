# -*- coding: utf-8 -*-

head="""\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
  <meta http-equiv="Content-Type" content="text/html; charset=utf-8"/>
  <title>{title}</title>
  <link rel="stylesheet" href="/inc/style.css" type="text/css" media="screen"/>
  <script type="text/javascript" src="http://{host}/javascript/jquery/jquery.js"></script>
  <script type="text/javascript" src="/inc/eyesJr.js"></script>
</head>
<body>
"""

foot="""\
<div id="interfaceOk">Detected Expeyes-Junior: {ok}</div>
<div id="validator">
  <a href="http://validator.w3.org/check?uri=referer">
    <img src="http://www.w3.org/Icons/valid-xhtml10" 
	 alt="Valid XHTML 1.0 Strict" 
	 height="31" width="88" />
  </a>
  <a href="http://jigsaw.w3.org/css-validator/check/referer">
    <img style="border:0;width:88px;height:31px"
	 src="http://jigsaw.w3.org/css-validator/images/vcss"
	 alt="CSS Valide !" />
  </a>
</div>
</body>
</html>
"""
