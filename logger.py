import os
import logging
import __main__

os.makedirs("./logs", exist_ok=True)


log_path = os.path.join(
    os.path.dirname(__main__.__file__),
    "logs",
    os.path.basename(__main__.__file__).split(".")[0],
)

logging.basicConfig(
    filename=f"{log_path}.log",
    filemode="a",
    format="%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
    level=logging.DEBUG,
)
