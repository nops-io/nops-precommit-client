import argparse
from nops_cli.utils.logger_util import logger
from nops_cli.subcommands.pricing.terraform_pricing import TerraformPricing
from nops_cli.subcommands.hello_world.hello_world import HelloWorld


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tf_dir', help="Terraform directory path")
    parser.add_argument('--hello-world', help="Hello World")
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
    tf_dir = args.tf_dir

    if pricing:
        if iac_type == "terraform":
            tf_pricing = TerraformPricing(tf_dir)
            delta = tf_pricing.get_plan_delta()
            logger.info(f"Result: {delta}")
    if hello_world:
        hello_world_obj = HelloWorld(hello_world)
        hello_world_obj.say_hi()


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
