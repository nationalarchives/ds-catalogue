from enum import IntEnum


class Reader(IntEnum):
    """
    Enumeration representing different types of users/readers accessing the system.
    Used to determine user permissions and available functionalities.
    """

    UNDEFINED = -1  # Default value when reader type cannot be determined
    STAFFIN = 0  # Staff members within the organisation
    ONSITEPUBLIC = 1  # Public users physically present at the facility
    SUBSCRIPTION = 2  # Users with a paid subscription
    OFFSITE = 3  # Remote users with no special access


class AvailabilityCondition(IntEnum):
    """
    Enumeration representing different availability conditions for records.
    Used to determine how records can be accessed or delivered to users.
    """

    InvigilationSafeRoom = 0  # Record accessible under supervision in safe room
    CollectionCare = 1  # Record requires special handling in Collection Care
    InUse = 2  # Record is currently in use by another user
    DigitizedDiscovery = 3  # Digitized record available for discovery
    DigitizedLia = 4  # Digitized record available through LIA
    DigitizedOther = 5  # Digitized record available through other means
    DigitizedAvailableButNotDownloadableAtPieceLevel = (
        6  # Digitized but not available for individual download
    )
    DigitizedAvailableButNotDownloadableAtItemLevel = (
        7  # Digitized but not available for item-level download
    )
    DigitizedPartiallyOpened = 8  # Digitized record partially available
    AV_Media = 9  # Audio/visual media
    AcademicSubscription = 10  # Available through academic subscription
    ImageLibrary = 11  # Available in image library
    ClosedFOIReview = 12  # Closed, but can be reviewed via FOI request
    AccessUnderReview = 13  # Access is currently under review
    ClosedRetainedDeptKnown = 14  # Closed and retained by a known department
    ClosedRetainedDeptUnKnown = 15  # Closed and retained by an unknown department
    PaidSearch = 16  # Available through paid search
    Offsite = 17  # Record is stored offsite
    Surrogate = 18  # Surrogate version is available
    Unfit = 19  # Record is unfit for production
    MouldTreatment = 20  # Record requires mould treatment
    Onloan = 21  # Record is on loan to another organisation
    DisplayAtMuseum = 22  # Record is on display at a museum
    MissingLost = 23  # Record is missing or lost
    GovtWebArchive = 24  # Record is in the government web archive
    LocalArchive = 25  # Record is in a local archive
    OrderOriginal = 26  # Original record can be ordered
    FileAuthority = 27  # Related to file authority
    TooLargeToCopyOriginal = 28  # Original too large to copy
    TooLargeToCopyOffsite = 29  # Offsite record too large to copy
    TooLargeToCopySurrogate = 30  # Surrogate too large to copy
    UnAvailable = 31  # Record is unavailable
    OrderException = 32  # Exception in ordering process
    AdvanceOrderOnly = 33  # Available for advance order only
    Relocation = 34  # Record is being relocated


# TODO: This is a temporary constant and will be removed when the templating solution is implemented
DELIVERY_OPTIONS_CONFIG = "app/deliveryoptions/delivery_options.json"

# TODO: Refactor to use Enums throughout the codebase
DELIVERY_OPTIONS_TNA_LEVELS = [6, 7]  # Piece and Item
DELIVERY_OPTIONS_NON_TNA_LEVELS = [3]  # Sub-sub-fonds
