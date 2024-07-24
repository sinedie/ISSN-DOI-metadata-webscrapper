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

        if data["authors"] is None or data["authors"]["author"] is None:
            return [None] * max_authors

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

        affiliations = (
            author_data["author-profile"]
            .get("affiliation-current", {})
            .get("affiliation", None)
        )

        if affiliations is None:
            affiliation = None
        elif type(affiliations) is dict:
            affiliation = affiliations
        else:
            affiliation = next(
                (
                    aff
                    for aff in affiliations
                    if aff["@affiliation-id"] == affiliation_id
                ),
                None,
            )

        name = author_data["author-profile"]["preferred-name"]["given-name"]
        lastname = author_data["author-profile"]["preferred-name"]["surname"]
        if (
            affiliation is not None
            and affiliation.get("ip-doc", None) is not None
            and affiliation["ip-doc"].get("address", None) is not None
        ):
            city = affiliation["ip-doc"]["address"].get("city", "")
            country = affiliation["ip-doc"]["address"].get("country", "")
        else:
            city = ""
            country = ""

        return [name, lastname, city, country]


def search_issn(issn: str, progress_handler=None):
    if progress_handler is not None:
        progress_handler()

    if issn == "" or issn == 0:
        return False

    filename = os.path.join("./results/issn_minciencias_homologadas", f"{issn}.json")
    if os.path.exists(filename):
        return True

    # Searching with "-"
    clean_issn = issn.replace("-", "")
    filename = os.path.join(
        "./results/issn_minciencias",
        f"{clean_issn[:4]}-{clean_issn[4:]}.json",
    )
    if os.path.exists(filename):
        return True

    # Searching without "-"
    filename = os.path.join("./results/issn_minciencias", f"{clean_issn}.json")
    if os.path.exists(filename):
        return True

    filename = os.path.join("./results/issn_scimagojr", f"{issn}.html")
    if not os.path.exists(filename):
        return False

    with open(filename, encoding="utf-8", errors="replace") as f:
        soup = BeautifulSoup(f, "html.parser")
        search_results = soup.find("div", class_="search_results")
        if not search_results:
            return False
        return search_results.find("a") is not None
