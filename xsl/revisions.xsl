<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns="http://www.w3.org/1999/xhtml">

<xsl:output method="xml"
	    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
	    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
	    encoding="utf-8"
	    version="1.0"/>

<xsl:template match="revisions">
  <xsl:variable name="title">
    <xsl:value-of select="@title"/>
  </xsl:variable>
  <html>
    <head>
      <title><xsl:value-of select="$title"/></title>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <link rel="stylesheet" type="text/css" href="../stylesheets/styles.css"/>
    </head>
    <body>
      <div class="page">
        <div class="titleblock">
          <h1>easyJet A319/A320 FCOM (<xsl:value-of select="@version"/>)</h1>
          <h2><xsl:value-of select="@title"/></h2>
        </div>
        <xsl:comment>linkbar</xsl:comment>
        <div class="revisions">
          <div class="section">
            <h2>Key:</h2>
            <ul>
              <li>(N): New Document Unit</li>
              <li>(R): Revised Document Unit</li>
            </ul>
            <p>Changes are only <span class="rev">highlighted</span> for revised document
            units. Where there are no highlights in a revised document unit, the visible text is not
            affected (e.g. there is a change of image or a change to a title that is being
            hidden).</p>
            <p>Where a link takes you to multiple versions of a documentation unit, the affected
            unit can be determined by checking revision dates.</p>
          </div>
          <xsl:apply-templates/>
        </div>
      </div>
    </body>
  </html>
</xsl:template>


<xsl:template match="section">
  <div class="section">
    <h2><xsl:value-of select="@title"></xsl:value-of></h2>
    <ul>
      <xsl:apply-templates/>
    </ul>
  </div>
</xsl:template>


<xsl:template match="rev">
  <li>
    (<xsl:value-of select="@code"/>) <xsl:value-of select="@duid"/>
    <xsl:text>: </xsl:text>
    <a>
      <xsl:copy-of select="@href"/>
      <xsl:value-of select="@title"/>
    </a>
  </li>
</xsl:template>



</xsl:stylesheet>
