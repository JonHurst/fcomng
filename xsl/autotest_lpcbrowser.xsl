<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:xhtml="http://www.w3.org/1999/xhtml">

<xsl:output method="text"/>
<xsl:strip-space elements="*"/>

<xsl:template match="/">
  <xsl:apply-templates select="xhtml:html/xhtml:body/xhtml:div[@id='body_content']"/>
</xsl:template>

<xsl:template match="text()">
  <xsl:if test="not(ancestor::xhtml:div[@class='DUInfo']|
                ancestor::xhtml:div[@class='blq70mm'])">
    <xsl:value-of select="."/>
    <xsl:text> </xsl:text>
  </xsl:if>
</xsl:template>

<xsl:template match="xhtml:td[@class='asterisk']"/>
<xsl:template match="xhtml:a">
  <xsl:if test="@class='abb'">
    <xsl:apply-templates/>
  </xsl:if>
</xsl:template>

</xsl:stylesheet>