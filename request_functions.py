import os
import sys
import json
import grequests
import logger
import logging


def await_all(urls, callback, concurrency=10, method="get", show_progress=None):
    # Setting all requests
    rs = (
        getattr(grequests, method)(
            url["url"],
            headers=url.get("headers", {}),
            data=url.get("body", None),
        )
        for url in urls
    )

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
    filename = url["name"].replace("/", "@")
    folder = folder or "./"
    # Create folder if not found
    os.makedirs(folder, exist_ok=True)

    # If download failed
    if not response.ok:
        logging.error(f"{response.status_code} Error al descargar {filename}")
        return

    if response.text == "":
        logging.error(f"Skipping {filename}, not found")
        return

    # Save downloaded file
    with open(
        os.path.join(folder, f"{filename}{extension}"), "w", encoding="utf-8"
    ) as f:
        logging.info(f"Downloaded {filename}, saving to file")
        f.write(response.text)


def download_metadata(
    items,
    url,
    out_folder,
    file_ext,
    concurrency=10,
    headers={},
    proxies={},
    method="get",
    body_getter=lambda x: "",
    query_params=lambda x: "",
):
    get_item_url = lambda item: dict(
        name=item,
        url=url.replace("{{slug}}", item) + query_params(item),
        headers=headers,
        proxies=proxies,
        body=json.dumps(body_getter(item)),
    )

    get_item_file_path = lambda item: os.path.join(
        out_folder, f"{item.replace('/', '@')}{file_ext}"
    )

    urls = [
        get_item_url(item)
        for item in items
        # Getting not downloaded list
        if not os.path.exists(get_item_file_path(item))
    ]

    logging.info(f"Found {len(urls)} to download. Total: {len(items)}")

    progress_handler = handle_progress(len(items), default=len(items) - len(urls))
    callback = lambda url, response: save_response_to_folder(
        url=url,
        response=response,
        folder=out_folder,
        extension=file_ext,
    )

    await_all(
        urls=urls,
        callback=callback,
        show_progress=lambda index: progress_handler.__next__(),
        method=method,
        concurrency=concurrency,
    )
