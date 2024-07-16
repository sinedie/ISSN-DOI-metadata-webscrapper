import os
import json
import bibtexparser
import logger
from bs4 import BeautifulSoup


def search_doi_entry(doi: str, entry: str, progress_handler=None):
    if progress_handler is not None:
        progress_handler()

    if doi == "":
        return ""

    fname = os.path.join("./results/dois", f"{doi.replace('/', '@')}.bib")
    if not os.path.exists(fname):
        return ""

    with open(fname, encoding="utf-8", errors="replace") as bibtex_file:
        bibtex_database = bibtexparser.load(bibtex_file)
        entries = bibtex_database.get_entry_list()

        if len(entries):
            return entries[0].get(entry, "")

        return ""


def search_doi_authors(doi: str, progress_handler=None, max_authors=10):
    if progress_handler is not None:
        progress_handler()

    if doi == "":
        return [None] * max_authors

    fname = os.path.join("./results/dois_scopus", f"{doi.replace('/', '@')}.json")

    if not os.path.exists(fname):
        return [None] * max_authors

    with open(fname, encoding="utf-8", errors="replace") as f:
        data = json.load(f)
        authors = [author["@auid"] for author in data["authors"]["author"]]
        if len(authors) > max_authors:
            authors = authors[:max_authors]
        if len(authors) != max_authors:
            authors += [None] * (max_authors - len(authors))

        return authors


def search_authors_info(author: str, progress_handler=None):
    if progress_handler is not None:
        progress_handler()

    if author is None:
        return [None] * 4

    fname = os.path.join("./results/author_scopus", f"{author}.json")

    if not os.path.exists(fname):
        return [None] * 4

    with open(fname, encoding="utf-8", errors="replace") as f:
        author_data = json.load(f)

        affiliation_id = author_data["affiliation-current"]["@id"]
        affiliations = author_data["author-profile"]["affiliation-current"][
            "affiliation"
        ]
        affiliation = next(
            (aff for aff in affiliations if aff["@affiliation-id"] == affiliation_id),
            None,
        )

        name = author_data["author-profile"]["name-variant"]["given-name"]
        lastname = author_data["author-profile"]["name-variant"]["surname"]
        city = affiliation["ip-doc"]["address"]["city"] if affiliation else ""
        country = affiliation["ip-doc"]["address"]["country"] if affiliation else ""

        return [name, lastname, city, country]


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

    with open(filename, encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f, "html.parser")
        search_results = soup.find("div", class_="search_results")
        if not search_results:
            print(f"Search results not found {filename}")
            return False
        return search_results.find("a") is not None
