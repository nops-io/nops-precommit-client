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
        self.cloud_cost = None

    def display_pricing(self):
        if IacTypes.TERRAFORM:
            tf_pricing = TerraformPricing(self.project_dir)
            tf_pricing.display_pricing(self.periodicity)
            self.cloud_cost = tf_pricing.cloud_cost
        else:
            logger.error(f"IAC type {self.iac_type} not supported")

    def get_project_total_cost_impact(self):
        """
        Compute total cloud cost impact for base branch out JSON
        """
        logger.debug("Get total cost impact")
        total_cost_impact = 0
        for op in self.cloud_cost.operation_group.operations:
            total_cost_impact += float(op.cost_effect)
        return total_cost_impact

