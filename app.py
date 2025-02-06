# app.py
from flask import Flask, request, jsonify
from scripts.csv_db import ( 
    create_user, get_user_by_id,
    update_user_preferences, get_preferences_by_user_id,
    create_shopping_session, get_shopping_session
)

app = Flask(__name__)

@app.route('/api/users', methods=['POST'])
def api_create_user():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    new_user = create_user(name, email, password)
    return jsonify(new_user), 201

@app.route('/api/users/<user_id>', methods=['GET'])
def api_get_user(user_id):
    user = get_user_by_id(user_id)
    if user is None:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user), 200

@app.route('/api/users/<user_id>/preferences', methods=['POST'])
def api_set_preferences(user_id):
    data = request.json
    prefs_list = data.get('preferences', [])
    updated = update_user_preferences(user_id, prefs_list)
    return jsonify({
        "message": "Preferences updated",
        "updated_preferences": updated
    }), 200

@app.route('/api/users/<user_id>/preferences', methods=['GET'])
def api_get_preferences(user_id):
    prefs = get_preferences_by_user_id(user_id)
    return jsonify({"user_id": user_id, "preferences": prefs}), 200

@app.route('/api/users/<user_id>/shopping_sessions', methods=['POST'])
def api_create_session(user_id):
    data = request.json
    intent = data.get('intent', '')
    thread_id = data.get('thread_id', None)
    new_session = create_shopping_session(user_id, intent, thread_id)
    return jsonify(new_session), 201

@app.route('/api/shopping_sessions/<session_id>', methods=['GET'])
def api_get_session(session_id):
    session = get_shopping_session(session_id)
    if not session:
        return jsonify({"error": "Session not found"}), 404
    return jsonify(session), 200

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)

