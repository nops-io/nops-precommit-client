"""
Module to get and process the terraform outputs/states for nops pricing API's
"""

from nops_sdk.pricing import CloudCost
from nops_sdk.cloud_infrastructure.enums import AWSRegion
from nops_sdk.cloud_infrastructure.cloud_operation import Periodicity
from nops_cli.utils.logger_util import logger
from nops_cli.libs.terraform import Terraform
from nops_cli.libs.aws_lib import get_aws_region
from nops_cli.libs.common_lib import get_terraform_resource_alias

class TerraformPricing(Terraform):
    """
    Terraform Pricing
    """
    def __init__(self, tf_dir, **kwargs):
        Terraform.__init__(self, tf_dir, **kwargs)
        self.tf_spec = []
        self.aws_region = None
        self.cloud_cost = None


    def _process_terraform_output(self, plan_out):
        """
        Process terraform output to create payload for nops pricing API
        :param plan_out: Terraform plan output in JSON format
        :return: processed_output can be used as a payload for nops pricing API
        """
        processed_output = []
        for resource_change in plan_out.get("resource_changes", {}):
            resource_id = None
            resource_payload = {}
            resource_op = None
            change_type = resource_change["change"]["actions"]
            resource_type = resource_change["type"]
            if "no-op" in change_type:
                continue
            old_data = resource_change["change"]["before"]
            new_data = resource_change["change"]["after"]
            if "create" in change_type:
                resource_op = "create"
            if "update" in change_type:
                resource_op = "update"
                resource_id = resource_change["change"]["after"]["id"]
            if "delete" in change_type:
                resource_op = "delete"
                resource_payload = {}
                resource_id = resource_change["change"]["before"]["id"]
            resource_payload["id"] = resource_id
            resource_payload["resource_type"] = get_terraform_resource_alias(resource_type)
            resource_payload["operation_type"] = resource_op
            resource_payload["old_data"] = old_data
            resource_payload["new_data"] = new_data
            processed_output.append(resource_payload)
        return processed_output


    def _set_aws_region(self):
        """
        Set AWS region
        """
        self.aws_region = get_aws_region()


    def _set_tf_spec(self):
        """
        Get "terraform plan" output in JSON format for pricing
        """
        logger.debug("Get terraform plan output")
        output = self.terraform_plan()
        logger.debug(f"Terraform plan output: {output}")
        # Process output to identify resource ids,type and delta from terraform plan output
        logger.debug("Process terraform plan output")
        if output:
            self.tf_spec = self._process_terraform_output(output)
            logger.debug(f"Processed terraform plan output {self.tf_spec}")
        return

    def _set_cloud_cost(self, periodicity):
        try:
            self.cloud_cost = CloudCost(aws_region=AWSRegion(self.aws_region), spec=self.tf_spec)
            self.cloud_cost.load_prices()
            self.cloud_cost.compute_cost_effects(period=Periodicity(periodicity))
        except Exception as e:
            logger.error(f"Error while computing/loading the pricing for terraform project {self.tf_dir}."
                         f" Error: {e}")

    def _display_nops_pricing(self, periodicity):
        """
        Display pricing using nOps SDK
        """
        try:
            print(f"{periodicity.capitalize()} cost impact for terraform project:"
                  f" {self.tf_dir}")
            self._set_cloud_cost(periodicity)
            self.cloud_cost.output_report()
        except Exception as e:
            logger.error(f"Error while display the pricing for terraform project {self.tf_dir}."
                         f" Error: {e}")
        return


    def display_pricing(self, periodicity):
        """
        Get and display pricing info for terraform project
        """
        try:
            self._set_tf_spec()
            self._set_aws_region()
            if self.tf_spec:
                self._display_nops_pricing(periodicity)
            else:
                print(f"No change found pricing in terraform project: {self.tf_dir}")
        except Exception as e:
            logger.error(f"Error while processing terraform project {self.tf_dir} for pricing."
                         f" Error: {e}")
