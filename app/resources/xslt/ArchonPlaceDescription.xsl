<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html"/>

  <!-- Root -->
  <!-- <xsl:template match="/">
    <xsl:apply-templates/>
  </xsl:template> -->

  <!-- ========== Place description (accessconditions) ========== -->

  <xsl:template match="span[contains(@class, 'wrapper')]">
    <xsl:apply-templates select="*"/>
  </xsl:template>

  <xsl:template match="span[contains(@class, 'accessconditions')]">
    <xsl:apply-templates select="
      *[contains(@class, 'openinghours')][normalize-space()] |
      *[contains(@class, 'holidays')][normalize-space()]
    "/>

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

    <xsl:apply-templates select="
      *[contains(@class, 'comments')][normalize-space()] |
      *[contains(@class, 'appointment')][normalize-space()]
    "/>
  </xsl:template>

  <xsl:template match="span[contains(@class, 'openinghours')] | span[contains(@class, 'holidays')]">
    <p>
      <strong>
        <xsl:choose>
          <xsl:when test="contains(@class, 'openinghours')">Open: </xsl:when>
          <xsl:otherwise>Closed: </xsl:otherwise>
        </xsl:choose>
      </strong>
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
    <div><xsl:value-of select="string($cleaned)" disable-output-escaping="yes"/></div>
  </xsl:template>

  <xsl:template match="span[contains(@class, 'appointment')]">
    <p>
      <strong>Appointment: </strong>
      <xsl:value-of select="."/>
    </p>
  </xsl:template>

  <!-- ========== Contacts (dl-icon-grid rows) ========== -->

  <xsl:template match="contacts">
    <dl class="dl-icon-grid">
      <xsl:if test="addressline1[normalize-space()] or addresstown[normalize-space()] or postcode[normalize-space()] or addresscountry[normalize-space()]">
        <xsl:call-template name="dl-icon-row">
          <xsl:with-param name="icon" select="'fa-building'"/>
          <xsl:with-param name="term" select="'Address'"/>
          <xsl:with-param name="content">
            <p>
              <xsl:for-each select="addressline1[normalize-space()] | addresstown[normalize-space()] | postcode[normalize-space()] | addresscountry[normalize-space()]">
                <xsl:if test="position() &gt; 1"><br/></xsl:if>
                <xsl:choose>
                  <xsl:when test="self::addressline1">
                    <xsl:value-of select="substring-before(concat(., ']]&gt;'), ']]&gt;')" disable-output-escaping="yes"/>
                  </xsl:when>
                  <xsl:otherwise>
                    <xsl:value-of select="."/>
                  </xsl:otherwise>
                </xsl:choose>
              </xsl:for-each>
            </p>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:if>

      <xsl:if test="mapURL[normalize-space()]">
        <xsl:variable name="mapURL-decoded">
          <xsl:call-template name="decode-url">
            <xsl:with-param name="url" select="mapURL"/>
          </xsl:call-template>
        </xsl:variable>
        <xsl:call-template name="dl-icon-row">
          <xsl:with-param name="icon" select="'fa-map-marker'"/>
          <xsl:with-param name="term" select="'Map'"/>
          <xsl:with-param name="term-extra-class" select="' tna-visually-hidden'"/>
          <xsl:with-param name="content">
            <p><a href="{string($mapURL-decoded)}" target="_blank" rel="noopener noreferrer">View on a map</a></p>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:if>

      <xsl:if test="telephone[normalize-space()]">
        <xsl:call-template name="dl-icon-row">
          <xsl:with-param name="icon" select="'fa-phone'"/>
          <xsl:with-param name="term" select="'Telephone'"/>
          <xsl:with-param name="content">
            <a href="tel:{translate(telephone, ' ', '')}"><xsl:value-of select="telephone"/></a>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:if>

      <xsl:if test="url[normalize-space()]">
        <xsl:variable name="url-decoded">
          <xsl:call-template name="decode-url">
            <xsl:with-param name="url" select="url"/>
          </xsl:call-template>
        </xsl:variable>
        <xsl:call-template name="dl-icon-row">
          <xsl:with-param name="icon" select="'fa-globe'"/>
          <xsl:with-param name="term" select="'Website'"/>
          <xsl:with-param name="content">
            <a href="{string($url-decoded)}" target="_blank" rel="noopener noreferrer"><xsl:value-of select="url"/></a>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:if>

      <xsl:if test="contactpeople[normalize-space()]">
        <xsl:call-template name="dl-icon-row">
          <xsl:with-param name="icon" select="'fa-user'"/>
          <xsl:with-param name="term" select="'Contact people'"/>
          <xsl:with-param name="content">
            <xsl:value-of select="contactpeople"/>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:if>
    </dl>
  </xsl:template>

  <!-- ========== Shared named templates ========== -->

  <xsl:template name="dl-icon-row">
    <xsl:param name="icon"/>
    <xsl:param name="term"/>
    <xsl:param name="term-extra-class" select="''"/>
    <xsl:param name="content"/>

    <div class="dl-icon-grid__item">
      <i class="dl-icon-grid__icon fa-solid {$icon}" aria-hidden="true"></i>
      <dt class="dl-icon-grid__term{$term-extra-class}">
        <xsl:value-of select="$term"/>
      </dt>
      <dd class="dl-icon-grid__definition">
        <xsl:copy-of select="$content"/>
      </dd>
    </div>
  </xsl:template>

  <xsl:template name="decode-url">
    <xsl:param name="url"/>
    <xsl:call-template name="replace-string">
      <xsl:with-param name="text" select="$url"/>
      <xsl:with-param name="from" select="'&amp;amp;'"/>
      <xsl:with-param name="to" select="'&amp;'"/>
    </xsl:call-template>
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
