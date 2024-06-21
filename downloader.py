import logging
import pandas as pd
from request_functions import download_metadata


def download_dois_metadata(dois):
    download_metadata(
        items=dois,
        url="https://doi.org/{{slug}}",
        headers={"Accept": "application/x-bibtex; charset=utf-8"},
        file_ext=".bib",
        out_folder="./results/dois",
        concurrency=2,
    )


def download_scimagojr_metadata(issns):
    download_metadata(
        items=issns,
        url="https://www.scimagojr.com/journalsearch.php?q={{slug}}",
        file_ext=".html",
        out_folder="./results/issn_scimagojr",
        headers={"Accept": "text/html; charset=utf-8"},
    )


def download_minciencias_metadata(issns):
    download_metadata(
        items=issns,
        url="https://scienti.minciencias.gov.co/publindex/api/publico/revistasPublindex",
        method="post",
        headers={"Content-Type": "application/json"},
        body_getter=lambda issn: {
            "tipoBusqueda": "R",
            "txtIssn": issn.replace("-", ""),
        },
        file_ext=".json",
        out_folder="./results/issn_minciencias",
    )


def download_minciencias_homologada_metadata(issns):
    download_metadata(
        items=issns,
        url="https://scienti.minciencias.gov.co/publindex/api/publico/revistasHomologadas",
        method="post",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        body_getter=lambda issn: {"txtIssn": issn.replace("-", "").strip()},
        file_ext=".json",
        out_folder="./results/issn_minciencias_homologadas",
    )


filename = "./dataset.xlsx"
logging.info(f"Reading {filename}")
df = pd.read_excel(filename, na_filter=False)

# Filter out duplicates
unique_doi = df["DOI"].unique()  # TODO Clean this column
unique_issn = df["ISSN"].unique()

# DOWNLOAD
# download_dois_metadata(unique_doi)
# download_scimagojr_metadata(unique_issn)
# download_minciencias_metadata(unique_issn)
# download_minciencias_homologada_metadata(unique_issn)
