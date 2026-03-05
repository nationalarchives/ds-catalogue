<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html"/>

  <!-- Match document root: input is description.raw with root element <contacts> -->
  <!-- Output matches archon_detail.html dummy: dl.dl-icon-grid with dl-icon-grid__item blocks -->
  <xsl:template match="/">
    <xsl:apply-templates select="contacts"/>
  </xsl:template>

  <xsl:template match="contacts">
    <dl class="dl-icon-grid">
      <!-- Address (same format as mock_archive.address in template) -->
      <xsl:if test="addressline1[normalize-space()] or addresstown[normalize-space()] or postcode[normalize-space()] or addresscountry[normalize-space()]">
        <div class="dl-icon-grid__item">
          <i class="dl-icon-grid__icon fa-solid fa-building" aria-hidden="true"></i>
          <dt class="dl-icon-grid__term">Address</dt>
          <dd class="dl-icon-grid__definition">
            <p>
              <xsl:if test="addressline1[normalize-space()]">
                <xsl:value-of select="substring-before(concat(addressline1, ']]&gt;'), ']]&gt;')" disable-output-escaping="yes"/>
              </xsl:if>
              <xsl:if test="addresstown[normalize-space()]">
                <xsl:if test="addressline1[normalize-space()]"><br/></xsl:if>
                <xsl:value-of select="addresstown"/>
              </xsl:if>
              <xsl:if test="postcode[normalize-space()]">
                <xsl:if test="addressline1[normalize-space()] or addresstown[normalize-space()]"><br/></xsl:if>
                <xsl:value-of select="postcode"/>
              </xsl:if>
              <xsl:if test="addresscountry[normalize-space()]">
                <xsl:if test="addressline1[normalize-space()] or addresstown[normalize-space()] or postcode[normalize-space()]"><br/></xsl:if>
                <xsl:value-of select="addresscountry"/>
              </xsl:if>
            </p>
          </dd>
        </div>
      </xsl:if>

      <!-- Map -->
      <xsl:if test="mapURL[normalize-space()]">
        <div class="dl-icon-grid__item">
          <i class="dl-icon-grid__icon fa-solid fa-map-marker" aria-hidden="true"></i>
          <dt class="dl-icon-grid__term tna-visually-hidden">Map</dt>
          <dd class="dl-icon-grid__definition">
            <p><a href="{mapURL}" target="_blank" rel="noopener noreferrer">View on a map</a></p>
          </dd>
        </div>
      </xsl:if>

      <!-- Telephone -->
      <xsl:if test="telephone[normalize-space()]">
        <div class="dl-icon-grid__item">
          <i class="dl-icon-grid__icon fa-solid fa-phone" aria-hidden="true"></i>
          <dt class="dl-icon-grid__term">Telephone</dt>
          <dd class="dl-icon-grid__definition">
            <a href="tel:{translate(telephone, ' ', '')}"><xsl:value-of select="telephone"/></a>
          </dd>
        </div>
      </xsl:if>

      <!-- Website -->
      <xsl:if test="url[normalize-space()]">
        <div class="dl-icon-grid__item">
          <i class="dl-icon-grid__icon fa-solid fa-globe" aria-hidden="true"></i>
          <dt class="dl-icon-grid__term">Website</dt>
          <dd class="dl-icon-grid__definition">
            <a href="{url}" target="_blank" rel="noopener noreferrer"><xsl:value-of select="url"/></a>
          </dd>
        </div>
      </xsl:if>

      <!-- Contact people (no equivalent in dummy; use fa-user) -->
      <xsl:if test="contactpeople[normalize-space()]">
        <div class="dl-icon-grid__item">
          <i class="dl-icon-grid__icon fa-solid fa-user" aria-hidden="true"></i>
          <dt class="dl-icon-grid__term">Contact people</dt>
          <dd class="dl-icon-grid__definition">
            <xsl:value-of select="contactpeople"/>
          </dd>
        </div>
      </xsl:if>
    </dl>
  </xsl:template>
</xsl:stylesheet>
