class BettingModule:
    """Extra module 1: Tracks street betting on races."""
    def __init__(self, inventory):
        self.inventory = inventory
        self.bets = {}

    def place_bet(self, race_id, amount, driver_name):
        if self.inventory.cash_balance < amount:
            return False, "Insufficient funds"
        self.inventory.update_cash(-amount)
        self.bets[race_id] = (amount, driver_name)
        return True, "Bet placed"

    def calculate_payout(self, race_id, winner_name):
        if race_id in self.bets:
            amount, driver_name = self.bets.pop(race_id)
            if driver_name == winner_name:
                payout = amount * 2
                self.inventory.update_cash(payout)
                return True, f"Won bet! Payout: {payout}"
        return False, "Bet lost or not found"

class ReputationModule:
    """Extra module 2: Tracks crew overall reputation levels."""
    def __init__(self, registration):
        self.registration = registration
        self.reputation = {}

    def update_reputation(self, driver_name, points):
        if self.registration.get_member(driver_name):
            self.reputation[driver_name] = self.reputation.get(driver_name, 0) + points
            return True, "Reputation updated"
        return False, "Member not found"

    def get_reputation(self, driver_name):
        return self.reputation.get(driver_name, 0)
