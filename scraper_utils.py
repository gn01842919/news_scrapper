"""
Common utilities used by other modules.

Attributes:
    log_format (str): default log format.

"""
import logging
import re

DEFAULT_LOG_FORMAT = '[%(levelname)s] [%(asctime)s] %(message)s\n'


def log_warning(msg, is_error=False):
    """Log warnings or errors.

    Args:
        msg (str): Error message to log.
        is_error (bool, optional): True to log as an error, and
            False (default) to log as a warning.

    Raises:
        NewsScrapperError: If a logger with name 'error_log' has not been set up.

    """
    if 'error_log' not in logging.Logger.manager.loggerDict:
        raise NewsScrapperError("Please set up 'error_log' logger first.")

    if is_error:
        logging.getLogger('error_log').error(msg)

    else:
        logging.getLogger('error_log').warning(msg)


def setup_logger(
        name,
        level=logging.INFO,
        logfile=None,
        to_console=True,
        log_format=DEFAULT_LOG_FORMAT):
    """Set up ``logging.logger``

    Args:
        name (str): Name of the logger to set up.

        level (int, optional): Default to logging.DEBUG.

        logfile (str, optional): Filename of the error log file.
            If specified, the error message will be written to the file.
            Defaults to None.

        to_console (bool, optional): Whether to log message to standard output.
            Defaults to True.

        log_format (str, optional): The log format. Default to ``DEFAULT_LOG_FORMAT``.

    Returns:
        logging.Logger: The logger object.

    """
    formatter = logging.Formatter(log_format)
    logger = logging.getLogger(name)

    logger.setLevel(level)

    if logfile:
        file_handler = logging.FileHandler(logfile)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    if to_console:
        console = logging.StreamHandler()
        console.setFormatter(formatter)
        logger.addHandler(console)

    return logger


def extract_domain_name_from_url(link):
    """Extract the domain name from a url.

    Args:
        link (str): A url.

    Returns:
        str: The domain name in the url.

    """
    base_url_pattern = re.compile('^https?://([a-zA-Z0-9.-]+)/')
    try:
        return base_url_pattern.match(link).group(1).lstrip('www.')
    except AttributeError:
        log_warning(
            'News link [%s] does not match base_url_pattern.' % link
        )


def read_json_from_file(filename):
    """Read data in JSON format from file.

    If the file does not exist yet, create an empty one, and return an empty dict.

    Args:
        filename (str): Name of the input file to read.

    Returns:
        dict: A JSON (dict) object.
    """
    import json

    try:
        with open(filename, 'r') as infile:
            return json.loads(infile.read())

    except FileNotFoundError:
        log_warning("File '%s' not found." % filename)
        return {}

    except json.decoder.JSONDecodeError:
        msg = "Fail to parse the content of file '%s' as JSON. " % filename
        log_warning(msg)
        return {}


class NewsScrapperError(RuntimeError):
    """Basic Error for the ``news_scraper`` project.

    Error messages are logged to ``logging.getLogger('error_log')``
        with the ``logging.error()`` method.

    If the logger is not set, write msg to both stdout and a file named 'error.log'.

    Attributes:
        logger (logging.Logger): The logger named 'error_log'.

    Args:
        msg (str): Error message to log.

    """
    logger = None

    def __init__(self, msg):
        cls = self.__class__
        if not cls.logger:
            cls.setup_error_logger()

        cls.logger.error(msg)

        super().__init__(msg)

    @classmethod
    def setup_error_logger(cls):
        """Set up logger for error log

        If a logger with name 'error_log' does not exist yet, set it up.

        """
        if 'error_log' in logging.Logger.manager.loggerDict:
            # The logger of name 'error_log' has been setup maybe by other modules.
            # Use the already existing one.
            cls.logger = logging.getLogger('error_log')
        else:
            cls.logger = setup_logger(
                'error_log', level=logging.WARNING, logfile='error.log', to_console=True
            )
