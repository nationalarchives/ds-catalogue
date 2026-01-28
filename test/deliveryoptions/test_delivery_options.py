import inspect
import json
import unittest
from copy import deepcopy
from unittest.mock import Mock, patch

from app.deliveryoptions.constants import (
    DELIVERY_OPTIONS_CONFIG,
    AvailabilityCondition,
    AvailabilityGroup,
    delivery_option_tags,
)
from app.deliveryoptions.delivery_options import (
    html_replacer,
    surrogate_link_builder,
)
from app.deliveryoptions.helpers import (
    BASE_TNA_HOME_URL,
    get_access_condition_text,
    get_added_to_basket_text,
    get_advance_order_information,
    get_advanced_orders_email_address,
    get_dept,
)
from app.records.models import APIResponse, Record
from app.records.views import RecordDetailView
from django.conf import settings
from django.test import RequestFactory, TestCase


class TestDeliveryOptionTags(TestCase):
    def setUp(self):
        self.delivery_option_tags = delivery_option_tags
        self.json_file_path = DELIVERY_OPTIONS_CONFIG

    def extract_tags(self, data):
        """Extract all markup tags in the form {TagName} from the JSON structure."""
        import re

        def find_tags(value):
            """Helper function to find tags within strings."""
            if isinstance(value, str):
                return re.findall(r"{(.*?)}", value)
            return []

        tags = set()

        def recurse(value):
            if isinstance(value, dict):
                for k, v in value.items():
                    if isinstance(v, (str, list, dict)):
                        tags.update(find_tags(v))
                        recurse(v)
            elif isinstance(value, list):
                for item in value:
                    recurse(item)

        recurse(data)
        return tags

    def test_all_markup_keys_have_corresponding_delivery_option_tags(self):
        with open(self.json_file_path, "r") as file:
            delivery_options_json = json.load(file)

        extracted_tags = self.extract_tags(delivery_options_json)

        for tag in extracted_tags:
            with self.subTest(tag=tag):
                self.assertIn(
                    f"{{{tag}}}",
                    self.delivery_option_tags,
                    f"Tag {tag} is missing in delivery_option_tags dictionary.",
                )


class TestDeliveryOptionSubstitution(TestCase):
    def setUp(self):
        fixture_path = f"{settings.BASE_DIR}/test/deliveryoptions/fixtures/response_C18281.json"
        with open(fixture_path, "r") as f:
            fixture_contents = json.loads(f.read())

        self.response = APIResponse(deepcopy(fixture_contents["data"][0]))
        self.record = self.response.record

        self.surrogate = [
            '<a target="_blank" href="https://www.thegenealogist.co.uk/non-conformist-records">The Genealogist</a>',
            '<a target="_blank" href="https://www.thegenealogist.co.uk/other-records">The Genealogist</a>',
        ]

    @patch(
        "app.deliveryoptions.helpers.BASE_TNA_HOME_URL",
        "https://tnabase.test.url",
    )
    @patch("app.deliveryoptions.helpers.MAX_BASKET_ITEMS", "5")
    @patch(
        "app.deliveryoptions.helpers.BASE_TNA_DISCOVERY_URL",
        "https://discovery.test.url",
    )
    def test_delivery_options_tags(self):
        test_cases = {
            "{AccessConditionText}": "Subject to 30 year closure",
            "{AddedToBasketText}": "Add to basket",
            "{AdvancedOrdersEmailAddress}": settings.ADVANCED_DOCUMENT_ORDER_EMAIL,
            "{AdvanceOrderInformationUrl}": "https://tnabase.test.url/about/visit-us/",
            "{ArchiveLink}": "https://discovery.nationalarchives.gov.uk/details/a/A13530124",
            "{ArchiveName}": "The National Archives, Kew",
            "{BasketType}": "Digital Downloads",
            "{BasketUrl}": "https://tnabase.test.url/basket/",
            "{BrowseUrl}": "https://tnabase.test.url/browse/tbd/C18281/",
            "{ContactFormUrlUnfit}": "https://tnabase.test.url/contact-us/document-condition-feedback/?catalogue-reference=FCO 65&conservation-treatment-required=true",
            "{ContactFormUrlMould}": "https://tnabase.test.url/contact-us/document-condition-feedback/?catalogue-reference=FCO 65&mould-treatment-required=true",
            "{ContactFormUrl}": "https://tnabase.test.url/contact-us/",
            "{DataProtectionActUrl}": "https://tnabase.test.url/content/documents/county-durham-home-guard-service-record-subject-access-request-form.pdf",
            "{DeptName}": "Foreign and Commonwealth Office",
            "{DeptUrl}": "http://www.fco.gov.uk/en/publications-and-documents/freedom-of-information/",
            "{DownloadFormat}": "(Unknown download format)",
            "{DownloadText}": "Download now",
            "{DownloadUrl}": "details/download",
            "{FAType}": " ",
            "{FoiUrl}": "https://tnabase.test.url/foirequest?reference=FCO 65",
            "{ImageLibraryUrl}": settings.IMAGE_LIBRARY_URL,
            "{ItemNumOfFilesAndSizeInMB}": "(Unknown number of files and file size)",
            "{KeepersGalleryUrl}": "https://tnabase.test.url/about/visit-us/whats-on/keepers-gallery/",
            "{KewBookingSystemUrl}": "https://tnabase.test.url/book-a-reading-room-visit/",
            "{MaxItems}": "5",
            "{OpenDateDesc}": "Opening date: ",
            "{OpeningTimesUrl}": "https://tnabase.test.url/about/visit-us/",
            "{OrderUrl}": "Order URL not yet available",
            "{PaidSearchUrl}": "https://tnabase.test.url/paidsearch/foirequest/C18281?type=foirequest",
            "{Price}": "(Unknown price)",
            "{ReadersTicketUrl}": "https://tnabase.test.url/about/visit-us/researching-here/do-i-need-a-readers-ticket/",
            "{RecordCopyingUrl}": "https://discovery.test.url/pagecheck/start/C18281/",
            "{RecordInformationType}": "(Unknown record information type)",
            "{RecordOpeningDate}": "26 February 1977",
            "{RecordUrl}": "https://tnabase.test.url/details/r/C18281/",
            "{AllWebsiteUrls}": ' <li><a target="_blank" href="https://www.thegenealogist.co.uk/non-conformist-records">The Genealogist</a></li><li><a target="_blank" href="https://www.thegenealogist.co.uk/other-records">The Genealogist</a></li>',
            "{SubsWebsiteUrls}": ' <li><a target="_blank" href="https://www.thegenealogist.co.uk/other-records">The Genealogist</a></li>',
            "{FirstWebsiteUrl}": "https://www.thegenealogist.co.uk/non-conformist-records",
            "{FirstWebsiteUrlFull}": '<a target="_blank" href="https://www.thegenealogist.co.uk/non-conformist-records">The Genealogist</a>',
            "{WebsiteUrlText}": "The Genealogist",
            "{YourOrderLink}": "(Unknown order link)",
        }

        for tag, expected_value in test_cases.items():
            with self.subTest(tag=tag):
                func = delivery_option_tags[tag]
                sig = inspect.signature(func)
                params = {}

                param_names = set(sig.parameters.keys())
                if "record" in param_names:
                    params["record"] = self.record

                if "api_surrogate_list" in param_names:
                    params["api_surrogate_list"] = self.surrogate
                elif "surrogate" in param_names:
                    params["surrogate"] = self.surrogate

                result = func(**params)
                self.assertEqual(result, expected_value)

    def test_get_dept_existing(self):
        self.assertEqual(
            get_dept("ADM 1234", "deptname"), "Ministry of Defence"
        )
        self.assertEqual(
            get_dept("CO 5678", "depturl"),
            "http://www.fco.gov.uk/en/publications-and-documents/freedom-of-information/",
        )

    def test_get_dept_non_existing(self):
        self.assertIsNone(get_dept("XYZ 1234", "deptname"))

    def test_get_access_condition_text(self):
        record = Mock()
        record.access_condition = "Open access"
        self.assertEqual(get_access_condition_text(record), "Open access")

        record.access_condition = None
        self.assertEqual(get_access_condition_text(record), " ")

    def test_get_added_to_basket_text(self):
        self.assertEqual(get_added_to_basket_text(), "Add to basket")

    def test_get_advanced_orders_email_address(self):
        self.assertEqual(
            get_advanced_orders_email_address(),
            settings.ADVANCED_DOCUMENT_ORDER_EMAIL,
        )

    @patch(
        "app.deliveryoptions.helpers.BASE_TNA_HOME_URL", "https://example.com"
    )
    def test_get_advance_order_information(self):
        self.assertEqual(
            get_advance_order_information(),
            "https://example.com/about/visit-us/",
        )


class TestSurrogateLinkBuilder(TestCase):
    def test_surrogate_link_builder(self):
        surrogates = [
            {"xReferenceURL": "http://example.com/1"},
            {"xReferenceURL": "http://example.com/2"},
            {"xReferenceURL": ""},
        ]

        result = surrogate_link_builder(surrogates)

        self.assertEqual(len(result), 2)
        self.assertIn("http://example.com/1", result)
        self.assertIn("http://example.com/2", result)


class TestHtmlReplacer(TestCase):
    def test_html_replacer(self):
        record = Mock()
        record.reference_number = "TEST 123"

        value = "Reference: {RecordReferenceNumber}, Number: {HeldByCount}"
        # Mock delivery_option_tags for testing
        with patch.dict(
            "app.deliveryoptions.delivery_options.delivery_option_tags",
            {
                "{RecordReferenceNumber}": lambda record: record.reference_number,
                "{HeldByCount}": lambda record: "10",
            },
        ):
            result = html_replacer(value, record, [])

        self.assertIn("TEST 123", result)
        self.assertIn("10", result)


class TestDeliveryOptionsContext(TestCase):
    """Tests for delivery options context generation in enrichment helper"""

    def setUp(self):
        self.factory = RequestFactory()

    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_empty_delivery_result(self, mock_get_group, mock_api_handler):
        """Test handling when API returns empty list."""
        from app.records.enrichment import RecordEnrichmentHelper

        iaid = "C123456"
        mock_api_handler.return_value = []

        mock_record = Mock()
        mock_record.id = iaid

        helper = RecordEnrichmentHelper(mock_record)
        result = helper._get_delivery_api_data()

        self.assertEqual(result, {})
        mock_get_group.assert_not_called()

    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_missing_options_value(self, mock_get_group, mock_api_handler):
        """Test handling when options value is missing from response."""
        from app.records.enrichment import RecordEnrichmentHelper

        iaid = "C123456"
        mock_api_handler.return_value = [
            {"surrogateLinks": [], "advancedOrderUrlParameters": None}
        ]

        mock_record = Mock()
        mock_record.id = iaid

        helper = RecordEnrichmentHelper(mock_record)
        result = helper._get_delivery_api_data()

        self.assertEqual(result, {})
        mock_get_group.assert_not_called()

    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_invalid_availability_condition(
        self, mock_get_group, mock_api_handler
    ):
        """Test handling when options value is not a valid AvailabilityCondition enum value."""
        from app.records.enrichment import RecordEnrichmentHelper

        iaid = "C123456"
        mock_api_handler.return_value = [{"options": 999, "surrogateLinks": []}]

        mock_record = Mock()
        mock_record.id = iaid

        helper = RecordEnrichmentHelper(mock_record)
        result = helper._get_delivery_api_data()

        self.assertEqual(result, {})
        mock_get_group.assert_not_called()

    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.enrichment.get_availability_group")
    def test_multiple_availability_conditions(
        self, mock_get_group, mock_api_handler
    ):
        """Test different availability conditions map to correct groups."""
        from app.records.enrichment import RecordEnrichmentHelper

        test_cases = [
            (
                3,
                "DigitizedDiscovery",
                AvailabilityGroup.AVAILABLE_ONLINE_TNA_ONLY,
            ),
            (
                4,
                "DigitizedLia",
                AvailabilityGroup.AVAILABLE_ONLINE_THIRD_PARTY_ONLY,
            ),
            (
                26,
                "OrderOriginal",
                AvailabilityGroup.AVAILABLE_IN_PERSON_WITH_COPYING,
            ),
            (14, "ClosedRetainedDeptKnown", AvailabilityGroup.CLOSED_TNA_OR_PA),
        ]

        for (
            options_value,
            expected_delivery_option,
            expected_group,
        ) in test_cases:
            with self.subTest(options_value=options_value):
                iaid = f"C{options_value}"
                mock_api_handler.return_value = [
                    {
                        "options": options_value,
                        "surrogateLinks": [],
                        "advancedOrderUrlParameters": None,
                    }
                ]
                mock_get_group.return_value = expected_group

                mock_record = Mock()
                mock_record.id = iaid

                helper = RecordEnrichmentHelper(mock_record)
                result = helper._get_delivery_api_data()

                self.assertEqual(
                    result,
                    {
                        "delivery_option": expected_delivery_option,
                        "do_availability_group": expected_group.name,
                    },
                )


class TestRecordDetailViewDeliveryOptions(TestCase):
    """Tests for delivery options integration in RecordDetailView."""

    def setUp(self):
        self.factory = RequestFactory()

    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.records.views.get_global_alert")
    @patch("app.records.views.get_mourning_notice")
    def test_delivery_options_added_to_context(
        self, mock_mourning, mock_alert, mock_record_details, mock_delivery, mock_distressing
    ):
        """Test that delivery options are added to context for standard records."""
        mock_alert.return_value = None
        mock_mourning.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record.reference_number = "TEST 123"
        mock_record.custom_record_type = "CAT"
        mock_record.subjects = []
        mock_record_details.return_value = mock_record
        # for Non-TNA record, series level, do delivery options should be included
        mock_record.is_tna = False
        mock_record.level_code = 3  # Sub-sub-fonds
        mock_record.level = "Series"
        mock_record.hierarchy_series = Mock()
        mock_record.hierarchy_series.reference_number = ""
        mock_record.hierarchy_series.summary_title = ""
        mock_record.summary_title = ""

        mock_delivery.return_value = [{"options": 25}]
        mock_distressing.return_value = False

        request = self.factory.get("/test/")
        view = RecordDetailView.as_view()
        response = view(request, id="C123456")

        self.assertIn("delivery_option", response.context_data)

    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.enrichment.delivery_options_request_handler")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.records.views.get_global_alert")
    @patch("app.records.views.get_mourning_notice")
    def test_no_delivery_options_for_archon_records(
        self, mock_mourning, mock_alert, mock_record_details, mock_delivery, mock_distressing
    ):
        """Test that delivery options are not fetched for ARCHON records."""
        mock_alert.return_value = None
        mock_mourning.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record.reference_number = "TEST 123"
        mock_record.custom_record_type = "ARCHON"
        mock_record.subjects = []
        mock_record_details.return_value = mock_record
        mock_record.level_code = 3
        mock_record.level = "Series"
        mock_record.hierarchy_series = Mock()
        mock_record.hierarchy_series.reference_number = ""
        mock_record.hierarchy_series.summary_title = ""
        mock_record.summary_title = ""

        mock_distressing.return_value = False

        request = self.factory.get("/test/")
        view = RecordDetailView.as_view()
        response = view(request, id="C123456")

        # Should not call delivery options handler for ARCHON records
        mock_delivery.assert_not_called()
        self.assertNotIn("do_availability_group", response.context_data)

    @patch("app.records.enrichment.has_distressing_content")
    @patch("app.records.mixins.record_details_by_id")
    @patch("app.records.views.get_global_alert")
    @patch("app.records.views.get_mourning_notice")
    def test_distressing_content_flag_added_to_context(
        self, mock_mourning, mock_alert, mock_record_details, mock_distressing
    ):
        """Test that distressing content flag is added to context."""
        mock_alert.return_value = None
        mock_mourning.return_value = None

        mock_record = Mock()
        mock_record.id = "C123456"
        mock_record.reference_number = "HO 616/123"
        mock_record.custom_record_type = None
        mock_record.subjects = []
        mock_record_details.return_value = mock_record
        mock_record.level_code = 3
        mock_record.level = "Series"
        mock_record.hierarchy_series = Mock()
        mock_record.hierarchy_series.reference_number = ""
        mock_record.hierarchy_series.summary_title = ""
        mock_record.summary_title = ""

        mock_distressing.return_value = True

        request = self.factory.get("/test/")
        view = RecordDetailView.as_view()
        response = view(request, id="C123456")

        self.assertIn("distressing_content", response.context_data)
        self.assertTrue(response.context_data["distressing_content"])
        mock_distressing.assert_called_once_with("HO 616/123")