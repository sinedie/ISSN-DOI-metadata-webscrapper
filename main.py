import os
import logger
import logging
import pandas as pd
from cleaner import clean_doi
from downloader import (
    download_dois_metadata,
    download_scimagojr_metadata,
    download_minciencias_metadata,
    download_minciencias_homologada_metadata,
    download_scopus_metadata,
)
from searcher import search_doi, search_issn, search_authors
from request_functions import handle_progress

# Reading file
filename = "./dataset.xlsx"
print(f"Reading {filename}")
logging.info(f"Reading {filename}")
df = pd.read_excel(filename, na_filter=False)

# Cleaning dois
new_doi_column = "CLEAN_DOI"
logging.info(f"Cleaning DOIS and saving to {new_doi_column} column")
df[new_doi_column] = df["DOI"].apply(clean_doi)

# Filter out duplicates
unique_doi = df["CLEAN_DOI"].unique()
unique_issn = df["ISSN"].unique()

# Downloading info
logging.info("Download scimagojr metadata")
download_scimagojr_metadata(unique_issn)

logging.info("Download dois metadata")
download_dois_metadata(unique_doi)

logging.info("Download minciencias metadata")
download_minciencias_metadata(unique_issn)

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

# Searching DOI metadata
entries = ["author", "url"]
for entry in entries:
    print(f"Searching {entry}")
    progress_handler = handle_progress(len(df))
    df[entry] = df["DOI"].apply(
        lambda doi: search_doi(
            doi,
            entry,
            progress_handler=lambda: progress_handler.__next__(),
        )
    )

# Downloading authors data
if "author" in df:
    n_author_max = 10
    logging.info("Getting unique authors")
    df_authors = df[df["author"].str.len() > 0]["author"]
    df_authors = df_authors.str.split(" and ", expand=True)
    df_authors = df_authors.map(lambda x: x.strip() if isinstance(x, str) else x)
    df_authors = df_authors.iloc[:, :n_author_max]

    authors = pd.unique(df_authors.values.ravel("K"))
    authors = [a for a in authors if a is not None]
    logging.info("Download Scopus Authors metadata")
    download_scopus_metadata(authors)

    logging.info("Searching unique authors info")
    df_authors = df["author"].str.split(" and ", expand=True)
    df_authors = df_authors.map(lambda x: x.strip() if isinstance(x, str) else x)
    df_authors = df_authors.iloc[:, :n_author_max]
    df_authors.columns = [f"Author {i}" for i in range(n_author_max)]

    print(f"Searching authors data")
    progress_handler = handle_progress(len(df))
    authors_info = df_authors.apply(
        lambda authors: search_authors(
            authors,
            progress_handler=lambda: progress_handler.__next__(),
        ),
        axis=1,
        result_type="expand",
    )
    columns = [[f"City author {i}", f"Country author {i}"] for i in range(n_author_max)]
    authors_info.columns = [x for author in columns for x in author]

    df = pd.concat([df, df_authors, authors_info], axis=1)


fileout = "_out".join(os.path.splitext(filename))
df.to_excel(fileout, index=False)
