from jsondiff import diff
from nops_cli.utils.logger_util import logger
from nops_cli.libs.terraform import Terraform
from nops_cli.constants.resource_mapping import TERRAFORM_RESOURCE_MAPPING

class TerraformPricing(Terraform):
    def __init__(self, tf_dir, **kwargs):
        Terraform.__init__(self, tf_dir, **kwargs)

    def _process_terraform_output(self, plan_out):
        processed_output = []
        for resource_change in plan_out["resource_changes"]:
            id = None
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
                id = resource_change["change"]["after"]["id"]
            if "delete" in change_type:
                resource_op = "delete"
                resource_payload = {}
                id = resource_change["change"]["before"]["id"]
            resource_payload["id"] = id
            resource_payload["resource_type"] = self.get_terraform_resource_alias(resource_type)
            resource_payload["operation_type"] = resource_op
            resource_payload["old_data"] = old_data
            resource_payload["new_data"] = new_data
            processed_output.append(resource_payload)
        return processed_output

    def get_terraform_resource_alias(self, resource_type):
        if resource_type in TERRAFORM_RESOURCE_MAPPING:
            return TERRAFORM_RESOURCE_MAPPING[resource_type]
        else:
            return resource_type

    def get_plan_delta(self):
        logger.debug("Get terraform plan output")
        output = self.terraform_plan()
        logger.debug(f"Terraform plan output: {output}")
        # Process output to identify resource ids,type and delta from terraform plan output
        logger.debug("Process terraform plan output")
        processed_output = self._process_terraform_output(output)
        logger.debug(f"Processed terraform plan output {processed_output}")
        return processed_output

    def get_nops_pricing(self):
        # TODO: Update the computed delta using nops SDK and return result to CLI
        pass

