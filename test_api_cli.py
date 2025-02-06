# test_api_cli.py
import requests
import sys

BASE_URL = "http://127.0.0.1:5000/api"

def menu():
    print("\n=== API Test Menu ===")
    print("1. Create User")
    print("2. Get User by ID")
    print("3. Update User Preferences")
    print("4. Get User Preferences")
    print("5. Create Shopping Session")
    print("6. Get Shopping Session")
    print("0. Exit")

def create_user_flow():
    print("\n--- Create User ---")
    name = input("Enter name: ")
    email = input("Enter email: ")
    password = input("Enter password: ")

    data = {
        "name": name,
        "email": email,
        "password": password
    }
    resp = requests.post(f"{BASE_URL}/users", json=data)
    if resp.status_code == 201:
        print("User created successfully!")
        print("Response:", resp.json())
    else:
        print("Error:", resp.status_code, resp.text)

def get_user_flow():
    print("\n--- Get User ---")
    user_id = input("Enter user_id: ")

    resp = requests.get(f"{BASE_URL}/users/{user_id}")
    if resp.status_code == 200:
        print("User found:")
        print(resp.json())
    else:
        print("Error:", resp.status_code, resp.text)

def update_user_preferences_flow():
    print("\n--- Update User Preferences ---")
    user_id = input("Enter user_id: ")

    print("\nEnter preferences (key=value).")
    print("Type 'done' when finished.\n")

    prefs_list = []
    while True:
        line = input("pref: ")
        if line.lower() == "done":
            break
        if "=" in line:
            key, value = line.split("=", 1)
            prefs_list.append({"key": key.strip(), "value": value.strip()})
        else:
            print("Invalid format. Use key=value or 'done' to finish.")

    data = {"preferences": prefs_list}
    resp = requests.post(f"{BASE_URL}/users/{user_id}/preferences", json=data)
    if resp.status_code == 200:
        print("Preferences updated.")
        print("Response:", resp.json())
    else:
        print("Error:", resp.status_code, resp.text)

def get_user_preferences_flow():
    print("\n--- Get User Preferences ---")
    user_id = input("Enter user_id: ")

    resp = requests.get(f"{BASE_URL}/users/{user_id}/preferences")
    if resp.status_code == 200:
        print("User preferences:")
        print(resp.json())
    else:
        print("Error:", resp.status_code, resp.text)

def create_shopping_session_flow():
    print("\n--- Create Shopping Session ---")
    user_id = input("Enter user_id: ")
    intent = input("What is the user shopping for? (intent): ")
    thread_id = input("Optionally, enter an OpenAI thread_id (or leave blank): ")

    data = {"intent": intent}
    if thread_id:
        data["thread_id"] = thread_id

    resp = requests.post(f"{BASE_URL}/users/{user_id}/shopping_sessions", json=data)
    if resp.status_code == 201:
        print("Shopping session created.")
        print("Response:", resp.json())
    else:
        print("Error:", resp.status_code, resp.text)

def get_shopping_session_flow():
    print("\n--- Get Shopping Session ---")
    session_id = input("Enter session_id: ")

    resp = requests.get(f"{BASE_URL}/shopping_sessions/{session_id}")
    if resp.status_code == 200:
        print("Shopping session:")
        print(resp.json())
    else:
        print("Error:", resp.status_code, resp.text)

def main():
    while True:
        menu()
        choice = input("Choose an option: ").strip()
        if choice == "1":
            create_user_flow()
        elif choice == "2":
            get_user_flow()
        elif choice == "3":
            update_user_preferences_flow()
        elif choice == "4":
            get_user_preferences_flow()
        elif choice == "5":
            create_shopping_session_flow()
        elif choice == "6":
            get_shopping_session_flow()
        elif choice == "0":
            print("Exiting...")
            sys.exit(0)
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
