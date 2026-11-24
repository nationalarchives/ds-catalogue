"""Utils used to support running Tests"""

import logging
from unittest.mock import patch


def prevent_request_warnings(original_function):
    """
    If we need to test for 404, 503s this decorator can prevent
    the request class from throwing warnings.

    Ex: suppresses 404 for get request
    """

    def new_function(*args, **kwargs):
        # set logging level before triggering original function
        logger = logging.getLogger("django.request")
        previous_logging_level = logger.getEffectiveLevel()
        logger.setLevel(logging.CRITICAL)  # Suppresses ERROR and below

        # trigger original function that would throw error
        original_function(*args, **kwargs)

        # set logging level back to previous
        logger.setLevel(previous_logging_level)

    return new_function


def patch_collection_choices(return_value: tuple[tuple[str, str], ...] | None = None):
    """Mock collection choices to avoid unintended reuse of test API responses.
    Overrides the default collection choices for testing purposes.
    """
    if not return_value:
        return_value = (
            ("Y", "Y - UK Parliament"),
            (
                "LEV",
                "LEV - Inquiry into the Culture, Practices and Ethics of the Press (Leveson Inquiry)",
            ),
            ("ADM", "ADM - Admiralty, Navy, Royal Marines, and Coastguard"),
            ("BT", "BT - Board of Trade and successors"),
            (
                "WO",
                "WO - War Office, Armed Forces, Judge Advocate General, and related bodies",
            ),
            ("HO", "HO - Home Office"),
            (
                "E",
                "E - Exchequer, Office of First Fruits and Tenths, and the Court of Augmentations",
            ),
            (
                "C",
                "C - Chancery, the Wardrobe, Royal Household, Exchequer and various commissions",
            ),
            ("AIR", "AIR - Air Ministry and Royal Air Force records"),
            ("GTI", "GTI - Grenfell Tower Inquiry"),
            (
                "RAIL",
                "RAIL - Pre-nationalisation railway companies, pre-nationalisation canal and related companies",
            ),
            (
                "YHL",
                "YHL - Records of the House of Commons; Records of the House of Lords",
            ),
            ("YBBK", "YBBK - The Beaverbrook Papers"),
            ("YHNN", "YHNN - Papers of Sir Patrick Joseph Henry Hannon MP (1874-1963)"),
            ("YFLS", "YFLS - Papers of Frances Stevenson (1888-1972)"),
            ("YHEA", "YHEA - Papers of Timothy Michael Healy, KC"),
            ("YWAR", "YWAR - The Wargrave Papers"),
            (
                "YBAL",
                "YBAL - Papers of Harold Harrington Balfour (1897-1988, 1st Baron Balfour of Inchrye",
            ),
            ("YBLU", "YBLU - Papers of Ralph David Blumenfeld"),
            ("YOWE", "YOWE - The Owen Papers"),
            ("YLG", "YLG - The Lloyd George Papers"),
            (
                "YBLK",
                "YBLK - Papers of Robert Norman William Blake (1916-2003, Baron Blake of Braydeston",
            ),
            ("PROB", "PROB - Prerogative Court of Canterbury"),
            ("FO", "FO - Foreign Office"),
            ("EF", "EF - Health and Safety Commission and Executive"),
            ("YHC", "YHC - Records of the House of Commons"),
            (
                "CO",
                "CO - Colonial Office, Commonwealth and Foreign and Commonwealth Offices",
            ),
            ("CSPR", "CSPR - Civil Service Pay Research Unit"),
            ("J", "J - Supreme Court of Judicature"),
        )
    return patch(
        "app.search.forms.get_all_collection_choices",
        return_value=return_value,
    )
