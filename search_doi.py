import os
import bibtexparser
import pandas as pd
from request_functions import handle_progress

folder = "./dois"
filename = "./dataset.xlsx"
extension = ".bib"


def search(doi: str, entry: str, progress_handler=None):
    if progress_handler is not None:
        progress_handler()

    if doi == "":
        return ""

    fname = os.path.join(folder, f"{doi.replace("/", '\\')}{extension}")
        
    if not os.path.exists(fname):
        return ""


    with open(fname) as bibtex_file:
        bibtex_database = bibtexparser.load(bibtex_file)
        entries = bibtex_database.get_entry_list()

        if len(entries):
            return entries[0].get(entry, "")

        return ""
    

df = pd.read_excel(filename, na_filter=False)
progress_handler = handle_progress(len(df))
df["author"] = df["DOI"].apply(lambda doi: search(doi, "author", progress_handler=lambda: progress_handler.__next__()))
progress_handler = handle_progress(len(df))
df["url"] = df["DOI"].apply(lambda doi: search(doi, "url", progress_handler=lambda: progress_handler.__next__()))

fileout = f"_with_author_and_url".join(os.path.splitext(filename))
df.to_excel(fileout, index=False)
