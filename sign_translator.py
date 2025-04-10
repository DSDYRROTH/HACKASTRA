import os
import cv2
import numpy as np
import string
import mediapipe as mp
import pyttsx3
from datetime import datetime
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.utils import to_categorical

# ===== CONFIG =====
LABELS = list(string.ascii_uppercase)
DATA_PATH = "dataset"
SEQUENCE_LENGTH = 30
NUM_SEQUENCES = 5

# ===== CREATE DIRECTORIES =====
os.makedirs(DATA_PATH, exist_ok=True)
for label in LABELS:
    os.makedirs(os.path.join(DATA_PATH, label), exist_ok=True)

# ===== MEDIAPIPE SETUP =====
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_draw = mp.solutions.drawing_utils

# ===== TEXT TO SPEECH =====
engine = pyttsx3.init()
engine.setProperty('rate', 150)  # Speed
engine.setProperty('volume', 1.0)  # Volume

# ===== SPEAK FUNCTION =====
def speak_text(text):
    engine.say(text)
    engine.runAndWait()

# ===== STEP 1: DATA COLLECTION =====
def collect_data():
    cap = cv2.VideoCapture(0)
    print("[1] STARTING DATA COLLECTION")

    for label in LABELS:
        print(f"\nCollecting data for: {label}")
        for seq in range(NUM_SEQUENCES):
            sequence = []
            print(f"  Sequence {seq+1}/{NUM_SEQUENCES}")
            frame_count = 0
            while frame_count < SEQUENCE_LENGTH:
                ret, frame = cap.read()
                image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                results = hands.process(image)
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

                if results.multi_hand_landmarks:
                    for hand_landmarks in results.multi_hand_landmarks:
                        mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                        landmarks = []
                        for lm in hand_landmarks.landmark:
                            landmarks.extend([lm.x, lm.y, lm.z])
                        sequence.append(landmarks)
                        frame_count += 1

                cv2.imshow("Collecting", image)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

            if len(sequence) == SEQUENCE_LENGTH:
                np.save(os.path.join(DATA_PATH, label, f"{label}_{seq}.npy"), sequence)

    cap.release()
    cv2.destroyAllWindows()
    print("Data collection completed.")

# ===== STEP 2: TRAIN LSTM MODEL =====
def train_model():
    print("[2] STARTING TRAINING")

    sequences, labels_list = [], []
    label_map = {label: num for num, label in enumerate(LABELS)}

    for label in LABELS:
        folder_path = os.path.join(DATA_PATH, label)
        if not os.listdir(folder_path):
            continue
        for file in os.listdir(folder_path):
            data_path = os.path.join(folder_path, file)
            sequence = np.load(data_path)
            sequences.append(sequence)
            labels_list.append(label_map[label])

    if not sequences:
        print("No data found. Please collect data first.")
        return

    X = np.array(sequences)
    y = to_categorical(labels_list)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1)

    model = Sequential()
    model.add(LSTM(64, return_sequences=True, activation='relu', input_shape=(SEQUENCE_LENGTH, X.shape[2])))
    model.add(LSTM(128, return_sequences=False, activation='relu'))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(len(LABELS), activation='softmax'))

    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=30, validation_data=(X_test, y_test))

    model.save("lstm_sign_model.h5")
    print("Model training completed and saved as lstm_sign_model.h5.")

# ===== STEP 3: REAL-TIME PREDICTION =====
def predict():
    print("[3] STARTING REAL-TIME TRANSLATION")
    model = load_model("lstm_sign_model.h5")
    cap = cv2.VideoCapture(0)
    sequence = []
    recognized_text = ""
    last_predicted = ""

    with open("output_log.txt", "a") as log_file:
        log_file.write(f"\n--- SESSION STARTED: {datetime.now()} ---\n")

        while True:
            ret, frame = cap.read()
            image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = hands.process(image)
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.multi_hand_landmarks:
                for hand_landmarks in results.multi_hand_landmarks:
                    mp_draw.draw_landmarks(image, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                    landmarks = []
                    for lm in hand_landmarks.landmark:
                        landmarks.extend([lm.x, lm.y, lm.z])
                    sequence.append(landmarks)

                    if len(sequence) == SEQUENCE_LENGTH:
                        res = model.predict(np.expand_dims(sequence, axis=0))[0]
                        predicted = LABELS[np.argmax(res)]

                        if predicted != last_predicted:
                            recognized_text += predicted
                            log_file.write(predicted)
                            log_file.flush()
                            speak_text(predicted)
                            last_predicted = predicted

                        sequence = []

            cv2.rectangle(image, (0, 0), (640, 40), (245, 117, 16), -1)
            cv2.putText(image, recognized_text, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow("Real-Time Translator", image)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()
    print("Session ended. Translation saved to output_log.txt.")

# ===== MAIN =====
if __name__ == "__main__":
    print("\nChoose step to run:")
    print("1 - Collect Data")
    print("2 - Train Model")
    print("3 - Run Real-Time Translator")

    step = input("Enter 1, 2 or 3: ").strip()
    if step == "1":
        collect_data()
    elif step == "2":
        train_model()
    elif step == "3":
        predict()
    else:
        print("Invalid input.")