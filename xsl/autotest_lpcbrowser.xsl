<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
      xmlns:dul="http://www.hursts.eclipse.co.uk/dul"
      xmlns:xhtml="http://www.w3.org/1999/xhtml">

<xsl:output method="xml" version="1.0" encoding="utf-8"/>
<xsl:strip-space elements="*"/>

<xsl:param name="synthesis" select="'False'"/>

<xsl:template match="/">
  <dul:dus>
    <xsl:apply-templates select="/xhtml:html/xhtml:body/xhtml:div[@id='body_content']"/>
  </dul:dus>
</xsl:template>


<xsl:template match="xhtml:div[@id='body_content']">
  <xsl:for-each select="xhtml:table">
    <dul:du>
      <xsl:attribute name="id">
        <xsl:value-of select="xhtml:tbody/xhtml:tr/xhtml:td/
                              xhtml:div[@class='DUInfo']/xhtml:table/
                              xhtml:tbody/xhtml:tr/xhtml:td/text()[1]"/>
      </xsl:attribute>
      <xsl:attribute name="title">
        <xsl:apply-templates  select="xhtml:tbody/xhtml:tr/xhtml:td/
                                      xhtml:div[@class='title_120percent']/
                                      xhtml:div"/>
      </xsl:attribute>
      <xsl:apply-templates/>
    </dul:du>
  </xsl:for-each>
</xsl:template>
<xsl:template match="xhtml:div[@class='DUInfo']"/>


<xsl:template match="xhtml:div[@class='graphrefcenter']//xhtml:img">
  <xsl:value-of select="@src"/>
</xsl:template>

<xsl:template match="xhtml:img[@class='graphrefthumbnail']">
  <xsl:value-of select="concat(substring-before(@src, '_thumbnail.png'), '.png')"/>
</xsl:template>


<xsl:template match="text()">
    <xsl:value-of select="."/>
</xsl:template>


<!-- <xsl:template match="xhtml:td[@class='asterisk']"/> -->
<xsl:template match="xhtml:em[@class='refint_ftnote']|xhtml:td[@class='ftnote']">
  <xsl:if test="$synthesis = 'False'">
    <xsl:apply-templates/>
  </xsl:if>
</xsl:template>

</xsl:stylesheet>