import os
import pandas as pd
import bibtexparser
import logger
from bs4 import BeautifulSoup
from request_functions import handle_progress


def search_doi(doi: str, entry: str, progress_handler=None):
    if progress_handler is not None:
        progress_handler()

    if doi == "":
        return ""

    fname = os.path.join("./results/dois", f"{doi.replace('/', '@')}.bib")
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


def search_authors(authors, progress_handler=None):
    if progress_handler is not None:
        progress_handler()

    results = []

    for author in authors:
        if author is None or author == "":
            results.append([None, None])
            continue

        filename = os.path.join("./results/scopus", f"{author}.html")
        try:
            pd_search = pd.read_html(filename, match="Country/Territory")

            author_info = pd_search[0].iloc[0]
            results.append([author_info["City"], author_info["Country/Territory"]])
        except:
            results.append([None, None])

    return [x for user in results for x in user]
