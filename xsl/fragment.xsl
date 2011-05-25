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

<xsl:template match="normalproc">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="xtitle"/>

<xsl:template match="inform">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="desc-cond/condbody">
  <div class="condbody">
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="procbody">
  <div class="procbody">
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="procitem">
  <div class="procitem">
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="procdesc">
  <div class="procdesc">
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="action">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="command">
  <div class="command">
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="cr-action">
  <table class="cr"><tr>
    <td width="1%">
      <xsl:apply-templates select="challenge"/>
    </td>
    <td width="100%"><div class="dots"> </div></td>
    <td width="1%">
      <xsl:apply-templates select="response"/>
    </td>
  </tr></table>
</xsl:template>

<xsl:template match="cr-action/challenge|cr-action/response">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="condition">
  <div class="condition">
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="ex-conditions">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="intro">
  <p class="intro">
    <xsl:text>&#x2022; </xsl:text>
    <xsl:apply-templates/>
  </p>
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
    <p class="img-detail">
      Image:
      <a>
    	<xsl:attribute name="href">
    	  ../fcom/DATA/DU/<xsl:value-of select="$ref"/>
    	</xsl:attribute>
    	<xsl:value-of select="$ref"/>
      </a>
    </p>
    <p class="img-detail">
      Companion:
      <a>
    	<xsl:attribute name="href">
    	  ../fcom/DATA/DU/<xsl:value-of select="$companion"/>
    	</xsl:attribute>
    	<xsl:value-of select="$companion"/>
      </a>
    </p>
    <img>
      <xsl:attribute name="src">
	../images/<xsl:value-of select="substring-before(substring-after($ref,
	'../ILLUS/'), '.cgm')"/>.png
      </xsl:attribute>
      <xsl:attribute name="alt">
	Illustration: <xsl:value-of select="$ref"/>
      </xsl:attribute>
    </img>
    <xsl:apply-templates select="interactive-graphic/illustration/sheet/*"/>
  </div>
</xsl:template>

<xsl:template match="sheet/fileref"/>
<xsl:template match="sheet/gcompanionref"/>

<xsl:template match="desctext">
  <xsl:for-each select="paradesc">
    <p><xsl:apply-templates/></p>
  </xsl:for-each>
</xsl:template>

<xsl:template match="gdesc">
  <div class="callout-list"><xsl:apply-templates/></div>
</xsl:template>


<xsl:template match="gdesc/listitem">
  <table class="callouts">
    <xsl:for-each select="grdescitem">
      <tr class="callout" valign="top">
	<th class="callout"><xsl:value-of select="gritem"/></th>
	<td class="callout">
	  <xsl:if test="title">
	    <h1><xsl:value-of select="title"/></h1>
	  </xsl:if>
	<xsl:apply-templates select="itembody"/></td>
      </tr>
  </xsl:for-each>
  </table>
</xsl:template>

<xsl:template match="gritem"/>
<xsl:template match="itembody">
  <xsl:apply-templates/>
</xsl:template>


<xsl:template match="note|noteproc">
  <div class="note">
    <h2>Note</h2>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="caution|cautionproc">
  <div class="caution">
    <h2>Caution</h2>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="warning|warningproc">
  <div class="caution">
    <h2>Warning</h2>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="comment">
  <xsl:choose>
    <xsl:when test="note|caution">
      <xsl:apply-templates/>
    </xsl:when>
    <xsl:otherwise>
      <div class="note">
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
	<xsl:attribute name="href">#fnid<xsl:value-of select="generate-id(key('ftnote-ids', @ref))"/></xsl:attribute>
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
  <xsl:attribute name="id">fnid<xsl:value-of select="generate-id()"/></xsl:attribute>
  (<xsl:number/>)
  </span>
  <div class="footnotetext"><xsl:apply-templates/></div>
</xsl:template>


<xsl:template match="equal">
  <xsl:if test="not(preceding-sibling::equal)">
    <div class="equal">
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
    </div>
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


<xsl:template match="table">
  <div class="table">
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="description|equ-l|equ-r|abb|
		     descbody|row-header|tech-label|
		     ex-desc-cond|limitation|limitbody|
		     perf|value|limititem|limit|
		     performance|perfbody|perfitem">
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

<xsl:template match="ecam-data">
    <xsl:if test="ecamsys">
      <span class="ecamsys"><xsl:value-of select="ecamsys"/></span> 
    </xsl:if>
    <xsl:if test="ecamtitle">
      <span class="ecamtitle"><xsl:value-of select="ecamtitle"/></span> 
    </xsl:if>
    <xsl:if test="ecamsubtitle">
      <span class="ecamsubtitle"><xsl:value-of select="ecamsubtitle"/></span>
    </xsl:if>
</xsl:template>

<xsl:template match="action-block">
  <div class="actionblock">
    <xsl:if test="title">
      <h2>
	<xsl:apply-templates select="title"></xsl:apply-templates>
      </h2>
    </xsl:if>
    <xsl:for-each select="action">
      <xsl:apply-templates select="action"/>
    </xsl:for-each>
  </div>
</xsl:template>

<xsl:template match="equation|inline-equation">
  <img class="equation" alt="equation">
    <xsl:attribute name="src">
      ../images/<xsl:value-of select="substring-after(equation-image/fileref/@href, '../EXTOBJ/')"/>
    </xsl:attribute>
    <!-- <xsl:attribute name="width"> -->
    <!--   <xsl:value-of select="equation-image/@width"/> -->
    <!-- </xsl:attribute> -->
    <!-- <xsl:attribute name="height"> -->
    <!--   <xsl:value-of select="equation-image/@height"/> -->
    <!-- </xsl:attribute> -->
  </img>
</xsl:template>

</xsl:stylesheet>
