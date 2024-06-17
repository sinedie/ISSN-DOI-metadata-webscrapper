import os
import sys
import logging
import grequests

logging.basicConfig(
    filename="run.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)


def await_all(urls, callback, concurrency=10, show_progress=None):
    # Setting all requests
    rs = (grequests.get(url["url"], headers=url.get("headers", {})) for url in urls)

    # Sending multiple request at once (concurrency value)
    for index, response in grequests.imap_enumerated(rs, size=concurrency):
        if show_progress is not None:
            show_progress(index)
        # Calling the callback function with the response value
        callback(urls[index], response)


def handle_progress(total, default=0):
    progress = default
    while progress < total:
        progress += 1
        show_progress(total, progress=progress)
        yield progress


def show_progress(total: int, progress: int):
    """Displays or updates a console progress bar"""

    barLength, status = 20, ""
    progress = float(progress) / float(total)
    if progress >= 1.0:
        progress, status = 1, "\r\n"
    block = int(round(barLength * progress))
    text = "\r[{}] {:.0f}% {}".format(
        "#" * block + "-" * (barLength - block), round(progress * 100, 0), status
    )
    sys.stdout.write(text)
    sys.stdout.flush()


def save_response_to_folder(url, response, folder=None, extension=""):
    filename = url["name"].replace("/", "\\")
    folder = folder or "./"
    # Create folder if not found
    os.makedirs(folder, exist_ok=True)

    # If download failed
    if not response.ok:
        logging.error(f"Error al descargar {filename}")
        return

    # Save downloaded file
    with open(os.path.join(folder, f"{filename}{extension}"), "w") as f:
        logging.info(f"Downloaded {filename}, saving to file")
        f.write(response.text)
