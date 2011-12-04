<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:dul="http://www.hursts.eclipse.co.uk/dul"
      xmlns:xhtml="http://www.w3.org/1999/xhtml">

<xsl:output method="xml" version="1.0" encoding="utf-8"/>
<xsl:strip-space elements="*"/>

<xsl:template match="/">
  <dul:dus>
    <xsl:apply-templates select="//xhtml:div[@class='main']"/>
  </dul:dus>
</xsl:template>


<xsl:template match="xhtml:div[@class='main']">
  <dul:du>
    <xsl:attribute name="id">
      <xsl:value-of select="@id"/>
    </xsl:attribute>
    <xsl:if test="../preceding-sibling::*[1][@class='group_heading']">
      <xsl:apply-templates select="../preceding-sibling::xhtml:h1"/>
    </xsl:if>
  <xsl:apply-templates/>
  </dul:du>
</xsl:template>


<xsl:template match="text()">
  <xsl:value-of select="."/>
</xsl:template>


<!--LPC Browser puts table titles underneath -->
<xsl:template match="xhtml:div[@class='table']">
  <xsl:apply-templates/>
  <xsl:value-of select="xhtml:h1"/>
</xsl:template>
<xsl:template  match="xhtml:div[@class='table']/xhtml:h1"/>

<xsl:template match="xhtml:div[@class='status']">
  <xsl:apply-templates select="xhtml:div[@class='info']"/>
  <xsl:apply-templates select="xhtml:div[@class!='info']"/>
</xsl:template>

<xsl:template match="xhtml:div[@class='fwspage']">
  <xsl:text>status</xsl:text>
  <xsl:apply-templates/>
</xsl:template>


<!--Filters-->
<xsl:template match="xhtml:p[@class='duident']"/>
<xsl:template match="xhtml:div[@class='infocontainer']"/>
<xsl:template match="xhtml:span[@class='sectionref']"/>
<xsl:template match="xhtml:th[@class='callout']"/>
<xsl:template match="xhtml:div[@class='deferred-proc']/xhtml:h1"/>
<xsl:template match="xhtml:div[@class='status']/xhtml:h1"/>
<xsl:template match="xhtml:div[@class='limitations']/xhtml:h1"/>
<xsl:template match="xhtml:div[@class='info']/xhtml:h1"/>
<xsl:template match="xhtml:div[@class='ecaminop']/xhtml:h1">
  <xsl:text>Inop SYS</xsl:text>
</xsl:template>
<xsl:template match="xhtml:div[@class='otherinop']/xhtml:h1">
  <xsl:text>Other inop SYS</xsl:text>
</xsl:template>
<xsl:template match="xhtml:div[@class='condsys']">
  <xsl:apply-templates select="xhtml:div[@class='condbody']"/>
  (<xsl:apply-templates select="xhtml:p[@class='intro']"/>)
</xsl:template>


</xsl:stylesheet>