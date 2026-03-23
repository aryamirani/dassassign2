class ResultsModule:
    def __init__(self, inventory):
        self.inventory = inventory
        self.rankings = {}

    def record_result(self, driver_name, position, prize_money):
        self.rankings[driver_name] = self.rankings.get(driver_name, 0) + (10 - position)
        self.inventory.update_cash(prize_money)
        return True, "Result recorded"

    def get_rank(self, driver_name):
        return self.rankings.get(driver_name, 0)
