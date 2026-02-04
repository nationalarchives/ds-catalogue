import json
import unittest

from app.deliveryoptions.constants import DELIVERY_OPTIONS_CONFIG


# These tests aren't comprehensive but check the important fields.
class TestDeliveryOptionsJSON(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Load JSON file once for all tests
        with open(DELIVERY_OPTIONS_CONFIG, "r") as f:
            cls.data = json.load(f)

    def test_delivery_options_exist(self):
        # Check if 'deliveryOptions' key exists in the JSON.
        self.assertIn("deliveryOptions", self.data)

    def test_option_list_exists(self):
        # Check if 'option' is a list inside 'deliveryOptions'.
        self.assertIn("option", self.data["deliveryOptions"])
        self.assertIsInstance(self.data["deliveryOptions"]["option"], list)

    def test_required_fields_in_option(self):
        # Ensure each delivery option has required fields.
        required_fields = {"deliveryoption", "offset", "readertype"}
        for option in self.data["deliveryOptions"]["option"]:
            self.assertTrue(required_fields.issubset(option.keys()))

    def test_readertype_structure(self):
        # Check if 'readertype' is properly structured.
        for option in self.data["deliveryOptions"]["option"]:
            self.assertIn("readertype", option)
            self.assertIsInstance(option["readertype"], list)
            offset = option["offset"]

            for reader in option["readertype"]:
                self.assertIn("reader", reader)

                # Not all types have a description
                if offset not in [7, 31]:
                    self.assertIn("description", reader)
                    self.assertIsInstance(reader["description"], list)

                    for desc in reader["description"]:
                        self.assertIn("name", desc)
                        self.assertIn("value", desc)

    def test_orderbuttons_format(self):
        # Ensure that 'orderbuttons', if present, contain required fields.
        for option in self.data["deliveryOptions"]["option"]:
            offset = option["offset"]

            for reader in option.get("readertype", []):
                if "orderbuttons" in reader:
                    self.assertIsInstance(
                        reader["orderbuttons"],
                        list,
                        msg=f"'orderbuttons' should be a list for option {offset}, found type: {type(reader['orderbuttons'])}",
                    )
                    for button in reader["orderbuttons"]:
                        self.assertIn("name", button)
                        self.assertIn("href", button)
                        self.assertIn("text", button)

    def test_readertype_list_length_and_values(self):
        # Test that each 'readertype' list has exactly 4 items with expected reader values.
        expected_readers = {
            "staffin",
            "onsitepublic",
            "subscription",
            "offsite",
        }

        for option in self.data["deliveryOptions"]["option"]:
            readertypes = option.get("readertype", [])

            # Assert length is exactly 4
            self.assertEqual(
                len(readertypes),
                4,
                msg=f"Expected 4 readertypes in '{option.get('deliveryoption')}', found {len(readertypes)}",
            )

            # Extract actual reader values
            actual_readers = {reader.get("reader") for reader in readertypes}

            # Assert expected readers are all present
            self.assertSetEqual(
                actual_readers,
                expected_readers,
                msg=f"Reader values mismatch in '{option.get('deliveryoption')}': "
                f"Expected {expected_readers}, found {actual_readers}",
            )
