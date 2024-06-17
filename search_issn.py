import os
import pandas as pd
from bs4 import BeautifulSoup
from request_functions import handle_progress

folder = "./pages"
filename = "./dataset.xlsx"
extension = ".html"


def search(issn: str, progress_handler=None):
    filename = os.path.join(folder, f"{issn}{extension}")

    if progress_handler is not None:
        progress_handler()

    if issn == "" or not os.path.exists(filename):
        return False

    with open(filename, "r") as f:
        soup = BeautifulSoup(f, "html.parser")
        search_results = soup.find("div", class_="search_results")
        return search_results.find("a") is not None


df = pd.read_excel(filename, na_filter=False)
progress_handler = handle_progress(len(df))
df["ISSNFound"] = df["ISSN"].apply(
    lambda issn: search(issn, progress_handler=lambda: progress_handler.__next__())
)

fileout = "_with_issn".join(os.path.splitext(filename))
df.to_excel(fileout, index=False)
