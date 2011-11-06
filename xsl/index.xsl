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
  <xsl:variable name="title">
    <xsl:if test="@ident">
      <xsl:value-of select="@ident"/><xsl:text>: </xsl:text>
    </xsl:if>
    <xsl:value-of select="@title"/>
  </xsl:variable>
  <html>
    <head>
      <title><xsl:value-of select="$title"/></title>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <link rel="stylesheet" type="text/css" href="../stylesheets/styles.css"/>
      <script type="text/javascript" src="../scripts/fleet.js"></script>
      <script type="text/javascript" src="../scripts/script.js"></script>
    </head>
    <body onload="set_folding_reg();">
      <div class="page">
        <div class="titleblock">
          <h1>easyJet A319/A320 FCOM (<xsl:value-of select="@version"/>)</h1>
          <h2><xsl:value-of select="@title"/></h2>
        </div>
        <xsl:comment>linkbar</xsl:comment>
        <div class="index">
          <div class="foldmessage">
            <p>This manual is pre-folded for <span id="folding_reg">G-XXXX</span>.
            (<a href="change-reg.html">change</a>)</p>
          </div>
          <xsl:apply-templates/>
        </div>
      </div>
    </body>
  </html>
</xsl:template>


<xsl:template match="section">
  <xsl:variable name="foldsection" select="ancestor::section
                                           or @ident = 'OEB' or @ident = 'FCB'"/><!--special case folding-->
  <p class="sectionheading">
    <a href="#" onclick="return toggle_folded(this);">
      <img alt="">
        <xsl:attribute name="src">
          <xsl:choose>
            <xsl:when test="$foldsection">../images/plus.gif</xsl:when>
            <xsl:otherwise>../images/minus.gif</xsl:otherwise>
          </xsl:choose>
        </xsl:attribute>
      </img>
    </a>
    <a>
      <xsl:copy-of select="@href"/>
      <xsl:value-of select="@ident"/>
      <xsl:text>: </xsl:text>
      <xsl:value-of select="@title"/>
    </a>
  </p>
  <div>
    <xsl:attribute name="class">
      <xsl:choose>
        <xsl:when test="$foldsection">section folded</xsl:when>
        <xsl:otherwise>section</xsl:otherwise>
      </xsl:choose>
    </xsl:attribute>
    <xsl:copy-of select="@id"/>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="page">
  <p><a><xsl:copy-of select="@href"/><xsl:value-of select="."/></a></p>
</xsl:template>



</xsl:stylesheet>
