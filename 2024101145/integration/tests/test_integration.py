import pytest
from integration.code.registration import RegistrationModule
from integration.code.crew_management import CrewManagementModule
from integration.code.inventory import InventoryModule
from integration.code.race_management import RaceManagementModule
from integration.code.results import ResultsModule
from integration.code.mission_planning import MissionPlanningModule

@pytest.fixture
def system():
    reg = RegistrationModule()
    crew = CrewManagementModule(reg)
    inv = InventoryModule(initial_cash=5000)
    race = RaceManagementModule(reg, inv)
    results = ResultsModule(inv)
    mission = MissionPlanningModule(reg, inv)
    return reg, crew, inv, race, results, mission

def test_full_race_flow(system):
    reg, crew, inv, race, results, _ = system
    
    # 1. Register driver
    reg.register_member("Dom", "driver")
    
    # 2. Buy car
    inv.add_car("Charger", 2000)
    assert inv.cash_balance == 3000
    
    # 3. Create race
    success, msg = race.create_race("R1", "Dom", "Charger")
    assert success is True
    
    # 4. Result and Prize Money
    results.record_result("Dom", 1, 1000)
    assert inv.cash_balance == 4000
    assert results.get_rank("Dom") == 9

def test_mission_mechanic_requirement(system):
    reg, crew, inv, _, _, mission = system
    
    reg.register_member("Brian", "driver")
    inv.add_car("Supra", 1000)
    inv.damage_car("Supra")
    
    # Attempt mission without mechanic
    success, msg = mission.assign_mission("M1", ["Brian"], "Supra")
    assert success is False
    assert "mechanic" in msg
    
    # Add mechanic and retry
    reg.register_member("Tej", "mechanic")
    success, msg = mission.assign_mission("M2", ["Brian", "Tej"], "Supra")
    assert success is True

def test_invalid_driver_race(system):
    reg, _, inv, race, _, _ = system
    reg.register_member("Mia", "strategist")
    inv.add_car("Skyline", 1500)
    
    # Strategist cannot drive in a race
    success, msg = race.create_race("R2", "Mia", "Skyline")
    assert success is False
    assert "invalid role" in msg.lower()

def test_insufficient_funds_car(system):
    _, _, inv, _, _, _ = system
    success, msg = inv.add_car("ExpensiveCar", 10000) # Only 5000 in system
    assert success is False
    assert "Insufficient funds" in msg
