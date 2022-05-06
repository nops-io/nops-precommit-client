from enum import Enum

class Periodicity(str, Enum):
    HOURLY = "hourly"
    DAILY = "daily"
    MONTHLY = "monthly"
    YEARLY = "yearly"


class IacTypes(str, Enum):
    TERRAFORM = "terraform"
