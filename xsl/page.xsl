<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns="http://www.w3.org/1999/xhtml">

<xsl:import href="fragment.xsl"/>

<xsl:output method="html"
	    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
	    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
	    version="1.0"/>


<xsl:template match="page">
  <html>
    <head>
      <title></title>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <script type="text/javascript" src="../scripts/script.js"></script>
      <link rel="stylesheet" type="text/css" href="../stylesheets/styles.css"/>
    </head>
    <body>
      <div class="page">
	<div class="titleblock">
	  <h1><xsl:value-of select="@title"/></h1>
	  <xsl:if test="@subtitle">
	    <h2><xsl:value-of select="@subtitle"/></h2>
	  </xsl:if>
	  <p>
	    <a>
	      <xsl:attribute name="href"><xsl:value-of select="@prev"/></xsl:attribute>
	    Prev</a>
	    <xsl:text> | </xsl:text>
	    <a href="index.html">Index</a>
	    <xsl:text> | </xsl:text>
	    <a>
	      <xsl:attribute name="href"><xsl:value-of select="@next"/></xsl:attribute>
	    Next</a>
	  </p>
	</div>
	<xsl:if test="count(section) > 1">
	  <div class="pageindex">
	    <xsl:for-each select="section">
	      <p><a>
		<xsl:attribute name="href">
		  #sid<xsl:value-of select="@sid"/>
		</xsl:attribute>
		<xsl:value-of select="@sid"/>: <xsl:value-of select="@title"/>
	      </a></p>
	    </xsl:for-each>
	  </div>
	</xsl:if>
	  <xsl:apply-templates/>
	<div class="footerblock">
	  <p>
	    <a>
	      <xsl:attribute name="href"><xsl:value-of select="@prev"/></xsl:attribute>
	    Prev</a>
	    <xsl:text> | </xsl:text>
	    <a href="index.html">Index</a>
	    <xsl:text> | </xsl:text>
	    <a>
	      <xsl:attribute name="href"><xsl:value-of select="@next"/></xsl:attribute>
	    Next</a>
	  </p>
	</div>
      </div>
    </body>
  </html>
</xsl:template>


<xsl:template match="section">
  <div class="section">
    <xsl:attribute name="id">sid<xsl:value-of select="@sid"/></xsl:attribute>
    <h1 class="sectionheading"><xsl:value-of select="@sid"/>: <xsl:value-of select="@title"/></h1>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="filename">
  <xsl:apply-templates select="document(@href)"/>
</xsl:template>

</xsl:stylesheet>