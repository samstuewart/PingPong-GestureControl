from flask import Flask, jsonify, request
from flask_cors import CORS
import cv2
import numpy as np
import os
import utils as ht
import base64

app = Flask(__name__)
CORS(app)  # Enable CORS for cross-origin requests

# Initialize Webcam
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    raise Exception("Failed to initialize webcam. Please check your camera connection.")

cap.set(3, 1280)  # Width
cap.set(4, 720)  # Height

# Initialize Hand Detector
handTracking = ht.HandDetector()

# Paths for Resources
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
imageFrontDesign = cv2.imread(os.path.join(BASE_DIR, "Resources/FrontDesign.png"))
imageGameOver = cv2.imread(os.path.join(BASE_DIR, "Resources/gameover.png"))
imageBat1 = cv2.imread(os.path.join(BASE_DIR, "Resources/imgbat1.png"), cv2.IMREAD_UNCHANGED)
imageBat2 = cv2.imread(os.path.join(BASE_DIR, "Resources/imgbat2.png"), cv2.IMREAD_UNCHANGED)
imageBall = cv2.imread(os.path.join(BASE_DIR, "Resources/Ball.png"), cv2.IMREAD_UNCHANGED)
winnerLeft = cv2.imread(os.path.join(BASE_DIR, "Resources/winnerLeft.png"), cv2.IMREAD_UNCHANGED)
winnerRight = cv2.imread(os.path.join(BASE_DIR, "Resources/winnerRight.png"), cv2.IMREAD_UNCHANGED)

# Test resource loading
resources = {
    "FrontDesign": imageFrontDesign,
    "GameOver": imageGameOver,
    "Bat1": imageBat1,
    "Bat2": imageBat2,
    "Ball": imageBall,
    "WinnerLeft": winnerLeft,
    "WinnerRight": winnerRight
}

for name, resource in resources.items():
    if resource is None:
        print(f"Failed to load: {name}")

if any(resource is None for resource in resources.values()):
    raise Exception("Failed to load one or more resources. Please check your file paths.")
else:
    print("All resources loaded successfully.")

# Game State
game_state = {
    "ball_position": [191, 82],
    "speedX": 25,  # Increased speed
    "speedY": 25,  # Increased speed
    "score": [0, 0],
    "gameOver": False,
    "winner": None,
    "gameStarted": False
}

# Reset Game State
def reset_game_state():
    global game_state
    game_state = {
        "ball_position": [191, 82],
        "speedX": 25,
        "speedY": 25,
        "score": [0, 0],
        "gameOver": False,
        "winner": None,
        "gameStarted": False
    }

@app.route('/api/reset', methods=['POST'])
def reset_game():
    reset_game_state()
    return jsonify({"message": "Game reset successfully", "game_state": game_state})

@app.route('/api/start', methods=['POST'])
def start_game():
    game_state["gameStarted"] = True
    return jsonify({"message": "Game started", "game_state": game_state})

@app.route('/api/run', methods=['POST'])
def run_game():
    if not cap.isOpened():
        return jsonify({"error": "Failed to capture webcam frame"}), 500

    ret, frame = cap.read()
    if not ret:
        return jsonify({"error": "Failed to read webcam frame"}), 500

    frame = cv2.resize(frame, (1280, 720))
    frame = cv2.flip(frame, 1)

    # Only update game if it has started
    if not game_state["gameStarted"]:
        _, buffer = cv2.imencode('.jpg', frame)
        frame_base64 = base64.b64encode(buffer).decode('utf-8')
        return jsonify({"game_state": game_state, "frame": frame_base64})

    frame, hands = handTracking.findPosition(frame, draw=True)
    frame = cv2.addWeighted(frame, 0.3, imageFrontDesign, 0.7, 0)

    if hands:
        for hand in hands:
            x, y, w, h = hand["bbox"]
            h1, w1, _ = imageBat1.shape
            y1 = y - h1 // 2
            y1 = np.clip(y1, 45, 510)

            if hand["type"] == "Left":
                frame = ht.overlayPNG(frame, imageBat1, (73, y1))
                if 73 < game_state["ball_position"][0] < 73 + w1 and y1 < game_state["ball_position"][1] < y1 + h1:
                    game_state["speedX"] = -game_state["speedX"]
                    game_state["ball_position"][0] += 30
                    game_state["score"][0] += 1

            if hand["type"] == "Right":
                frame = ht.overlayPNG(frame, imageBat2, (1192, y1))
                if 1192 - 60 < game_state["ball_position"][0] < 1192 - 30 and y1 < game_state["ball_position"][1] < y1 + h1:
                    game_state["speedX"] = -game_state["speedX"]
                    game_state["ball_position"][0] -= 30
                    game_state["score"][1] += 1

    # Move Ball
    game_state["ball_position"][0] += game_state["speedX"]
    game_state["ball_position"][1] += game_state["speedY"]

    # Ball Bounces on Walls
    if game_state["ball_position"][1] >= 480 or game_state["ball_position"][1] <= 22:
        game_state["speedY"] = -game_state["speedY"]

    # Check Game Over
    if game_state["ball_position"][0] < 16 or game_state["ball_position"][0] > 1276:
        game_state["gameOver"] = True
        game_state["gameStarted"] = False
        game_state["winner"] = "Lefty" if game_state["score"][0] > game_state["score"][1] else "Righty"

    if game_state["gameOver"]:
        if game_state["winner"] == "Lefty":
            frame = ht.overlayPNG(frame, winnerLeft, (500, 200))
        else:
            frame = ht.overlayPNG(frame, winnerRight, (500, 200))

    # Draw Ball
    if not game_state["gameOver"]:
        frame = ht.overlayPNG(frame, imageBall, (game_state["ball_position"][0], game_state["ball_position"][1]))

    # Encode the frame as a base64 string
    _, buffer = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')

    return jsonify({"game_state": game_state, "frame": frame_base64})

if __name__ == "__main__":
    app.run(debug=True)
