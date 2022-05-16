import os
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
            if os.path.isfile(path) :
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
