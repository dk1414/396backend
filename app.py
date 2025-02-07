# app.py
from flask import Flask, request, jsonify
from scripts.csv_db import ( 
    create_user, get_user_by_id,
    update_user_preferences, get_preferences_by_user_id,
    create_shopping_session, get_shopping_session
)
from scripts.assistant_helpers import create_chat_thread, ChatAgent
import openai
import os

from dotenv import load_dotenv
load_dotenv()

MAIN_ASSIST_ID = os.getenv('MAIN_CHAT_ASSIST_ID')
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

print("Creating OpenAI Client")
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
print("Client Created")

app = Flask(__name__)

@app.route('/api/users', methods=['POST'])
def api_create_user():
    print("Received request: POST /api/users")
    data = request.json
    print("Data received:", data)
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    new_user = create_user(name, email, password)
    print("User created:", new_user)
    return jsonify(new_user), 201

@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    print(f"Received request: GET /api/users/{user_id}")
    user = get_user_by_id(user_id)
    if user is None:
        print("User not found for user_id:", user_id)
        return jsonify({"error": "User not found"}), 404
    print("Returning user:", user)
    return jsonify(user), 200

@app.route('/api/users/<user_id>/preferences', methods=['POST'])
def api_set_preferences(user_id):
    print(f"Received request: POST /api/users/{user_id}/preferences")
    data = request.json
    print("Preferences data received:", data)
    prefs_list = data.get('preferences', [])
    updated = update_user_preferences(user_id, prefs_list)
    print("Updated preferences for user", user_id, ":", updated)
    return jsonify({
        "message": "Preferences updated",
        "updated_preferences": updated
    }), 200

@app.route('/api/users/<user_id>/preferences', methods=['GET'])
def api_get_preferences(user_id):
    print(f"Received request: GET /api/users/{user_id}/preferences")
    prefs = get_preferences_by_user_id(user_id)
    print("Returning preferences for user", user_id, ":", prefs)
    return jsonify({"user_id": user_id, "preferences": prefs}), 200

@app.route('/api/users/<user_id>/shopping_sessions', methods=['POST'])
def api_create_session(user_id):
    print(f"Received request: POST /api/users/{user_id}/shopping_sessions")
    data = request.json
    print("Session creation data:", data)
    intent = data.get("intent", "")
    
    # Retrieve the user from CSV.
    user = get_user_by_id(user_id)
    if not user:
        print("User not found for shopping session, user_id:", user_id)
        return jsonify({"error": "User not found"}), 404

    user_preferences = get_preferences_by_user_id(user_id)
    print("User preferences:", user_preferences)
    
    # Create a new thread using the Assistants API.
    print("Creating chat thread via Assistants API...")
    thread_id, initial_messages = create_chat_thread(openai_client, user_preferences, intent)
    print("Chat thread created with thread_id:", thread_id)
    print("Initial messages:", initial_messages)
    
    # Save the new shopping session (with the thread_id) to CSV.
    new_session = create_shopping_session(user_id, intent, thread_id)
    print("Shopping session created:", new_session)
    
    return jsonify(new_session), 201

@app.route('/api/shopping_sessions/<session_id>', methods=['GET'])
def api_get_session(session_id):
    print(f"Received request: GET /api/shopping_sessions/{session_id}")
    session = get_shopping_session(session_id)
    if not session:
        print("Session not found for session_id:", session_id)
        return jsonify({"error": "Session not found"}), 404
    print("Returning shopping session:", session)
    return jsonify(session), 200

@app.route('/api/shopping_sessions/<session_id>/messages', methods=['POST'])
def api_add_message(session_id):
    print(f"Received request: POST /api/shopping_sessions/{session_id}/messages")
    data = request.json
    print("Message data received:", data)
    user_message = data.get("message", "")
    
    # Retrieve the session to get the thread_id.
    session = get_shopping_session(session_id)
    if not session:
        print("Session not found when adding message, session_id:", session_id)
        return jsonify({"error": "Session not found"}), 404
    
    thread_id = session.get("thread_id")
    print("Using thread_id:", thread_id, "for session", session_id)
    
    # Use the ChatAgent to add the new message and generate a response.
    print("Initializing ChatAgent with assistant_id:", MAIN_ASSIST_ID)
    agent = ChatAgent(openai_client, thread_id, MAIN_ASSIST_ID)
    print("Adding user message to thread...")
    updated_messages = agent.add_message(user_message)
    print("Updated messages:", updated_messages)
    
    return jsonify(updated_messages), 200

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='127.0.0.1', port=5000)

