import os
import yaml
import math
import random
import string
import subprocess
from pathlib import Path
from nops_cli.utils.logger_util import logger
from nops_cli.libs.common_lib import get_indentation, check_if_file_is_available, query_yes_no
from nops_cli.constants.helm_recommendations_constants \
    import SEARCH_CONTAINER_STRING, SEARCH_RESOURCE_STRING, SEARCH_CONTAINER_NAME, PERIODICITY
from nops_cli.constants.helm_recommendations_constants import colors
from nops_sdk.k8s.pod_recommendations import K8SRecommendations


class Container:
    def __init__(self, helm_chart_dir, deployment_file, **kwargs):
        self.deployment_file = deployment_file
        self.helm_chart_dir = helm_chart_dir
        self.container_name = kwargs.get("container_name", None)
        self.resource_start_line = kwargs.get("resource_start_line", None)
        self.resource_end_line = kwargs.get("resource_end_line", None)
        self.resources_indent = kwargs.get("resource_end_line", None)
        self.indent = kwargs.get("indent", 2)

    def get_container_name(self, name):
        """
        Get indirect container name eg. if container name is in form {{ .Chart.Name }}
        """
        parsed_name = name.strip()
        if parsed_name.startswith("{{") and parsed_name.endswith("}}"):
            parsed_name = parsed_name[2:-2].strip()
            values_file_name = parsed_name.split('.')[1]
            value_hierarchy = parsed_name.split('.')[2:]
            values_file = f"{self.helm_chart_dir}/{values_file_name}.yaml"
            values_file_name_small_case = values_file_name.lower()
            values_file_name_camel_case = ''.join([values_file_name_small_case[0].lower(),
                                                   values_file_name_small_case[1:]])
            is_file_available = False
            if check_if_file_is_available(values_file):
                is_file_available = True
            elif check_if_file_is_available(values_file_name_small_case):
                is_file_available = True
                values_file = values_file_name_small_case
            elif check_if_file_is_available(values_file_name_camel_case):
                is_file_available = True
                values_file = values_file_name_small_case

            if is_file_available:
                values_file_data = {}
                with open(values_file, "r") as val_file:
                    try:
                        values_file_data = yaml.safe_load(val_file)
                    except yaml.YAMLError as exc:
                        logger.error(f"Error while reading file {values_file}. Error: {exc}")
                if values_file_data:
                    value_dict = values_file_data
                    for key in value_hierarchy:
                        camel_case_key = ''.join([key[0].upper(), key[1:]])
                        small_case_key = key.lower()
                        if key in value_dict:
                            value_dict = value_dict[key]
                        elif camel_case_key in value_dict:
                            value_dict = value_dict[camel_case_key]
                        elif small_case_key in value_dict:
                            value_dict = value_dict[small_case_key]
                        else:
                            return name
                    else:
                        return value_dict
        return name

    def set_container_name(self, name):
        """
        Get indirect container name eg. if container name is in form {{ .Chart.Name }}
        """
        self.container_name = self.get_container_name(name)
        return

    def write_recommendations(self, recommendation):
        """
        Write the recommendations in helm YAML file
        """
        self.refresh_container()
        yml_recommendation = self.__get_yml_recommendation(recommendation)
        contents = ""
        with open(self.deployment_file, "r") as deployment_file:
            contents = deployment_file.readlines()
        contents = self.__add_recommendations(yml_recommendation, contents)
        with open(self.deployment_file, "w") as deployment_file:
            deployment_file.write(contents)

    def refresh_container(self):
        """
        Get all the containers and resources information from the deplyment file
        """
        containers_indent = 0
        search_resource = False
        container_name = ""
        self.deployment_file
        try:
            with open(self.deployment_file, 'r') as fp:
                lines = fp.readlines()
                for line_no, row in enumerate(lines):
                    indent = get_indentation(row)
                    if search_resource and indent <= containers_indent:
                        break
                    if not search_resource:
                        if row.find(SEARCH_CONTAINER_STRING) != -1:
                            logger.info(f"Refresh container {self.container_name}")
                            containers_word = row.split(':')[0].strip()
                            if containers_word == 'containers':
                                search_resource = True
                                containers_indent = indent
                    if search_resource:
                        if row.find(SEARCH_CONTAINER_NAME) != -1:
                            name_indent = indent
                            if name_indent == containers_indent + self.indent:
                                name = row.split(':')[-1].strip()
                                container_name = name
                        if row.find(SEARCH_RESOURCE_STRING) != -1:
                            resources = row.split(':')[0].strip()
                            if resources == 'resources':
                                current_line_no = line_no + 1
                                parsed_container_name = self.get_container_name(container_name)
                                if self.container_name == parsed_container_name:
                                    if self.resource_start_line != current_line_no:
                                        logger.info(f"Refreshing Start Line from "
                                                    f"{self.resource_start_line} to "
                                                    f"{current_line_no} for container "
                                                    f"{self.container_name}")
                                        self.resource_start_line = current_line_no
                                        self.resources_indent = indent
                                for resource_row_no, resource_row in enumerate(
                                        lines[current_line_no:]):
                                    resource_row_indent = get_indentation(resource_row)
                                    if resource_row_indent <= indent:
                                        end_line_no = line_no + resource_row_no + 1
                                        if self.resource_end_line != end_line_no:
                                            logger.info(f"Refreshing Start Line from "
                                                        f"{self.resource_start_line} to "
                                                        f"{current_line_no} for container "
                                                        f"{self.container_name}")
                                        break
        except Exception as e:
            logger.error(f"Error while refreshing container {self.container_name} for helm chart "
                         f"{self.helm_chart_dir}. Error: {e}")

    def __get_yml_recommendation(self, recommendation):
        """
        Get recommendations in YAML format.
        """
        yml_indent = self.resources_indent + 2
        recommendation = yaml.dump(recommendation)
        yml_recommendation = []
        for line in recommendation.split('\n')[:-1]:
            yml_recommendation.append(f"{' ' * yml_indent}{line}")
        yml_recommendation = "\n".join(yml_recommendation)
        yml_recommendation = f"{' ' * self.resources_indent}resources:\n{yml_recommendation}\n"
        return yml_recommendation

    def __add_recommendations(self, yml_recommendation, file_contents):
        """
        Add our recommendations in helm YAML content
        """
        start_index_no = self.resource_start_line - 1
        end_index_no = self.resource_end_line

        file_contents[start_index_no] = yml_recommendation
        if start_index_no < end_index_no:
            del file_contents[start_index_no + 1:end_index_no]
        file_contents = "".join(file_contents)
        return file_contents


class HelmRecommendations:
    def __init__(self, helm_chart_dir, cluster_id, periodicity, auto_approve_helm_recommendations,
                 yml_indent=2):
        self.helm_chart_dir = os.path.abspath(helm_chart_dir)
        self.containers = []
        self.yml_indent = yml_indent
        self.deployment_yamls = []
        self.cluster_id = cluster_id
        self.periodicity = periodicity
        self.recommendations_applied = False
        self.auto_approve_helm_recommendations = auto_approve_helm_recommendations

    def __set_deployment_yamls(self):
        """
        Get YAML's with kind deployment from helm chart
        """
        result = list(Path(self.helm_chart_dir).rglob("*.[yT][aX][mT][lT]"))
        for file in result:
            with open(file, 'r') as fp:
                lines = fp.readlines()
                for row in lines:
                    word = 'kind'
                    if row.find(word) == 0:
                        kind = row.split(':')[-1].strip()
                        if kind == 'Deployment':
                            logger.debug(f'Got deployment config in file {file}')
                            self.deployment_yamls.append(file)
                            break
        logger.info(f"Deployment files {self.deployment_yamls}")
        return self.deployment_yamls

    def set_containers(self):
        """
        Get all the containers and resources information from the deplyment file
        """
        self.__set_deployment_yamls()
        containers_indent = 0
        search_resource = False
        container_name = ""
        try:
            for deploymentfile in self.deployment_yamls:
                with open(deploymentfile, 'r') as fp:
                    lines = fp.readlines()
                    for line_no, row in enumerate(lines):
                        indent = get_indentation(row)
                        if search_resource and indent <= containers_indent:
                            break
                        if not search_resource:
                            if row.find(SEARCH_CONTAINER_STRING) != -1:
                                logger.info("Got containers")
                                containers_word = row.split(':')[0].strip()
                                if containers_word == 'containers':
                                    search_resource = True
                                    containers_indent = indent
                        if search_resource:
                            if row.find(SEARCH_CONTAINER_NAME) != -1:
                                name_indent = indent
                                if name_indent == containers_indent + self.yml_indent:
                                    name = row.split(':')[-1].strip()
                                    container_name = name
                            if row.find(SEARCH_RESOURCE_STRING) != -1:
                                resources = row.split(':')[0].strip()
                                if resources == 'resources':
                                    current_line_no = line_no + 1
                                    container = Container(self.helm_chart_dir, deploymentfile)
                                    container.set_container_name(container_name)
                                    container.resource_start_line = current_line_no
                                    container.resources_indent = indent
                                    self.containers.append(container)
                                    logger.info(f"Found container with name "
                                                f"{container.container_name}")
                                    for resource_row_no, resource_row in enumerate(
                                            lines[current_line_no:]):
                                        resource_row_indent = get_indentation(resource_row)
                                        if resource_row_indent <= indent:
                                            container.resource_end_line = line_no + resource_row_no + 1
                                            logger.debug(
                                                f"Resources block starts at line "
                                                f"{container.resource_start_line} and ends at line "
                                                f"{container.resource_end_line} for container "
                                                f"{container.container_name}")
                                            break
        except Exception as e:
            logger.error(f"Error while setting containers for helm chart {self.helm_chart_dir}"
                         f". Error: {e}")

    def get_container_by_name(self, name):
        """
        Get container object by its name
        """
        for container in self.containers:
            if container.container_name == name:
                return container
        return

    def get_periodicity(self):
        """
        Get recommendation periodicity
        """
        return PERIODICITY[self.periodicity]

    def get_int_recommendation(self, k8s_recommendations, recommendation_key):
        """
        Get recommendation in integer format
        """
        recommendation = k8s_recommendations.get(recommendation_key, None)
        if recommendation:
            try:
                recommendation = math.ceil(recommendation)
            except Exception as e:
                logger.error(f"Error while converting the recommendation {recommendation_key} to "
                             f"int. Error {e}")
        return recommendation

    def convert_byte_to_mb(self, ram_in_bytes):
        """
        Convert bytes into Mega Bytes
        """
        try:
            ram_in_mb = math.ceil(ram_in_bytes / 1024.0 ** 2)
        except Exception as e:
            logger.error(f"Error while converting the RAM from bytes to MB. Error {e}")
        return ram_in_mb

    def print_resource_recommendation(self, recommendations):
        """
        Print container resources recommendations
        """
        recommendation_key_list = ["limits", "requests"]
        for recommendation_key in recommendation_key_list:
            recommendation = recommendations.get(recommendation_key, None)
            if recommendation:
                memory = recommendation.get("memory", None)
                cpu = recommendation.get("cpu", None)
                self.print_recommndation("".join([recommendation_key[0].upper(),
                                                  recommendation_key[1:]]))
                if memory:
                    self.print_recommndation(f"\tMemory: {memory}")
                if cpu:
                    self.print_recommndation(f"\tCPU: {cpu}")



    def print_recommndation(self, message, error=False):
        """
        Print recommendations
        """
        if error:
            print(f"{colors.RED}{message}{colors.ENDC}")
        else:
            print(f"{colors.GREEN}{message}{colors.ENDC}")


    def apply_containers_recommendations(self):
        """
        Apply nOps recommendations for available containers
        """
        try:
            for container in self.containers:
                pod_base_name = container.container_name
                recommendations = K8SRecommendations(self.cluster_id)
                k8s_recommendations = recommendations.by_pod(base_name=pod_base_name,
                                                             period=self.get_periodicity())
                if k8s_recommendations:
                    self.print_recommndation(f"Based on analysis of your usage, nOps "
                                             f"recommends following configurations for container"
                                             f" {pod_base_name} resources")
                    # logger.info(f"Applying recommendations for the container {pod_base_name}")
                else:
                    self.print_recommndation(f"No recommendation available from nOps for container"
                                             f" {pod_base_name}")
                for recommendation in k8s_recommendations:
                    nops_recommendation = {}
                    recommended_ram_limit = self.get_int_recommendation(recommendation,
                                                                        "recommended_ram_limit")
                    recommended_cpu_limit = self.get_int_recommendation(recommendation,
                                                                        "recommended_cpu_limit")
                    recommended_ram_request = self.get_int_recommendation(recommendation,
                                                                          "recommended_ram_request")
                    recommended_cpu_request = self.get_int_recommendation(recommendation,
                                                                          "recommended_cpu_request")

                    nops_recommendation_limits = {}
                    nops_recommendation_requests = {}
                    if recommended_ram_limit:
                        recommended_ram_limit = self.convert_byte_to_mb(recommended_ram_limit)
                        nops_recommendation_limits["memory"] = f"{recommended_ram_limit}Mi"
                    if recommended_cpu_limit:
                        nops_recommendation_limits["cpu"] = recommended_cpu_limit
                    if recommended_ram_request:
                        recommended_ram_request = self.convert_byte_to_mb(recommended_ram_request)
                        nops_recommendation_requests["memory"] = f"{recommended_ram_request}Mi"
                    if recommended_cpu_request:
                        nops_recommendation_requests["cpu"] = recommended_cpu_request

                    if nops_recommendation_limits:
                        nops_recommendation["limits"] = nops_recommendation_limits
                    if nops_recommendation_requests:
                        nops_recommendation["requests"] = nops_recommendation_requests
                    if nops_recommendation:
                        self.print_resource_recommendation(nops_recommendation)
                        apply_recommendations = True
                        if not self.auto_approve_helm_recommendations:
                            apply_recommendations = query_yes_no(
                                f"Do you want to add the above recommendations in your helm chart "
                                f"{self.helm_chart_dir}?")
                        if apply_recommendations:
                            container.write_recommendations(nops_recommendation)
                            self.recommendations_applied = True
                            self.print_recommndation(
                                f"Applied nOps recommendations for container {pod_base_name} in "
                                f"file {container.deployment_file}")
                        else:
                            self.print_recommndation("You opted to skip the recommendations", True)
                    else:
                        self.print_recommndation(f"No recommendation available for container "
                                                 f"{pod_base_name} resources")
        except Exception as e:
            logger.error(f"Error while applying recommendations. Error: {e}")

    def execute_git_command(self, command):
        """
        Execute git commands
        """
        try:
            logger.debug(f"Executing command: {command}")
            logger.debug(command)
            cmd_out = subprocess.run(command, stdout=subprocess.PIPE, shell=True, text=True,
                                     check=True, cwd=self.helm_chart_dir)
            output = cmd_out.stdout
            logger.debug(f"Executed command: {command}. Output: {output}")
            return output
        except Exception as e:
            raise Exception(f"Failed while executing command. Command: {command}. Error: {str(e)}")

    def commit_changes_and_create_pr(self):
        """
        Commit Recommendations and create Pull Request for recommended changes
        """
        try:
            if self.recommendations_applied:
                commit_recommendations = True
                if not self.auto_approve_helm_recommendations:
                    commit_recommendations = query_yes_no(
                        f"Do you want to commit the recommendations in git for your helm chart"
                        f" {self.helm_chart_dir}?")
                if commit_recommendations:
                    branch_name = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
                    branch_name = f"nOps-recommendations-{branch_name}"
                    for deployment_file in self.deployment_yamls:
                        self.execute_git_command(f"git add {deployment_file}")
                    self.execute_git_command(f"git checkout -b {branch_name}")
                    self.execute_git_command("git commit -m 'Added nOps recommendations'")
                    # self.execute_git_command(f"git push --set-upstream origin {branch_name}"
                    #                          f" -o merge_request.create")
                    self.print_recommndation(
                        f"Recommendation applied and created Merge Request using branch "
                        f"{branch_name} for helm chart {self.helm_chart_dir}")
                else:
                    self.print_recommndation("You opted to skip the recommendations for git", True)
            else:
                self.print_recommndation(f"No recommendantion applied yet for helm chart "
                                         f"{self.helm_chart_dir}")
        except Exception as e:
            logger.error(f"Error while commit the changes to repository. Error: {e}")
