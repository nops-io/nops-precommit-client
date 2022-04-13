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

#from nops_cli.subcommands.get_accounts.get_accounts import Accounts


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
                print(f"SDK Payload: {sdk_payload}")
                if sdk_payload:
                    # out = compute_terraform_cost_change(aws_region, periodicity, sdk_payload)
                    # print(out)
                    sdk_output = tmp_process_output(sdk_payload)
                    sdk_output = json.dumps(sdk_output, indent=4)
                    print(sdk_output)
                else:
                    print(f"No change found in terraform project: {tf_dir_paths}")
            if dependency:
                tf_dependency = TerraformDependency(tf_dir_path)
                sdk_payload = tf_dependency.get_plan_delta()
                print(f"SDK Payload: {sdk_payload}")
                if sdk_payload:
                    print(sdk_output)
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


def tmp_process_output(sdk_payload):
    """
    Temporary function to simulate nops SDK/API response
    """
    output = {}
    total_cost = 0
    created_resources_cost = {}
    updated_resources_cost = {}
    output["created_resources_cost"] = created_resources_cost
    output["updated_resources_cost"] = updated_resources_cost
    for resource in sdk_payload:
        resource_type = resource["resource_type"]
        operation_type = resource["operation_type"]
        if operation_type == "create":
            total_cost = get_resource_cost(resource_type, created_resources_cost, total_cost)
        elif operation_type == "update":
            total_cost = get_resource_cost(resource_type, created_resources_cost, total_cost)
        output["total_cost"] = total_cost
        output["unit"] = "hourly"
    return output


if __name__ == '__main__':
    main()
