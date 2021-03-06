"""
Module to get and process the terraform outputs/states for nops dependency API's
"""
import json
import sys

from nops_cli.utils.logger_util import logger
from nops_cli.libs.terraform import Terraform
from nops_cli.libs.get_accounts import NOpsAPIClient
from nops_sdk.account.account import Account

class TerraformDependency(Terraform):
    """
    Terraform Dependencies
    """
    def __init__(self, tf_dir, **kwargs):
        Terraform.__init__(self, tf_dir, **kwargs)
        self.account_dep = None

    def _process_terraform_output(self, plan_out):
        """
        Process terraform output to create payload for nops dependency API
        :param plan_out: Terraform plan output in JSON format
        :return: processed_output can be used to create payload for nops dependency API
        """
        processed_output = []
        for resource_change in plan_out["resource_changes"]:

            resource_id = None
            change_type = resource_change["change"]["actions"]
            if "no-op" in change_type:
                continue
            if "update" in change_type:
                resource_id = resource_change["change"]["after"]["id"]
            if "delete" in change_type:
                resource_id = resource_change["change"]["before"]["id"]
            if resource_id:
                processed_output.append(resource_id)
        return processed_output


    def _get_plan_delta(self):
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


    def display_dependencies(self):
        """
        Get and display dependencies info for terraform project
        """
        try:
            resource_ids = self._get_plan_delta()
            self._set_nOps_account_for_dependency()
            account_id = self._get_nOps_cloud_account_id()
            if account_id:
                if resource_ids:
                    sdk_payload = {}
                    sdk_payload["aws_account_number"] = account_id
                    sdk_payload["resource_ids"] = resource_ids
                    output = self._get_resources_dependencies(resource_ids)
                    # output = self.tmp_process_output()
                    print("Dependencies:")
                    print(json.dumps(output, indent=4))
                else:
                    print(f"No change found for dependencies in terraform project: {self.tf_dir}")
        except Exception as e:
            logger.error(f"Error while processing terraform project {self.tf_dir} for dependencies"
                         f". Error: {e}")


    def _get_nOps_cloud_account_id(self):
        """
        Get nOps cloud account ID
        """
        account = NOpsAPIClient()
        accound_id = None
        try:
            accound_ids = account.get_accounts_ids()
            if not accound_ids:
                logger.error("nOps Cloud account is not available")
            else:
                accound_id = accound_ids[0]
        except Exception as e:
            logger.error(f"Error while getting nOps cloud accounts. Error: {e}")
        return accound_id


    def _set_nOps_account_for_dependency(self):
        """
        Set nOps account for cloud resource dependencies
        """
        account_id = self._get_nOps_cloud_account_id()
        if account_id:
            self.account_dep = Account(account_id)
        else:
            sys.exit("nOps Cloud account is not available")


    def _get_resources_dependencies(self, resource_ids):
        """
        Get resource dependencies for resource ids
        """
        resources_dependencies = []
        for resource_id in resource_ids:
            resource_dependency = self.account_dep.get_related_resources(resource_id)
            resources_dependencies.append(resource_dependency.__dict__)
        return resources_dependencies


    def tmp_process_output(self):
        """
        Temporary function to simulate nops SDK/API response
        """
        output = [
            {
                "resource_type": "vpc",
                "resource_id": "vpc_121312123",
                "related_resources": [
                    "sg_121312123",
                    "ec2_121312123"
                ]
            },
            {
                "resource_type": "vpc",
                "resource_id": "vpc_242425252",
                "related_resources": [
                    "sg_898989898",
                    "vpc_898989898",
                    "ebs_898989898",
                    "subnet_1231231"
                ]
            }
        ]
        return output
