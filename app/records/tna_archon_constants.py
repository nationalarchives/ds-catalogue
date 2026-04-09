# Added noqa comments to the XML fragments to ignore trailing whitespace warnings (W291) from flake8.


DESCRIPTION_XML_FRAGMENT = """
<contacts>
  <addressline1><![CDATA[Kew]]></addressline1>
  <addresstown><![CDATA[Richmond]]></addresstown>
  <postcode><![CDATA[TW9 4DU]]></postcode>
  <addresscountry><![CDATA[England]]></addresscountry>
  <telephone><![CDATA[]]></telephone>
  <fax><![CDATA[]]></fax>
  <email><![CDATA[]]></email>
  <url><![CDATA[http://www.nationalarchives.gov.uk]]></url>
  <mapURL><![CDATA[http://www.streetmap.co.uk/streetmap.dll?postcode2map?TW9+4DU]]></mapURL>
  <correspaddr><![CDATA[]]></correspaddr>
  <contactpeople/>
</contacts>
"""  # noqa: W291

PLACE_DESCRIPTION_XML_FRAGMENT: str = """
<span class="accessconditions">
  <span class="openinghours">
    For opening times please consult the &lt;a href="https://www.nationalarchives.gov.uk/about/visit-us/opening-times/" target="_blank"&gt;website&lt;/a&gt;
  </span>
  <span class="holidays">
    See the &lt;a href="https://www.nationalarchives.gov.uk/about/visit-us/opening-times/" target="_blank"&gt;website&lt;/a&gt;
  </span>
  <span class="disabledaccess">
    Wheelchair access
  </span>
  <span class="comments">
    If you would like to contact The National Archives please go to the 
    &lt;a href="http://www.nationalarchives.gov.uk/contact-us/" target="_blank"&gt;contact form&lt;/a&gt; 
    page on the website and use the form provided.

    &lt;li&gt;
    Readers tickets are required for access to original records only.
    Proof of identity and current address are required to obtain reader tickets.
    For further details please consult the 
    &lt;a href="https://www.nationalarchives.gov.uk/about/visit-us/researching-here/do-i-need-a-readers-ticket/" target="_blank"&gt;website&lt;/a&gt;.
    &lt;/li&gt;

  </span>
</span>
"""  # noqa: W291
