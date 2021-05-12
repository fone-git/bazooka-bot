import logging
import sys

_logger = logging.getLogger()


def log(msg, log_level=logging.INFO):
    global _logger
    _logger.log(log_level, msg)


def setup_logging(log_level=logging.INFO):
    global _logger

    if _logger.hasHandlers():
        log('\n<<<<<<<<<<<<<<<<<<< CLOSING HANDLERS >>>>>>>>>>>>>>>>>>')
        handlers = _logger.handlers[:]  # Copy handlers list
        for handler in handlers:  # Iterate over copy to close and remove
            handler.close()
            _logger.removeHandler(handler)

    # Set up standard output
    std_stream_handler = logging.StreamHandler(sys.stdout)
    std_stream_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    std_stream_handler.setLevel(logging.DEBUG)
    _logger.addHandler(std_stream_handler)

    # Set up error output
    err_stream_handler = logging.StreamHandler(sys.stderr)
    err_stream_handler.setFormatter(
        logging.Formatter('%(asctime)s %(levelname)s: %(message)s'))
    err_stream_handler.setLevel(logging.ERROR)
    _logger.addHandler(err_stream_handler)

    # Set default log level accepted
    _logger.setLevel(log_level)
