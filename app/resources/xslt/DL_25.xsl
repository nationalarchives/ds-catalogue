<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html"/>
  <!-- MATCH FOR MONGO DATA -->
  <xsl:template match="scopecontent">
    <dl class="tna-dl tna-dl--lined tna-dl--dotted">
      <xsl:apply-templates select="p"/>
    </dl>
  </xsl:template>
  <!-- MATCH FOR ROSETTA DATA -->
  <xsl:template match="span[@class='scopecontent']">
    <dl class="tna-dl tna-dl--lined tna-dl--dotted">
      <xsl:apply-templates select="p"/>
    </dl>
  </xsl:template>
  <xsl:template match="p">
    <dt>
      <xsl:choose>
        <xsl:when test="substring(text(),(string-length(text()) - 1),1)=':'">
          <xsl:value-of select="substring(text(),0,(string-length(text()) - 1))"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="text()"/>
        </xsl:otherwise>
      </xsl:choose>
    </dt>
    <dd>
      <xsl:value-of select="*/text()"/>
    </dd>
  </xsl:template>
</xsl:stylesheet>
