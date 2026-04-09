from app.records.constants import TNA_ARCHON_CODE, RecordTypes
from app.records.models import Record
from config.jinja import sanitise_record_field
from django.test import SimpleTestCase


class NonTnaArchonRecordTransformationTests(SimpleTestCase):
    """Tests for XSLT transformations applied to non-TNA ARCHON records, which use the same XSLT
    as TNA ARCHON records but with some differences in the input data"""

    maxDiff = None

    def setUp(self):

        self.template_details = {"some value": "some value"}

    def test_description(
        self,
    ):
        """Test that the description field is transformed correctly for a non-TNA ARCHON record."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "A13531985"
        self.record._raw["referenceNumber"] = "188"
        self.record._raw["source"] = "ARCHON"
        self.record._raw["description"] = {
            "raw": """\u003ccontacts\u003e\u003caddressline1\u003e\u003c![CDATA[The Shakespeare Centre \u003cbr /\u003e\u003cbr /\u003eHenley Street]]\u003e\u003c/addressline1\u003e\u003caddresstown\u003e\u003c![CDATA[Stratford-upon-Avon]]\u003e\u003c/addresstown\u003e\u003cpostcode\u003e\u003c![CDATA[CV37 6QW]]\u003e\u003c/postcode\u003e\u003caddresscountry\u003e\u003c![CDATA[England]]\u003e\u003c/addresscountry\u003e\u003ctelephone\u003e\u003c![CDATA[01789 204 016]]\u003e\u003c/telephone\u003e\u003cfax\u003e\u003c![CDATA[]]\u003e\u003c/fax\u003e\u003cemail\u003e\u003c![CDATA[collections@shakespeare.org.uk]]\u003e\u003c/email\u003e\u003curl\u003e\u003c![CDATA[https://www.shakespeare.org.uk/]]\u003e\u003c/url\u003e\u003cmapURL\u003e\u003c![CDATA[http://www.streetmap.co.uk/streetmap.dll?postcode2map?CV37+6QW]]\u003e\u003c/mapURL\u003e\u003ccorrespaddr\u003e\u003c![CDATA[]]\u003e\u003c/correspaddr\u003e\u003ccontactpeople\u003e\u003ccontact\u003e\u003cjobTitle\u003e\u003c![CDATA[Director of Cultural Engagement]]\u003e\u003c/jobTitle\u003e\u003ctitle\u003e\u003c![CDATA[Dr]]\u003e\u003c/title\u003e\u003cfirstName\u003e\u003c![CDATA[Delia]]\u003e\u003c/firstName\u003e\u003clastName\u003e\u003c![CDATA[Garratt]]\u003e\u003c/lastName\u003e\u003c/contact\u003e\u003ccontact\u003e\u003cjobTitle\u003e\u003c![CDATA[Collections Archivist]]\u003e\u003c/jobTitle\u003e\u003ctitle\u003e\u003c![CDATA[Ms]]\u003e\u003c/title\u003e\u003cfirstName\u003e\u003c![CDATA[Amy]]\u003e\u003c/firstName\u003e\u003clastName\u003e\u003c![CDATA[Hurst]]\u003e\u003c/lastName\u003e\u003c/contact\u003e\u003ccontact\u003e\u003cjobTitle\u003e\u003c![CDATA[Head of Collections]]\u003e\u003c/jobTitle\u003e\u003cfirstName\u003e\u003c![CDATA[Paul]]\u003e\u003c/firstName\u003e\u003clastName\u003e\u003c![CDATA[Taylor]]\u003e\u003c/lastName\u003e\u003c/contact\u003e\u003ccontact\u003e\u003cjobTitle\u003e\u003c![CDATA[]]\u003e\u003c/jobTitle\u003e\u003ctitle\u003e\u003c![CDATA[]]\u003e\u003c/title\u003e\u003cfirstName\u003e\u003c![CDATA[Paul  ]]\u003e\u003c/firstName\u003e\u003clastName\u003e\u003c![CDATA[Carlyle]]\u003e\u003c/lastName\u003e\u003c/contact\u003e\u003ccontact\u003e\u003cjobTitle\u003e\u003c![CDATA[Archivist]]\u003e\u003c/jobTitle\u003e\u003ctitle\u003e\u003c![CDATA[]]\u003e\u003c/title\u003e\u003cfirstName\u003e\u003c![CDATA[James]]\u003e\u003c/firstName\u003e\u003clastName\u003e\u003c![CDATA[Ranahan]]\u003e\u003c/lastName\u003e\u003c/contact\u003e\u003c/contactpeople\u003e\u003c/contacts\u003e"""
        }
        self.assertEqual(self.record.custom_record_type, RecordTypes.ARCHON)
        self.assertNotEqual(self.record.reference_number, TNA_ARCHON_CODE)

        # field is sanitised in the template
        self.assertEqual(
            sanitise_record_field(self.record.description),
            """<dl class="tna-dl tna-dl--stacked">
<dt>
<i class="fa-solid fa-fw fa-building" aria-hidden="true"></i>Address</dt>
<dd><p>The Shakespeare Centre <br /><br />Henley Street<br>Stratford-upon-Avon<br>CV37 6QW<br>England</p></dd>
<dt>
<i class="fa-solid fa-fw fa-phone" aria-hidden="true"></i>Telephone</dt>
<dd><a href="tel:01789204016">01789 204 016</a></dd>
<dt>
<i class="fa-solid fa-fw fa-envelope" aria-hidden="true"></i>Email</dt>
<dd><a href="mailto:collections@shakespeare.org.uk">collections@shakespeare.org.uk</a></dd>
<dt>
<i class="fa-solid fa-fw fa-globe" aria-hidden="true"></i>Website</dt>
<dd><a href="https://www.shakespeare.org.uk/" target="_blank" rel="noopener noreferrer">https://www.shakespeare.org.uk/</a></dd>
</dl>""",
        )

    def test_archon_website(
        self,
    ):
        """Test that the archon_website field is transformed correctly for a non-TNA ARCHON record."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "A13531985"
        self.record._raw["referenceNumber"] = "188"
        self.record._raw["source"] = "ARCHON"
        self.record._raw["description"] = {
            "raw": """\u003ccontacts\u003e\u003caddressline1\u003e\u003c![CDATA[The Shakespeare Centre \u003cbr /\u003e\u003cbr /\u003eHenley Street]]\u003e\u003c/addressline1\u003e\u003caddresstown\u003e\u003c![CDATA[Stratford-upon-Avon]]\u003e\u003c/addresstown\u003e\u003cpostcode\u003e\u003c![CDATA[CV37 6QW]]\u003e\u003c/postcode\u003e\u003caddresscountry\u003e\u003c![CDATA[England]]\u003e\u003c/addresscountry\u003e\u003ctelephone\u003e\u003c![CDATA[01789 204 016]]\u003e\u003c/telephone\u003e\u003cfax\u003e\u003c![CDATA[]]\u003e\u003c/fax\u003e\u003cemail\u003e\u003c![CDATA[collections@shakespeare.org.uk]]\u003e\u003c/email\u003e\u003curl\u003e\u003c![CDATA[https://www.shakespeare.org.uk/]]\u003e\u003c/url\u003e\u003cmapURL\u003e\u003c![CDATA[http://www.streetmap.co.uk/streetmap.dll?postcode2map?CV37+6QW]]\u003e\u003c/mapURL\u003e\u003ccorrespaddr\u003e\u003c![CDATA[]]\u003e\u003c/correspaddr\u003e\u003ccontactpeople\u003e\u003ccontact\u003e\u003cjobTitle\u003e\u003c![CDATA[Director of Cultural Engagement]]\u003e\u003c/jobTitle\u003e\u003ctitle\u003e\u003c![CDATA[Dr]]\u003e\u003c/title\u003e\u003cfirstName\u003e\u003c![CDATA[Delia]]\u003e\u003c/firstName\u003e\u003clastName\u003e\u003c![CDATA[Garratt]]\u003e\u003c/lastName\u003e\u003c/contact\u003e\u003ccontact\u003e\u003cjobTitle\u003e\u003c![CDATA[Collections Archivist]]\u003e\u003c/jobTitle\u003e\u003ctitle\u003e\u003c![CDATA[Ms]]\u003e\u003c/title\u003e\u003cfirstName\u003e\u003c![CDATA[Amy]]\u003e\u003c/firstName\u003e\u003clastName\u003e\u003c![CDATA[Hurst]]\u003e\u003c/lastName\u003e\u003c/contact\u003e\u003ccontact\u003e\u003cjobTitle\u003e\u003c![CDATA[Head of Collections]]\u003e\u003c/jobTitle\u003e\u003cfirstName\u003e\u003c![CDATA[Paul]]\u003e\u003c/firstName\u003e\u003clastName\u003e\u003c![CDATA[Taylor]]\u003e\u003c/lastName\u003e\u003c/contact\u003e\u003ccontact\u003e\u003cjobTitle\u003e\u003c![CDATA[]]\u003e\u003c/jobTitle\u003e\u003ctitle\u003e\u003c![CDATA[]]\u003e\u003c/title\u003e\u003cfirstName\u003e\u003c![CDATA[Paul  ]]\u003e\u003c/firstName\u003e\u003clastName\u003e\u003c![CDATA[Carlyle]]\u003e\u003c/lastName\u003e\u003c/contact\u003e\u003ccontact\u003e\u003cjobTitle\u003e\u003c![CDATA[Archivist]]\u003e\u003c/jobTitle\u003e\u003ctitle\u003e\u003c![CDATA[]]\u003e\u003c/title\u003e\u003cfirstName\u003e\u003c![CDATA[James]]\u003e\u003c/firstName\u003e\u003clastName\u003e\u003c![CDATA[Ranahan]]\u003e\u003c/lastName\u003e\u003c/contact\u003e\u003c/contactpeople\u003e\u003c/contacts\u003e"""
        }

        self.assertEqual(self.record.custom_record_type, RecordTypes.ARCHON)
        self.assertNotEqual(self.record.reference_number, TNA_ARCHON_CODE)

        # field is sanitised in the template
        self.assertEqual(
            sanitise_record_field(self.record.archon_website),
            """https://www.shakespeare.org.uk/""",
        )

    def test_place_description(
        self,
    ):
        """Test that the place_description field is transformed correctly for a non-TNA ARCHON record."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "A13531985"
        self.record._raw["referenceNumber"] = "188"
        self.record._raw["source"] = "ARCHON"
        self.record._raw["placeDescription"] = {
            "raw": """\u003cspan class=\"wrapper\"\u003e\u003cspan class=\"accessconditions\"\u003e\u003cspan class=\"openinghours\"\u003eMonday 10.15-12.30, Tuesday 10.15-3, Wednesday 10.15-12.30 by appointment\u003c/span\u003e\u003cspan class=\"holidays\"\u003eBank holidays; Christmas/New Year\u003c/span\u003e\u003cspan class=\"disabledaccess\"\u003eWheelchair access\u003c/span\u003e\u003cspan class=\"comments\"\u003e&lt;b&gt;Two hour appointment slots must by booked in advance.  See &lt;a href=\"https://www.shakespeare.org.uk/visit/plan-your-visit/reading-room/\" target=\"_blank\"&gt;website&lt;/a&gt; for details&lt;/b&gt;\n&lt;li&gt;Readers will need to provide a letter of recommendation to see certain items - please &lt;a href=\"mailto:collections@shakespeare.org.uk\"&gt;email&lt;/a&gt; for further details&lt;/li&gt;\n&lt;li&gt;Reprographics: Staff can copy certain items for a small fee; self-service photograph permits (certain items only) - £5 per day&lt;/li&gt;\u003c/span\u003e\u003cspan class=\"idrequired\"\u003eProof of identity required\u003c/span\u003e\u003cspan class=\"ticket\"\u003eReaders ticket required\u003c/span\u003e\u003c/span\u003e\u003c/span\u003e"""
        }

        self.assertEqual(self.record.custom_record_type, RecordTypes.ARCHON)
        self.assertNotEqual(self.record.reference_number, TNA_ARCHON_CODE)

        # field is sanitised in the template
        self.assertEqual(
            sanitise_record_field(self.record.place_description),
            """<p><strong>Open: </strong>Monday 10.15-12.30, Tuesday 10.15-3, Wednesday 10.15-12.30 by appointment</p><p><strong>Closed: </strong>Bank holidays; Christmas/New Year</p><ul class="tna-ul">
<li>Wheelchair access</li>
<li>Proof of identity required</li>
<li>Readers ticket required</li>
</ul><div><p>Two hour appointment slots must by booked in advance.  See <a href="https://www.shakespeare.org.uk/visit/plan-your-visit/reading-room/" target="_blank">website</a> for details</p><p>Readers will need to provide a letter of recommendation to see certain items - please <a href="mailto:collections@shakespeare.org.uk">email</a> for further details</p><p>Reprographics: Staff can copy certain items for a small fee; self-service photograph permits (certain items only) - £5 per day</p></div>""",
        )


class TnaArchonRecordTransformationTests(SimpleTestCase):
    """Tests for XSLT transformations applied to TNA ARCHON records, which use the same XSLT
    as Non-TNA ARCHON records but with some differences in the input data"""

    maxDiff = None

    def setUp(self):

        self.template_details = {"some value": "some value"}

    def test_description(
        self,
    ):
        """Test that the description field is transformed correctly for a TNA ARCHON record."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "A13530124"
        self.record._raw["referenceNumber"] = "66"
        self.record._raw["source"] = "ARCHON"
        self.record._raw["description"] = {
            "raw": """API DATA WILL BE IGNORED AND REPLACED WITH STATIC DATA FOR TNA ARCHON RECORDS"""
        }

        self.assertEqual(self.record.custom_record_type, RecordTypes.ARCHON)
        self.assertEqual(self.record.reference_number, TNA_ARCHON_CODE)

        # field is sanitised in the template
        self.assertEqual(
            sanitise_record_field(self.record.description),
            """<dl class="tna-dl tna-dl--stacked">
<dt>
<i class="fa-solid fa-fw fa-building" aria-hidden="true"></i>Address</dt>
<dd><p>Kew<br>Richmond<br>TW9 4DU<br>England</p></dd>
<dt>
<i class="fa-solid fa-fw fa-globe" aria-hidden="true"></i>Website</dt>
<dd><a href="http://www.nationalarchives.gov.uk" target="_blank" rel="noopener noreferrer">http://www.nationalarchives.gov.uk</a></dd>
</dl>""",
        )

    def test_archon_website(
        self,
    ):
        """Test that the archon_website field is transformed correctly for a TNA ARCHON record.
        The website url should not be extracted for TNA ARCHON records, so the field should be an empty string
        even if there is a website url in the description."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "A13530124"
        self.record._raw["referenceNumber"] = "66"
        self.record._raw["source"] = "ARCHON"
        # contains a website url in the description
        self.record._raw["description"] = {
            "raw": """API DATA WILL BE IGNORED AND REPLACED WITH STATIC DATA FOR TNA ARCHON RECORDS"""
        }

        self.assertEqual(self.record.custom_record_type, RecordTypes.ARCHON)
        self.assertEqual(self.record.reference_number, TNA_ARCHON_CODE)

        # website url should not be extracted for TNA ARCHON records, so empty string
        # field is sanitised in the template
        self.assertEqual(
            sanitise_record_field(self.record.archon_website), """"""
        )

    def test_place_description(
        self,
    ):
        """Test that the place_description field is transformed correctly for a TNA ARCHON record."""

        self.record = Record(self.template_details)
        # patch raw data
        self.record._raw["id"] = "A13531985"
        self.record._raw["referenceNumber"] = "66"
        self.record._raw["source"] = "ARCHON"
        self.record._raw["placeDescription"] = {
            "raw": """API DATA WILL BE IGNORED AND REPLACED WITH STATIC DATA FOR TNA ARCHON RECORDS"""
        }

        self.assertEqual(self.record.custom_record_type, RecordTypes.ARCHON)
        self.assertEqual(self.record.reference_number, TNA_ARCHON_CODE)

        # field is sanitised in the template
        self.assertEqual(
            sanitise_record_field(self.record.place_description),
            """<p><strong>Open: </strong>
    For opening times please consult the <a href="https://www.nationalarchives.gov.uk/about/visit-us/opening-times/" target="_blank">website</a>
  </p><p><strong>Closed: </strong>
    See the <a href="https://www.nationalarchives.gov.uk/about/visit-us/opening-times/" target="_blank">website</a>
  </p><ul class="tna-ul"><li>
    Wheelchair access
  </li></ul><div>
    If you would like to contact The National Archives please go to the 
    <a href="http://www.nationalarchives.gov.uk/contact-us/" target="_blank">contact form</a> 
    page on the website and use the form provided.

    <p>
    Readers tickets are required for access to original records only.
    Proof of identity and current address are required to obtain reader tickets.
    For further details please consult the 
    <a href="https://www.nationalarchives.gov.uk/about/visit-us/researching-here/do-i-need-a-readers-ticket/" target="_blank">website</a>.
    </p>

  </div>""",  # noqa: W291
        )
