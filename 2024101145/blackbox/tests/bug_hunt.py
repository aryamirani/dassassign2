import requests

BASE_URL = "http://localhost:8080/api/v1"
HEADERS = {
    "X-Roll-Number": "20241010",
    "X-User-ID": "1",
    "Content-Type": "application/json"
}

def check_bug_non_existent_product():
    print("Testing: Add non-existent product to cart")
    payload = {"product_id": 99999, "quantity": 1} # Changed to integer
    response = requests.post(f"{BASE_URL}/cart/add", headers=HEADERS, json=payload)
    print(f"Status: {response.status_code}")
    print(f"Body: {response.text}")

if __name__ == "__main__":
    check_bug_non_existent_product()
