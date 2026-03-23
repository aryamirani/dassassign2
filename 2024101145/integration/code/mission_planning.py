class MissionPlanningModule:
    def __init__(self, registration_module, inventory_module):
        self.registration = registration_module
        self.inventory = inventory_module
        self.missions = {}

    def assign_mission(self, mission_id, crew_names, car_model):
        if not car_model in self.inventory.cars:
            return False, "Car not in inventory"

        # Check for mechanic if car is damaged
        if self.inventory.cars[car_model].is_damaged:
            mechanic_present = any(self.registration.get_member(name).role == "mechanic" for name in crew_names if self.registration.get_member(name))
            if not mechanic_present:
                return False, "Damaged car requires a mechanic for mission"

        # Verify all crew members are registered
        for name in crew_names:
            if not self.registration.get_member(name):
                return False, f"Crew member {name} not registered"

        self.missions[mission_id] = {"crew": crew_names, "car": car_model}
        return True, "Mission assigned"
