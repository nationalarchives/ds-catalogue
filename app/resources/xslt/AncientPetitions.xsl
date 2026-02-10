<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html" encoding="utf-8"/>
  <xsl:template match="emph[@altrender='doctype']">
	</xsl:template>
  <xsl:template match="/">
    <dl class="tna-dl tna-dl--lined tna-dl--dotted">
      <xsl:apply-templates/>
    </dl>
  </xsl:template>
  <xsl:template match="persname">
    <dt>
      <xsl:text disable-output-escaping="yes">Name(s)</xsl:text>
    </dt>
    <dd>
      <xsl:value-of select="emph[@altrender='surname']/text()"/>
      <xsl:if test="emph[@altrender='surname'] and emph[@altrender='forenames']">
        <xsl:text>, </xsl:text>
      </xsl:if>
      <xsl:value-of select="emph[@altrender='forenames']/text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='petitioners']">
    <dt>Petitioners</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='placesmentioned']">
    <dt>Places mentioned</dt>
    <xsl:for-each select="./geogname">
      <dd>
        <xsl:value-of disable-output-escaping="yes" select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="emph[@altrender='addressees']">
    <dt>Addressees</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="occupation">
    <dt>Occupation</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='date']">
    <dt>Date derivation</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='request']">
    <dt>Nature of request</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='endorsement']">
    <dt>Nature of endorsement</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='people']">
    <dt>People mentioned</dt>
    <xsl:for-each select="./persname">
      <dd>
        <xsl:value-of disable-output-escaping="yes" select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
