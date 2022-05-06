"""
Module to get and process the terraform outputs/states for nops pricing API's
"""
from nops_cli.utils.logger_util import logger
from nops_cli.subcommands.dependancy.terraform_dependency import TerraformDependency
from nops_cli.constants.input_enums import Periodicity, IacTypes

class Dependency():
    """
    nOps Pricing
    """
    def __init__(self, project_dir, periodicity=Periodicity.MONTHLY, iac_type=IacTypes.TERRAFORM,
                 **kwargs):
        self.project_dir = project_dir
        self.periodicity = periodicity
        self.iac_type = iac_type

    def display_dependency(self):
        if IacTypes.TERRAFORM:
            tf_dependency = TerraformDependency(self.project_dir)
            tf_dependency.display_dependencies()
        else:
            logger.error(f"IAC type {self.iac_type} not supported")
