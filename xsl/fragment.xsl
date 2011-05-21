<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns="http://www.w3.org/1999/xhtml">

<xsl:import href="lib.xsl"/>
<xsl:include href="table.xsl"/>

<xsl:output method="html"/>

<!--Stuff needed to get tables to work until properly cleaned up-->
<xsl:template name="anchor"/>
<xsl:param name="table.borders.with.css" select="0"/>

<!--Test mode - if true, produces a valid page from a fragment-->
<xsl:variable name="test-mode" select="0"/>

<xsl:key name="ftnote-ids" match="ftnote" use="@lid"/>


<xsl:template match="descitem">
  <div class="descitem">
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="desc-cond">
  <div class="desccond">
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="desc-cond/intro">
  <div class="intro">
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="desc-cond/condbody">
  <div class="condbody">
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="title">
  <xsl:if test=".. != /">
    <h1><xsl:apply-templates/></h1>
  </xsl:if>
</xsl:template>


<xsl:template match="para">
  <p><xsl:apply-templates/></p>
</xsl:template>


<xsl:template match="unlist">
  <xsl:apply-templates select="title|para"/>
  <xsl:element name="ul">
    <xsl:attribute name="class">
      <xsl:value-of select="@bulltype"/>
    </xsl:attribute>
    <xsl:apply-templates select="item"/>
  </xsl:element>
</xsl:template>


<xsl:template match="numlist">
  <xsl:apply-templates select="title|para"/>
  <xsl:element name="ol">
    <xsl:attribute name="class">
      <xsl:value-of select="@format"/>
    </xsl:attribute>
    <xsl:apply-templates select="item"/>
  </xsl:element>
</xsl:template>


<xsl:template match="item">
  <li><xsl:apply-templates/></li>
</xsl:template>


<xsl:template match="graphref">
  <xsl:variable name="ref" select="interactive-graphic/illustration/sheet/fileref/@href"/>
  <xsl:variable name="companion" select="interactive-graphic/illustration/sheet/gcompanionref/@href"/>
  <div class="image">
    <p>
      Image:
      <a>
	<xsl:attribute name="href">
	  ../fcom/DATA/DU/<xsl:value-of select="$ref"/>
	</xsl:attribute>
	<xsl:value-of select="$ref"/>
      </a>
    </p>
    <p>
      Companion:
      <a>
	<xsl:attribute name="href">
	  ../fcom/DATA/DU/<xsl:value-of select="$companion"/>
	</xsl:attribute>
	<xsl:value-of select="$companion"/>
      </a>
    </p>
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


<xsl:template match="caution">
  <div class="caution">
    <h2>Caution</h2>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="comment">
  <xsl:choose>
    <xsl:when test="note">
      <xsl:apply-templates/>
    </xsl:when>
    <xsl:otherwise>
      <div class="note">
	<h2>Comment</h2>
	<xsl:apply-templates/>
      </div>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template match="example">
  <div class="example">
    <h2>Example</h2>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="refint">
  <xsl:variable name="marker" select="normalize-space(text())"/>
  <xsl:choose>
    <xsl:when test="$marker">
      <xsl:value-of select="$marker"/>
    </xsl:when>
    <xsl:otherwise>
      <a class="footnoteref">
	<xsl:attribute name="href">#fnid<xsl:value-of select="key('ftnote-ids', @ref)/@code"/></xsl:attribute>
	(<xsl:value-of select="count(key('ftnote-ids', @ref)/preceding-sibling::ftnote) + 1"/>)
      </a>
    </xsl:otherwise>
  </xsl:choose>
</xsl:template>


<xsl:template match="footnotes">
  <div class="footnotes">
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="ftnote">
  <span class="footnotenum">
  <xsl:attribute name="id">fnid<xsl:value-of select="@code"/></xsl:attribute>
  (<xsl:number/>)
  </span>
  <div class="footnotetext"><xsl:apply-templates/></div>
</xsl:template>


<xsl:template match="equal">
  <xsl:if test="not(preceding-sibling::equal)">
    <table class="equal">
      <tr>
	<th class="equ-l">
	  <xsl:apply-templates select="equ-l"/>
	</th>
	<td class="equ-r">
	  <xsl:apply-templates select="equ-r"/>
	</td>
      </tr>
      <xsl:for-each select="following-sibling::equal">
	<tr>
	  <th class="equ-l">
	    <xsl:apply-templates select="equ-l"/>
	  </th>
	  <td class="equ-r">
	    <xsl:apply-templates select="equ-r"/>
	  </td>
	</tr>
      </xsl:for-each>
    </table>
  </xsl:if>
</xsl:template>


<xsl:template match="measure">
  <xsl:value-of select="."/>
  <xsl:value-of select="@unit"/>
</xsl:template>


<xsl:template match="if-installed">
  <xsl:apply-templates/><span class="ifinst"> (if inst)</span>
</xsl:template>


<xsl:template match="emph">
  <strong><xsl:apply-templates/></strong>
</xsl:template>


<xsl:template match="duref">
  <span class="duref">DUREF to <xsl:value-of select="@product"/> here</span>
</xsl:template>


<xsl:template match="symbol">
  <span class="symbol">SYMBOL</span>
</xsl:template>


<xsl:template match="lit-limit">
  <p><strong><xsl:apply-templates/></strong></p>
</xsl:template>


<xsl:template match="perf-value">
    <p><strong><xsl:apply-templates select="perf"/>:</strong>  <xsl:apply-templates  select="value"/></p>
</xsl:template>


<xsl:template match="description|table|equ-l|equ-r|abb|
		     descbody|row-header|tech-label|
		     ex-desc-cond|limitation|limitbody|
		     perf|value|limititem|limit">
  <xsl:apply-templates/>
</xsl:template>


<xsl:template match="*">
  <div class="not-impl">
    <p>
      <xsl:value-of select="name()"/>
      <xsl:text> is not implemented yet!</xsl:text>
    </p>
    <xsl:if test="node()">
      <p><xsl:text>Content:</xsl:text></p>
      <xsl:value-of select="node()"/>
    </xsl:if>
  </div>
</xsl:template>


</xsl:stylesheet>
