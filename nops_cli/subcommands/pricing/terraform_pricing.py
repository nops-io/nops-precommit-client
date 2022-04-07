from jsondiff import diff
from nops_cli.utils.logger_util import logger
from nops_cli.libs.terraform import Terraform


class TerraformPricing(Terraform):
    def __init__(self, tf_dir, **kwargs):
        Terraform.__init__(self, tf_dir, **kwargs)

    def _process_terraform_output(self, plan_out):
        processed_output = {}
        for resource_change in plan_out["resource_changes"]:
            id = None
            delta = {}
            change_type = resource_change["change"]["actions"]
            if "no-op" in change_type:
                continue
            if "create" in change_type:
                delta = resource_change["change"]["after"]
            if "update" in change_type:
                old_data = resource_change["change"]["before"]
                new_data = resource_change["change"]["after"]
                delta = diff(old_data, new_data)
                id = resource_change["change"]["after"]["id"]
            if "delete" in change_type:
                id = resource_change["change"]["before"]["id"]
            resource_type = resource_change["type"]
            resource_data = {
                "id": id,
                "delta": delta,
                "change_type": change_type
            }

            if resource_type in processed_output:
                processed_output[resource_type].append(resource_data)
            else:
                processed_output[resource_type] = []
                processed_output[resource_type].append(resource_data)
        return processed_output

    def get_plan_delta(self):
        # TODO: Get resource ids,type and delta from terraform plan result
        logger.info("Get terraform plan output")
        output = self.terraform_plan()
        logger.debug(f"Terraform plan output: {output}")
        # Process output to identify resource ids,type and delta from terraform plan output
        logger.info("Process terraform plan output")
        processed_output = self._process_terraform_output(output)
        logger.debug(f"Processed terraform plan output {processed_output}")
        return processed_output

    def get_nops_pricing(self):
        # TODO: Update the computed delta using nops SDK and return result to CLI
        pass


