import requests
import json
from nops_cli.utils.logger_util import logger

class GithubPullRequestAction:
    def __init__(self, pr_number, token, repo_name):
        self.pull_request_number = pr_number
        self._git_token = token
        self.repo_name = repo_name
        self.total_cost_impact = 0

    def _get_project_total_cost_impact(self, cloud_cost):
        """
        Compute total cloud cost impact for base branch out JSON
        """
        logger.debug("Get total cost impact")
        total_cost_impact = 0
        for op in cloud_cost.operation_group.operations:
            total_cost_impact += float(op.cost_effect)
        return total_cost_impact

    def _get_signed_number_string_for_markdown(self, number, diff=False):
        """
        Get string representation for signed integer/float cost/number
        """
        if number == "-":
            markdown_number = number
        else:
            number = float(f"{number:.2f}")
            if number < 0:
                number = abs(number)
                markdown_number = f"-${number}"
            else:
                if diff:
                    markdown_number = f"+${number}"
                else:
                    markdown_number = f"${number}"
        return markdown_number

    def _add_markdown_table_cloud_cost(self, table_markdown, project, previous_cloud_cost,
                                       current_cloud_cost, diff):
        """
        Add row in markdown table for github action comment
        """
        previous_cloud_cost = self._get_signed_number_string_for_markdown(previous_cloud_cost)
        current_cloud_cost = self._get_signed_number_string_for_markdown(current_cloud_cost)
        diff = self._get_signed_number_string_for_markdown(diff, True)
        table_markdown = f"{table_markdown} \n | {project} | {previous_cloud_cost} | " \
                         f"{current_cloud_cost} | {diff} |"
        logger.debug(f"Added row in markdown table with previous_cloud_cost: {previous_cloud_cost},"
                     f" current_cloud_cost: {current_cloud_cost} and diff: {diff}")
        return table_markdown

    def _compute_cloud_cost_impact_valid_projects(self, current_cloud_cost_json,
                                                  previous_cloud_cost_json, table_markdown):
        """
        Compute cloud cost impact for projects available in current source github branch
        """
        logger.debug("Compute cloud cost impact for valid projects")
        for project in current_cloud_cost_json:
            logger.debug(f"Computing cloud cost for project {project}")
            if project in previous_cloud_cost_json:
                current_cloud_cost = current_cloud_cost_json[project]["cost"]
                previous_cloud_cost_available = previous_cloud_cost_json[project]["present"]
                if previous_cloud_cost_available:
                    previous_cloud_cost = previous_cloud_cost_json[project]["cost"]
                    diff = current_cloud_cost - previous_cloud_cost
                    self.total_cost_impact += diff
                else:
                    previous_cloud_cost = "-"
                    diff = current_cloud_cost
                    self.total_cost_impact += diff
                table_markdown = self._add_markdown_table_cloud_cost(table_markdown, project,
                                                                     previous_cloud_cost,
                                                                     current_cloud_cost, diff)
        return table_markdown

    def _compute_cloud_cost_impact_invalid_projects(self, previous_cloud_cost_json,
                                                    invalid_project_dir_paths, table_markdown):
        """
        Compute cloud cost impact for projects those are not available in current source
        github branch
        """
        logger.debug("Compute cloud cost impact for invalid projects")
        for project in invalid_project_dir_paths:
            logger.debug(f"Computing cloud cost for project {project}")
            diff = 0
            current_cloud_cost = "-"
            previous_cloud_cost_available = previous_cloud_cost_json[project]["present"]
            if previous_cloud_cost_available:
                previous_cloud_cost = previous_cloud_cost_json[project]["cost"]
                diff = -previous_cloud_cost
                self.total_cost_impact -= previous_cloud_cost
            else:
                previous_cloud_cost = "-"
            table_markdown = self._add_markdown_table_cloud_cost(table_markdown, project,
                                                                 previous_cloud_cost,
                                                                 current_cloud_cost, diff)
        return table_markdown

    def _create_cloud_cost_payload(self, current_cloud_cost_json, previous_cloud_cost_json,
                                   invalid_project_dir_paths, periodicity):
        """
        Compute total cost impact for github action markdown payload
        """
        table_markdown = "| Project | Previous | New | Diff | \n |------|------|------|-------| "
        self.total_cost_impact = 0
        table_markdown = self._compute_cloud_cost_impact_valid_projects(
            current_cloud_cost_json, previous_cloud_cost_json, table_markdown
        )
        table_markdown = self._compute_cloud_cost_impact_invalid_projects(
            previous_cloud_cost_json, invalid_project_dir_paths, table_markdown
        )
        m_total_cost_impact = self._get_signed_number_string_for_markdown(self.total_cost_impact,
                                                                          True)
        logger.debug(f"Total cloud cost impact is {m_total_cost_impact}")
        markdown_message = f"Total estimated **{periodicity}** cost impact for your projects" \
                           f" is **{m_total_cost_impact}**"
        markdown_message = f"{markdown_message} \n {table_markdown}"
        return markdown_message

    def _get_cloud_cost_json(self, projects_pricing):
        """
        Get cloud cost JSON
        """
        logger.debug("Get cloud cost JSON")
        cloud_cost_json = {}
        for project_pricing in projects_pricing:
            logger.debug(f"Computing pricing for project {project_pricing.project_dir}")
            total_cost_impact = self._get_project_total_cost_impact(project_pricing.cloud_cost)
            project_dir = project_pricing.project_dir
            project_dir = self._get_relative_path_for_project(project_dir)
            cloud_cost_json[project_dir] = {
                "present": True,
                "cost": total_cost_impact
            }
        logger.debug(f"Cloud cost JSON: {cloud_cost_json}")
        return cloud_cost_json

    def get_headers(self, token):
        """
        Get headers for github API
        """
        headers = {}
        headers["Authorization"] = "token {}".format(token)
        headers["Content-Type"] = "application/json"
        return headers

    def _get_relative_path_for_project(self, project_path):
        """
        Get project path relative to github workspace
        """
        git_repo_name = self.repo_name.split("/")[1]
        relative_project_path = project_path.split(f"{git_repo_name}/")
        if len(relative_project_path) > 1:
            return f"{git_repo_name}/".join(relative_project_path[1:])
        return project_path

    def add_cloud_cost_impact_on_pr(self, projects_pricing, previous_cloud_cost_json_file,
                                    invalid_project_dir_paths, periodicity):
        """
        Add cloud cost impact on github pull request
        """
        logger.debug(f"Compute and add cloud cost on PR number {self.pull_request_number} for repo"
                     f" {self.repo_name}")
        try:
            url = f"https://api.github.com/repos/{self.repo_name}/" \
                  f"issues/{self.pull_request_number}/comments"
            print(f"URL: {url}")
            headers = self.get_headers(self._git_token)
            previous_cloud_cost = {}
            with open(previous_cloud_cost_json_file, "r") as pcf:
                previous_cloud_cost = json.load(pcf)
            logger.debug(f"Previous cloud cost JSON: {previous_cloud_cost}")
            current_cloud_cost_json = self._get_cloud_cost_json(projects_pricing)
            message = self._create_cloud_cost_payload(current_cloud_cost_json, previous_cloud_cost,
                                                      invalid_project_dir_paths, periodicity)
            payload = json.dumps({"body": message})
            logger.debug("Adding cloud cost impact on Pull Request")
            pr_response = requests.request("POST", url, headers=headers, data=payload)
            if pr_response.status_code > 199 and pr_response.status_code < 300:
                logger.debug("Successfully added comment to PR for cloud cost impact")
            else:
                raise RuntimeError(
                    "Error while updating CI status %s. Status Code: %s. Error Message: %s"
                    % (self.pull_request_number, pr_response.status_code, pr_response.text))
        except Exception as e:
            logger.error(f"Failed while adding comment on PR. Error: {e}")

    def get_cloud_cost_json(self, projects_pricing):
        try:
            return self._get_cloud_cost_json(projects_pricing)
        except Exception as e:
            logger.error(f"Error while generating cloud cost. Error: {e}")

    def create_cloud_cost_json_file(self, projects_pricing, json_out_file,
                                    invalid_project_dir_paths):
        """
        Create cloud cost JSON file. (This file we can use to compute the
        comparative cloud cost impact in later run)
        """
        try:
            cloud_cost_json = self._get_cloud_cost_json(projects_pricing)
            for invalid_project_dir_path in invalid_project_dir_paths:
                cloud_cost_json[invalid_project_dir_path] = {
                    "present": False,
                    "cost": 0
                }
            with open(json_out_file, "w") as jf:
                json.dump(cloud_cost_json, jf)
                logger.debug(f"Successfully created JSON output file {json_out_file} with "
                             f"content {cloud_cost_json}")
        except Exception as e:
            logger.error(f"Error while creating cloud cost JSON file {json_out_file}. Error: {e}")
