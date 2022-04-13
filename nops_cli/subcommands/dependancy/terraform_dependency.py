"""
Module to get and process the terraform outputs/states for nops dependency API's
"""
from nops_cli.utils.logger_util import logger
from nops_cli.libs.terraform import Terraform
from nops_cli.constants.resource_mapping import TERRAFORM_RESOURCE_MAPPING


class TerraformDependency(Terraform):
    def __init__(self, tf_dir, **kwargs):
        Terraform.__init__(self, tf_dir, **kwargs)

    def _process_terraform_output(self, plan_out):
        """
        Process terraform output to create payload for nops dependency API
        :param plan_out: Terraform plan output in JSON format
        :return: processed_output can be used to create payload for nops dependency API
        """
        processed_output = []
        for resource_change in plan_out["resource_changes"]:

            id = None
            change_type = resource_change["change"]["actions"]
            if "no-op" in change_type:
                continue
            if "update" in change_type:
                id = resource_change["change"]["after"]["id"]
            if "delete" in change_type:
                id = resource_change["change"]["before"]["id"]
            if id:
                processed_output.append(id)
        return processed_output

    def get_terraform_resource_alias(self, resource_type):
        """
        Get the generic alias for terraform resource name(To make resource name consistent
        across the different IAC)
        :param resource_type: Terraform resource name
        :return: generic resource name
        """
        if resource_type in TERRAFORM_RESOURCE_MAPPING:
            return TERRAFORM_RESOURCE_MAPPING[resource_type]
        else:
            return resource_type

    def get_plan_delta(self):
        """
        Get "terraform plan" output in JSON format
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
