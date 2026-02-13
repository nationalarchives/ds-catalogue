<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html"/>
  <xsl:template match="emph[@altrender='doctype']">
    <dt>
      <xsl:choose>
        <xsl:when test="text()='W'">
          <xsl:text>Will of </xsl:text>
        </xsl:when>
        <xsl:when test="text()='P'">
          <xsl:text>Papers relating to </xsl:text>
        </xsl:when>
      </xsl:choose>
    </dt>
  </xsl:template>
  <xsl:template match="/">
    <dl class="tna-dl tna-dl--lined tna-dl--dotted">
      <xsl:apply-templates/>
    </dl>
  </xsl:template>
  <xsl:template match="persname">
    <dd>
      <xsl:value-of select="emph[@altrender='forenames']/text()"/>
      <xsl:if test="emph[@altrender='surname']">
        <xsl:text disable-output-escaping="yes"> </xsl:text>
        <xsl:value-of select="emph[@altrender='surname']/text()"/>
      </xsl:if>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='rank']">
    <dt>Rank/rating</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="corpname">
    <dt>Ship name</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='num']">
    <dt>Ship's pay book number</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='date']">
    <dt>Date of will</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
</xsl:stylesheet>
