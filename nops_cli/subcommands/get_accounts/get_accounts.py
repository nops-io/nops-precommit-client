"""
Module to manage nops accounts
"""
from nops_sdk.api import APIClient


class Accounts:
    def __init__(self):
        self.api_client = APIClient()

    def get_accounts(self):
        """
        List all the available accounts
        """
        account_list = self.api_client.get_accounts()
        print("Accounts List: ")
        for account in account_list:
            # account_id, name, _ = self.api_client.get_accounts()
            print(f"Account id : {account.id}")
            print(f"Name : {account.name}")
            # print(f"Hi {self.name}")
