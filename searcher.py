import os
import pandas as pd
import bibtexparser
from bs4 import BeautifulSoup
from request_functions import handle_progress


def search_doi(doi: str, entry: str, progress_handler=None):
    if progress_handler is not None:
        progress_handler()

    if doi == "":
        return ""

    fname = os.path.join("./results/dois", f"{doi.replace('/', '\\')}.bib")
    if not os.path.exists(fname):
        return ""

    with open(fname) as bibtex_file:
        bibtex_database = bibtexparser.load(bibtex_file)
        entries = bibtex_database.get_entry_list()

        if len(entries):
            return entries[0].get(entry, "")

        return ""


def search_issn(issn: str, progress_handler=None):
    if progress_handler is not None:
        progress_handler()

    if issn == "" or issn == 0:
        return False

    filename = os.path.join("./results/issn_minciencias_homologadas", f"{issn}.json")
    if os.path.exists(filename):
        return True

    filename = os.path.join("./results/issn_minciencias", f"{issn}.json")
    if os.path.exists(filename):
        return True

    filename = os.path.join("./results/issn_scimagojr", f"{issn}.html")
    if not os.path.exists(filename):
        return False

    with open(filename, "r") as f:
        soup = BeautifulSoup(f, "html.parser")
        search_results = soup.find("div", class_="search_results")
        return search_results.find("a") is not None


filename = "./dataset.xlsx"
df = pd.read_excel(filename, na_filter=False)


progress_handler = handle_progress(len(df))
df["ISSNFound"] = df["ISSN"].apply(
    lambda issn: search_issn(
        issn,
        progress_handler=lambda: progress_handler.__next__(),
    )
)

progress_handler = handle_progress(len(df))
df["author"] = df["DOI"].apply(
    lambda doi: search_doi(
        doi,
        "author",
        progress_handler=lambda: progress_handler.__next__(),
    )
)
progress_handler = handle_progress(len(df))
df["url"] = df["DOI"].apply(
    lambda doi: search_doi(
        doi,
        "url",
        progress_handler=lambda: progress_handler.__next__(),
    )
)


fileout = "_out".join(os.path.splitext(filename))
df.to_excel(fileout, index=False)
