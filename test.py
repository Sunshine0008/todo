import requests
import json

BASE_URL = "http://127.0.0.1:5000"

def test_api():
    print("🚀 Starting API Test Chaos...")

    # 1. TEST SIGNUP
    user_data = {"email": "chad@example.com", "password": "password123"}
    print("\n--- Testing Signup ---")
    signup_res = requests.post(f"{BASE_URL}/signup", json=user_data)
    print(f"Status: {signup_res.status_code}")
    print(f"Response: {signup_res.json()}")

    # 2. TEST LOGIN
    print("\n--- Testing Login ---")
    login_res = requests.post(f"{BASE_URL}/login", json=user_data)
    user_id = login_res.json().get("user_id")
    print(f"Logged in! User ID: {user_id}")

    # 3. CREATE A TASK
    print("\n--- Adding a Task ---")
    task_data = {"user_id": user_id, "text": "🔥 Buy more RGB lights"}
    task_res = requests.post(f"{BASE_URL}/tasks", json=task_data)
    task_id = task_res.json().get("id")
    print(f"Task Created: {task_res.json()}")

    # 4. GET TASKS
    print("\n--- Fetching User Tasks ---")
    get_res = requests.get(f"{BASE_URL}/tasks/{user_id}")
    print(f"Tasks in DB: {get_res.json()}")

    # 5. UPDATE TASK (Move to Done)
    print("\n--- Moving Task to Done ---")
    update_data = {"status": "done"}
    update_res = requests.put(f"{BASE_URL}/tasks/{task_id}", json=update_data)
    print(f"Update Status: {update_res.json()}")

    # 6. BANISH TASK (Delete)
    print("\n--- Banishing Task to the Shadow Realm ---")
    del_res = requests.delete(f"{BASE_URL}/tasks/{task_id}")
    print(f"Delete Status: {del_res.json()}")

    print("\n✨ Test Complete. Your backend is officially vibing.")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Is your FastAPI server running? (uvicorn app:app --port 5000)")
