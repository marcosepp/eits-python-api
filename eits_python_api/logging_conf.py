import logging


def setup_logger(name: str = __name__) -> logging.Logger:
    """Setup INFO logging to stdout and DEBUG logging to "debug.log" file."""
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    log_format_info = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(message)s"
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(log_format_info)
    stream_handler.setLevel(logging.INFO)
    logger.addHandler(stream_handler)

    file_handler = logging.FileHandler(filename="debug.log", mode="w")
    file_handler.setFormatter(log_format_info)
    file_handler.setLevel(logging.DEBUG)
    logger.addHandler(file_handler)

    return logger


LOGGER = setup_logger(__name__)
