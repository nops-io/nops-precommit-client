import json
import argparse
from nops_cli.utils.logger_util import logger
from nops_cli.subcommands.pricing.terraform_pricing import TerraformPricing
from nops_cli.subcommands.hello_world.hello_world import HelloWorld
#from nops_cli.subcommands.get_accounts.get_accounts import Accounts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tf_dir', help="Terraform directory path")
    parser.add_argument('--hello_world', help="Hello World")
    parser.add_argument('--get_accounts', help="Hello World", action="store_true")
    parser.add_argument('--pricing', default=False, action="store_true",
                        help="Enable Pricing Projection")
    parser.add_argument('--dependency', default=False, action="store_true",
                        help="Enable Dependency module")
    parser.add_argument('--iac-type', default="terraform", choices=["terraform"],
                        help="IAC type")
    parser.add_argument("filenames", nargs="*")

    args = parser.parse_args()

    pricing = args.pricing
    dependency = args.dependency
    iac_type = args.iac_type
    hello_world = args.hello_world
    get_accounts = args.get_accounts
    tf_dir = args.tf_dir

    if pricing:
        if iac_type == "terraform":
            tf_pricing = TerraformPricing(tf_dir)
            sdk_payload = tf_pricing.get_plan_delta()
            print(f"SDK Payload: {sdk_payload}")
            # sdk_output = tmp_process_output(sdk_payload)
            # sdk_output = json.dumps(sdk_output, indent=4)
            # print(sdk_output)
    if hello_world:
        hello_world_obj = HelloWorld(hello_world)
        hello_world_obj.say_hi()
    #if get_accounts:
    #    accounts = Accounts()
    #    accounts.get_accounts()

def tmp_process_output(sdk_payload):
    output = {}
    total_cost = 0
    created_resources = sdk_payload["create"]
    updated_resources = sdk_payload["update"]
    created_resources_cost = {}
    updated_resources_cost = {}
    output["created_resources_cost"] = created_resources_cost
    output["updated_resources_cost"] = updated_resources_cost
    for resource in created_resources:
        resource_type = resource["resource_type"]
        if resource_type not in created_resources_cost:
            created_resources_cost[resource_type] = {}
            created_resources_cost[resource_type]["cost"] = 0
            created_resources_cost[resource_type]["count"] = 0
        created_resources_cost[resource_type]["cost"] += 4
        total_cost += 4
        created_resources_cost[resource_type]["count"] += 1
    for resource in updated_resources:
        resource_type = resource["resource_type"]
        id = resource["id"]
        if resource_type not in updated_resources_cost:
            updated_resources_cost[resource_type] = {}
            updated_resources_cost[resource_type]["cost"] = 0
            updated_resources_cost[resource_type]["count"] = 0
            updated_resources_cost[resource_type]["ids"] = []
        updated_resources_cost[resource_type]["cost"] += 2
        total_cost += 2
        updated_resources_cost[resource_type]["count"] += 1
        updated_resources_cost[resource_type]["ids"].append(id)
    output["total_cost"] = total_cost
    output["unit"] = "hourly"
    return output




if __name__ == '__main__':
    main()











"""


WELCOME TO  CLI 
    PLEASE SELECT ONE OF THE BELOW OPTION TO CONTINUE
    1.HELLO WORLD  2.FILE HANDLING)

    # parser = argparse.ArgumentParser()
    # parser.add_argument('option', help='Please select one of above option')
    # args = parser.parse_args()
"""
