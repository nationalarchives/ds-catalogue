from typing import Any

from django.http import HttpRequest


class DataLayerMixin:
    """
    A mixin applied to Page types, Record subclasses,
    or View classes to allow them to customise the Analytics datalayer.
    """

    content_group: str = (
        "Not in use"  # Default value; should be overridden in subclasses
    )

    def get_content_group(self) -> str:
        """
        Return a string to use as the 'content_group' value in DataLayer
        for this object.

        Subclasses should either set the 'content_group' attribute
        or override this method to return a string.
        """

        return self.content_group

    def get_datalayer_data(self, request: HttpRequest) -> dict[str, Any]:
        """
        Return values that should be included in the datalayer
        when rendering this object for the provided ``request``.

        Override this method on subclasses to add data that is relevant to the
        subclass.
        """

        # Set defaults
        data = {
            "content_group": self.get_content_group(),
            "page_type": "",
            "reader_type": None,  # Reserved for reader location; null if no value
        }

        return data
