"""
Library to execute the commands on local machine
"""
import subprocess
from nops_cli.utils.logger_util import logger


def execute(command, cwd=None):
    """
    Execute command on local machine
    :param command: Command to be executed
    :param cwd: Execute command inside cwd
    :return: command std output
    """
    try:
        logger.debug(f"Executing command: {command}")
        logger.debug(command)
        cmd_out = subprocess.run(command, stdout=subprocess.PIPE,  shell = True, text=True, check=True, cwd=cwd)
        output = cmd_out.stdout
        logger.debug(f"Executed command: {command}. Output: {output}")
        return output
    except Exception as e:
        logger.error(f"Failed while executing command. Command: {command}. Error: {str(e)}")
    return None
