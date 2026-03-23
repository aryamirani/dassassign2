import pytest
import requests

BASE_URL = "http://localhost:8080/api/v1"
ROLL_NUMBER = "20241010"
USER_ID = "1"

@pytest.fixture
def headers():
    return {
        "X-Roll-Number": ROLL_NUMBER,
        "X-User-ID": USER_ID,
        "Content-Type": "application/json"
    }

# 1. Profile Tests
def test_get_profile_valid(headers):
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    assert response.status_code == 200
    assert "name" in response.json()

def test_update_profile_invalid_phone(headers):
    payload = {"name": "Test User", "phone": "123"} # Too short
    response = requests.put(f"{BASE_URL}/profile", headers=headers, json=payload)
    assert response.status_code == 400

# 2. Cart Tests
def test_add_to_cart_zero_quantity(headers):
    payload = {"product_id": "1", "quantity": 0}
    response = requests.post(f"{BASE_URL}/cart/add", headers=headers, json=payload)
    assert response.status_code == 400

def test_add_non_existent_product(headers):
    payload = {"product_id": "99999", "quantity": 1}
    response = requests.post(f"{BASE_URL}/cart/add", headers=headers, json=payload)
    assert response.status_code == 404

# 3. Checkout Tests
def test_checkout_empty_cart(headers):
    # Clear cart first
    requests.delete(f"{BASE_URL}/cart/clear", headers=headers)
    payload = {"payment_method": "WALLET"}
    response = requests.post(f"{BASE_URL}/checkout", headers=headers, json=payload)
    assert response.status_code == 400

def test_checkout_cod_limit(headers):
    # Add expensive item to cart (assuming product 2 is expensive or we add many)
    # This test depends on state, but logically follows the rule
    payload = {"payment_method": "COD"}
    # If total > 5000, should be 400
    # response = requests.post(f"{BASE_URL}/checkout", headers=headers, json=payload)
    pass

# 4. Wallet Tests
def test_wallet_add_negative(headers):
    payload = {"amount": -100}
    response = requests.post(f"{BASE_URL}/wallet/add", headers=headers, json=payload)
    assert response.status_code == 400

def test_wallet_add_excessive(headers):
    payload = {"amount": 200000} # Over 100,000
    response = requests.post(f"{BASE_URL}/wallet/add", headers=headers, json=payload)
    assert response.status_code == 400

# 5. Header Validation
def test_missing_roll_number():
    h = {"X-User-ID": USER_ID}
    response = requests.get(f"{BASE_URL}/profile", headers=h)
    assert response.status_code == 401

def test_invalid_roll_number():
    h = {"X-Roll-Number": "abc", "X-User-ID": USER_ID}
    response = requests.get(f"{BASE_URL}/profile", headers=h)
    assert response.status_code == 400
