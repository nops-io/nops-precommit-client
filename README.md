# nOps pre-commit hooks
To use nOps hook with pre-commit, we need to use [.pre-commit-config.yaml](.pre-commit-config.yaml) file in your repo.

It will run pricing and resource dependency pre commit hooks when you make terraform code changes and commit them.
It will ignore non-terraform code changes. nops pre-commit hooks will be skipped in this case.


# nOps CLI
nOps CLI can be independently installed and executed.

## How to install
1. Clone repo [https://github.com/nops-io/nops-precommit-client.git](https://github.com/nops-io/nops-precommit-client.git)
2. Checkout to git directory
3. Run: (Use python3.9)
`pip install .`

It will install nops-cli and dependencies.


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

# nOps Github Action
nOps Github Action will help you to get the estimated cost impact for your IAC(currently we are 
supporting terraform only) projects impacted by Github pull request code changes. It will run cloud
pricing checks when you make the pull request code changes for your IAC projects configured as a 
part of nOps-action.yml.
<img src=".github/images/Action-Result.png" alt="nOps Github Action Result" />

# How to use
To use nOps Github action: 
1. Create a **.github/workflows** directory in your repository on GitHub if this directory does not already exist.
```shell
cd ${GITHUB_REPOSITORY}
mkdir -p .github/workflows
```
3. In the .github/workflows directory, create a file named nOps-action.yml. 
4. Copy the **[nOps-action.yml](nOps-action.yml)** YAML contents into the nOps-action.yml file. 
5. Configure the list of terraform project as a space separated values in yml for TERRAFORM_PROJECT. 
6. Add following required secrets in github. [Please refer to add Github secrets](https://docs.github.com/en/actions/security-guides/encrypted-secrets)
     - **ACCESS_TOKEN_GITHUB** - Your personal github action token. nOps action will use this token to add the comment on you Pull Request.
     - **NOPS_API_KEY** - Your nOps account API key .
     - **NOPS_AWS_ACCESS_KEY** - Any valid AWS_ACCESS_KEY. This key is required for terraform.
     - **NOPS_AWS_SECRET_KEY** - Any valid AWS_SECRET_ACCESS_KEY.  This key is required for terraform.
     - **NOPS_AWS_REGION** - AWS region. This region is required for terraform and nOps sdk.
7. We are ready to create/update the pull requests and Github will trigger the nOps action for it 
 once we complete above steps.
<img src=".github/images/Action-Execution.png" alt="nOps Github Action Execution" />
