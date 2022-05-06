from nops_cli.constants.resource_mapping import TERRAFORM_RESOURCE_MAPPING

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