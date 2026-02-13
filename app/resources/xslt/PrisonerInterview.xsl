<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html"/>
  <xsl:template match="emph[@altrender='doctype']">
	</xsl:template>
  <xsl:template match="/">
    <dl class="tna-dl tna-dl--lined tna-dl--dotted">
      <xsl:apply-templates/>
    </dl>
  </xsl:template>
  <xsl:template match="persname">
    <dt>
      <xsl:text>Name</xsl:text>
    </dt>
    <dd>
      <xsl:value-of select="emph[@altrender='surname']/text()"/>
      <xsl:if test="emph[@altrender='surname'] and emph[@altrender='forenames']">
        <xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:value-of select="emph[@altrender='forenames']/text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='page']">
    <dt>Page number</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="corpname">
    <dt>Corps</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='rank']">
    <dt>Rank</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='regno']">
    <dt>Regiment number</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='people']">
    <dt>People mentioned</dt>
    <xsl:for-each select="./persname">
      <dd>
        <xsl:value-of select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="emph[@altrender='orgsmentioned']">
    <dt>Organisations mentioned</dt>
    <xsl:for-each select="./corpname">
      <dd>
        <xsl:value-of select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
