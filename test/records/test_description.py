import unittest

from jinja2 import Environment

from app.lib.xslt_transformations import apply_schema_xsl
from app.records.models import Record
from config.jinja import remove_string_case_insensitive, truncate_preserve_mark_tags


class RecordDescriptionTestCase(unittest.TestCase):
    """Test cases for the Record description property and related functions."""

    def setUp(self):
        """Set up the test case."""
        self.env = Environment()

        self.env.filters["truncate_preserve_mark_tags"] = truncate_preserve_mark_tags
        self.env.filters["remove_string_case_insensitive"] = (
            remove_string_case_insensitive
        )

        # used in app/templates/search/macros/search_results.html
        self.search_results_template = self.env.from_string(
            "<p>{{ description | truncate_preserve_mark_tags() | remove_string_case_insensitive('scope and content') | safe }}</p>"
        )

        # used in app/templates/records/macros/whats_this_about_sub_sub_series_or_above.html
        self.whats_this_about_template = self.env.from_string(
            "<p>{{ description | striptags | remove_string_case_insensitive('scope and content') | truncate(250) }}</p>"
        )

    def test_description_in_search_results_for_highlighted_search_term(self):
        """Previously clean_description was used for search results where it removed all HTML except <mark> tags.
        Now the description property is used for search results, which retains the <mark> tags for highlighting search terms.
        This test ensures that the description property correctly retains the <mark> tags in the search results."""

        # C8076473
        description_value = "Appellant: <mark>Florence</mark> Emily <mark>Fenn</mark>. Respondent: Ernest William <mark>Fenn</mark>. Type: Wife's petition for divorce [wd]. "
        record = Record({"description": {"value": description_value}})

        # test description property output
        self.assertEqual(
            record.description,
            (
                "Appellant: <mark>Florence</mark> Emily <mark>Fenn</mark>. Respondent: Ernest William <mark>Fenn</mark>. Type: Wife's petition for divorce [wd]."
            ),
        )

        # test discription property output macthes transformed schema output,
        # uses default schema as no schema is provided
        transformed_description = apply_schema_xsl(
            source=description_value,
            schema="",
        )
        self.assertEqual(record.description, transformed_description)

        # test search results template rendering using description property
        rendered_output = self.search_results_template.render(
            description=record.description
        )
        self.assertEqual(
            "<p>Appellant: <mark>Florence</mark> Emily <mark>Fenn</mark>. Respondent: Ernest William <mark>Fenn</mark>. Type: Wife's petition for divorce [wd].</p>",
            rendered_output,
        )

    def test_whats_this_about_description(self):
        """Previously no_html_description was used for the "What's this about?" section of the record details,
        which removed all HTML tags.
        Now the description property is used for this section, which retains some HTML tags.
        This test ensures that the description property correctly removes the necessary HTML tags for the "What's this about?" section."""

        # C12483430
        description_value = "<scopecontent><p>These records are the service records of individuals serving in the Home Guard in the Second World War. The records are the Form of Enrolment - Army Form W3066 - and contain personal information and other service information such as length of service in the Home Guard and discharge details for each individual.</p> <p>This is a digital-only accession. <extref href=&#34https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/durham-home-guard-records-1939-1945/&#34>Durham Home Guard 1939-1945</extref> records are available to search and download.</p></scopecontent>"
        record = Record({"description": {"value": description_value}})

        # test description property output
        self.assertEqual(
            record.description,
            (
                """<p>These records are the service records of individuals serving in the """
                """Home Guard in the Second World War. The records are the Form of Enrolment """
                """- Army Form W3066 - and contain personal information and other service """
                """information such as length of service in the Home Guard and discharge """
                """details for each individual.</p><p>This is a digital-only accession. """
                """<a href="https://www.nationalarchives.gov.uk/help-with-your-research/research-guides/durham-home-guard-records-1939-1945/" """
                """title="Opens in a new tab">Durham Home Guard 1939-1945</a> records are """
                """available to search and download.</p>"""
            ),
        )

        # test discription property output macthes transformed schema output,
        # uses default schema as no schema is provided
        transformed_description = apply_schema_xsl(
            source=description_value,
            schema="",
        )
        self.assertEqual(record.description, transformed_description)

        rendered_output = self.whats_this_about_template.render(
            description=record.description
        )
        expected_whats_this_about = (
            """<p>These records are the service records of individuals """
            """serving in the Home Guard in the Second World War. The records are the Form of """
            """Enrolment - Army Form W3066 - and contain personal information and other service """
            """information such as length of...</p>"""
        )
        self.assertEqual(
            expected_whats_this_about,
            rendered_output,
        )

    def test_description_with_generic_schema_various_cases(self):

        test_data = [
            # format: label,
            #         schema
            #         description_value,
            #         expected_description_or_schema_output,
            #         expected_search_results, # final output for search results template rendering
            #         expected_whats_this_about, # final output for whats this about template rendering
            (
                "plain_text_only",
                "Generic",
                " This is plain text only without any HTML tags. ",
                "This is plain text only without any HTML tags.",
                "<p>This is plain text only without any HTML tags.</p>",
                "<p>This is plain text only without any HTML tags.</p>",
            ),
            (
                "without_sc_p_tag",
                "Generic",
                "<p>data1</p>",
                "<p>data1</p>",
                "<p>data1</p>",
                "<p>data1</p>",
            ),
            (
                "without_sc_multiple_p_preserves_spaces_between_p_tags",
                "Generic",
                "<p>data1</p> <p>data2</p>",
                "<p>data1</p> <p>data2</p>",
                "<p>data1 data2</p>",
                "<p>data1 data2</p>",
            ),
            (
                "sc_with_head_tag",
                "Generic",
                "<scopecontent><head>Scope and Content</head></scopecontent>",
                "",  # Scope and Content is removed by the Generic.xsl transformation
                "<p></p>",
                "<p></p>",
            ),
            (
                "sc_without_head_tag_text_only",
                "Generic",
                "<scopecontent>Data that is not within p-tag IS NOT returned</scopecontent>",
                "",
                "<p></p>",
                "<p></p>",
            ),
            (
                "sc_multiple_p_removes_spaces_between_p_tags",
                "Generic",
                "<scopecontent><head>Scope and Content</head> <p>data1</p> <p>data2</p>Data that is not within p-tag IS NOT returned</scopecontent>",
                "<p>data1</p><p>data2</p>",
                "<p>data1data2</p>",
                "<p>data1data2</p>",
            ),
            (
                "sc_multiple_p_tags_with_missing_closing_p_tag",
                "Generic",
                "<scopecontent><head>Scope and Content</head> <p>data1 <p>data2 </scopecontent>",
                "<p>data1 </p><p>data2 </p>",  # The XSL transformation adds the missing closing p-tag
                "<p>data1 data2 </p>",
                "<p>data1 data2</p>",
            ),
            (
                "sc_whitespace_chars_are_removed",  # C11835316
                "Generic",
                "<scopecontent> \r\n\t</scopecontent>",
                "",
                "<p></p>",
                "<p></p>",
            ),
            (
                "sc_extref_tag",  # C16411
                "Generic",
                "<scopecontent><extref href=&#34http://discovery.nationalarchives.gov.uk/SearchUI/Details?uri=C1226&#34>Websites Division</extref></scopecontent>",
                """<a href="http://discovery.nationalarchives.gov.uk/SearchUI/Details?uri=C1226" title="Opens in a new tab" target="_blank">Websites Division</a>""",
                """<p>Websites Division</p>""",
                """<p>Websites Division</p>""",
            ),
            (
                "sc_list_item_processing_instruction",  # C16411
                "Generic",
                "<scopecontent><p><list><?xm-replace_text {p}?><item>ListItem1</item><item>(Details of exhibition references are given at piece level scope and content)</item></p></scopecontent>",
                # scope and content within p tag is retained in the Generic.xsl transformation
                """<p><ul class="tna-ul">
<li>ListItem1</li>
<li>(Details of exhibition references are given at piece level scope and content)</li>
</ul></p>""",
                # scope and content within p tag is removed by the remove_string_case_insensitive filter
                # however the whitespace before scope is retained
                """<p>
ListItem1
(Details of exhibition references are given at piece level )
</p>""",
                """<p>ListItem1 (Details of exhibition references are given at piece level )</p>""",
            ),
            (
                "sc_ref_tag",  # C11969
                "Generic",
                '<scopecontent><p>(in <ref href=&#34PRO-d4-c30s23-p4">PRO 30/23/4</ref>)</p></scopecontent>',
                """<p>(in <a href="/catalogue/search/?q=PRO%2030/23/4" title="Opens in a new tab">PRO 30/23/4</a>)</p>""",
                """<p>(in PRO 30/23/4)</p>""",
                """<p>(in PRO 30/23/4)</p>""",
            ),
        ]

        for (
            label,
            schema,
            description_value,
            expected_description_or_schema_output,
            expected_search_results,
            expected_whats_this_about,
        ) in test_data:
            with self.subTest(label=label):
                record = Record({"description": {"value": description_value}})

                # test description property output
                self.assertEqual(
                    expected_description_or_schema_output,
                    record.description,
                )

                # test apply_schema_xsl function
                self.assertEqual(
                    expected_description_or_schema_output,
                    apply_schema_xsl(description_value, schema),
                )

                # test search results template rendering using description property
                rendered_output = self.search_results_template.render(
                    description=record.description
                )
                self.assertEqual(
                    expected_search_results,
                    rendered_output,
                )

                # test what's this about template rendering using description property
                rendered_output = self.whats_this_about_template.render(
                    description=record.description
                )
                self.assertEqual(
                    expected_whats_this_about,
                    rendered_output,
                )

    def test_description_with_non_generic_schema_various_cases(self):

        test_data = [
            # format: label,
            #         schema,
            #         description_value,
            #         expected_description_or_schema_output,
            #         expected_search_results, # final output for search results template rendering
            #         expected_whats_this_about, # final output for whats this about template rendering
            (
                "CabinetPapers_C9003842",
                '<colltype id="CabinetPapers">,</colltype>',
                """<emph altrender=\"doctype\">CP</emph><emph altrender=\"type\">Memorandum</emph><emph altrender=\"formerreference\">WP (R) (41) 19</emph><emph altrender=\"title\">Economic Warfare. Report for February, 1941.</emph><emph altrender=\"author\">Hugh Dalton</emph>""",
                """<dl class="tna-dl tna-dl--lined tna-dl--dotted">
<dt>Record type</dt>
<dd>Memorandum</dd>
<dt>Former reference</dt>
<dd>WP (R) (41) 19</dd>
<dt>Title</dt>
<dd>Economic Warfare. Report for February, 1941.</dd>
<dt>Author</dt>
<dd>Hugh Dalton</dd>
</dl>""",
                """<p>
Record type
Memorandum
Former reference
WP (R) (41) 19
Title
Economic Warfare. Report for February, 1941.
Author
Hugh Dalton
</p>""",
                """<p>Record type Memorandum Former reference WP (R) (41) 19 Title Economic Warfare. Report for February, 1941. Author Hugh Dalton</p>""",
            ),
        ]

        for (
            label,
            schema,
            description_value,
            expected_description_or_schema_output,
            expected_search_results,
            expected_whats_this_about,
        ) in test_data:
            with self.subTest(label=label):
                record = Record(
                    {"description": {"schema": schema, "value": description_value}}
                )

                # test description property output
                self.assertEqual(
                    expected_description_or_schema_output,
                    record.description,
                )

                # test apply_schema_xsl function
                self.assertEqual(
                    expected_description_or_schema_output,
                    apply_schema_xsl(description_value, record.description_schema),
                )

                # test search results template rendering using description property
                rendered_output = self.search_results_template.render(
                    description=record.description
                )
                self.assertEqual(
                    expected_search_results,
                    rendered_output,
                )

                # test what's this about template rendering using description property
                rendered_output = self.whats_this_about_template.render(
                    description=record.description
                )
                self.assertEqual(
                    expected_whats_this_about,
                    rendered_output,
                )
