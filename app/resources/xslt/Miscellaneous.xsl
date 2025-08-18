<?xml version="1.0"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" version="1.0">
  <xsl:output method="html"/>
  <xsl:template match="XMLFragment">
    <xsl:apply-templates/>
  </xsl:template>
  <xsl:template match="emph[@altrender='doctype']">
	</xsl:template>
</xsl:stylesheet>
