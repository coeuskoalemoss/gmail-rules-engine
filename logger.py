import logging
import os


class LoggerInstance:
    def __init__(
        self,
        name,
        log_folder=None,
        log_file="app.log",
        console_level=logging.DEBUG,
        file_level=logging.DEBUG,
    ):
        """
        Initializes the logger with a given name, log folder/file, and log levels.

        :param name: Name of the logger, usually __name__
        :param log_folder: Folder where log files will be stored
        :param log_file: Log file name (default: app.log)
        :param console_level: Logging level for console (default: DEBUG)
        :param file_level: Logging level for file (default: DEBUG)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Capture all logs

        if not self.logger.hasHandlers():  # Prevent duplicate handlers
            self._add_console_handler(console_level)

            # Combine folder and file to get full path
            if log_folder:
                os.makedirs(log_folder, exist_ok=True)
                log_path = os.path.join(log_folder, log_file)
            else:
                log_path = log_file

            self._add_file_handler(log_path, file_level)

    def _add_console_handler(self, level):
        """Adds a console handler to the logger."""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        console_formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] %(message)s"
        )
        console_handler.setFormatter(console_formatter)
        self.logger.addHandler(console_handler)

    def _add_file_handler(self, log_file, level):
        """Adds a file handler to the logger."""
        file_handler = logging.FileHandler(log_file, mode="a")
        file_handler.setLevel(level)
        file_formatter = logging.Formatter(
            "[%(asctime)s] [%(name)s] [%(levelname)s] - %(message)s"
        )
        file_handler.setFormatter(file_formatter)
        self.logger.addHandler(file_handler)

    def get_logger(self):
        """Returns the configured logger."""
        return self.logger
