from django.test import TestCase
from django.urls import resolve, reverse


class TestMachineReadableDetailsRouteResolution(TestCase):
    def test_resolves_id(self):
        resolver = resolve("/catalogue/id/C7810139/")

        self.assertEqual(resolver.view_name, "records:details")
        self.assertEqual(resolver.kwargs["id"], "C7810139")

    def test_id_with_non_standard_prefix(self):
        resolver = resolve("/catalogue/id/C123456/")

        self.assertEqual(resolver.view_name, "records:details")
        self.assertEqual(resolver.kwargs["id"], "C123456")

    def test_resolves_uuid(self):
        # Some IDs are UUIDs. Tested ID is a real example
        resolver = resolve(
            "/catalogue/id/43f766a9-e968-4b82-93dc-8cf11a841d41/"
        )

        self.assertEqual(resolver.view_name, "records:details")
        self.assertEqual(
            resolver.kwargs["id"], "43f766a9-e968-4b82-93dc-8cf11a841d41"
        )


class TestMachineReadableDetailsURL(TestCase):
    def test_reverse_id(self):
        url = reverse("records:details", kwargs={"id": "C7810139"})

        self.assertEqual(url, "/catalogue/id/C7810139/")

    def test_reverse_uuid(self):
        url = reverse(
            "records:details",
            kwargs={"id": "43f766a9-e968-4b82-93dc-8cf11a841d41"},
        )

        self.assertEqual(
            url, "/catalogue/id/43f766a9-e968-4b82-93dc-8cf11a841d41/"
        )
