import os
import logging
import pandas as pd
from request_functions import await_all, handle_progress, save_response_to_folder

logging.info(f"Initializing {50 * "."}")

folder = "./pages"
filename = "./dataset.xlsx"
extension = ".html"

# Reading dataset
logging.info(f"Reading {filename}")
df = pd.read_excel(filename, na_filter=False)

# Filter out duplicates
unique_issn = df["ISSN"].unique()

# Getting not download ISSN list
issn_urls = [
    dict(
        name=issn,
        url=f"https://www.scimagojr.com/journalsearch.php?q={issn}",
    )
    for issn in unique_issn
    # Filter out downloaded ISSNs
    if not os.path.exists(os.path.join(folder, f"{issn}{extension}"))
]
logging.info(f"Found {len(issn_urls)} ISSNs to download. Total: {len(unique_issn)}")

# Download .html files to folder
logging.info(f"Starting download")
progress_handler = handle_progress(len(unique_issn), default=len(unique_issn) - len(issn_urls))
await_all(
    issn_urls,
    lambda url, response: save_response_to_folder(
        url=url, response=response, folder=folder, extension=extension),
    show_progress=lambda index: progress_handler.__next__()
)



