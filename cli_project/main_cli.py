import argparse
from utils.logger_util import logger
from subcommands.pricing.terraform_pricing import TerraformPricing



def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--tf_dir', help='hi')
    parser.add_argument('--pricing', default=False, action="store_true",
                              help='Please enter firstname')
    parser.add_argument('--dependency', default=False, action="store_true",
                              help='Please enter lastname')
    parser.add_argument('--iac_type', default="terraform", choices=["terraform"],
                        help='Please enter lastname')
    args = parser.parse_args()

    pricing = args.pricing
    dependency = args.dependency
    iac_type = args.iac_type
    tf_dir = args.tf_dir

    if pricing:
        if iac_type == "terraform":
            tf_pricing = TerraformPricing(tf_dir)
            delta = tf_pricing.get_plan_delta()
            logger.info(f"Result: {delta}")
    if dependency:
        pass


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
