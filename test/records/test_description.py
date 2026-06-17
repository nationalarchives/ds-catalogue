import unittest

from jinja2 import Environment

from app.lib.xslt_transformations import apply_schema_xsl
from app.records.models import Record
from config.jinja import remove_string_case_insensitive, truncate_preserve_mark_tags


class RecordDescriptionTestCase(unittest.TestCase):
    """Test cases for the Record description property and related functions."""

    def test_description_generic_schema_with_scopecontent_tag_various_cases(self):

        schema = "Generic"
        test_data = [
            # format:  label,
            #          description_value,
            #          expected_apply_schema_output,
            #          expected_search_results,
            #          expected_whats_this_about,
            (
                "with_head_tag",
                "<scopecontent><head>Scope and Content</head></scopecontent>",
                "",
                "<p></p>",
                "<p></p>",
            ),
            (
                "without_head_tag_text_only",
                "<scopecontent>Data that is not within p-tag IS NOT returned</scopecontent>",
                "",
                "<p></p>",
                "<p></p>",
            ),
            (
                "multiple_p_removes_spaces_between_p_tags",
                "<scopecontent><head>Scope and Content</head> <p>data1</p> <p>data2</p>Data that is not within p-tag IS NOT returned</scopecontent>",
                "<p>data1</p><p>data2</p>",
                "<p>data1data2</p>",
                "<p>data1data2</p>",
            ),
            (
                "whitespace_chars_are_removed",
                "<scopecontent> \r\n\t</scopecontent>",
                "",
                "<p></p>",
                "<p></p>",
            ),
            (
                "extref_tag",  # C16411
                "<scopecontent><extref href=&#34http://discovery.nationalarchives.gov.uk/SearchUI/Details?uri=C1226&#34>Websites Division</extref></scopecontent>",
                """<a href="http://discovery.nationalarchives.gov.uk/SearchUI/Details?uri=C1226" title="Opens in a new tab" target="_blank">Websites Division</a>""",
                """<p>Websites Division</p>""",
                """<p>Websites Division</p>""",
            ),
            (
                "list_item",  # C16411
                "<scopecontent><p><list><item>ListItem1</item><item>(Details of exhibition references are given at piece level scope and content)</item></p></scopecontent>",
                """<p><ul class="tna-ul">
<li>ListItem1</li>
<li>(Details of exhibition references are given at piece level scope and content)</li>
</ul></p>""",
                """<p>
ListItem1
(Details of exhibition references are given at piece level )
</p>""",
                """<p>ListItem1 (Details of exhibition references...</p>""",
            ),
        ]

        env = Environment()
        env.filters["truncate_preserve_mark_tags"] = truncate_preserve_mark_tags
        env.filters["remove_string_case_insensitive"] = remove_string_case_insensitive
        for (
            label,
            description_value,
            expected_apply_schema_output,
            expected_search_results,
            expected_whats_this_about,
        ) in test_data:
            with self.subTest(label=label):
                # test the apply_schema_xsl function
                apply_schema_xsl_value = apply_schema_xsl(description_value, schema)
                self.assertEqual(
                    expected_apply_schema_output,
                    apply_schema_xsl_value,
                )
                # test Record description property
                record = Record({"description": {"value": description_value}})
                self.assertEqual(
                    expected_apply_schema_output,
                    record.description,
                )

                # test the jinja2 template rendering
                # used with app/templates/search/macros/search_results.html
                # truncate_preserve_mark_tags is used with search results
                template = env.from_string(
                    "<p>{{ description | truncate_preserve_mark_tags() | remove_string_case_insensitive('scope and content') | safe }}</p>"
                )
                rendered_output = template.render(description=record.description)
                self.assertEqual(
                    expected_search_results,
                    rendered_output,
                )

                # test the jinja2 template rendering
                # use with app/templates/records/macros/whats_this_about_sub_sub_series_or_above.html
                template = env.from_string(
                    "<p>{{ description | striptags | remove_string_case_insensitive('scope and content') | truncate(50) }}</p>"
                )
                rendered_output = template.render(description=record.description)
                self.assertEqual(
                    expected_whats_this_about,
                    rendered_output,
                )

    def test_description_generic_schema_without_scopecontent_tag_various_cases(self):
        schema = "Generic"
        test_data = [
            # format:  label,
            #          description_value,
            #          expected_apply_schema_output,
            #          expected_search_results,
            #          expected_whats_this_about,
            (
                "text_without_p_tags_is_returned",
                "Data that is not within p-tag IS returned",
                "Data that is not within p-tag IS returned",
                "<p>Data that is not within p-tag IS returned</p>",
                "<p>Data that is not within p-tag IS returned</p>",
            ),
            (
                "multiple_p_preserves_spaces_between_p_tags",
                "<p>data1</p> <p>data2</p>",
                "<p>data1</p> <p>data2</p>",
                "<p>data1 data2</p>",
                "<p>data1 data2</p>",
            ),
        ]

        env = Environment()
        env.filters["truncate_preserve_mark_tags"] = truncate_preserve_mark_tags
        for (
            label,
            description_value,
            expected_apply_schema_output,
            expected_search_results,
            expected_whats_this_about,
        ) in test_data:
            with self.subTest(label=label):
                # test the apply_schema_xsl function
                apply_schema_xsl_value = apply_schema_xsl(description_value, schema)
                self.assertEqual(
                    expected_apply_schema_output,
                    apply_schema_xsl_value,
                )

                # test Record description property
                record = Record({"description": {"value": description_value}})
                self.assertEqual(
                    expected_apply_schema_output,
                    record.description,
                )

                # test the jinja2 template rendering
                # used with app/templates/search/macros/search_results.html
                # truncate_preserve_mark_tags is used with search results
                template = env.from_string(
                    "<p>{{ description | truncate_preserve_mark_tags() | safe }}</p>"
                )
                rendered_output = template.render(description=record.description)
                self.assertEqual(
                    expected_search_results,
                    rendered_output,
                )

                # test the jinja2 template rendering
                # use with app/templates/records/macros/whats_this_about_sub_sub_series_or_above.html
                template = env.from_string(
                    "<p>{{ apply_schema_xsl_value | striptags | truncate(50) }}</p>"
                )
                rendered_output = template.render(
                    apply_schema_xsl_value=apply_schema_xsl_value
                )
                self.assertEqual(
                    expected_whats_this_about,
                    rendered_output,
                )
