"""Module to handle logging functionality"""
import logging
import os
import sys


def get_logger(logger_name, file_name):
    """
    Return logger for nops-cli
    :param logger_name: Name for the logger
    :param file_name: File path to write the logs
    :param console_logs: Flag to enable logs on console
    :return: logger instance
    """
    loggers = logging.getLogger(logger_name)
    file_handler = logging.FileHandler(file_name)
    formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
    file_handler.setFormatter(formatter)
    # add file handler to loggers
    loggers.addHandler(file_handler)
    loggers.setLevel(os.environ.get('LOG_LEVEL', 'INFO'))
    console_logs = os.environ.get('CONSOLE_LOG', False)
    if console_logs:
        console_handle = logging.StreamHandler(sys.stdout)
        console_handle.setFormatter(formatter)
        loggers.addHandler(console_handle)
    return loggers


logger = get_logger("NOPS CLI Service Logger", "NOPSCLI.log")
