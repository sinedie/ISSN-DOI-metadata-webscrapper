import gevent.monkey

gevent.monkey.patch_all()

import os
import logger
import logging
import pandas as pd
from cleaner import clean_doi
from downloader import (
    download_scimagojr_metadata,
    download_minciencias_metadata,
    download_minciencias_homologada_metadata,
    download_pybliometrics_doi_data,
    download_pybliometrics_authors_data,
    download_dois_metadata,
)
from searcher import (
    search_issn,
    search_doi_authors,
    search_doi_entry,
    search_authors_info,
)
from request_functions import handle_progress

# Reading file
filename = "./dataset.xlsx"
print(f"Reading {filename}")
logging.info(f"Reading {filename}")
df = pd.read_excel(filename, na_filter=False)

# Cleaning dois
logging.info(f"Cleaning DOIS and saving to CLEAN_DOI column")
df["CLEAN_DOI"] = df["DOI"].apply(clean_doi)

# Filter out duplicates
unique_doi = df["CLEAN_DOI"].unique()
unique_issn = df["ISSN"].unique()

# Downloading info
logging.info("Download scimagojr metadata")
download_scimagojr_metadata(unique_issn)

logging.info("Download dois metadata")
download_dois_metadata(unique_doi)
download_pybliometrics_doi_data(unique_doi)
download_pybliometrics_authors_data()

logging.info("Download minciencias metadata")
download_minciencias_metadata()

logging.info("Download minciencias homologada metadata")
download_minciencias_homologada_metadata(unique_issn)

# Searching ISSN
print("Searching ISSN")
progress_handler = handle_progress(len(df))
df["ISSNFound"] = df["ISSN"].apply(
    lambda issn: search_issn(
        issn,
        progress_handler=lambda: progress_handler.__next__(),
    )
)

print("Searching doi URL")
progress_handler = handle_progress(len(df))
entry = "url"
df[entry] = df["CLEAN_DOI"].apply(
    lambda doi: search_doi_entry(
        doi,
        entry,
        progress_handler=lambda: progress_handler.__next__(),
    )
)

print("Searching doi authors")
progress_handler = handle_progress(len(df))
max_authors = 10
df_doi_authors = df["CLEAN_DOI"].apply(
    lambda doi: search_doi_authors(
        doi,
        max_authors=max_authors,
        progress_handler=lambda: progress_handler.__next__(),
    ),
)

df_doi_authors = pd.DataFrame(df_doi_authors.to_list())
df_doi_authors.columns = [f"Autor {i}" for i in range(max_authors)]

print("Searching authors data")
progress_handler = handle_progress(len(df) * max_authors)
df_doi_authors = df_doi_authors.map(
    lambda author: search_authors_info(
        author,
        progress_handler=lambda: progress_handler.__next__(),
    ),
)

print("Saving data")
for c in df_doi_authors.columns:
    df[[f"Nombre {c}", f"Apellido {c}", f"Ciudad {c}", f"Pais {c}"]] = pd.DataFrame(
        df_doi_authors[c].tolist()
    )

fileout = "_out".join(os.path.splitext(filename))
df.to_excel(fileout, index=False)
