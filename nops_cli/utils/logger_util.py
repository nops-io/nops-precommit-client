"""Module to handle logging functionality"""
import logging
import os
import sys


def get_logger(logger_name, file_name, console_logs=False):
    """
    Return logger for nops-cli
    :param logger_name: Name for the logger
    :param file_name: File path to write the logs
    :param console_logs: Flag to enable logs on console
    :return: logger instance
    """
    logger = logging.getLogger(logger_name)
    file_handler = logging.FileHandler(file_name)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)
    # add file handler to logger
    logger.addHandler(file_handler)
    logger.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))
    if console_logs:
        console_handle = logging.StreamHandler(sys.stdout)
        console_handle.setFormatter(formatter)
        logger.addHandler(console_handle)
    return logger


logger = get_logger("NOPS CLI Service Logger", "NOPSCLI.log", True)

