# Assignment 2: Software Testing
**Roll Number:** 20241010  
**Name:** Arya Mirani  

## Repistory Link
[Add your repo link here]

## 1. White Box Testing (MoneyPoly)
### How to run:
1. Navigate to `whitebox/`
2. Run `export PYTHONPATH=$PYTHONPATH:$(pwd)`
3. Run `pytest tests/test_basic.py`
4. Run `pylint moneypoly/ main.py`

### Bugs Found:
1. **Error 1:** Player only collected salary if they landed exactly on Go. Fixed to reward salary when passing Go.
2. **Error 2:** Dice roll used `random.randint(1, 5)`, excluding 6. Fixed to `(1, 6)`.
3. **Error 3:** `Dice` class was missing `is_triple_doubles()` method, causing game crashes when someone rolled too many doubles.

---

## 2. Integration Testing (StreetRace Manager)
### How to run:
1. Navigate to `integration/`
2. Run `export PYTHONPATH=$PYTHONPATH:$(pwd)` 
3. Run `pytest tests/test_integration.py`

### Custom Modules:
1. **Betting Module:** Allows placing bets on race winners and receiving payouts.
2. **Reputation Module:** Tracks overall crew reputation based on performance.

---

## 3. Black Box API Testing (QuickCart)
### How to run:
1. Ensure the QuickCart server is running on `localhost:8080`.
2. Navigate to `blackbox/`
3. Run `pytest tests/test_api.py`

### Bug Reports (Example):
- **Endpoint:** `PUT /api/v1/profile`
- **Payload:** `{"phone": "123"}`
- **Expected:** `400 Bad Request`
- **Result:** Seen as handled in logic.
