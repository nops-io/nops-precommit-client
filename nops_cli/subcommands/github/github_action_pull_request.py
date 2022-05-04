import requests
import json
from nops_cli.utils.logger_util import logger

class GithubPullRequestAction:
    def __init__(self, pr_number, token, repo_owner, repo_name):
        self.pull_request_number = pr_number
        self._git_token = token
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.total_cost_impact = 0

    def _get_project_total_cost_impact(self, cloud_cost):
        self.total_cost_impact = 0
        for op in cloud_cost.operation_group.operations:
            self.total_cost_impact += float(op.cost_effect)
        return self.total_cost_impact

    def _create_cloud_cost_payload(self, projects_pricing):
        payload = []
        for project_pricing in projects_pricing:
            total_cost_impact = self._get_project_total_cost_impact(project_pricing.cloud_cost)
            project_dir = project_pricing.project_dir
            payload.append(f"Total cost impact for project {project_dir} is {total_cost_impact}")
        payload = " \n".join(payload)
        print("Cost Impact for all projects")
        print(payload)
        return payload

    def get_headers(self, token):
        headers = {}
        headers["Authorization"] = "token {}".format(token)
        headers["Content-Type"] = "application/json"
        return headers

    def add_cloud_cost_impact_on_pr(self, projects_pricing):
        url = f"https://api.github.com/repos/{self.repo_owner}/" \
              f"{self.repo_name}/issues/{self.pull_request_number}/comments"
        #"https://api.github.com/repos/yograjopcito/github-action-test/issues/1/comments"
        headers = self.get_headers(self._git_token)
        message = self._create_cloud_cost_payload(projects_pricing)
        payload = json.dumps({"body": message})
        pr_response = requests.request("POST", url, headers=headers, data=payload)
        if pr_response.status_code > 199 and pr_response.status_code < 300:
            logger.error("Successfully added comment to PR for cloud cost impact")
        else:
            raise RuntimeError(
                "Error while updating CI status %s. Status Code: %s. Error Message: %s"
                % (self.pull_request_number, pr_response.status_code, pr_response.text))