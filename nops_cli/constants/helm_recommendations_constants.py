from nops_sdk.k8s.pod_recommendations import K8SPeriodicity

SEARCH_CONTAINER_STRING = 'containers:'
SEARCH_RESOURCE_STRING = 'resources:'
SEARCH_CONTAINER_NAME = 'name:'

PERIODICITY = {
    "TWENTY_FOUR_HOURS": K8SPeriodicity.THIRTY_DAYS,
    "SEVEN_DAYS": K8SPeriodicity.THIRTY_DAYS,
    "THIRTY_DAYS": K8SPeriodicity.THIRTY_DAYS
}

class colors:
    RED = '\33[31m'
    GREEN = '\33[32m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
