<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html"/>

  <xsl:template match="contacts">
    <xsl:if test="url[normalize-space()]">
      <xsl:variable name="url-decoded">
        <xsl:call-template name="decode-url">
          <xsl:with-param name="url" select="url"/>
        </xsl:call-template>
      </xsl:variable>
      <xsl:value-of select="string($url-decoded)"/>
    </xsl:if>
  </xsl:template>

  <xsl:template name="decode-url">
    <xsl:param name="url"/>
    <xsl:call-template name="replace-string">
      <xsl:with-param name="text" select="$url"/>
      <xsl:with-param name="from" select="'&amp;amp;'"/>
      <xsl:with-param name="to" select="'&amp;'"/>
    </xsl:call-template>
  </xsl:template>

  <xsl:template name="replace-string">
    <xsl:param name="text"/>
    <xsl:param name="from"/>
    <xsl:param name="to"/>

    <xsl:choose>
      <xsl:when test="contains($text, $from)">
        <xsl:value-of select="substring-before($text, $from)"/>
        <xsl:value-of select="$to"/>
        <xsl:call-template name="replace-string">
          <xsl:with-param name="text" select="substring-after($text, $from)"/>
          <xsl:with-param name="from" select="$from"/>
          <xsl:with-param name="to" select="$to"/>
        </xsl:call-template>
      </xsl:when>
      <xsl:otherwise>
        <xsl:value-of select="$text"/>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>
