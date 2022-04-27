"""
Module to manage nops accounts
"""
from nops_sdk.api import APIClient
from nops_cli.utils.logger_util import logger

class NOpsAPIClient:
    """
    Manage nOps accounts
    """
    def __init__(self):
        self.api_client = APIClient()

    def get_accounts_ids(self):
        """
        List all the available accounts
        """
        account_list = self.api_client.get_accounts()
        account_ids = []
        for account in account_list:
            # account_id, name, _ = self.api_client.get_accounts()
            account_ids.append(account.id)
            # print(f"Hi {self.name}")
        logger.debug(f"Account Ids: {account_ids}")
        return account_ids
