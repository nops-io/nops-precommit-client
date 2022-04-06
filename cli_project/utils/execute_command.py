import subprocess
from utils.logger_util import logger


def execute(command, cwd=None):
    try:
        logger.debug(f"Executing command: {command}")
        logger.debug(command)
        cmd_out = subprocess.run(command, stdout=subprocess.PIPE,  shell = True, text=True, check=True, cwd=cwd)
        output = cmd_out.stdout
        logger.debug(f"Executed command: {command}. Output: {output}")
        return output
    except Exception as e:
        logger.error(f"Failed while executing command. Error: {str(e)}")
    return None
