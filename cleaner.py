import os
import logging
import pandas as pd
import logger


def clean_doi(original_doi):

    doi = original_doi.lower().strip()
    if doi == "" or "10." not in doi:
        return ""

    # Start from prefix 10.
    doi = doi[doi.index("10.") :]

    if "/" not in doi:
        return ""

    # Removing trail dot
    if doi[-1] == ".":
        doi = doi[:-1]

    # Removing spaces
    doi = doi.replace(" ", "").replace("\n", "")

    if doi != original_doi.lower():
        logging.info(f"Changed doi")
        logging.info(f"==== From {original_doi}")
        logging.info(f"==== To {doi}")

    return doi
