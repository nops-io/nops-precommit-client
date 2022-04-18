"""
Module to get and process the terraform outputs/states for nops pricing API's
"""

from nops_sdk.pricing.pricing import compute_terraform_cost_change

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


    def _get_plan_delta(self):
        """
        Get "terraform plan" output in JSON format for pricing
        """
        processed_output = None
        logger.debug("Get terraform plan output")
        output = self.terraform_plan()
        logger.debug(f"Terraform plan output: {output}")
        # Process output to identify resource ids,type and delta from terraform plan output
        logger.debug("Process terraform plan output")
        if output:
            processed_output = self._process_terraform_output(output)
            logger.debug(f"Processed terraform plan output {processed_output}")
        return processed_output

    def display_pricing(self, periodicity):
        """
        Get and display pricing info for terraform project
        """
        try:
            sdk_payload = self._get_plan_delta()
            aws_region = get_aws_region()
            if sdk_payload:
                out = compute_terraform_cost_change(aws_region, periodicity, sdk_payload)
                print(f"{periodicity.capitalize()} cost impact for terraform project:"
                      f" {self.tf_dir}")
                for op in out:
                    print(op.report)
            else:
                print(f"No change found pricing in terraform project: {self.tf_dir}")
        except Exception as e:
            logger.error(f"Error while processing terraform project {self.tf_dir} for pricing."
                         f" Error: {e}")
