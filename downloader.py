import os
import json
import logger
import pybliometrics
from request_functions import download_metadata, handle_progress

pybliometrics.scopus.init()
from pybliometrics.scopus import AbstractRetrieval, AuthorRetrieval


def download_dois_metadata(dois):
    print("Downloading from https://doi.org")
    download_metadata(
        items=dois,
        url="https://doi.org/{{slug}}",
        headers={"Accept": "application/x-bibtex; charset=utf-8"},
        file_ext=".bib",
        out_folder="./results/dois",
        concurrency=2,
    )


def download_scimagojr_metadata(issns):
    print("Downloading from https://www.scimagojr.com")
    download_metadata(
        items=issns,
        url="https://www.scimagojr.com/journalsearch.php?q={{slug}}",
        file_ext=".html",
        out_folder="./results/issn_scimagojr",
        headers={
            "Accept": "text/html; charset=utf-8",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
        },
    )


def download_minciencias_metadata():
    # SOLO ES NECESARIO DESCARGAR ESTE, QUE SE TRAE TODAS
    issns = [""]
    folder = "./results/issn_minciencias/"

    print("Downloading from https://scienti.minciencias.gov.co")
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
        out_folder=folder,
    )

    with open(f"{folder}.json", encoding="utf-8") as f:
        magazines = json.load(f)
        for magazine in magazines:
            if magazine["ISSNS"] is None:
                continue

            for issn in magazine["ISSNS"].split(","):
                with open(f"{folder}{issn.strip()}.json", "w", encoding="utf-8") as fout:
                    json.dump(magazine, fout)


def download_minciencias_homologada_metadata(issns):
    print("Downloading from https://scienti.minciencias.gov.co (Homologadas)")
    download_metadata(
        items=issns,
        url="https://scienti.minciencias.gov.co/publindex/api/publico/revistasHomologadas",
        method="post",
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        body_getter=lambda issn: {"txtIssn": issn.replace("-", "").strip()},
        file_ext=".json",
        out_folder="./results/issn_minciencias_homologadas",
    )


# def download_scopus_metadata(authors):
#     print("Downloading from https://www.scopus.com")

#     def query_params(item):
#         items = item.split(",")
#         if len(items) == 2:
#             lastname, firstname = items
#             return f"?st1={lastname.strip()}&st2={firstname.strip()}"

#         # This should never happen, but just in case
#         return f"?st1={item}"

#     download_metadata(
#         items=authors,
#         url="https://www.scopus.com/results/authorNamesList.uri",
#         query_params=query_params,
#         file_ext=".html",
#         out_folder="./results/scopus",
#         headers={
#             "Accept": "text/html; charset=utf-8",
#             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36",
#         },
#         concurrency=2,
#     )


def download_pybliometrics_doi_data(dois):
    folder = "./results/dois_scopus"
    progress = handle_progress(len(dois))

    os.makedirs(folder, exist_ok=True)

    for doi in dois:
        progress.__next__()

        if doi == "" or doi is None:
            continue

        article = AbstractRetrieval(doi)
        with open(f"{folder}/{doi.replace("/", "@")}.json", "w", encoding="utf-8") as f:
            json.dump(article._json, f)


def download_pybliometrics_authors_data():
    folder = "./results/author_scopus"
    os.makedirs(folder, exist_ok=True)
    dois = os.listdir("./results/dois_scopus/")

    authors = {}
    for filename in dois:
        with open(filename, encoding="utf-8") as f:
            data = json.load(f)

            for author in data["authors"]['author']:
                if not author.get("@auid", False):
                    continue

                authors[author["@auid"]] = author.get(
                    "ce:indexed-name", 
                    author.get("ce:given-name", "Desconocido")
                )

    progress = handle_progress(len(authors.values()))

    for uid, name in authors.items():
        progress.__next__()

        author_data = AuthorRetrieval(uid)
        with open(f"{folder}/{uid}.json", "w", encoding="utf-8") as f:
            json.dump(author_data._json, f)
