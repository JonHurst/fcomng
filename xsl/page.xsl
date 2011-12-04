<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
		xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
		xmlns="http://www.w3.org/1999/xhtml">

<xsl:import href="fragment.xsl"/>

<xsl:output method="html"
	    doctype-system="http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"
	    doctype-public="-//W3C//DTD XHTML 1.0 Strict//EN"
	    version="1.0"/>


<xsl:template match="page">
  <html>
    <head>
      <title><xsl:value-of select="@title"/>: <xsl:value-of select="@subtitle"/></title>
      <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
      <link rel="stylesheet" type="text/css" href="../stylesheets/styles.css"/>
      <link rel="alternate stylesheet" title="Debug" type="text/css"
            href="../stylesheets/debug.css"/>
      <script type="text/javascript">
        <xsl:comment>jsvariable</xsl:comment>
      </script>
      <script type="text/javascript" src="../scripts/script.js"></script>
    </head>
    <body onload="initial_fold();">
      <div class="page">
        <div id="topbar">
          <table class="navbar">
            <tr>
              <td class="left">
                <xsl:if test="@prev">
                  <xsl:text>Prev: </xsl:text>
                  <a accesskey="p">
                    <xsl:attribute name="href"><xsl:value-of select="@prev"/></xsl:attribute>
                    <xsl:value-of select="@prevtitle"/>
                  </a>
                </xsl:if>
              </td>
              <td class="right">
                <xsl:if test="@next">
                  <xsl:text>Next: </xsl:text>
                  <a accesskey="n">
                    <xsl:attribute name="href"><xsl:value-of select="@next"/></xsl:attribute>
                    <xsl:value-of select="@nexttitle"/>
                  </a>
                </xsl:if>
              </td>
            </tr>
          </table>
          </div>
          <div class="content">
	<div class="titleblock">
	  <h1>easyJet A319/A320 FCOM (<xsl:value-of select="@version"/>)</h1>
     <h2><xsl:value-of select="@title"/></h2>
	</div>
   <xsl:comment>linkbar</xsl:comment>
	<xsl:if test="count(section) > 1">
	  <div class="pageindex">
	    <xsl:for-each select="section">
         <p><a>
           <xsl:attribute name="href">
             #<xsl:value-of select="@sid"/>
           </xsl:attribute>
           <xsl:value-of select="@title"/>
         </a></p>
       </xsl:for-each>
	  </div>
	</xsl:if>
	  <xsl:apply-templates/>
          </div>
     <div id="bottombar">
       <table class="navbar">
         <tr>
           <td class="left">
             <xsl:if test="@prev">
               <xsl:text>Prev: </xsl:text>
               <a>
                 <xsl:attribute name="href"><xsl:value-of select="@prev"/></xsl:attribute>
                 <xsl:value-of select="@prevtitle"/>
               </a>
             </xsl:if>
           </td>
           <td>
             <a href="#topbar">Top</a>
           </td>
           <td class="right">
             <xsl:if test="@next">
               <xsl:text>Next: </xsl:text>
               <a>
                 <xsl:attribute name="href"><xsl:value-of select="@next"/></xsl:attribute>
                 <xsl:value-of select="@nexttitle"/>
               </a>
             </xsl:if>
           </td>
         </tr>
       </table>
     </div>
      </div>
    </body>
  </html>
</xsl:template>


<xsl:template match="section">
  <div class="section">
    <xsl:attribute name="id"><xsl:value-of select="@sid"/></xsl:attribute>
    <h1 class="sectionheading"><xsl:value-of select="@title"/></h1>
    <xsl:if test="count(du_container) + count(group) &gt; 1">
      <div class="duindex">
        <xsl:for-each select="du_container|group">
          <p><a>
            <xsl:choose>
              <xsl:when test="self::du_container">
                <xsl:attribute name="href">#<xsl:value-of select="@id"/></xsl:attribute>
              </xsl:when>
              <xsl:otherwise>
                <xsl:attribute name="href">#<xsl:value-of select="@id"/></xsl:attribute>
              </xsl:otherwise>
            </xsl:choose>
            <xsl:value-of select="@title"/>
          </a></p>
        </xsl:for-each>
      </div>
    </xsl:if>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="group">
  <div class="group">
    <xsl:attribute name="id">
      <xsl:value-of select="@id"/>
    </xsl:attribute>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="du_container">
  <div class="du_container">
    <xsl:attribute name="id">
      <xsl:value-of select="@id"/>
    </xsl:attribute>
    <xsl:if test="count(du) > 1">
      <xsl:variable name="max_width" select="floor(80 div count(du))"/>
      <div class="tags">
      <xsl:for-each select="du">
        <a class="alternate">
          <xsl:attribute name="href">
            <xsl:text>#</xsl:text><xsl:value-of select="@id"/>
          </xsl:attribute>
          <xsl:variable name="label" select="substring(applies, 1, $max_width)"/>
          <xsl:value-of select="$label"/>
          <xsl:if test="string-length($label) = $max_width">
            <xsl:text>&#x2026;</xsl:text>
          </xsl:if>
        </a>
      </xsl:for-each>
      </div>
    </xsl:if>
    <xsl:if test="@overridden_by">
      <div class="tdu_warning">
        <p>This DU is overridden by TDU
        <a>
          <xsl:attribute name="href">
            <xsl:text>#duid</xsl:text>
            <xsl:value-of select="@overridden_by"/>
          </xsl:attribute>
          <xsl:value-of select="@overridden_by"/>
        </a></p>
      </div>
    </xsl:if>
    <xsl:apply-templates/>
  </div>
</xsl:template>


<xsl:template match="du">
  <div>
    <xsl:choose>
      <xsl:when test="@tdu">
	<xsl:attribute name="class">main tdu</xsl:attribute>
      </xsl:when>
      <xsl:otherwise>
	<xsl:attribute name="class">main</xsl:attribute>
      </xsl:otherwise>
    </xsl:choose>
	<xsl:attribute name="id"><xsl:value-of select="@id"/></xsl:attribute>
    <p class="duident">
      <a>
	<xsl:attribute name="href"><xsl:value-of select="@href"/></xsl:attribute>
	<xsl:value-of select="@href"/>
      </a>
    </p>
    <div class="infocontainer">
      <img src="../images/isymbol.gif" alt=""/>
      <div class="info">
         <p><xsl:value-of select="ancestor::section/@title"/>/<xsl:value-of select="substring(@id,
         5)"/></p>
         <p><strong>Revised: </strong>
         <xsl:choose>
           <xsl:when test="@revcode">
             <span class="rev"><xsl:value-of select="@revdate"/>
             <xsl:text> (</xsl:text>
             <xsl:value-of select="@revcode"/>
             <xsl:text>)</xsl:text>
             </span>
           </xsl:when>
           <xsl:otherwise>
             <xsl:value-of select="@revdate"/>
           </xsl:otherwise>
         </xsl:choose>
         </p>
        <xsl:if test="applies">
          <p class="applies"><strong>Applies to</strong>: <xsl:value-of select="applies"/></p>
        </xsl:if>
      </div>
    </div>
   <xsl:choose>
     <xsl:when test="@href != ''">
       <xsl:apply-templates select="document(@href)/*">
         <xsl:with-param name="group_pos">
           <xsl:choose>
             <xsl:when test="ancestor::group">
               <xsl:value-of select="count(../preceding-sibling::du_container)"/>
             </xsl:when>
             <xsl:otherwise>-1</xsl:otherwise>
           </xsl:choose>
         </xsl:with-param>
         <xsl:with-param name="group_title">
           <xsl:value-of select="ancestor::group/@title"/>
         </xsl:with-param>
       </xsl:apply-templates>
     </xsl:when>
     <xsl:when test="@tdu">
       <h1><xsl:value-of select="@title"/></h1>
       <p>TDU does not apply to selected aircraft. If applicable, use original DU.</p>
     </xsl:when>
     <xsl:otherwise>
       <h1><xsl:value-of select="@title"/></h1>
       <p>DU does not apply to selected aircraft.</p>
     </xsl:otherwise>
   </xsl:choose>
  </div>
</xsl:template>


<xsl:template name="revised_text">
  <span class="rev">
    <xsl:value-of select="."/>
  </span>
</xsl:template>

</xsl:stylesheet>
