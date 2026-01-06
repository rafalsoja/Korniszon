import logging
import os

os.makedirs("/app/data/logs", exist_ok=True)

logging.basicConfig(
    filename="/app/data/logs/app.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)


def get_logger(name: str):
    return logging.getLogger(name)
