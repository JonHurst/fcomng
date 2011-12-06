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

<xsl:template match="xhtml:div[@class='image']/xhtml:img">
  <xsl:value-of select="substring-before(@src, '.cgm')"/>
</xsl:template>

<!--Filters-->
<xsl:template match="xhtml:p[@class='duident']"/>
<xsl:template match="xhtml:div[@class='infocontainer']"/>
<xsl:template match="xhtml:span[@class='sectionref']"/>
<xsl:template match="xhtml:th[@class='callout']">
  (<xsl:apply-templates/>)
</xsl:template>
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
  <xsl:for-each select="xhtml:div[@class='condbody']/xhtml:div[@class='sys']">
    <xsl:apply-templates/>
    (<xsl:apply-templates select="../../xhtml:p[@class='intro']"/>)
  </xsl:for-each>
</xsl:template>

<xsl:template match="xhtml:thead">
  <xsl:if test="not(ancestor::xhtml:div[@class='synthesisitem']) or
                ancestor::xhtml:div[@class='synthesisitem']/preceding-sibling::xhtml:h1">
    <xsl:apply-templates/>
  </xsl:if>
</xsl:template>

<xsl:template match="xhtml:a[@class='footnoteref']|xhtml:div[@class='footnotes']">
  <xsl:if test="not(ancestor::xhtml:div[@class='synthesisitem'])">
    <xsl:apply-templates/>
  </xsl:if>
</xsl:template>

</xsl:stylesheet>