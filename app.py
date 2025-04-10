from flask import Flask, request, jsonify, send_from_directory
import os
import numpy as np
import cv2
from tensorflow.keras.models import load_model
import mediapipe as mp
import uuid
from datetime import datetime

# --- Configuration ---
LABELS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
MODEL_PATH = "lstm_sign_model.h5"

app = Flask(__name__, static_folder='static')

# --- Load Model ---
print("Loading model...")
model = load_model(MODEL_PATH)
print("Model loaded.")

# --- MediaPipe Setup ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()

# --- Session Store ---
sessions = {}

# --- Serve HTML Files ---
@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    return send_from_directory(app.static_folder, path)

# --- Auth Endpoint ---
@app.route('/auth', methods=['POST'])
def auth():
    auth_header = request.headers.get('Authorization', '')
    if not auth_header.startswith("Bearer"):
        return jsonify({"error": "Unauthorized"}), 401
    session_id = str(uuid.uuid4())
    sessions[session_id] = {"created": datetime.now(), "active": True}
    return jsonify({"sessionId": session_id}), 200

# --- Start Session ---
@app.route('/sessions', methods=['POST'])
def start_session():
    data = request.get_json()
    session_id = data.get("sessionId")
    if session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400
    return jsonify({"sessionId": session_id, "status": "started"}), 200

# --- Detect Sign from Image Frame ---
@app.route('/detect', methods=['POST'])
def detect():
    session_id = request.form.get("sessionId", None)
    if session_id not in sessions:
        return jsonify({"error": "Invalid session"}), 400

    if 'image' not in request.files:
        return jsonify({"error": "No image provided"}), 400

    file = request.files['image']
    image_bytes = file.read()
    nparr = np.frombuffer(image_bytes, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(img_rgb)

    if not results.multi_hand_landmarks:
        return jsonify({"error": "No hand detected", "detected": []}), 200

    hand_landmarks = results.multi_hand_landmarks[0]
    landmark_sequence = []
    for lm in hand_landmarks.landmark:
        landmark_sequence.extend([lm.x, lm.y, lm.z])
    sequence = [landmark_sequence] * 30  # repeat to match input shape

    sequence = np.array(sequence)
    sequence = sequence[:30]
    sequence = np.expand_dims(sequence, axis=0)

    prediction = model.predict(sequence)[0]
    predicted_label = LABELS[np.argmax(prediction)]
    confidence = float(np.max(prediction))

    return jsonify({
        "detected": [{
            "sign": predicted_label,
            "confidence": confidence
        }]
    })

# --- End Session ---
@app.route('/sessions/<session_id>', methods=['DELETE'])
def end_session(session_id):
    if session_id in sessions:
        sessions[session_id]["active"] = False
        return jsonify({"status": "ended"}), 200
    return jsonify({"error": "Invalid session"}), 400

# --- Run Server ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)
