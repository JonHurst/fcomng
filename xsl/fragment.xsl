<?xml version="1.0"?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">

<xsl:output method="html"/>

<xsl:variable name="test-mode" select="0"/>


<xsl:template match="/">
  <xsl:choose>
    <xsl:when test="$test-mode">
      <html xmlns="http://www.w3.org/1999/xhtml">
	<head>
	  <title>Test</title>
	  <link rel="stylesheet" type="text/css" href="../stylesheets/styles.css"/>
	</head>
	<body>
	  <div class="page">
	    <xsl:call-template name="fragment"/>
	  </div>
	</body>
      </html>
    </xsl:when>
    <xsl:otherwise>
      <xsl:call-template name="fragment"/>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template name="fragment">
  <div class="fragment">
  <xsl:choose>
    <xsl:when test="description">
      <xsl:apply-templates select="description"/>
    </xsl:when>
    <xsl:otherwise>
      <div class="not-impl"><p>
	<xsl:text>Root element "</xsl:text>
	<xsl:value-of select="name(*)"/>
	<xsl:text>" is not implemented yet!</xsl:text>
      </p></div>
    </xsl:otherwise>
  </xsl:choose>
  </div>
</xsl:template>

<xsl:template match="description">
    <h1><xsl:value-of select="title"/></h1>
    <xsl:apply-templates select="descbody|descitem"/>
</xsl:template>

<xsl:template match="descitem">
  <div class="descitem">
    <h1><xsl:value-of select="title"/></h1>
    <xsl:apply-templates select="descitem|descbody"/>
  </div>
</xsl:template>

<xsl:template match="descbody">
  <xsl:apply-templates select="para|unlist|numlist|warning|caution|
			       note|table|graphref|graphref|launcher|
			       equal|desc-cond|whatif|equation|example"/>
</xsl:template>

<xsl:template match="para">
  <p><xsl:apply-templates select="node()"/></p>
</xsl:template>

<xsl:template match="unlist">
  <xsl:apply-templates select="para"/>
  <xsl:element name="ul">
    <xsl:attribute name="class">
      <xsl:value-of select="@bulltype"/>
    </xsl:attribute>
    <xsl:apply-templates select="item"/>
  </xsl:element>
</xsl:template>

<xsl:template match="numlist">
  <xsl:apply-templates select="para"/>
  <xsl:element name="ol">
    <xsl:attribute name="class">
      <xsl:value-of select="@format"/>
    </xsl:attribute>
    <xsl:apply-templates select="item"/>
  </xsl:element>
</xsl:template>

<xsl:template match="item">
  <li>
    <xsl:apply-templates select="para|unlist|numlist|warning|caution|
				 note|table|graphref|launcher|
				 equal|equation"/>
  </li>
</xsl:template>

<xsl:template match="graphref">
  <xsl:variable name="ref" select="interactive-graphic/illustration/sheet/fileref/@href"/>
  <div class="image">
    <p><xsl:value-of select="$ref"/></p>
  <!-- <xsl:element name="img" use-attribute-sets="imgsrc"> -->
  <!--   <xsl:attribute name="src"> -->
  <!--     <xsl:value-of select="concat($ref, '.png')"/> -->
  <!--   </xsl:attribute> -->
  <!-- </xsl:element> -->
  </div>
</xsl:template>

<xsl:template match="note">
  <div class="note">
    <h2>Note</h2>
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="example">
  <div class="example">
    <h2>Example</h2>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="equal">
  <table class="equal"><tr>
    <td class="equ-l">
      <p><xsl:apply-templates select="equ-l"/></p>
    </td>
    <td class="equ-r">
      <xsl:apply-templates select="equ-r"/>
    </td>
  </tr></table>
</xsl:template>


<xsl:template match="warning|caution|
		     launcher|
		     equation|desc-cond|whatif|footnotes">
  <div class="not-impl">
    <p>
      <xsl:value-of select="name()"/>
      <xsl:text> is not implemented yet!</xsl:text></p>
  </div>
</xsl:template>

<xsl:template match="measure">
  <xsl:value-of select="."/>
  <xsl:value-of select="@unit"/>
</xsl:template>




</xsl:stylesheet>