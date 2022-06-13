from nops_cli.subcommands.pricing.pricing import Pricing

class CheckovPricing(Pricing):
    def __init__(self, conf):
        self.conf = conf
        project_path, periodicity, iac_type = self.get_pricing_params_from_conf()
        super().__init__(project_path, periodicity, iac_type)

    def _get_project_total_cost(self):
        self.display_pricing()
        total_cost_impact = self.get_project_total_cost_impact()
        return total_cost_impact

    def _check_cost_threshold(self, total_cost, operation, threshold):
        if operation == "less_than" and total_cost < threshold:
            return True
        if operation == "greater_than" and total_cost > threshold:
            return True
        return False

    def get_pricing_params_from_conf(self):
        project_path = self.conf.get("project_path")
        periodicity = self.conf.get("periodicity", "monthly")
        iac_type = self.conf.get("iac_type", "terraform")
        return project_path, periodicity, iac_type

    def check_project_cost(self):
        total_cost = self._get_project_total_cost()
        operation = self.conf.get("operation", "less_than")
        threshold = self.conf.get("threshold", 10)
        return self._check_cost_threshold(total_cost, operation, threshold)



