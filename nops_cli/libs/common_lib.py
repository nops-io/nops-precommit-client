import os
import sys
from pathlib import Path
from nops_cli.constants.resource_mapping import TERRAFORM_RESOURCE_MAPPING
from nops_cli.utils.logger_util import logger

def get_terraform_resource_alias(resource_type):
    """
    Get the generic alias for terraform resource name(To make resource name consistent
    across the different IAC)
    :param resource_type: Terraform resource name
    :return: Generic resource name
    """
    if resource_type in TERRAFORM_RESOURCE_MAPPING:
        return TERRAFORM_RESOURCE_MAPPING[resource_type]
    return resource_type

def check_and_get_terraform_project(filenames):
    """
    Check if the input file is valid terraform plan/project and return terraform project path
    """
    valid_project_dir_paths = []
    invalid_project_dir_paths = []
    for path in filenames:
        if os.path.exists(path):
            if os.path.isfile(path):
                if path.endswith(".tf"):
                    valid_project_dir_paths.append("/".join(path.split("/")[:-1]))
                    continue
            else:
                if any(File.endswith(".tf") for File in os.listdir(path)):
                    valid_project_dir_paths.append(path)
                    continue
        logger.debug(f"Input file path {path} is not a valid file or directory")
        invalid_project_dir_paths.append(check_and_get_invalid_path(path))
    return valid_project_dir_paths, invalid_project_dir_paths


def check_and_get_invalid_path(path):
    if path.endswith(".tf"):
        path = "/".join(path.split("/")[:-1])
    return path

def get_indentation(line):
    """
    Get the indentation for a line
    """
    return len(line) - len(line.lstrip())


def check_if_file_is_available(file_path):
    """
    Check if file is available on file_path
    """
    path = Path(file_path)
    return path.is_file()


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.
    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).
    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")