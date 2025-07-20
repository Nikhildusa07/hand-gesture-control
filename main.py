import cv2
import mediapipe as mp
import pyautogui
import time
import webbrowser
import os

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands = mp_hands.Hands(max_num_hands=1)
cap = cv2.VideoCapture(0)

gesture_buffer = []
CONFIRM_FRAMES = 5
cooldown_time = 1.5
last_gesture_time = time.time()
current_gesture = None

def detect_gesture(landmarks):
    finger_states = []
    tips_ids = [4, 8, 12, 16, 20]
    pip_ids = [3, 6, 10, 14, 18]

    for tip, pip in zip(tips_ids, pip_ids):
        finger_states.append(landmarks[tip].y < landmarks[pip].y)

    # Define gestures with emojis
    if finger_states == [False, True, False, False, False]:
        return "volumeup", "🔊"
    elif finger_states == [False, False, True, False, False]:
        return "volumedown", "🔉"
    elif finger_states == [False, True, True, False, False]:
        return "mute", "🔇"
    elif finger_states == [True, False, False, False, False]:
        return "playpause", "⏯️"
    elif finger_states == [True, True, True, True, True]:
        return "stop", "⏹️"
    elif all(not state for state in finger_states):
        return "screenshot", "📸"
    elif finger_states == [False, False, True, True, False]:
        return "openbrowser", "🌐"
    elif finger_states == [True, False, False, False, True]:
        return "lockscreen", "🔒"
    else:
        return None, None

def perform_action(gesture):
    if gesture == "volumeup":
        pyautogui.press("volumeup")
    elif gesture == "volumedown":
        pyautogui.press("volumedown")
    elif gesture == "mute":
        pyautogui.press("volumemute")
    elif gesture == "playpause":
        pyautogui.press("playpause")
    elif gesture == "stop":
        pyautogui.hotkey("ctrl", "s")
    elif gesture == "screenshot":
        pyautogui.screenshot("gesture_screenshot.png")
    elif gesture == "openbrowser":
        webbrowser.open("https://www.google.com")
    elif gesture == "lockscreen":
        os.system("rundll32.exe user32.dll,LockWorkStation")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = hands.process(rgb)

    if result.multi_hand_landmarks:
        for hand_landmarks in result.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            gesture, emoji = detect_gesture(hand_landmarks.landmark)

            if gesture:
                gesture_buffer.append(gesture)
                if len(gesture_buffer) > CONFIRM_FRAMES:
                    gesture_buffer.pop(0)

                if (gesture_buffer.count(gesture) == CONFIRM_FRAMES and
                    gesture != current_gesture and
                    time.time() - last_gesture_time > cooldown_time):
                    current_gesture = gesture
                    last_gesture_time = time.time()
                    perform_action(gesture)

            else:
                gesture_buffer.clear()
                current_gesture = None

            if current_gesture and emoji:
                cv2.putText(frame, f"{current_gesture} {emoji}", (10, 50),
                            cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)

    cv2.imshow("Hand Gesture Control", frame)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
