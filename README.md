# nOps pre-commit hooks
To use nOps hook with pre-commit, we need to use [.pre-commit-config.yaml](.pre-commit-config.yaml) file in your repo.

It will run pricing and resource dependency pre commit hooks when you make terraform code changes and commit them.
It will ignore non-terraform code changes. nops pre-commit hooks will be skipped in this case.


# nOps CLI
nOps CLI can be independently installed and executed.

## How to install

## How to run
```CLI Help
terminal#nops-cli  --help                                                                                              
usage: nops-cli [-h] [--pricing] [--dependency] [--iac-type {terraform}] [--periodicity {hourly,daily,monthly,yearly}] [filenames ...]
positional arguments:
  filenames             Terraform plans/hcl files
optional arguments:
  -h, --help            show this help message and exit
  --pricing             Enable Pricing Projection
  --dependency          Enable Dependency module
  --iac-type {terraform}
                        IAC type
  --periodicity {hourly,daily,monthly,yearly}
                        Select periodicity for pricing
terminal#
```