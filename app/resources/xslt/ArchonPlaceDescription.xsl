<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html"/>

  <xsl:template match="span[contains(@class, 'wrapper')]">
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <xsl:template match="span[contains(@class, 'accessconditions')]">
    <xsl:apply-templates select="*[contains(@class, 'openinghours')][normalize-space()]"/>
    <xsl:apply-templates select="*[contains(@class, 'holidays')][normalize-space()]"/>

    <xsl:if test="
      *[contains(@class, 'disabledaccess')][normalize-space()] or
      *[contains(@class, 'idrequired')][normalize-space()] or
      *[contains(@class, 'ticket')][normalize-space()]
    ">
      <ul class="tna-ul">
        <xsl:apply-templates select="
          *[contains(@class, 'disabledaccess')][normalize-space()] |
          *[contains(@class, 'idrequired')][normalize-space()] |
          *[contains(@class, 'ticket')][normalize-space()]
        " mode="li"/>
      </ul>
    </xsl:if>

    <xsl:apply-templates select="*[contains(@class, 'comments')][normalize-space()]"/>
    <xsl:apply-templates select="*[contains(@class, 'appointment')][normalize-space()]"/>
  </xsl:template>

  <xsl:template match="span[contains(@class, 'openinghours')]">
    <p>
      <strong>Open: </strong>
      <xsl:value-of select="." disable-output-escaping="yes"/>
    </p>
  </xsl:template>

  <xsl:template match="span[contains(@class, 'holidays')]">
    <p>
      <strong>Closed: </strong>
      <xsl:value-of select="." disable-output-escaping="yes"/>
    </p>
  </xsl:template>

  <xsl:template match="span[contains(@class, 'disabledaccess')] | span[contains(@class, 'idrequired')] | span[contains(@class, 'ticket')]" mode="li">
    <li><xsl:value-of select="."/></li>
  </xsl:template>

  <xsl:template match="span[contains(@class, 'comments')]">
    <xsl:variable name="cleaned">
      <xsl:call-template name="normalize-comment-markup">
        <xsl:with-param name="text" select="."/>
      </xsl:call-template>
    </xsl:variable>
    <div>
      <xsl:value-of select="string($cleaned)" disable-output-escaping="yes"/>
    </div>
  </xsl:template>

  <xsl:template match="span[contains(@class, 'appointment')]">
    <p>
      <strong>Appointment: </strong>
      <xsl:value-of select="."/>
    </p>
  </xsl:template>

  <xsl:template name="normalize-comment-markup">
    <xsl:param name="text"/>

    <xsl:variable name="no-b">
      <xsl:call-template name="replace-string">
        <xsl:with-param name="text" select="$text"/>
        <xsl:with-param name="from" select="'&lt;b&gt;'"/>
        <xsl:with-param name="to" select="'&lt;p&gt;'"/>
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="no-b-end">
      <xsl:call-template name="replace-string">
        <xsl:with-param name="text" select="string($no-b)"/>
        <xsl:with-param name="from" select="'&lt;/b&gt;'"/>
        <xsl:with-param name="to" select="'&lt;/p&gt;'"/>
      </xsl:call-template>
    </xsl:variable>

    <xsl:variable name="no-li">
      <xsl:call-template name="replace-string">
        <xsl:with-param name="text" select="string($no-b-end)"/>
        <xsl:with-param name="from" select="'&lt;li&gt;'"/>
        <xsl:with-param name="to" select="'&lt;p&gt;'"/>
      </xsl:call-template>
    </xsl:variable>

    <xsl:call-template name="replace-string">
      <xsl:with-param name="text" select="string($no-li)"/>
      <xsl:with-param name="from" select="'&lt;/li&gt;'"/>
      <xsl:with-param name="to" select="'&lt;/p&gt;'"/>
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
