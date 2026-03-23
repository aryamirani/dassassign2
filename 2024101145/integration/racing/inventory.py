class Car:
    def __init__(self, model, value):
        self.model = model
        self.value = value
        self.is_damaged = False

class InventoryModule:
    def __init__(self, initial_cash=10000):
        self.cash_balance = initial_cash
        self.cars = {}
        self.parts = []
        self.tools = []

    def add_car(self, model, value):
        if self.cash_balance < value:
            return False, "Insufficient funds"
        self.cash_balance -= value
        self.cars[model] = Car(model, value)
        return True, "Car added"

    def damage_car(self, model):
        if model in self.cars:
            self.cars[model].is_damaged = True
            return True, "Car damaged"
        return False, "Car not found"

    def repair_car(self, model, cost):
        if model in self.cars and self.cars[model].is_damaged:
            if self.cash_balance < cost:
                return False, "Insufficient funds"
            self.cash_balance -= cost
            self.cars[model].is_damaged = False
            return True, "Car repaired"
        return False, "Car does not need repair"

    def update_cash(self, amount):
        self.cash_balance += amount

    def remove_car(self, model):
        if model in self.cars:
            del self.cars[model]
            return True, "Car removed"
        return False, "Car not found"
