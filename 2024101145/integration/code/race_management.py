class RaceManagementModule:
    def __init__(self, registration, inventory):
        self.registration = registration
        self.inventory = inventory
        self.active_races = {}

    def create_race(self, race_id, driver_name, car_model):
        member = self.registration.get_member(driver_name)
        if not member or member.role != "driver":
            return False, "Driver not registered or invalid role"
        
        car = self.inventory.cars.get(car_model)
        if not car:
            return False, "Car not in inventory"
        if car.is_damaged:
            return False, "Car is damaged"
        
        self.active_races[race_id] = {"driver": driver_name, "car": car_model}
        return True, "Race created"
