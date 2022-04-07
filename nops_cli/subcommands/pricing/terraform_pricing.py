from jsondiff import diff
from nops_cli.utils.logger_util import logger
from nops_cli.libs.terraform import Terraform


class TerraformPricing(Terraform):
    def __init__(self, tf_dir, **kwargs):
        Terraform.__init__(self, tf_dir, **kwargs)

    def _process_terraform_output(self, plan_out):
        processed_output = {}
        processed_output["create"] = []
        processed_output["update"] = []
        processed_output["delete"] = []
        for resource_change in plan_out["resource_changes"]:
            id = None
            delta = {}

            change_type = resource_change["change"]["actions"]
            resource_type = resource_change["type"]
            if "no-op" in change_type:
                continue
            if "create" in change_type:
                resource_payload = {}
                delta = resource_change["change"]["after"]
                resource_payload["changes"] = delta
                resource_payload["resource_type"] = resource_type
                processed_output["create"].append(resource_payload)
            if "update" in change_type:
                resource_payload = {}
                id = resource_change["change"]["after"]["id"]
                old_data = resource_change["change"]["before"]
                new_data = resource_change["change"]["after"]
                delta = diff(old_data, new_data)
                resource_payload["id"] = id
                resource_payload["changes"] = delta
                resource_payload["resource_type"] = resource_type
                processed_output["update"].append(resource_payload)
            if "delete" in change_type:
                resource_payload = {}
                id = resource_change["change"]["before"]["id"]
                resource_payload["id"] = id
                resource_payload["resource_type"] = resource_type
                processed_output["delete"].append(resource_payload)
        return processed_output

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

