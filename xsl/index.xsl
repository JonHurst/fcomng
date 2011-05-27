<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns="http://www.w3.org/1999/xhtml">

<xsl:output method="xml"
	    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
	    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
	    encoding="utf-8"
	    version="1.0"/>

<xsl:template match="index">
  <html>
    <head>
      <title>Index</title>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <link rel="stylesheet" type="text/css" href="../stylesheets/styles.css"/>
    </head>
    <body>
      <div class="page">
	<div class="titleblock">
	  <h1>easyJet FCOM NG - XHTML version - G-EJAR build</h1>
	  <h2>Version 0.9 (Prototype)</h2>
	</div>
	<div class="index">
	  <xsl:for-each select="book">
	    <p>
	      <a>
		<xsl:attribute name="href">
		  #<xsl:value-of  select="@id"/>
		</xsl:attribute>
		<xsl:value-of select="@id"/>
		<xsl:text>: </xsl:text>
		<xsl:value-of select="@title"/>
	      </a>
	    </p>
	  </xsl:for-each>
	</div>
	<xsl:apply-templates/>
      </div>
    </body>
  </html>
</xsl:template>


<xsl:template match="book">
  <div class="index">
    <xsl:copy-of select="@id"/>
    <h1 class="title"><xsl:value-of select="@title"/></h1>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="a">
  <p><a><xsl:copy-of select="@href"/><xsl:value-of select="."/></a></p>
</xsl:template>


<xsl:template match="h1">
  <h1><xsl:value-of select="."/></h1>
</xsl:template>

</xsl:stylesheet>
