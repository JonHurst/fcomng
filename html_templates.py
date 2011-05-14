
page = """\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <title>%(title)s</title>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
    <script type="text/javascript" src="../scripts/script.js"></script>
    <link rel="stylesheet" type="text/css" href="../stylesheets/styles.css"/>
  </head>
  <body>
    <div class="page">
       %(fragments)s
    </div>
  </body>
</html>
"""

titleblock = """\
<div class="titleblock">
<h2>%(sid)s</h2>
<h1>%(title)s</h1>
<h2>%(subtitle)s</h2>
<div class="links"><a href="%(next)s">Next</a></div>
</div>
"""

footerblock="""\
<div class="footerblock">
<div class="links"><a href="%(next)s">Next</a></div>
</div>
"""


