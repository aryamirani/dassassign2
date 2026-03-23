import pytest
from racing.registration import RegistrationModule
from racing.crew_management import CrewManagementModule
from racing.inventory import InventoryModule
from racing.race_management import RaceManagementModule
from racing.results import ResultsModule
from racing.mission_planning import MissionPlanningModule

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

def test_duplicate_registration_prevention(system):
    reg, _, _, _, _, _ = system
    reg.register_member("Deckard", "driver")
    success, msg = reg.register_member("Deckard", "driver") # Duplicate
    assert success is False
    assert "already registered" in msg.lower()

def test_car_destruction_flow(system):
    _, _, inv, _, _, _ = system
    inv.add_car("Rubicon", 2000)
    inv.remove_car("Rubicon")
    # Should not be able to use in mission
    assert "Rubicon" not in inv.cars

# --- 2. Mission & Requirements Tests ---

def test_mission_profit_and_inventory_interaction(system):
    reg, _, inv, _, _, mission = system
    reg.register_member("Dom", "driver")
    inv.add_car("Charger", 2000)
    
    # Successful mission should provide cash
    success, msg = mission.assign_mission("HEIST", ["Dom"], "Charger")
    assert success is True
    
    # Completing mission gives profit (logic in Results usually)
    # Let's check results integration
    results = ResultsModule(inv)
    initial_cash = inv.cash_balance
    results.record_result("Dom", 1, 5000)
    assert inv.cash_balance == initial_cash + 5000

def test_crew_scaling_and_limits(system):
    reg, crew, _, _, _, _ = system
    # Bulk register
    for i in range(10):
        reg.register_member(f"Member{i}", "driver")
    
    # Verify crew management keeps track
    assert len(crew.get_available_members("driver")) == 10

def test_multi_role_mission_failure(system):
    reg, _, inv, _, _, mission = system
    reg.register_member("Han", "driver")
    reg.register_member("Gisele", "driver")
    inv.add_car("LFA", 3000)
    inv.damage_car("LFA") # Damage the car
    
    # Mission with damaged car requires a mechanic
    success, msg = mission.assign_mission("ELITE_HEIST", ["Han", "Gisele"], "LFA")
    assert success is False
    assert "mechanic" in msg.lower()

def test_race_result_impacts_future_inventory(system):
    reg, _, inv, race, results, _ = system
    reg.register_member("Riley", "driver")
    inv.add_car("Falcon", 1000)
    
    # Race 1
    race.create_race("R1", "Riley", "Falcon")
    results.record_result("Riley", 1, 500) # Win
    
    # Race 2 (Using prize money from Race 1)
    # 5000 - 1000 + 500 = 4500
    success, msg = inv.add_car("Viper", 4000)
    assert success is True
    assert inv.cash_balance == 500

