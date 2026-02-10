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
  <xsl:template match="geogname">
    <dt>Place name</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='domesdayform']">
    <dt>Domesday place name</dt>
    <xsl:for-each select="./geogname">
      <dd>
        <xsl:value-of select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="emph[@altrender='folio']">
    <dt>Folio</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='placesmentioned']">
    <dt>Places mentioned</dt>
    <xsl:for-each select="./geogname">
      <dd>
        <xsl:value-of select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="emph[@altrender='peoplementioned']">
    <dt>People mentioned within entire folio</dt>
    <xsl:for-each select="./persname">
      <dd>
        <xsl:value-of select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
</xsl:stylesheet>
