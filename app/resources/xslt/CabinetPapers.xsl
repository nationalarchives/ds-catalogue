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
  <xsl:template match="emph[@altrender='surname']">
    <dt>Attendees</dt>
    <xsl:for-each select="./surname">
      <dd>
        <xsl:value-of disable-output-escaping="yes" select="text()"/>
      </dd>
    </xsl:for-each>
  </xsl:template>
  <xsl:template match="emph[@altrender='agenda']">
    <dt>Agenda</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='formerreference']">
    <dt>Former reference</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='type']">
    <dt>Record type</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='title']">
    <dt>Title</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
  <xsl:template match="emph[@altrender='author']">
    <dt>Author</dt>
    <dd>
      <xsl:value-of select="text()"/>
    </dd>
  </xsl:template>
</xsl:stylesheet>
