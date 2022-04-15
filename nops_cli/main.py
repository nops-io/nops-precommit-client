"""
Usage:
Use this script to get the pricing and dependencies details for your terraform projects
python3 main.py  --tf_dir /Users/user/terraform_project_dir --pricing --iac-type terraform
python3 main.py  --tf_dir /Users/user/terraform_project_dir --dependency --iac-type terraform
"""
import argparse
from nops_cli.subcommands.pricing.terraform_pricing import TerraformPricing
from nops_cli.subcommands.dependancy.terraform_dependency import TerraformDependency


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
    if iac_type == "terraform":
        for tf_dir_path in tf_dir_paths:
            if pricing:
                tf_pricing = TerraformPricing(tf_dir_path)
                tf_pricing.display_pricing(periodicity)
            if dependency:
                tf_dependency = TerraformDependency(tf_dir_path)
                tf_dependency.display_dependencies()

if __name__ == '__main__':
    main()
