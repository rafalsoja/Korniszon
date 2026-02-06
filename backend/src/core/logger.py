import logging
import sys

import colorlog


def setup_logging():
    formatter = colorlog.ColoredFormatter(
        fmt="%(log_color)s%(levelname)s%(reset)s:     %(cyan)s%(name)s%(reset)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)

    return root_logger
