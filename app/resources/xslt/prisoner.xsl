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
      <xsl:text disable-output-escaping="yes">Name (and alias if used) of prisoner</xsl:text>
    </dt>
    <dd>
      <xsl:value-of select="emph[@altrender='surname']/text()"/>
      <xsl:if test="emph[@altrender='surname'] and emph[@altrender='forenames']">
        <xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:value-of select="emph[@altrender='forenames']/text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="geogname">
    <dt>Place of birth</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='age']">
    <dt>Age</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='court']">
    <dt>Place/court of conviction</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='offence']">
    <dt>Offence</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='sentence']">
    <dt>Sentence</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
</xsl:stylesheet>
