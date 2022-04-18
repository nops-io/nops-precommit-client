"""
Usage:
Use this script to get the pricing and dependencies details for your terraform projects
python3 main.py  <tf_file1>.tf <tf_file2>.tf --pricing --iac-type terraform
python3 main.py  <tf_file1>.tf <<tf_file2>.tf --dependency --iac-type terraform
python3 main.py  <tf_file1>.tf <tf_file2>.tf --pricing --dependency --iac-type terraform
"""
import argparse
from nops_cli.subcommands.pricing.pricing import Pricing
from nops_cli.subcommands.dependancy.dependency import Dependency
from nops_cli.constants.input_enums import Periodicity, IacTypes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pricing', default=False, action="store_true",
                        help="Enable Pricing Projection")
    parser.add_argument('--dependency', default=False, action="store_true",
                        help="Enable Dependency module")
    parser.add_argument('--iac-type', default="terraform", choices=[IacTypes.TERRAFORM],
                        help="IAC type")
    parser.add_argument('--periodicity', default=Periodicity.MONTHLY,
                        choices=[Periodicity.HOURLY, Periodicity.DAILY,
                                 Periodicity.MONTHLY, Periodicity.YEARLY],
                        help="Select periodicity for pricing")
    parser.add_argument("filenames", nargs="*", help="Space separated terraform plans(.tf) files")

    args = parser.parse_args()

    pricing = args.pricing
    dependency = args.dependency
    iac_type = args.iac_type
    periodicity = args.periodicity
    filenames = args.filenames
    print(f"Terraform plans {filenames}")
    project_dir_paths = []
    for file in filenames:
        project_dir_paths.append("/".join(file.split("/")[:-1]))
    print(f"Terraform projects {project_dir_paths}")
    for project_dir_path in project_dir_paths:
        if pricing:
            pricing = Pricing(project_dir_path, periodicity=periodicity, iac_type=iac_type)
            pricing.display_pricing()
        if dependency:
            dependency = Dependency(project_dir_path, periodicity=periodicity, iac_type=iac_type)
            dependency.display_dependency()

if __name__ == '__main__':
    main()
