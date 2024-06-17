import os
import logging
import pandas as pd
from request_functions import await_all, handle_progress, save_response_to_folder

logging.info(f"Initializing {50 * "."}")

folder = "./dois"
filename = "./dataset.xlsx"
extension = ".bib"

# Reading dataset
logging.info(f"Reading {filename}")
df = pd.read_excel(filename, na_filter=False)

# Filter out duplicates
unique_doi = df["DOI"].unique()

# Getting not download doi list
doi_urls = [
    dict(
        name=doi,
        url=f"https://doi.org/{doi}",
        headers={"Accept": "application/x-bibtex; charset=utf-8"},
    )
    for doi in unique_doi
    # Filter out downloaded dois
    if not os.path.exists(os.path.join(folder, f"{doi.replace("/", '\\')}{extension}"))
]
logging.info(f"Found {len(doi_urls)} dois to download. Total: {len(unique_doi)}")

# Download .html files to folder
logging.info(f"Starting download")
progress_handler = handle_progress(len(unique_doi), default=len(unique_doi) - len(doi_urls))
await_all(
    doi_urls,
    lambda url, response: save_response_to_folder(url=url, response=response, folder=folder, extension=extension),
    show_progress=lambda index: progress_handler.__next__(),
    concurrency=2
)




