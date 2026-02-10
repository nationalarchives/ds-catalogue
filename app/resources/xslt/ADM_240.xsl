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
        <xsl:when test="not(contains(text(),':'))">
          Title
        </xsl:when>
        <xsl:when test="substring(text(),(string-length(text()) - 1),1)=':'">
          <xsl:value-of select="substring(text(),0,(string-length(text()) - 1))"/>
        </xsl:when>
        <xsl:when test="contains(text(),'Date of Seniority')">
          <xsl:text>Date of seniority</xsl:text>
        </xsl:when>
        <xsl:when test="contains(text(),'Date of Birth')">
          <xsl:text>Date of birth</xsl:text>
        </xsl:when>
        <xsl:when test="contains(text(),'Place of Birth')">
          <xsl:text>Place of birth</xsl:text>
        </xsl:when>
        <xsl:when test="contains(text(),': [not given].')">
          <xsl:value-of select="substring-before(text(),': [not given].')"/>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="text()"/>
        </xsl:otherwise>
      </xsl:choose>
    </dt>
    <dd>
      <xsl:choose>
        <xsl:when test="not(contains(text(),':'))">
          <xsl:value-of select="text()"/>
        </xsl:when>
        <xsl:when test="(persname | span[@class='persname'])">
          <xsl:value-of select="*/*[@altrender='surname']/text()"/>
          <xsl:if test="*/*[@altrender='surname'] and */*[@altrender='forenames']">
            <xsl:text>, </xsl:text>
          </xsl:if>
          <xsl:value-of select="*/*[@altrender='forenames']/text()"/>
        </xsl:when>
        <xsl:when test="contains(text(),'Date of Seniority')">
          <xsl:value-of select="substring-after(text(),': ')"/>
        </xsl:when>
        <xsl:when test="contains(text(),'[not given]')">
          <xsl:text>[not given]</xsl:text>
        </xsl:when>
        <xsl:otherwise>
          <xsl:value-of select="*/text()"/>
        </xsl:otherwise>
      </xsl:choose>
    </dd>
  </xsl:template>
</xsl:stylesheet>
