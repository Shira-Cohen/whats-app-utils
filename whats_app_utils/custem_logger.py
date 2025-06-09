import logging
import sys

from utils.settings import LOGLEVEL


class CustomFormatter(logging.Formatter):
    def format(self, record):
        # Time format: DD-MM-YY  T HH:MM:SS
        time = self.formatTime(record, "%d-%m-%y  T%H:%M:%S")
        level = record.levelname.ljust(7)  # Pad log level to align
        func_name = record.funcName  # Only function name
        msg = record.getMessage()
        return f"{time} {level} {func_name}: {msg}"


class CustomLogger:
    def __init__(self, log_file='app.log'):
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(LOGLEVEL)
        self.logger.propagate = False

        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(CustomFormatter())
        self.logger.addHandler(file_handler)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(CustomFormatter())
        self.logger.addHandler(console_handler)

        logging.getLogger('sqlalchemy').setLevel(logging.WARNING)
        logging.getLogger('sqlalchemy.pool').setLevel(logging.WARNING)

    def debug(self, msg, *args, extra=None, **kwargs):
        self.logger.debug(msg, *args, extra=extra, **kwargs, stacklevel=2)

    def info(self, msg, *args, extra=None, **kwargs):
        self.logger.info(msg, *args, extra=extra, **kwargs, stacklevel=2)

    def warning(self, msg, *args, extra=None, **kwargs):
        self.logger.warning(msg, *args, extra=extra, **kwargs, stacklevel=2)

    def exception(self, msg, *args, extra=None, **kwargs):
        self.logger.exception(msg, *args, extra=extra, **kwargs, stacklevel=2)

    def error(self, msg, *args, extra=None, **kwargs):
        self.logger.error(msg, *args, extra=extra, **kwargs, exc_info=True, stacklevel=2)


logger = CustomLogger()
