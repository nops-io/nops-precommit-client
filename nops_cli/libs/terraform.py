"""
Library to interact with terraform CLI
"""
import string
import random
from os import remove, path
from json import loads, JSONDecodeError
from nops_cli.utils.execute_command import execute
from nops_cli.utils.logger_util import logger


class Terraform:
    """
    Manage terraform CLI interactions
    """
    def __init__(self, tf_dir, **kwargs):
        self.tf_dir = tf_dir
        self.tf_vars = kwargs.get("tf_vars")
        self.tf_var_file = kwargs.get("tf_var_file")

    def _generate_terrform_binary(self, binary_name=None):
        """
        Create terraform plan binary
        :param binary_name: (Optional) Name for output binary
        :return: Terraform binary name
        """
        if not binary_name:
            binary_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
            binary_name = f"{binary_name}.out"
        execute(f"terraform plan -out={binary_name}", self.tf_dir)
        return binary_name

    def terraform_plan(self):
        """
        Get terraform plan output in JSON format for terraform project
        """
        binary_name = self._generate_terrform_binary()
        binary_file_path = f"{self.tf_dir}/{binary_name}"
        binary_exists = path.isfile(binary_file_path)
        if binary_exists:
            json_out = {}
            try:
                logger.debug("Binary exists for terraform plan. Now processing output.")
                output = execute(f"terraform show -json {binary_name}", self.tf_dir)
                json_out = loads(output)
                remove(binary_file_path)
            except JSONDecodeError as je:
                logger.error(f"Error while converting terraform output to JSON. Error: {je}")
            except OSError as oe:
                logger.error(f"Error while removing temporary binary file {binary_file_path}. "
                             f"Error: {oe}")
            except Exception as e:
                logger.error(f"Error while reading temporary binary file {binary_file_path}. "
                             f"Error: {e}")
            return json_out
        logger.debug(f"No change found in terraform project {self.tf_dir}")
        return {}
