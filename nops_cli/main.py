"""
Usage:
Use this script to get the pricing and dependencies details for your terraform projects
python3 main.py  --tf_dir /Users/user/terraform_project_dir --pricing --iac-type terraform
python3 main.py  --tf_dir /Users/user/terraform_project_dir --dependency --iac-type terraform
"""
import json
import os
import argparse
import sys

from nops_cli.subcommands.pricing.terraform_pricing import TerraformPricing
from nops_cli.subcommands.dependancy.terraform_dependency import TerraformDependency
from nops_sdk.pricing.pricing import compute_terraform_cost_change
from nops_cli.subcommands.get_accounts.get_accounts import Accounts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pricing', default=False, action="store_true",
                        help="Enable Pricing Projection")
    parser.add_argument('--dependency', default=False, action="store_true",
                        help="Enable Dependency module")
    parser.add_argument('--iac-type', default="terraform", choices=["terraform"],
                        help="IAC type")
    parser.add_argument('--periodicity', default="hourly",
                        choices=["hourly", "daily", "monthly", "yearly"],
                        help="Select periodicity for pricing")
    parser.add_argument("filenames", nargs="*", help="Terraform plans/hcl files")

    args = parser.parse_args()

    pricing = args.pricing
    dependency = args.dependency
    iac_type = args.iac_type
    periodicity = args.periodicity
    filenames = args.filenames
    print(f"Terraform plans {filenames}")
    tf_dir_paths = []
    for file in filenames:
        tf_dir_paths.append("/".join(file.split("/")[:-1]))
    print(f"Terraform projects {tf_dir_paths}")
    aws_region = get_aws_region()
    if iac_type == "terraform":
        for tf_dir_path in tf_dir_paths:
            if pricing:
                tf_pricing = TerraformPricing(tf_dir_path)
                sdk_payload = tf_pricing.get_plan_delta()
                # print(f"SDK Payload: {sdk_payload}")
                if sdk_payload:
                    out = compute_terraform_cost_change(aws_region, periodicity, sdk_payload)
                    for op in out:
                        print(op.report)
                else:
                    print(f"No change found in terraform project: {tf_dir_paths}")
            if dependency:
                tf_dependency = TerraformDependency(tf_dir_path)
                resource_ids = tf_dependency.get_plan_delta()
                accound_ids = get_account_ids()
                if accound_ids:
                    if resource_ids:
                        sdk_payload = {}
                        sdk_payload["aws_account_number"] = accound_ids[0]
                        sdk_payload["resource_ids"] = resource_ids
                        # print(f"SDK Payload: {resource_ids}")
                        output = tmp_process_output()
                        print(output)
                    else:
                        print(f"No resource id found in terraform project: {tf_dir_paths}")


def get_aws_region():
    """
    Get AWS region
    """
    aws_region = os.environ.get('AWS_REGION')
    if aws_region:
        print(f"Current AWS region is {aws_region}")
        return aws_region
    else:
        sys.exit("Please set AWS_REGION in env")


def get_resource_cost(resource_type, operation_payload, total_cost):
    """
    Temporary function to simulate pricing computation
    """
    if resource_type not in operation_payload:
        operation_payload[resource_type] = {}
        operation_payload[resource_type]["cost"] = 0
        operation_payload[resource_type]["count"] = 0
    operation_payload[resource_type]["cost"] += 4
    total_cost += 4
    operation_payload[resource_type]["count"] += 1
    return total_cost

def get_account_ids():
    """
    Select nops accound id
    """
    account = Accounts()
    account_ids = account.get_accounts_ids()
    return account_ids

def tmp_process_output():
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



if __name__ == '__main__':
    main()
