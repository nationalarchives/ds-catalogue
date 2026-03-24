<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html"/>

  <xsl:template match="contacts">
    <dl class="tna-dl tna-dl-archon-contact">
      <xsl:if test="addressline1[normalize-space()] or addresstown[normalize-space()] or postcode[normalize-space()] or addresscountry[normalize-space()]">
        <xsl:call-template name="dl-icon-row">
          <xsl:with-param name="icon" select="'fa-building'"/>
          <xsl:with-param name="term" select="'Address'"/>
          <xsl:with-param name="content">
            <p>
              <xsl:for-each select="addressline1[normalize-space()] | addresstown[normalize-space()] | postcode[normalize-space()] | addresscountry[normalize-space()]">
                <xsl:if test="position() &gt; 1"><br/></xsl:if>
                <xsl:value-of select="." disable-output-escaping="yes"/>
              </xsl:for-each>
            </p>
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
        <xsl:call-template name="dl-icon-row">
          <xsl:with-param name="icon" select="'fa-globe'"/>
          <xsl:with-param name="term" select="'Website'"/>
          <xsl:with-param name="content">
            <a href="{url}" target="_blank" rel="noopener noreferrer"><xsl:value-of select="url"/></a>
          </xsl:with-param>
        </xsl:call-template>
      </xsl:if>
    </dl>
  </xsl:template>

  <xsl:template name="dl-icon-row">
    <xsl:param name="icon"/>
    <xsl:param name="term"/>
    <xsl:param name="content"/>

    <dt>
      <i class="fa-solid fa-fw {$icon}" aria-hidden="true"></i>
      <xsl:value-of select="$term"/>
    </dt>
    <dd>
      <xsl:copy-of select="$content"/>
    </dd>
  </xsl:template>
</xsl:stylesheet>
