import pytest
import requests
import json

BASE_URL = "http://localhost:8080/api/v1"
ROLL_NUMBER = "2024101145"
USER_ID = "1"

@pytest.fixture
def headers():
    return {
        "X-Roll-Number": ROLL_NUMBER,
        "X-User-ID": USER_ID,
        "Content-Type": "application/json"
    }

@pytest.fixture
def h():
    return {
        "X-Roll-Number": ROLL_NUMBER,
        "X-User-ID": USER_ID,
        "Content-Type": "application/json"
    }

def clear_cart(h):
    requests.delete(f"{BASE_URL}/cart/clear", headers=h)

# --- 1. Profile Tests ---
def test_get_profile_valid(headers):
    response = requests.get(f"{BASE_URL}/profile", headers=headers)
    assert response.status_code == 200
    assert "name" in response.json()

@pytest.mark.parametrize("name", ["A", "a" * 51])
def test_update_profile_invalid_name_length(headers, name):
    payload = {"name": name, "phone": "9876543210"}
    response = requests.put(f"{BASE_URL}/profile", headers=headers, json=payload)
    assert response.status_code == 400

@pytest.mark.parametrize("phone", ["123", "123456789", "12345678901", "abcdefghij"])
def test_update_profile_invalid_phone(headers, phone):
    payload = {"name": "Test User", "phone": phone}
    response = requests.put(f"{BASE_URL}/profile", headers=headers, json=payload)
    assert response.status_code == 400

# --- 2. Address Tests ---
@pytest.mark.parametrize("label", ["HOME", "OFFICE", "OTHER"])
def test_add_address_valid_labels(headers, label):
    payload = {
        "label": label,
        "street": "123 Main St",
        "city": "Hyderabad",
        "pincode": "500032",
        "is_default": False
    }
    response = requests.post(f"{BASE_URL}/addresses", headers=headers, json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["address"]["label"] == label

def test_add_address_invalid_pincode(headers):
    payload = {
        "label": "HOME",
        "street": "123 Main St",
        "city": "Hyderabad",
        "pincode": "50003", # 5 digits
        "is_default": False
    }
    response = requests.post(f"{BASE_URL}/addresses", headers=headers, json=payload)
    assert response.status_code == 400

def test_address_default_uniqueness(headers):
    # Add first default
    response1 = requests.post(f"{BASE_URL}/addresses", headers=headers, json={
        "label": "HOME", "street": "Street 1", "city": "City 1", "pincode": "111111", "is_default": True
    })
    a1 = response1.json()["address"]
    # Add second default
    response2 = requests.post(f"{BASE_URL}/addresses", headers=headers, json={
        "label": "OFFICE", "street": "Street 2", "city": "City 2", "pincode": "222222", "is_default": True
    })
    a2 = response2.json()["address"]
    
    # Check if a1 is still default
    all_addresses = requests.get(f"{BASE_URL}/addresses", headers=headers).json()
    for addr in all_addresses:
        if addr["address_id"] == a1["address_id"]:
            assert addr["is_default"] is False
        if addr["address_id"] == a2["address_id"]:
            assert addr["is_default"] is True

# --- 3. Product Tests ---
def test_product_list_active_only(headers):
    response = requests.get(f"{BASE_URL}/products", headers={"X-Roll-Number": ROLL_NUMBER})
    products = response.json()
    for p in products:
        # Some items might be inactive but only active should be returned in list
        assert p["is_active"] is True

def test_product_detail_404(headers):
    response = requests.get(f"{BASE_URL}/products/99999", headers={"X-Roll-Number": ROLL_NUMBER})
    assert response.status_code == 404

# --- 4. Cart Tests ---
def test_add_to_cart_zero_quantity(headers):
    payload = {"product_id": 1, "quantity": 0}
    response = requests.post(f"{BASE_URL}/cart/add", headers=headers, json=payload)
    assert response.status_code == 400

def test_add_non_existent_product(headers):
    payload = {"product_id": 99999, "quantity": 1}
    response = requests.post(f"{BASE_URL}/cart/add", headers=headers, json=payload)
    assert response.status_code == 404

def test_add_to_cart_stock_limit(headers):
    # Try adding more than 195 (Apple - Red stock)
    payload = {"product_id": 1, "quantity": 1000}
    response = requests.post(f"{BASE_URL}/cart/add", headers=headers, json=payload)
    assert response.status_code == 400

def test_cart_subtotal_calculation(headers):
    requests.delete(f"{BASE_URL}/cart/clear", headers=headers)
    requests.post(f"{BASE_URL}/cart/add", headers=headers, json={"product_id": 1, "quantity": 2})
    cart = requests.get(f"{BASE_URL}/cart", headers=headers).json()
    # Apple Red price 120 * 2 = 240
    assert cart["items"][0]["subtotal"] == 240

# --- 5. Coupon Application Logic ---
@pytest.mark.parametrize("code, items, expected_status", [
    ("BIGDEAL500", [{"id": 1, "qty": 50}], 200),  # Valid (120*50 > 5000)
    ("BIGDEAL500", [{"id": 1, "qty": 1}], 400),   # Under min value (120 < 5000)
    ("EXPIRED10", [{"id": 1, "qty": 10}], 400),   # Expired (from admin check)
    ("INVALID_CODE", [{"id": 1, "qty": 1}], 404), # Not found
])
def test_coupon_application_logic(h, code, items, expected_status):
    clear_cart(h)
    for item in items:
        requests.post(f"{BASE_URL}/cart/add", headers=h, json={"product_id": item["id"], "quantity": item["qty"]})
    
    response = requests.post(f"{BASE_URL}/coupon/apply", headers=h, json={"coupon_code": code})
    assert response.status_code == expected_status

def test_coupon_discount_calculation_precision(h):
    clear_cart(h)
    requests.post(f"{BASE_URL}/cart/add", headers=h, json={"product_id": 1, "quantity": 10}) # 1200
    requests.post(f"{BASE_URL}/coupon/apply", headers=h, json={"coupon_code": "SAVE10"})
    cart = requests.get(f"{BASE_URL}/cart", headers=h).json()
    assert "discount" in cart or "applied_coupon" in cart

# --- 6. Support Ticket Tests ---
def test_ticket_creation_boundaries(h):
    # Subject < 5 chars
    res = requests.post(f"{BASE_URL}/support/ticket", headers=h, json={"subject": "abc", "message": "Valid message"})
    assert res.status_code == 400
    # Message > 500 chars
    res = requests.post(f"{BASE_URL}/support/ticket", headers=h, json={"subject": "Valid Subject", "message": "a" * 501})
    assert res.status_code == 400

def test_ticket_status_state_machine(h):
    # Create ticket
    ticket_res = requests.post(f"{BASE_URL}/support/ticket", headers=h, json={
        "subject": "Status Test", "message": "Testing transitions"
    })
    ticket = ticket_res.json()["ticket"]
    tid = ticket["ticket_id"]
    assert ticket["status"] == "OPEN"

    # IN_PROGRESS -> OPEN (Illegal backward transition)
    requests.put(f"{BASE_URL}/support/tickets/{tid}", headers=h, json={"status": "IN_PROGRESS"})
    res = requests.put(f"{BASE_URL}/support/tickets/{tid}", headers=h, json={"status": "OPEN"})
    assert res.status_code == 400

# --- 7. Checkout & GST ---
def test_checkout_invalid_method(headers):
    payload = {"payment_method": "BITCOIN"}
    response = requests.post(f"{BASE_URL}/checkout", headers=headers, json=payload)
    assert response.status_code == 400

def test_checkout_cod_limit(headers):
    requests.delete(f"{BASE_URL}/cart/clear", headers=headers)
    requests.post(f"{BASE_URL}/cart/add", headers=headers, json={"product_id": 1, "quantity": 50}) # 120 * 50 = 6000
    payload = {"payment_method": "COD"}
    response = requests.post(f"{BASE_URL}/checkout", headers=headers, json=payload)
    assert response.status_code == 400

def test_checkout_empty_cart(headers):
    requests.delete(f"{BASE_URL}/cart/clear", headers=headers)
    payload = {"payment_method": "WALLET"}
    response = requests.post(f"{BASE_URL}/checkout", headers=headers, json=payload)
    assert response.status_code == 400

def test_checkout_gst_application(h):
    clear_cart(h)
    requests.post(f"{BASE_URL}/cart/add", headers=h, json={"product_id": 1, "quantity": 1}) # 120
    res = requests.post(f"{BASE_URL}/checkout", headers=h, json={"payment_method": "CARD"})
    oid = res.json()["order_id"]
    invoice = requests.get(f"{BASE_URL}/orders/{oid}/invoice", headers=h).json()
    assert invoice["total"] == 126
    assert invoice["gst_amount"] == 6

# --- 8. Wallet Tests ---
@pytest.mark.parametrize("amount", [-100, -1, 0, 100001])
def test_wallet_add_boundaries(headers, amount):
    payload = {"amount": amount}
    response = requests.post(f"{BASE_URL}/wallet/add", headers=headers, json=payload)
    assert response.status_code == 400

# --- 9. Reviews & Average Rating ---
def test_review_rating_decimal_accuracy(h):
    pid = 1 # Apple Red
    requests.post(f"{BASE_URL}/products/{pid}/reviews", headers=h, json={"rating": 4, "comment": "Good"})
    requests.post(f"{BASE_URL}/products/{pid}/reviews", headers=h, json={"rating": 5, "comment": "Great"})
    
    res = requests.get(f"{BASE_URL}/products/{pid}", headers={"X-Roll-Number": ROLL_NUMBER})
    product = res.json()
    assert product["average_rating"] == 4.5

# --- 10. Data Consistency ---
def test_cancel_order_restores_stock(h):
    pid = 1
    initial_stock = requests.get(f"{BASE_URL}/products/{pid}", headers={"X-Roll-Number": ROLL_NUMBER}).json()["stock_quantity"]
    
    clear_cart(h)
    requests.post(f"{BASE_URL}/cart/add", headers=h, json={"product_id": pid, "quantity": 5})
    order = requests.post(f"{BASE_URL}/checkout", headers=h, json={"payment_method": "CARD"}).json()
    
    mid_stock = requests.get(f"{BASE_URL}/products/{pid}", headers={"X-Roll-Number": ROLL_NUMBER}).json()["stock_quantity"]
    assert mid_stock == initial_stock - 5
    
    requests.post(f"{BASE_URL}/orders/{order['order_id']}/cancel", headers=h)
    final_stock = requests.get(f"{BASE_URL}/products/{pid}", headers={"X-Roll-Number": ROLL_NUMBER}).json()["stock_quantity"]
    assert final_stock == initial_stock

# --- 11. Header Validation ---
def test_missing_roll_number():
    response = requests.get(f"{BASE_URL}/profile", headers={"X-User-ID": USER_ID})
    assert response.status_code == 401

@pytest.mark.parametrize("roll", ["abc", "12.34", "!@#"])
def test_invalid_roll_number(roll):
    response = requests.get(f"{BASE_URL}/profile", headers={"X-Roll-Number": roll, "X-User-ID": USER_ID})
    assert response.status_code == 400

# --- 12. Security / Bug Hunt ---
def test_user_cannot_access_others_data(h):
    res = requests.get(f"{BASE_URL}/orders/999", headers=h) 
    assert res.status_code in [403, 404]
