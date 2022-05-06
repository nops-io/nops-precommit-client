"""
Module to get and process the terraform outputs/states for nops pricing API's
"""
from nops_cli.utils.logger_util import logger
from nops_cli.subcommands.pricing.terraform_pricing import TerraformPricing
from nops_cli.constants.input_enums import Periodicity, IacTypes

class Pricing():
    """
    nOps Pricing
    """
    def __init__(self, project_dir, periodicity=Periodicity.MONTHLY, iac_type=IacTypes.TERRAFORM,
                 **kwargs):
        self.project_dir = project_dir
        self.periodicity = periodicity
        self.iac_type = iac_type

    def display_pricing(self):
        if IacTypes.TERRAFORM:
            tf_pricing = TerraformPricing(self.project_dir)
            tf_pricing.display_pricing(self.periodicity)
        else:
            logger.error(f"IAC type {self.iac_type} not supported")
