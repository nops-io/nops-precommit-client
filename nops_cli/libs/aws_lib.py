import os
import sys
from nops_cli.utils.logger_util import logger

def get_aws_region():
    """
    Get AWS region
    """
    aws_region = os.environ.get('AWS_REGION')
    if aws_region:
        logger.debug(f"Current AWS region is {aws_region}")
        return aws_region
    else:
        sys.exit("Please set AWS_REGION in env")
