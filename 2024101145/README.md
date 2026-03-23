# Assignment 2: Software Testing
**Roll Number:** 2024101145
**Name:** Arya Mirani  

## Repository Link
https://github.com/aryamirani/dassassign2

## Unified Test Execution
To run all tests (Black Box, White Box, and Integration) from the root project folder:
1. Ensure the QuickCart server is running at `localhost:8080`.
   - **Docker Setup:** Run `docker-compose up` in the QuickCart image directory.
2. Navigate to the root folder: `DASS_assignment2/2024101145/`
3. Set the Python path: `export PYTHONPATH=$PYTHONPATH:$(pwd)/whitebox:$(pwd)/integration`
4. Use our Python environment (recommending `python 3.8+`).
5. Run all tests using pytest:
   ```bash
   pytest blackbox/tests/test_blackbox.py whitebox/tests/test_whitebox.py integration/tests/test_integration.py
   ```

## 1. White Box Testing (MoneyPoly)
### How to run:
1. Navigate to `whitebox/`
2. Run `export PYTHONPATH=$PYTHONPATH:$(pwd)`
3. Run `pytest tests/test_whitebox.py`
4. Run `pylint moneypoly/ main.py`

### Bugs Found:
1. **Bank Loan Fund Integrity [CRITICAL]:** When a player takes a loan, the player receives cash but the bank's internal balance remains unchanged.
2. **Player Net Worth Calculation Error:** The `get_net_worth()` function fails to account for the value of properties owned by the player.

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
3. Run `pytest tests/test_blackbox.py`

### Critical Bugs Found:
1. **Cart Subtotal Calculation Error [CRITICAL]:** Quantity multipliers result in negative subtotals.
2. **Invoice Totals Mismatch [CRITICAL]:** Checkout returns different totals than the `/invoice` endpoint.
3. **Default Address Uniqueness Logic:** Multiple default addresses allowed.
4. **Phone Number Type Validation:** Non-numeric strings accepted.
5. **COD Limit Enforcement:** 5,000 unit limit is ignored.
6. **Product Not Found Status Code:** Returns 400 instead of 404 for missing IDs.
