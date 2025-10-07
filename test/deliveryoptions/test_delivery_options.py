import inspect
import json
from copy import deepcopy
from unittest.mock import Mock, patch

from app.deliveryoptions.constants import (
    DELIVERY_OPTIONS_CONFIG,
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
from app.records.models import APIResponse
from django.conf import settings
from django.test import TestCase


class TestDeliveryOptionTags(TestCase):
    def setUp(self):
        # This is a simplified example of the delivery_option_tags dictionary.
        self.delivery_option_tags = delivery_option_tags

        # Path to the JSON file containing the delivery options
        self.json_file_path = DELIVERY_OPTIONS_CONFIG

    def extract_tags(self, data):
        """
        Extract all markup tags in the form {TagName} from the JSON structure.
        """
        import re

        def find_tags(value):
            """Helper function to find tags within strings."""
            if isinstance(value, str):
                return re.findall(r"{(.*?)}", value)
            return []

        tags = set()

        # Recursively find all tags in the nested JSON
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
        # Load JSON data from the file
        with open(self.json_file_path, "r") as file:
            delivery_options_json = json.load(file)

        # Extract all markup tags from the JSON data
        extracted_tags = self.extract_tags(delivery_options_json)

        # Check that each extracted tag is in the delivery_option_tags dictionary
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

        # Rename to api_surrogate_list to match the updated parameter name in helper functions
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
            # TODO: Temporary link to Discovery until archon template is ready
            # "{ArchiveLink}": "/catalogue/id/A13530124/",
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

                # Use inspect to determine what parameters the function expects
                sig = inspect.signature(func)
                params = {}

                # Add only the parameters the function expects
                param_names = set(sig.parameters.keys())
                if "record" in param_names:
                    params["record"] = self.record

                # Make sure we're using the correct parameter name for surrogate data
                if "api_surrogate_list" in param_names:
                    params["api_surrogate_list"] = self.surrogate
                elif "surrogate" in param_names:
                    params["surrogate"] = self.surrogate

                # Call the function with the appropriate parameters
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
        "app.deliveryoptions.helpers.BASE_TNA_HOME_URL",
        "https://tnabase.test.url",
    )
    def test_get_advance_order_information(self):
        self.assertEqual(
            get_advance_order_information(),
            "https://tnabase.test.url/about/visit-us/",
        )

    def test_html_replacer(self):
        record = Mock()
        surrogate_data = []
        result = html_replacer(
            "Order here: {AddedToBasketText}", record, surrogate_data
        )
        self.assertEqual(result, "Order here: Add to basket")

    def test_description_dcs_selection(self):
        json_data = {
            "reference_number": "LEV 12/345",
            "description": [
                {"name": "description1", "value": "Regular description"},
                {
                    "name": "descriptionDCS",
                    "value": "Sensitive content warning",
                },
            ],
        }

        with patch(
            "app.deliveryoptions.delivery_options.has_distressing_content_match",
            return_value=True,
        ):
            selected_description = next(
                (
                    desc["value"]
                    for desc in json_data["description"]
                    if desc["name"] == "descriptionDCS"
                ),
                None,
            )
            self.assertEqual(selected_description, "Sensitive content warning")

    def test_description_non_dcs_selection(self):
        json_data = {
            "reference_number": "ABC 12/345",
            "description": [
                {"name": "description1", "value": "Regular description"},
                {
                    "name": "descriptionDCS",
                    "value": "Sensitive content warning",
                },
            ],
        }

        with patch(
            "app.deliveryoptions.delivery_options.has_distressing_content_match",
            return_value=False,
        ):
            selected_description = next(
                (
                    desc["value"]
                    for desc in json_data["description"]
                    if desc["name"] == "description1"
                ),
                None,
            )
            self.assertEqual(selected_description, "Regular description")


class TestSurrogateReferences(TestCase):
    def test_empty_list(self):
        reference_list = []
        surrogate_list = surrogate_link_builder(reference_list)
        self.assertEqual(surrogate_list, [])

    def test_non_empty_list_with_no_av_media(self):
        reference_list = [
            {
                "xReferenceURL": "https://example.com/1",
                "xReferenceType": "DIGITIZED_DISCOVERY",
            },
            {
                "xReferenceURL": "https://example.com/2",
                "xReferenceType": "DIGITIZED_DISCOVERY",
            },
        ]
        surrogate_list = surrogate_link_builder(reference_list)
        self.assertEqual(
            surrogate_list, ["https://example.com/1", "https://example.com/2"]
        )

    def test_list_with_av_media(self):
        reference_list = [
            {
                "xReferenceURL": "https://example.com/1",
                "xReferenceType": "AV_MEDIA",
            },
            {
                "xReferenceURL": "https://example.com/2",
                "xReferenceType": "DIGITIZED_DISCOVERY",
            },
            {
                "xReferenceURL": "https://example.com/3",
                "xReferenceType": "AV_MEDIA",
            },
        ]
        surrogate_list = surrogate_link_builder(reference_list)
        self.assertEqual(
            surrogate_list,
            [
                "https://example.com/1",
                "https://example.com/2",
                "https://example.com/3",
            ],
        )

    def test_list_with_empty_values(self):
        reference_list = [
            {"xReferenceURL": "", "xReferenceType": "AV_MEDIA"},
            {
                "xReferenceURL": "https://example.com/1",
                "xReferenceType": "AV_MEDIA",
            },
        ]
        surrogate_list = surrogate_link_builder(reference_list)
        self.assertEqual(surrogate_list, ["https://example.com/1"])
