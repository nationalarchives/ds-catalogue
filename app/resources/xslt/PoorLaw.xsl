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
    <dt>Name(s)</dt>
    <xsl:for-each select="./emph[@altrender='surname']/surname">
      <dd>
        <xsl:value-of select="."/>
        <xsl:text>, </xsl:text>
        <xsl:for-each select="../../emph[@altrender='forenames']/firstname">
          <xsl:value-of select="."/>
          <xsl:text> </xsl:text>
        </xsl:for-each>
      </dd>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="emph[@altrender='placesmentioned']">
    <dt>Places mentioned</dt>
    <xsl:for-each select="./geogname">
      <dd>
        <xsl:value-of select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="emph[@altrender='orgsmentioned']">
    <dt>Corporations</dt>
    <xsl:for-each select="./corpname">
      <dd>
        <xsl:value-of select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="emph[@altrender='occupation']">
    <dt>Occupation</dt>
    <xsl:for-each select="./occupation">
      <dd>
        <xsl:value-of select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="emph[@altrender='date']">
    <dt>Date of correspondence</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='scope']">
    <dt>Content</dt>
    <dd>
      <xsl:for-each select="p | ul">
        <xsl:for-each select="descendant-or-self::*">
          <xsl:choose>
            <xsl:when test="self::ul">
              <ul class="tna-ul">
                <xsl:for-each select="child::li">
                  <li/>
                  <xsl:value-of disable-output-escaping="yes" select="."/>
                </xsl:for-each>
              </ul>
            </xsl:when>
            <xsl:when test="self::p">
              <xsl:value-of disable-output-escaping="yes" select="."/>
            </xsl:when>
          </xsl:choose>
        </xsl:for-each>
      </xsl:for-each>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='scope2']">
    <dt>Content</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
</xsl:stylesheet>
