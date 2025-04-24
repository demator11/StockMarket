import logging


def setup_logging(name: str, level: int = logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)

    formatter = logging.Formatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s [%(module)s.%(funcName)s]"  # noqa
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler("py_log.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger
