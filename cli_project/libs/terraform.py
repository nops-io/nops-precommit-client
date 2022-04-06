import json
import string
import random
from utils.execute_command import execute
from utils.logger_util import logger


class Terraform:
    def __init__(self, tf_dir, **kwargs):
        self.tf_dir = tf_dir
        self.tf_vars = kwargs.get("tf_vars")
        self.tf_var_file = kwargs.get("tf_var_file")

    def _generate_terrform_binary(self, binary_name=None):
        if not binary_name:
            binary_name = ''.join(random.choices(string.ascii_uppercase +
                                         string.digits, k=7))
            binary_name = f"{binary_name}.out"
        execute(f"terraform plan -out={binary_name}", self.tf_dir)
        return binary_name

    def terraform_plan(self):
        binary_name = self._generate_terrform_binary()
        output = execute(f"terraform show -json {binary_name}", self.tf_dir)
        json_out = {}
        try:
            json_out = json.loads(output)
        except Exception as e:
            logger.error(f"Error while converting terraform output to JSON")
        return json_out