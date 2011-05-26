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

<xsl:template match="normalproc|abnormalproc|emergencyproc">
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

<xsl:template match="land">
  <p>
    <xsl:attribute name="class">
      <xsl:value-of select="@type"/>
    </xsl:attribute>
    <xsl:choose>
      <xsl:when test="@type = 'landasap'">
	LAND ASAP
      </xsl:when>
      <xsl:otherwise>
	LAND type not implemented yet!
      </xsl:otherwise>
    </xsl:choose>
  </p>
</xsl:template>

<xsl:template match="command">
  <div class="command">
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="cr-action">
  <div class="cr">
    <table class="cr"><tr>
      <td class="cr-left">
	<xsl:apply-templates select="challenge"/>
      </td>
      <td class="cr-dots"><div class="dots"> </div></td>
      <td class="cr-right">
	<xsl:apply-templates select="response"/>
      </td>
    </tr></table>
  </div>
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
    <xsl:when test="note|caution|warning">
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
  <xsl:choose>
    <xsl:when test="@product = 'FCOM'">
      <a class="duref">
	<xsl:attribute name="href">
	  <xsl:value-of select="@ref"/>
	</xsl:attribute>
      </a>
    </xsl:when>
    <xsl:otherwise>
      <span class="duref">See <xsl:value-of select="@product"/></span>
    </xsl:otherwise>
  </xsl:choose>
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
      <xsl:apply-templates/>
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


<xsl:template match="associated-procs">
  <div class="associated-procs">
    <h1>Associated Procedures</h1>
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="associated-proc">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="associated-proc/xtitle">
  <xsl:if test="ecamsystem">
    <span class="ecamsys"><xsl:value-of select="ecamsystem"/></span> 
  </xsl:if>
  <span class="ecamtitle"><xsl:value-of select="title"/></span> 
  <xsl:apply-templates select="title/*"/>
  <xsl:if test="subtitle">
    <span class="ecamsubtitle"><xsl:value-of select="subtitle"/></span>
  </xsl:if>
</xsl:template>

<xsl:template match="secondary-failures">
  <div class="secondary-failures">
    <h1>Secondary Failures</h1>
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="ecampage">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="ecamsyspage">
  <p><xsl:value-of select="."/></p>
</xsl:template>

<xsl:template match="ecam-info">
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="reason">
  <div class="note">
    <h2>Reason</h2>
    <xsl:apply-templates/>
  </div>
</xsl:template>

<!-- fwspage -->

<xsl:template match="fwspage">
  <!-- (limitations?,deferredproc?,status?,moreinfopage?,memopage?) -->
  <xsl:apply-templates/>
</xsl:template>

<!-- fwspage/* -->
<!-- not implemented: moreinfopage -->
<!-- not implemented: memopage -->

<xsl:template match="limitations">
  <div class="limitations">
    <h1>Limitations:</h1>
    <!-- (ecamlimit?,pfdlimit?,comment?) -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="deferredproc">
  <div class="deferred-proc">
    <h1>Deferred procedures:</h1>
    <!-- ((allphase-proc|flightphase-proc)+,comment?) -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="status">
  <div class="status">
    <h1>Status:</h1>
    <!-- (ecaminopsys?,otherinopsys?,info?,comment?) -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<!-- fwspage/*/* -->

<xsl:template match="ecamlimit">
  <div class="ecamlimit">
    <!-- (((allphase-limit|flightphase-limit)+,comment?)) -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="pfdlimit">
  <div class="pfdlimit">
    <!-- (((allphase-limit|flightphase-limit)+,comment?)) -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="allphase-proc">
  <div class="all-phase">
    <!-- ((procbody+,comment?)) -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="flightphase-proc">
  <div class="flight-phase">
    <!-- ((procbody+,comment?)) -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="ecaminopsys">
  <div class="ecaminop">
    <h1>Inop systems:</h1>
    <!-- (((duref| (allphase-sys|flightphase-sys)+),comment?)) -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="otherinopsys">
  <div class="otherinop">
    <h1>Inop systems not displayed by ECAM:</h1>
    <!-- (((duref|(allphase-sys|flightphase-sys)+),comment?)) -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="info">
  <div class="info">
    <h1>Info:</h1>
    <!-- (((infobody|info-cond),comment?)+) -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<!-- fwspage/*/*/* -->
<!-- not implemented: flightphase-limit -->
<!-- not implemented: flightphase-sys -->

<xsl:template match="allphase-limit">
  <!-- (((limit|condlimit),comment?)+) -->
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="allphase-sys">
  <div class="all-phase">
    <!-- comment | condsys | sys -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="infobody">
  <!-- subset of standard block -->
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="info-cond">
  <!-- ((intro|introblock),info-condbody) -->
    &#x2022; <xsl:apply-templates select="intro|introblock"/>:
    <xsl:apply-templates select="info-condbody"/>
</xsl:template>


<!-- fwspage/*/*/*/* -->
<!-- not implemented: allphase-limit -->
<!-- not implemented: flightphase-limit-->
<!-- not implemented: condlimit -->
<!-- not implemented: info-condbody -->

<xsl:template match="limit">
  <!-- ((lit-limit|perf-value),comment?) -->
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="condlimit">
  <!-- ((intro|introblock),condlimitbody) -->
  &#x2022; <xsl:apply-templates select="intro|introblock"/>:
  <xsl:apply-templates select="condlimitbody"/>
</xsl:template>

<xsl:template match="condsys">
  <div class="condsys">
    <!-- (intro | introblock), condsysbody -->
    &#x2022; <xsl:apply-templates select="intro|introblock"/>:
    <xsl:apply-templates select="condsysbody"/>
  </div>
</xsl:template>

<xsl:template match="sys">
  <div class="sys">
    <!-- standard inline -->
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="info-condbody">
  <!-- ((infobody+,comment?)) -->
  <div class="condbody">
    <xsl:apply-templates/>
  </div>
</xsl:template>

<!-- fwspage/*/*/*/*/* -->
<!-- not implemented: lit-limit -->
<!-- not implemented: perf-value -->

<xsl:template match="intro">
  <!-- standard inline -->
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="introblock">
  <!-- (intro, intro+) -->
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="condlimitbody">
  <!-- (limit|lit-limit)+ -->
  <div class="condbody">
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="condsysbody">
  <!-- (sys+) -->
  <div class="condbody">
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="infobody">
  <!-- standard block -->
  <xsl:apply-templates/>
</xsl:template>


<!-- approbation -->
<xsl:template match="approbation">
  <!-- (reason?,title,
  (tr-data|env-data|heading-data|bulletin-data),approbation-frame?
  ,approbation-area?)-->
  <xsl:apply-templates/>
</xsl:template>

<!-- approbation/* -->
<!-- not implemented: tr-data -->
<!-- not implemented: env-data -->
<!-- not implemented: heading-data -->
<!-- not implemented: bulletin-data -->
<!-- not implemented: approbation-frame -->

<xsl:template match="bulletin-data">
  <!-- (reason-for-issue,applicable-to?,bul-cancelled-by?) -->
  <xsl:apply-templates/>
</xsl:template>

<xsl:template match="approbation-area">
  <!--(approbation-authority?,approval-date,approval-reference,
  approved-by?)-->
  <div class="approbation">
    <h1>Approbation:</h1>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<!-- approbation/*/* -->

<xsl:template match="reason-for-issue">
  <!-- subset of standard block elements -->
  <div class="reason">
    <h1>Reason for issue:</h1>
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="applicable-to">
  <!-- subset of standard block elements -->
  <div class="applicable">
    <h1>Applicability:</h1>
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="bul-cancelled-by">
  <!-- subset of standard block elements -->
  <div class="cancelled-by">
    <h1>Cancelled by:</h1>
    <xsl:apply-templates/>
  </div>
</xsl:template>

<xsl:template match="approbation-authority">
  <!-- (#PCDATA) -->
  <p>Authority: <xsl:value-of select="."/></p>
</xsl:template>

<xsl:template match="approval-date">
  <!-- (#PCDATA) -->
  <p>Date: <xsl:value-of select="."/></p>
</xsl:template>

<xsl:template match="approval-reference">
  <!-- (#PCDATA) -->
  <p>Reference: <xsl:value-of select="."/></p>
</xsl:template>

<xsl:template match="approved-by">
  <!--(name?,job-title?,approval-comment?)-->
  <p>Approved by:
  <xsl:choose>
    <xsl:when test="name and job-title">
      <xsl:value-of select="name"/>, <xsl:value-of select="job-title"/>
    </xsl:when>
    <xsl:otherwise>
      <xsl:value-of select="name"/>
      <xsl:value-of select="job-title"/>
    </xsl:otherwise>
  </xsl:choose>
  </p>
  <xsl:if test="approval-comment">
    <p> <xsl:value-of select="approval-comment"/></p>
  </xsl:if>
</xsl:template>

</xsl:stylesheet>
