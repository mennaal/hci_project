import cv2
import mediapipe as mp

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Initialize webcam
cap = cv2.VideoCapture(0)

# Finger names for indexing
FINGER_NAMES = ["Thumb", "Index", "Middle", "Ring", "Pinky"]


def count_fingers(hand_landmarks):
    """
    Counts the number of fingers that are up.
    Returns the number of fingers extended.
    """
    # Thumb: Check x-coordinates (horizontal movement, not vertical)
    thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
    thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
    thumb_up = thumb_tip.x < thumb_ip.x  # Adjust condition for hand orientation

    # Other fingers: Check y-coordinates (vertical movement)
    finger_tips = [
        mp_hands.HandLandmark.INDEX_FINGER_TIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
        mp_hands.HandLandmark.RING_FINGER_TIP,
        mp_hands.HandLandmark.PINKY_TIP,
    ]
    finger_pips = [
        mp_hands.HandLandmark.INDEX_FINGER_PIP,
        mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
        mp_hands.HandLandmark.RING_FINGER_PIP,
        mp_hands.HandLandmark.PINKY_PIP,
    ]

    fingers_up = [thumb_up]  # Start with thumb status
    for tip, pip in zip(finger_tips, finger_pips):
        fingers_up.append(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y)

    return sum(fingers_up)  # Return the count of fingers up


# Start hand tracking
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Flip the frame for a mirror effect
        frame = cv2.flip(frame, 1)

        # Convert BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame and detect hands
        results = hands.process(rgb_frame)

        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on the frame
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Count the number of fingers up
                num_fingers = count_fingers(hand_landmarks)

                # Display the number on the frame
                cv2.putText(frame, f"Number: {num_fingers}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX,
                            1, (0, 255, 0), 2)

        # Display the frame
        cv2.imshow("Hand Gesture Recognition", frame)

        # Break the loop on pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Clean up
cap.release()
cv2.destroyAllWindows()