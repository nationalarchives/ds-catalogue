import unittest

from app.lib.xslt_transformations import (
    apply_schema_xsl,
    apply_series_xsl,
    xsl_transformation,
)


class XsltTransformationsTestCase(unittest.TestCase):
    def test_Airwomen(self):
        # D7493830
        source = '<emph altrender="doctype">AW</emph><persname><emph altrender="surname">Aarons</emph> <emph altrender="forenames">Ethel</emph></persname><emph altrender="num">21906</emph><emph altrender="doe">19 October 1918</emph>'
        schema = "Airwomen"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Aarons, Ethel</dd>
<dt>Service number</dt>
<dd>21906</dd>
<dt>Date of enrolment</dt>
<dd>19 October 1918</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_AliensRegCards(self):
        # C8675691
        source = '<emph altrender="doctype">AR</emph><persname><emph altrender="forenames">Jean Margaret</emph><emph altrender="surname">Aal</emph></persname><emph altrender="age">27 January 1917</emph><emph altrender="nation">German</emph>'
        schema = "AliensRegCards"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Aal, Jean Margaret</dd>
<dt>Date of birth</dt>
<dd>27 January 1917</dd>
<dt>Nationality</dt>
<dd>German</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_AncientPetitions(self):
        # C9439604
        source = '<emph altrender="doctype">AP</emph><emph altrender="petitioners">John de Heghman.</emph><emph altrender="name"><persname><emph altrender="surname">de Heghman</emph> <emph altrender="forenames">John</emph></persname></emph><emph altrender="addressees">King.</emph><emph altrender="request">Heghman requests that the king grant his letters to Guildford and his companions assigned to take an attaint at the suit of Heghman that they not assent to the order to be at parliament.</emph><emph altrender="endorsement">[None].</emph><emph altrender="people"><persname>Henry de Gyldeford (Guildford), justice.</persname></emph>'
        schema = "AncientPetitions"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Petitioners</dt>
<dd>John de Heghman.</dd>
<dt>Name(s)</dt>
<dd>de Heghman, John</dd>
<dt>Addressees</dt>
<dd>King.</dd>
<dt>Nature of request</dt>
<dd>Heghman requests that the king grant his letters to Guildford and his companions assigned to take an attaint at the suit of Heghman that they not assent to the order to be at parliament.</dd>
<dt>Nature of endorsement</dt>
<dd>[None].</dd>
<dt>People mentioned</dt>
<dd>Henry de Gyldeford (Guildford), justice.</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_BritishWarMedal(self):
        # D8030479
        source = '<emph altrender="doctype">BW</emph><persname><emph altrender="surname">Hillyard</emph><emph altrender="forenames">Henry William</emph></persname><geogname>Rowhedge</geogname><emph altrender="dob">1873</emph>'
        schema = "BritishWarMedal"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Hillyard, Henry William</dd>
<dt>Place of birth</dt>
<dd>Rowhedge</dd>
<dt>Date of birth</dt>
<dd>1873</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_CabinetPapers(self):
        # C11083504
        source = '<emph altrender="doctype">CP</emph><emph altrender="type">Precedent Book</emph><emph altrender="agenda">1. Constitutional Position - The Cabinet and the Cabinet System - Collective Responsibility; 2. Composition of the Cabinet and the Position of Ministers Outside the Cabinet - Appointment to the Cabinet - Composition of the Cabinet  - Ministers with Co-ordinating Functions - Ministers Outside the Cabinet - Law Officers - Junior Ministers - Precedence of Members of  Cabinet and Other Ministers; 3. Attendence at the Cabinet - Members of the Cabinet and Ministers of Cabinet Rank - Junior Ministers - Chiefs of Staff - Officials and Others - Historical Notes -  War Cabinet, 1916-1919 - Cabinet, 1919-1939 - War Cabinet, 1939-1945 - Attendance at \'Budget Cabinets\' - Leave of Absence - Movements of Ministers; 4. Cabinet Business - Scope of Business - Foreign and Military Affairs - Parliamentary Business -  Economic Affairs - The Budget - White Papers; 5. Action Prior to Submission of Business; 6. Submission of Business; 7. Action in the Cabinet Office; 8. Programme of Future Business; 9. Agenda; 10. Meetings - General Practice - Frequency of Meetings - Special Meetings - Meetings in Holiday Periods - Messages during Meetings - Attendance of Secretariat; 11. Cabinet Conclusions - General - Dissent from Conclusions - Implementation of Conclusions - Outstanding Conclusions; 12. Secrecy of Cabinet Proceedings; 13. Announcement of Cabinet Decisions; 14. Press Communiques about Cabinet Meetings; 15. War Cabinet Reports; 16. Miscellaneous - Cabinet Photographs - Cabinet Presents, etc</emph><emph altrender="title">Part I - The Cabinet</emph>'
        schema = "CabinetPapers"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Record type</dt>
<dd>Precedent Book</dd>
<dt>Agenda</dt>
<dd>1. Constitutional Position - The Cabinet and the Cabinet System - Collective Responsibility; 2. Composition of the Cabinet and the Position of Ministers Outside the Cabinet - Appointment to the Cabinet - Composition of the Cabinet  - Ministers with Co-ordinating Functions - Ministers Outside the Cabinet - Law Officers - Junior Ministers - Precedence of Members of  Cabinet and Other Ministers; 3. Attendence at the Cabinet - Members of the Cabinet and Ministers of Cabinet Rank - Junior Ministers - Chiefs of Staff - Officials and Others - Historical Notes -  War Cabinet, 1916-1919 - Cabinet, 1919-1939 - War Cabinet, 1939-1945 - Attendance at 'Budget Cabinets' - Leave of Absence - Movements of Ministers; 4. Cabinet Business - Scope of Business - Foreign and Military Affairs - Parliamentary Business -  Economic Affairs - The Budget - White Papers; 5. Action Prior to Submission of Business; 6. Submission of Business; 7. Action in the Cabinet Office; 8. Programme of Future Business; 9. Agenda; 10. Meetings - General Practice - Frequency of Meetings - Special Meetings - Meetings in Holiday Periods - Messages during Meetings - Attendance of Secretariat; 11. Cabinet Conclusions - General - Dissent from Conclusions - Implementation of Conclusions - Outstanding Conclusions; 12. Secrecy of Cabinet Proceedings; 13. Announcement of Cabinet Decisions; 14. Press Communiques about Cabinet Meetings; 15. War Cabinet Reports; 16. Miscellaneous - Cabinet Photographs - Cabinet Presents, etc</dd>
<dt>Title</dt>
<dd>Part I - The Cabinet</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_CombatRepWW2(self):
        # D7440727
        source = '<emph altrender="doctype">CR</emph><persname> <emph altrender="surname">Gibson</emph> <emph altrender="forenames">G P</emph></persname><emph altrender="rank">Flight Lieutenant, Squadron Leader</emph><emph altrender= "corpname">29</emph><emph altrender="date">14 March 1941; 23 April 1941, 03 May 1941, 07 July 1941</emph>'
        schema = "CombatRepWW2"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Gibson, G P</dd>
<dt>Rank</dt>
<dd>Flight Lieutenant, Squadron Leader</dd>
<dt>Squadron</dt>
<dd>29</dd>
<dt>Other dates of combat</dt>
<dd>14 March 1941; 23 April 1941, 03 May 1941, 07 July 1941</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_DeathDuty(self):
        # D7238397
        source = '<emph altrender="doctype">A</emph><persname> <emph altrender="forenames">Edmund</emph><emph altrender="surname">Barnes</emph></persname><occupation>Farmer</occupation><geogname>Cringleford, Norfolk</geogname>'
        schema = "DeathDuty"
        self.assertEqual(
            "Abstract of administration of Edmund Barnes, Farmer of Cringleford, Norfolk",
            str(apply_schema_xsl(source, schema)),
        )

    def test_DNPC(self):
        # C9147871
        source = '<emph altrender="doctype">DNPC</emph><emph altrender="scope">Naturalisation by Act of Parliament: Dumas, Henry.10 Geo.4.c.57</emph>'
        schema = "DNPC"
        self.assertEqual(
            "Naturalisation by Act of Parliament: Dumas, Henry.10 Geo.4.c.57",
            str(apply_schema_xsl(source, schema)),
        )

    def test_DomesdayBook(self):
        # D7296365
        source = '<emph altrender="doctype">D</emph><emph altrender="placename"><geogname>North Benfleet, Essex</geogname></emph><emph altrender="folio">1v Little Domesday Book</emph><emph altrender="domesdayform"><geogname>Benflet</geogname></emph><emph altrender="peoplementioned"><persname>Church of St Mary, Benfleet</persname><persname>Earl Harold Godwineson</persname><persname>Ralph Baynard, sheriff of Essex</persname><persname>Ranulf brother of Ilger</persname><persname>Swein of Essex, sheriff of Essex</persname><persname>sokemen</persname></emph>'
        schema = "DomesdayBook"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Place name</dt>
<dd>North Benfleet, Essex</dd>
<dt>Folio</dt>
<dd>1v Little Domesday Book</dd>
<dt>Domesday place name</dt>
<dd>Benflet</dd>
<dt>People mentioned within entire folio</dt>
<dd>Church of St Mary, Benfleet</dd>
<dd>Earl Harold Godwineson</dd>
<dd>Ralph Baynard, sheriff of Essex</dd>
<dd>Ranulf brother of Ilger</dd>
<dd>Swein of Essex, sheriff of Essex</dd>
<dd>sokemen</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_EffectsPapers(self):
        # C9943251
        source = '<emph altrender="doctype">EP</emph><emph altrender="scope">Number: 1   Thomas Finn, Superannuated boatswain, who died: 2 August 1854. Notes on executor\'s application for money owed by the Royal Navy.</emph>'
        schema = "EffectsPapers"
        self.assertEqual(
            "Number: 1   Thomas Finn, Superannuated boatswain, who died: 2 August 1854. Notes on executor's application for money owed by the Royal Navy.",
            str(apply_schema_xsl(source, schema)),
        )

    def test_FameWill(self):
        # C198019
        source = '<emph altrender="doctype">G</emph> Will of <persname> <emph altrender="forenames">Robert</emph> <emph altrender="surname">Dudley, Earl of Leicester</emph></persname>  (copy) 1 August 1587. Proved 6 September 1588.'
        schema = "FameWill"
        self.assertEqual(
            "Will of Robert Dudley, Earl of Leicester   (copy) 1 August 1587. Proved 6 September 1588.",
            str(apply_schema_xsl(source, schema)),
        )

    def test_GallantrySea(self):
        # C432714
        source = '<emph altrender="doctype">GS</emph><emph altrender="scope">Lists of persons rewarded by British, Colonial and foreign Governments</emph>'
        schema = "GallantrySea"
        self.assertEqual(
            "Lists of persons rewarded by British, Colonial and foreign Governments",
            str(apply_schema_xsl(source, schema)),
        )

    def test_Generic(self):
        # C361
        source = "<scopecontent><p>The records held in the Archives of the <extref href=&#34https://www.kew.org/kew-gardens?gclid=Cj0KCQjwhY-aBhCUARIsALNIC05tGF54QYaBFnIu_yapO1fpozZwqjyWuLNOUUEAKNQn80v5nWZZkY4aAoA6EALw_wcB&#34>Royal Botanic Gardens, Kew</extref>, comprising: <list><item>Papers of Francis Kingdon-Ward, Explorer and Botanist, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/6556c5f5-0f02-4d03-9b5c-8ec7973794b7&#34>RM 1</extref>; </item><item>Papers of Marianne North, Botanical Painter, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/a48f41eb-1496-446c-8bf8-21dc681223da&#34>RM 2</extref>; </item><item>Papers of Sir Joseph Banks, Botanist, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/4a40b8c2-c701-4054-8c62-1ee21ee98851&#34>RM 3</extref>; </item><item>Papers of George Bentham, Botanist, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/32227b77-f7a4-49ec-8d28-a13f0494404a&#34>RM 4</extref>; </item><item>Papers of Joseph Hooker, Director of Kew Gardens, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/782b3368-c4ec-42d3-8e03-b4c261cb1e6b&#34>RM 5</extref>; </item><item>Papers of Sir William Jackson Hooker, Botanist and first Director of the Royal Botanic Gardens, Kew, in<extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/b794a746-c861-4c21-b51b-1be10e5ccac6&#34> RM 6</extref>; </item><item>Papers relating to the Pleasure Grounds of the Royal Botanic Gardens, Kew, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/f4826bd8-2f22-49bc-bda4-70a918f88179&#34>RM 7</extref>; </item><item>Papers relating to Richard Spruce, Explorer and Botanist, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/c2e75f4e-03b9-45ee-864c-de4bcf2c02d7&#34>RM 8</extref>; </item><item>Papers of Sir Arthur William Hill, Director of the Royal Botanic Gardens, Kew, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/d888174e-d9d6-4651-900a-82ae7d865632&#34>RM 9</extref>; </item><item>Papers of Henry Nicholas Ridley, Director of Gardens and Forests, Straits Settlements, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/7973f020-a18e-4dfc-90c1-da202a8177f4&#34>RM 10</extref>; </item><item>Papers relating to Kew Collectors, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/97e96470-66d4-4887-a453-190fa296f31a&#34>RM 11</extref>; </item><item>Papers of Augustine Henry, Plant collector, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/fe169eca-9d88-46b7-88df-9787122e1d0a&#34>RM 12</extref>; </item><item>Papers relating to William Burchell, Botanist, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/813ab2eb-7694-4164-8f9a-3d7cb0e7ab73&#34>RM 13</extref>; </item><item>Second World War papers, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/2c9f6db0-233a-42d3-8600-81199b0f9f09&#34>RM 14</extref>; </item><item>Papers relating to John Eliot Howard, Quinologist, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/b2b60181-c3c6-400d-9b3f-9862a5a14bf8&#34>RM 15</extref>; </item><item>Papers of the Lovell Reeve Publishing Company, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/a6faaadc-27bc-4673-a0f0-dab7f878b99b&#34>RM 16</extref>; </item><item>Papers relating to Colin Graham Trapnell OBE, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/c820e493-63e2-42c4-acea-6bbd635ef2df&#34>RM 17</extref>;</item><item>Papers of Dr William Arnold Bromfield, Botanist, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/553f9087-6b1c-4f5d-90ea-bca4a80b7305&#34>RM 18</extref>; </item><item> Papers relating to African expeditions, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/ea1eed7b-e1c2-45b2-83dc-17df01b13e7e&#34>RM 19</extref>; </item><item> Papers of Norman Douglas Simpson, Botanist, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/c2cfd361-40df-4f62-aab6-0bcd15c472eb&#34>RM 20</extref>; </item><item>Economic Botany Collection papers, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/c2a17e11-1ce3-43fa-91a1-896a4b64af81&#34>RM 21</extref>; </item><item>Papers of George W Robinson, horticulturist, in <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/c9c3398d-247d-4225-ac66-57e9ded2ff6c&#34>RM 22</extref>. </item></list></p> <p>NOTE: Please use the document references found in the 'Former reference (Department)' field when wishing to consult these documents at the Archives of The Royal Botanic Gardens, Kew.</p> <p>For series created for regularly archived websites, please see the separate <extref href=&#34https://discovery.nationalarchives.gov.uk/details/r/C1528&#34>Websites Division</extref>.</p> <p>The Royal Botanic Gardens, Kew <extref href=&#34https://www2.calmview.co.uk/Kew/CalmView/default.aspx&#34>online catalogue</extref> is available to search. </p></scopecontent>"
        schema = "Generic"
        self.assertEqual(
            """<p>The records held in the Archives of the <a href="https://www.kew.org/kew-gardens?gclid=Cj0KCQjwhY-aBhCUARIsALNIC05tGF54QYaBFnIu_yapO1fpozZwqjyWuLNOUUEAKNQn80v5nWZZkY4aAoA6EALw_wcB" title="Opens in a new tab" target="_blank">Royal Botanic Gardens, Kew</a>, comprising: <ul class="tna-ul">
<li>Papers of Francis Kingdon-Ward, Explorer and Botanist, in <a href="https://discovery.nationalarchives.gov.uk/details/r/6556c5f5-0f02-4d03-9b5c-8ec7973794b7" title="Opens in a new tab" target="_blank">RM 1</a>; </li>
<li>Papers of Marianne North, Botanical Painter, in <a href="https://discovery.nationalarchives.gov.uk/details/r/a48f41eb-1496-446c-8bf8-21dc681223da" title="Opens in a new tab" target="_blank">RM 2</a>; </li>
<li>Papers of Sir Joseph Banks, Botanist, in <a href="https://discovery.nationalarchives.gov.uk/details/r/4a40b8c2-c701-4054-8c62-1ee21ee98851" title="Opens in a new tab" target="_blank">RM 3</a>; </li>
<li>Papers of George Bentham, Botanist, in <a href="https://discovery.nationalarchives.gov.uk/details/r/32227b77-f7a4-49ec-8d28-a13f0494404a" title="Opens in a new tab" target="_blank">RM 4</a>; </li>
<li>Papers of Joseph Hooker, Director of Kew Gardens, in <a href="https://discovery.nationalarchives.gov.uk/details/r/782b3368-c4ec-42d3-8e03-b4c261cb1e6b" title="Opens in a new tab" target="_blank">RM 5</a>; </li>
<li>Papers of Sir William Jackson Hooker, Botanist and first Director of the Royal Botanic Gardens, Kew, in<a href="https://discovery.nationalarchives.gov.uk/details/r/b794a746-c861-4c21-b51b-1be10e5ccac6" title="Opens in a new tab" target="_blank"> RM 6</a>; </li>
<li>Papers relating to the Pleasure Grounds of the Royal Botanic Gardens, Kew, in <a href="https://discovery.nationalarchives.gov.uk/details/r/f4826bd8-2f22-49bc-bda4-70a918f88179" title="Opens in a new tab" target="_blank">RM 7</a>; </li>
<li>Papers relating to Richard Spruce, Explorer and Botanist, in <a href="https://discovery.nationalarchives.gov.uk/details/r/c2e75f4e-03b9-45ee-864c-de4bcf2c02d7" title="Opens in a new tab" target="_blank">RM 8</a>; </li>
<li>Papers of Sir Arthur William Hill, Director of the Royal Botanic Gardens, Kew, in <a href="https://discovery.nationalarchives.gov.uk/details/r/d888174e-d9d6-4651-900a-82ae7d865632" title="Opens in a new tab" target="_blank">RM 9</a>; </li>
<li>Papers of Henry Nicholas Ridley, Director of Gardens and Forests, Straits Settlements, in <a href="https://discovery.nationalarchives.gov.uk/details/r/7973f020-a18e-4dfc-90c1-da202a8177f4" title="Opens in a new tab" target="_blank">RM 10</a>; </li>
<li>Papers relating to Kew Collectors, in <a href="https://discovery.nationalarchives.gov.uk/details/r/97e96470-66d4-4887-a453-190fa296f31a" title="Opens in a new tab" target="_blank">RM 11</a>; </li>
<li>Papers of Augustine Henry, Plant collector, in <a href="https://discovery.nationalarchives.gov.uk/details/r/fe169eca-9d88-46b7-88df-9787122e1d0a" title="Opens in a new tab" target="_blank">RM 12</a>; </li>
<li>Papers relating to William Burchell, Botanist, in <a href="https://discovery.nationalarchives.gov.uk/details/r/813ab2eb-7694-4164-8f9a-3d7cb0e7ab73" title="Opens in a new tab" target="_blank">RM 13</a>; </li>
<li>Second World War papers, in <a href="https://discovery.nationalarchives.gov.uk/details/r/2c9f6db0-233a-42d3-8600-81199b0f9f09" title="Opens in a new tab" target="_blank">RM 14</a>; </li>
<li>Papers relating to John Eliot Howard, Quinologist, in <a href="https://discovery.nationalarchives.gov.uk/details/r/b2b60181-c3c6-400d-9b3f-9862a5a14bf8" title="Opens in a new tab" target="_blank">RM 15</a>; </li>
<li>Papers of the Lovell Reeve Publishing Company, in <a href="https://discovery.nationalarchives.gov.uk/details/r/a6faaadc-27bc-4673-a0f0-dab7f878b99b" title="Opens in a new tab" target="_blank">RM 16</a>; </li>
<li>Papers relating to Colin Graham Trapnell OBE, in <a href="https://discovery.nationalarchives.gov.uk/details/r/c820e493-63e2-42c4-acea-6bbd635ef2df" title="Opens in a new tab" target="_blank">RM 17</a>;</li>
<li>Papers of Dr William Arnold Bromfield, Botanist, in <a href="https://discovery.nationalarchives.gov.uk/details/r/553f9087-6b1c-4f5d-90ea-bca4a80b7305" title="Opens in a new tab" target="_blank">RM 18</a>; </li>
<li> Papers relating to African expeditions, in <a href="https://discovery.nationalarchives.gov.uk/details/r/ea1eed7b-e1c2-45b2-83dc-17df01b13e7e" title="Opens in a new tab" target="_blank">RM 19</a>; </li>
<li> Papers of Norman Douglas Simpson, Botanist, in <a href="https://discovery.nationalarchives.gov.uk/details/r/c2cfd361-40df-4f62-aab6-0bcd15c472eb" title="Opens in a new tab" target="_blank">RM 20</a>; </li>
<li>Economic Botany Collection papers, in <a href="https://discovery.nationalarchives.gov.uk/details/r/c2a17e11-1ce3-43fa-91a1-896a4b64af81" title="Opens in a new tab" target="_blank">RM 21</a>; </li>
<li>Papers of George W Robinson, horticulturist, in <a href="https://discovery.nationalarchives.gov.uk/details/r/c9c3398d-247d-4225-ac66-57e9ded2ff6c" title="Opens in a new tab" target="_blank">RM 22</a>. </li>
</ul></p> <p>NOTE: Please use the document references found in the 'Former reference (Department)' field when wishing to consult these documents at the Archives of The Royal Botanic Gardens, Kew.</p> <p>For series created for regularly archived websites, please see the separate <a href="https://discovery.nationalarchives.gov.uk/details/r/C1528" title="Opens in a new tab" target="_blank">Websites Division</a>.</p> <p>The Royal Botanic Gardens, Kew <a href="https://www2.calmview.co.uk/Kew/CalmView/default.aspx" title="Opens in a new tab" target="_blank">online catalogue</a> is available to search. </p>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_LootedArt(self):
        # C13373873
        source = '<emph altrender="doctype">LA</emph><emph altrender="scope">Registry Number: W 15182/108/64. Correspondence between Sir E Maclagan of the Victoria and Albert Museum and Sir S Gaselee at the Foreign Office about a request from exiled governments for the Central Institute of Art and Design under the chairmanship of Mr Charles Tennyson to assist firstly in the restitution of works of art from enemy-occupied countries, secondly in the prevention of their sale in the US and elsewhere, and lastly in the assurance of their return after the declaration of peace, dated October 1942. No reference to specific works of art.</emph>'
        schema = "LootedArt"
        self.assertEqual(
            "Registry Number: W 15182/108/64. Correspondence between Sir E Maclagan of the Victoria and Albert Museum and Sir S Gaselee at the Foreign Office about a request from exiled governments for the Central Institute of Art and Design under the chairmanship of Mr Charles Tennyson to assist firstly in the restitution of works of art from enemy-occupied countries, secondly in the prevention of their sale in the US and elsewhere, and lastly in the assurance of their return after the declaration of peace, dated October 1942. No reference to specific works of art.",
            str(apply_schema_xsl(source, schema)),
        )

    def test_Medal(self):
        # D2874592
        source = '<emph altrender="doctype">M</emph><persname><emph altrender="surname">Hillyard</emph> <emph altrender="forenames">Ernest S</emph></persname><emph altrender="medal"><corpname>Northamptonshire Regiment</corpname><emph altrender="regno">9004</emph><emph altrender="rank">Driver</emph></emph><emph altrender="medal"><corpname>Northamptonshire Regiment</corpname><emph altrender="regno">9004</emph><emph altrender="rank">Private</emph></emph><emph altrender="medal"><corpname>Northamptonshire Regiment</corpname><emph altrender="regno">5875061</emph><emph altrender="rank">Private</emph></emph>'
        schema = "Medal"
        self.assertEqual(
            """<div class="tna-table-wrapper"><table class="tna-table">
<caption class="tna-table__caption">Medal card of Hillyard, Ernest S</caption>
<thead class="tna-table__head"><tr class="tna-table__row">
<th scope="col" class="tna-table__header">Corps</th>
<th scope="col" class="tna-table__header">Regiment number</th>
<th scope="col" class="tna-table__header">Rank</th>
</tr></thead>
<tbody class="tna-table__body">
<tr class="tna-table__row">
<th class="tna-table__header" scope="row">Northamptonshire Regiment</th>
<td class="tna-table__cell">9004</td>
<td class="tna-table__cell">Driver</td>
</tr>
<tr class="tna-table__row">
<th class="tna-table__header" scope="row">Northamptonshire Regiment</th>
<td class="tna-table__cell">9004</td>
<td class="tna-table__cell">Private</td>
</tr>
<tr class="tna-table__row">
<th class="tna-table__header" scope="row">Northamptonshire Regiment</th>
<td class="tna-table__cell">5875061</td>
<td class="tna-table__cell">Private</td>
</tr>
</tbody>
</table></div>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_Miscellaneous(self):
        # C1386377
        source = '<emph altrender="doctype">G</emph>Report of Committee on Homosexual Offences and Prostitution (Cmnd 247).(Keyword: gay).'
        schema = "Miscellaneous"
        self.assertEqual(
            """Report of Committee on Homosexual Offences and Prostitution (Cmnd 247).(Keyword: gay).""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_MusterRolls(self):
        # D7152922
        source = '<emph altrender="doctype">MS</emph><persname><emph altrender="surname">Boisnard</emph> <emph altrender="forenames">Francois</emph></persname><corpname>Duguay-Trouin</corpname><emph altrender="rating">Etat Major</emph>'
        schema = "MusterRolls"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Boisnard, Francois</dd>
<dt>Ship name</dt>
<dd>Duguay-Trouin</dd>
<dt>Rank</dt>
<dd>Etat Major</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_NavalOfficers(self):
        # C10340247
        source = '<emph altrender="doctype">NO</emph><persname><emph altrender="surname">Abbott</emph><emph altrender="forenames">Charles Henry</emph></persname><emph altrender="rank">Lieutenant</emph><emph altrender="num">0857</emph><geogname>Whitby, Yorkshire</geogname><emph altrender="dob">23 September 1870</emph>'
        schema = "NavalOfficers"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Abbott, Charles Henry</dd>
<dt>Rank</dt>
<dd>Lieutenant</dd>
<dt>Number</dt>
<dd>0857</dd>
<dt>Place of birth</dt>
<dd>Whitby, Yorkshire</dd>
<dt>Date of birth</dt>
<dd>23 September 1870</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_NavalReserve(self):
        # D8485886
        source = '<emph altrender="doctype">RR</emph><persname><emph altrender="surname">Hillyard</emph><emph altrender="forenames">Edward Joshua</emph></persname><geogname>Rowhedge, Essex</geogname><emph altrender="certno">B 3813</emph><emph altrender="rank"></emph><emph altrender="date"></emph><emph altrender="dob">19 November 1885</emph>'
        schema = "NavalReserve"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Hillyard, Edward Joshua</dd>
<dt>Place of birth</dt>
<dd>Rowhedge, Essex</dd>
<dt>Number</dt>
<dd>B 3813</dd>
<dt>Date of birth</dt>
<dd>19 November 1885</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_NavyLandService(self):
        # D7287863
        source = '<emph altrender="doctype">LS</emph><persname><emph altrender="surname">Hillyard</emph> <emph altrender="forenames">James</emph></persname><emph altrender="num">Z/3146</emph><emph altrender="age">13 October 1894</emph>'
        schema = "NavyLandService"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Hillyard, James</dd>
<dt>Service number(s)</dt>
<dd>Z/3146</dd>
<dt>Date of birth</dt>
<dd>13 October 1894</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_NursingService(self):
        # C10792723
        source = '<emph altrender="doctype">NS</emph><persname><emph altrender="surname">Abbott</emph><emph altrender="forenames">Ada</emph></persname>'
        schema = "NursingService"
        self.assertEqual(
            "Abbott, Ada",
            str(apply_schema_xsl(source, schema)),
        )

    def test_Olympic(self):
        # C12462510
        source = '<emph altrender="doctype">OL</emph><geogname>Berlin, Germany</geogname><emph altrender="scope">Olympic Games: German propaganda in Iraq; marked activity encouraging Iraqis to visit Germany</emph>'
        schema = "Olympic"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Place</dt>
<dd>Berlin, Germany</dd>
<dt>Scope and content</dt>
<dd>Olympic Games: German propaganda in Iraq; marked activity encouraging Iraqis to visit Germany</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_PoorLaw(self):
        # C9723960
        source = '<emph altrender="doctype">PL</emph><persname><emph altrender="surname"><surname>Smith</surname><surname>Chadwick</surname></emph> <emph altrender="forenames"><firstname>Josiah</firstname><firstname>Edwin</firstname></emph></persname><emph altrender="placesmentioned"><geogname>Grassthorpe</geogname></emph><emph altrender="orgsmentioned"><corpname>Poor Law Commission</corpname></emph><emph altrender="scope"><p>Folio 23. Letter from Josiah Smith, to Edwin Chadwick, Poor Law Commission, requesting an answer by return of post to his letter of 20 May, regarding the election of a new guardian for Grassthorpe. It is annotated on 4 June \'acknowledge and state order issued on 1 June\'.</p></emph>'
        schema = "PoorLaw"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name(s)</dt>
<dd>Smith, Josiah Edwin </dd>
<dd>Chadwick, Josiah Edwin </dd>
<dt>Places mentioned</dt>
<dd>Grassthorpe</dd>
<dt>Corporations</dt>
<dd>Poor Law Commission</dd>
<dt>Content</dt>
<dd>Folio 23. Letter from Josiah Smith, to Edwin Chadwick, Poor Law Commission, requesting an answer by return of post to his letter of 20 May, regarding the election of a new guardian for Grassthorpe. It is annotated on 4 June 'acknowledge and state order issued on 1 June'.</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_prisoner(self):
        # C9072323
        source = '<emph altrender="doctype">P</emph><persname><emph altrender="surname">Wells</emph> <emph altrender="forenames">Benjamin</emph></persname><emph altrender="age">18</emph><geogname>Surrey</geogname><emph altrender="court">Surrey Sessions</emph><emph altrender="offence">Larceny (after a previous conviction):  stealing a piece of bacon</emph><emph altrender="sentence">12 calendar months hard labour</emph>'
        schema = "prisoner"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name (and alias if used) of prisoner</dt>
<dd>Wells, Benjamin</dd>
<dt>Age</dt>
<dd>18</dd>
<dt>Place of birth</dt>
<dd>Surrey</dd>
<dt>Place/court of conviction</dt>
<dd>Surrey Sessions</dd>
<dt>Offence</dt>
<dd>Larceny (after a previous conviction):  stealing a piece of bacon</dd>
<dt>Sentence</dt>
<dd>12 calendar months hard labour</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_PrisonerInterview(self):
        # C9207436
        source = '<emph altrender="doctype">I</emph><persname> <emph altrender="surname">Beaman</emph></persname><emph altrender="page">2-9</emph><corpname>Royal Army Medical Corps.</corpname><emph altrender="rank">Captain</emph><emph altrender="people"><persname>Major Philip Davy, Royal Army Medical Corps</persname></emph>'
        schema = "PrisonerInterview"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Beaman</dd>
<dt>Page number</dt>
<dd>2-9</dd>
<dt>Corps</dt>
<dd>Royal Army Medical Corps.</dd>
<dt>Rank</dt>
<dd>Captain</dd>
<dt>People mentioned</dt>
<dd>Major Philip Davy, Royal Army Medical Corps</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_RAFOfficers(self):
        # D8272609
        source = '<emph altrender="doctype">RO</emph><persname><emph altrender="surname">Hillyard</emph><emph altrender="forenames">Frederick</emph></persname><emph altrender="dob">08 July 1898</emph>'
        schema = "RAFOfficers"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Hillyard, Frederick</dd>
<dt>Date of birth</dt>
<dd>08 July 1898</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_RecHonours(self):
        # C9041173
        source = '<emph altrender="doctype">H</emph><persname> <emph altrender="surname">Fetterley</emph><emph altrender="forenames">James</emph></persname><emph altrender="rank">Lieutenant</emph><emph altrender="regno">CDN541</emph><corpname>2 Battalion The East Yorkshire Regiment</corpname><geogname>North West Europe</geogname><emph altrender="award">Military Cross</emph><emph altrender="date">21 December 1944</emph><emph altrender="folio">2-3</emph>'
        schema = "RecHonours"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Fetterley, James</dd>
<dt>Rank</dt>
<dd>Lieutenant</dd>
<dt>Service number</dt>
<dd>CDN541</dd>
<dt>Regiment</dt>
<dd>2 Battalion The East Yorkshire Regiment</dd>
<dt>Theatre of combat or operation</dt>
<dd>North West Europe</dd>
<dt>Award</dt>
<dd>Military Cross</dd>
<dt>Date of announcement in London Gazette</dt>
<dd>21 December 1944</dd>
<dt>Folio</dt>
<dd>2-3</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_RNASOfficers(self):
        # C9749441
        source = '<emph altrender="doctype">SQ</emph><emph altrender="num">Page 1: William Harry Ellison.</emph>'
        schema = "RNASOfficers"
        self.assertEqual(
            "Page 1: William Harry Ellison.",
            str(apply_schema_xsl(source, schema)),
        )

    def test_RNOfficer(self):
        # D7590755
        source = '<emph altrender="doctype">RN</emph><persname><emph altrender="surname">Hillyard</emph><emph altrender="forenames">George Whiteside</emph></persname><emph altrender="rank">06 February 1864</emph><emph altrender="date">Commander</emph><emph altrender="doe">15 July 1877</emph>'
        schema = "RNOfficer"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Hillyard, George Whiteside</dd>
<dt>Date of birth</dt>
<dd>06 February 1864</dd>
<dt>Rank</dt>
<dd>Commander</dd>
<dt>Date of appointment</dt>
<dd>15 July 1877</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_RoyalMarines(self):
        # D7829042
        source = '<emph altrender="doctype">RM</emph><persname><emph altrender="surname">Hillyard</emph><emph altrender="forenames">Ernest Percy</emph></persname><emph altrender="num">21311</emph><emph altrender="division">Royal Marine Light Infantry: Plymouth Division</emph><emph altrender="date2">01 October 1918</emph><emph altrender="dob">09 October 1900</emph>'
        schema = "RoyalMarines"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Hillyard, Ernest Percy</dd>
<dt>Register number</dt>
<dd>21311</dd>
<dt>Division</dt>
<dd>Royal Marine Light Infantry: Plymouth Division</dd>
<dt>When enlisted/date of enlistment</dt>
<dd>01 October 1918</dd>
<dt>Date of birth</dt>
<dd>09 October 1900</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_SeamenMedal(self):
        # D4340681
        source = '<emph altrender="doctype">S</emph><persname><emph altrender="surname">Hillyard</emph><emph altrender="forenames">William Henry</emph></persname><emph altrender="dischargeno">R166522</emph><emph altrender="dob">01 September 1919</emph>'
        schema = "SeamenMedal"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Hillyard, William Henry</dd>
<dt>Discharge number</dt>
<dd>R166522</dd>
<dt>Date of birth</dt>
<dd>01 September 1919</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_SeamenRegister(self):
        # D7004597
        source = '<emph altrender="doctype">R</emph><persname><emph altrender="surname">Hillyard</emph> <emph altrender="forenames">Ernest Edward</emph></persname><emph altrender="num">K46763</emph><geogname>Luton, Bedfordshire</geogname><emph altrender="dob">24 August 1899</emph>'
        schema = "SeamenRegister"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Hillyard, Ernest Edward</dd>
<dt>Official number</dt>
<dd>K46763</dd>
<dt>Place of birth</dt>
<dd>Luton, Bedfordshire</dd>
<dt>Date of birth</dt>
<dd>24 August 1899</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_SeamenWill(self):
        # D7468207
        source = '<emph altrender="doctype">W</emph><persname><emph altrender="surname">Adams</emph> <emph altrender="forenames">George</emph></persname><emph altrender="rank">Armourer</emph><corpname>Blonde</corpname><emph altrender="num">75</emph>'
        schema = "SeamenWill"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Will of </dt>
<dd>George Adams</dd>
<dt>Rank/rating</dt>
<dd>Armourer</dd>
<dt>Ship name</dt>
<dd>Blonde</dd>
<dt>Ship's pay book number</dt>
<dd>75</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_ShippingSeamen(self):
        # D8658651
        source = '<emph altrender="doctype">SS</emph><emph altrender="name">Ioannis Chandris</emph><emph altrender="name2">Ionion,  Empire Keats</emph><emph altrender="size">7035</emph>'
        schema = "ShippingSeamen"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Ship name</dt>
<dd>Ioannis Chandris</dd>
<dt>Former ship name</dt>
<dd>Ionion,  Empire Keats</dd>
<dt>Gross tonnage</dt>
<dd>7035</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_Squadron(self):
        # C2504271
        source = '<emph altrender="doctype">SQ</emph><emph altrender="num">292</emph><emph altrender="append">Y</emph><emph altrender="comments">Diary  </emph>'
        schema = "Squadron"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Squadron number</dt>
<dd>292</dd>
<dt>Appendices</dt>
<dd>Y</dd>
<dt>Comments</dt>
<dd>Diary  </dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_Titanic(self):
        # D8455647
        source = '<emph altrender="doctype">TC</emph><persname><emph altrender="surname">Buckley</emph><emph altrender="forenames">Kath</emph></persname><emph altrender="scope">Female aged 20. Travelling Third class. Occupation: Spinster.</emph>'
        schema = "Titanic"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Buckley, Kath</dd>
<dt>Content</dt>
<dd>Female aged 20. Travelling Third class. Occupation: Spinster.</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_VictoriaCross(self):
        # D7231288
        source = '<emph altrender="doctype">V</emph><persname><emph altrender="surname">Buckley</emph> <emph altrender="forenames">Cecil William</emph></persname><emph altrender="rank">Lieutenant</emph><corpname>Royal Navy</corpname><emph altrender="date">29 May 1855</emph><emph altrender="campaign">Crimea</emph><geogname>Genitichi, Tanganrog</geogname>'
        schema = "VictoriaCross"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Buckley, Cecil William</dd>
<dt>Rank</dt>
<dd>Lieutenant</dd>
<dt>Regiment</dt>
<dd>Royal Navy</dd>
<dt>Date of act of bravery</dt>
<dd>29 May 1855</dd>
<dt>Campaign</dt>
<dd>Crimea</dd>
<dt>Locale</dt>
<dd>Genitichi, Tanganrog</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_VolunteerReserve(self):
        # D7670951
        source = '<emph altrender="doctype">RV</emph><persname><emph altrender="surname">Hillyard</emph><emph altrender="forenames">William Stanley</emph></persname><emph altrender="num">Z/8171</emph><emph altrender="division">Bristol</emph><emph altrender="dob">28 November 1900</emph>'
        schema = "VolunteerReserve"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Hillyard, William Stanley</dd>
<dt>Service number</dt>
<dd>Z/8171</dd>
<dt>RNVR division</dt>
<dd>Bristol</dd>
<dt>Date of birth</dt>
<dd>28 November 1900</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_Will(self):
        # D538741
        source = '<emph altrender="doctype">W</emph><persname><emph altrender="forenames">William</emph><emph altrender="surname">Cribb</emph></persname><occupation>Baker</occupation><geogname>Wareham , Dorset</geogname>'
        schema = "Will"
        self.assertEqual(
            "Will of William Cribb, Baker of Wareham , Dorset",
            str(apply_schema_xsl(source, schema)),
        )

    def test_WomensCorps(self):
        # D538741
        source = '<emph altrender="doctype">WA</emph><persname><emph altrender="forenames">Sarah Ann nee Phillips</emph><emph altrender="surname">Aaron</emph></persname><geogname>High Street Cefn Mawr, North Wales</geogname><emph altrender="dob">22 August 1894</emph>'
        schema = "WomensCorps"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Aaron, Sarah Ann nee Phillips</dd>
<dt>Place of birth</dt>
<dd>High Street Cefn Mawr, North Wales</dd>
<dt>Date of birth</dt>
<dd>22 August 1894</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_Wrns(self):
        # D7430419
        source = '<emph altrender="doctype">WR</emph><persname><emph altrender="surname">Kingham</emph> <emph altrender="forenames">Gwendoline</emph></persname><emph altrender="rank">Motordriver</emph><emph altrender="num">G1</emph><emph altrender="date">21 January 1918</emph>'
        schema = "Wrns"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Kingham, Gwendoline</dd>
<dt>Rating</dt>
<dd>Motordriver</dd>
<dt>Service number</dt>
<dd>G1</dd>
<dt>Date of enrolment</dt>
<dd>21 January 1918</dd>
</dl>""",
            str(apply_schema_xsl(source, schema)),
        )

    def test_unknown_schema(self):
        source = '<emph altrender="doctype">G</emph>Joint meeting of the Army-Navy Communication Intelligence Board and Army-Navy Communication Intelligence Co-ordinating Committee, 29 October 1945'
        schema = "UNKNOWN"
        self.assertEqual(
            "Joint meeting of the Army-Navy Communication Intelligence Board and Army-Navy Communication Intelligence Co-ordinating Committee, 29 October 1945",
            str(apply_schema_xsl(source, schema)),
        )

    def test_no_schema(self):
        source = '<emph altrender="doctype">G</emph>Joint meeting of the Army-Navy Communication Intelligence Board and Army-Navy Communication Intelligence Co-ordinating Committee, 29 October 1945'
        schema = ""
        self.assertEqual(
            "Joint meeting of the Army-Navy Communication Intelligence Board and Army-Navy Communication Intelligence Co-ordinating Committee, 29 October 1945",
            str(apply_schema_xsl(source, schema)),
        )

    def test_no_source_content(self):
        source = ""
        schema = "Generic"
        self.assertEqual(
            "",
            str(apply_schema_xsl(source, schema)),
        )

    def test_series_ADM_240_xsl(self):
        # C16128233
        self.maxDiff = None
        source = '<scopecontent>\r\n\t<p>Name: <persname><emph altrender="forenames">Lewis Martin </emph>\r\n\t\t\t<emph altrender="surname">Wibmer</emph></persname>. </p>\r\n\t<p>Rank: <emph altrender="rank">Commander</emph>. </p>\r\n\t<p>Date of Seniority: 07 March 1904. </p>\r\n\t<p>Date of Birth: [not given]. </p>\r\n\t<p>Place of Birth: [not given]. </p>\r\n</scopecontent>'
        series = "ADM 240"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Wibmer, Lewis Martin </dd>
<dt>Rank</dt>
<dd>Commander</dd>
<dt>Date of seniority</dt>
<dd>07 March 1904. </dd>
<dt>Date of birth</dt>
<dd>[not given]</dd>
<dt>Place of birth</dt>
<dd>[not given]</dd>
</dl>""",
            str(apply_series_xsl(source, series)),
        )

    def test_series_DL_25_xsl(self):
        # C16099010
        source = '<scopecontent>\r\n\t<p>Name: <persname>Matilda Avranches (de Abrinco), wife of Robert son of King Henry</persname></p>\r\n\t<p>Places: Property in <geogname>Alphington, Devon / Aylesbeare, Devon</geogname>. </p>\r\n\t<p>Document Note: <emph altrender="docnote">The date is from internal evidence: G.E.C., Complete peerage, iv.317; xi.app.106n, 109n.</emph>\r\n\t</p>\r\n\t<p>Seal Design: <emph altrender="sealdesign">Design: includes woman standing full face with a chain (?plait) on the left, Size: 27 x 35 mm, Shape: unknown shape, Colour: uncoloured, Legend: if any lost, Personal</emph>. </p>\r\n\t<p>Material: <emph altrender="material">Wax</emph>. </p>\r\n\t<p>Attachment: <emph altrender="attachment">On tongue</emph>. </p>\r\n\t<p>Seal Note: <emph altrender="sealnote">No name on seal. Impression: fair. Condition: fragment</emph>. </p>\r\n</scopecontent>'
        series = "DL 25"
        self.assertEqual(
            """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Name</dt>
<dd>Matilda Avranches (de Abrinco), wife of Robert son of King Henry</dd>
<dt>Places: Property in </dt>
<dd>Alphington, Devon / Aylesbeare, Devon</dd>
<dt>Document Note</dt>
<dd>The date is from internal evidence: G.E.C., Complete peerage, iv.317; xi.app.106n, 109n.</dd>
<dt>Seal Design</dt>
<dd>Design: includes woman standing full face with a chain (?plait) on the left, Size: 27 x 35 mm, Shape: unknown shape, Colour: uncoloured, Legend: if any lost, Personal</dd>
<dt>Material</dt>
<dd>Wax</dd>
<dt>Attachment</dt>
<dd>On tongue</dd>
<dt>Seal Note</dt>
<dd>No name on seal. Impression: fair. Condition: fragment</dd>
</dl>""",
            str(apply_series_xsl(source, series)),
        )

    def test_xsl_transformation_empty_source(self):
        """Tests that a warning is logged and an empty string is returned when
        the source is empty."""

        source = None
        schema = "Generic.xsl"

        with self.assertLogs(
            "app.lib.xslt_transformations", level="WARNING"
        ) as lc:
            return_value = xsl_transformation(source, schema)
            self.assertIn("", return_value)

        self.assertIn(
            "WARNING:app.lib.xslt_transformations:Empty source provided for XSLT transformation",
            lc.output,
        )

    def test_xsl_transformation_loading_xslt_file_error(self):
        """Tests that an error is logged and the original source is returned when there
        is an error loading the XSLT file."""

        source = '<emph altrender="doctype">G</emph>Joint meeting of the Army-Navy Communication Intelligence Board and Army-Navy Communication Intelligence Co-ordinating Committee, 29 October 1945'
        schema = "SCHEMA_THAT_DOES_NOT_EXIST"

        with self.assertLogs(
            "app.lib.xslt_transformations", level="ERROR"
        ) as lc:
            return_value = xsl_transformation(source, schema)
            self.assertEqual(source, return_value)

        self.assertIn(
            "ERROR:app.lib.xslt_transformations:Unexpected error while loading XSLT file "
            "'SCHEMA_THAT_DOES_NOT_EXIST': Error reading file 'app/resources/xslt/SCHEMA_THAT_DOES_NOT_EXIST': "
            'failed to load "app/resources/xslt/SCHEMA_THAT_DOES_NOT_EXIST": No such file or directory',
            lc.output,
        )
