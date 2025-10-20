
from configs.logging import configure_logging


def init_logging(settings) -> None:
    configure_logging(settings.LOG_LEVEL)


