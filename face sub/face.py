# import cv2
# import mediapipe as mp
# import os
# import face_recognition
# import numpy as np

# mp_hands = mp.solutions.hands
# hands = mp_hands.Hands(min_detection_confidence=0.5, min_tracking_confidence=0.5)
# mp_drawing = mp.solutions.drawing_utils

# # Directory to store known faces
# KNOWN_FACES_DIR = "known_faces"
# if not os.path.exists(KNOWN_FACES_DIR):
#     os.makedirs(KNOWN_FACES_DIR)

# # Load known users' images
# known_face_encodings = []
# known_face_names = []

# try:
#     # Load existing user images (if any)
#     for filename in os.listdir(KNOWN_FACES_DIR):
#         if filename.endswith(".jpg"):
#             image_path = os.path.join(KNOWN_FACES_DIR, filename)
#             user_image = face_recognition.load_image_file(image_path)
#             user_encoding = face_recognition.face_encodings(user_image)[0]
#             known_face_encodings.append(user_encoding)
#             known_face_names.append(filename.split(".")[0])  # User name based on the filename
# except Exception as e:
#     print(f"Error loading known faces: {e}")

# # Hand motion thresholds
# HAND_MOVEMENT_THRESHOLD = 0.05  # Threshold to detect upward/downward motion of the hand
# previous_y_tip = None

# def process_frame():
#     global previous_y_tip

#     cap = cv2.VideoCapture(0)

#     if not cap.isOpened():
#         print("Error: Unable to access the webcam.")
#         return

#     while cap.isOpened():
#         ret, frame = cap.read()
#         if not ret:
#             print("Failed to grab frame")
#             break

#         frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         results = hands.process(frame)

#         frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

#         if results.multi_hand_landmarks:
#             for hand_landmarks in results.multi_hand_landmarks:
#                 # Get the y-coordinate of the index finger tip
#                 y_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP].y

#                 if previous_y_tip is not None:
#                     y_diff = previous_y_tip - y_tip
#                     if y_diff > HAND_MOVEMENT_THRESHOLD:
#                         print("Hand moved up. Check for deletion.")
#                     elif y_diff < -HAND_MOVEMENT_THRESHOLD:
#                         print("Hand moved down. Check for deletion.")
                        
#                         # If hand moved down, attempt to delete a user
#                         if len(known_face_names) > 0:
#                             print(f"Deleting {known_face_names[0]}...")
#                             # Remove the first user from the list
#                             del known_face_names[0]
#                             del known_face_encodings[0]
#                             # Remove the user's file from the directory
#                             user_file = os.path.join(KNOWN_FACES_DIR, f"{known_face_names[0]}.jpg")
#                             if os.path.exists(user_file):
#                                 os.remove(user_file)
#                             print(f"User deleted: {known_face_names[0]}")
#                             break

#                 previous_y_tip = y_tip  # Update the previous y-coordinate

#                 mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

#         # Show the frame
#         cv2.imshow("Mediapipe Hands", frame)

#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

#     cap.release()
#     cv2.destroyAllWindows()
#     hands.close()
#     print("Connection closed.")


# if __name__ == "_main_":
#     process_frame()




# ###############################
# ################################
# # name , emotion , add after unknown , delete by gesture (1)


# import cv2
# import face_recognition
# import numpy as np
# import os
# import time
# import mediapipe as mp
# from deepface import DeepFace  # For emotion analysis

# # Directory to store known faces
# KNOWN_FACES_DIR = "known_faces"
# if not os.path.exists(KNOWN_FACES_DIR):
#     os.makedirs(KNOWN_FACES_DIR)

# # Initialize MediaPipe Hands
# mp_hands = mp.solutions.hands
# mp_draw = mp.solutions.drawing_utils

# # Load known users' images
# known_face_encodings = []
# known_face_names = []

# # Finger names for indexing
# FINGER_NAMES = ["Thumb", "Index", "Middle", "Ring", "Pinky"]

# def count_fingers(hand_landmarks):
#     """
#     Counts the number of fingers that are up.
#     Returns the number of fingers extended.
#     """
#     # Thumb: Check x-coordinates (horizontal movement, not vertical)
#     thumb_tip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_TIP]
#     thumb_ip = hand_landmarks.landmark[mp_hands.HandLandmark.THUMB_IP]
#     thumb_up = thumb_tip.x < thumb_ip.x  # Adjust condition for hand orientation

#     # Other fingers: Check y-coordinates (vertical movement)
#     finger_tips = [
#         mp_hands.HandLandmark.INDEX_FINGER_TIP,
#         mp_hands.HandLandmark.MIDDLE_FINGER_TIP,
#         mp_hands.HandLandmark.RING_FINGER_TIP,
#         mp_hands.HandLandmark.PINKY_TIP,
#     ]
#     finger_pips = [
#         mp_hands.HandLandmark.INDEX_FINGER_PIP,
#         mp_hands.HandLandmark.MIDDLE_FINGER_PIP,
#         mp_hands.HandLandmark.RING_FINGER_PIP,
#         mp_hands.HandLandmark.PINKY_PIP,
#     ]

#     fingers_up = [thumb_up]  # Start with thumb status
#     for tip, pip in zip(finger_tips, finger_pips):
#         fingers_up.append(hand_landmarks.landmark[tip].y < hand_landmarks.landmark[pip].y)

#     return sum(fingers_up)  # Return the count of fingers up

# def delete_last_user():
#     """Deletes the last added user image and updates the lists."""
#     global known_face_encodings, known_face_names

#     if len(known_face_names) > 0:
#         # Remove the last user from the known_faces directory
#         last_user = known_face_names[-1]
#         last_user_image_path = os.path.join(KNOWN_FACES_DIR, f"{last_user}.jpg")
#         if os.path.exists(last_user_image_path):
#             os.remove(last_user_image_path)
#             print(f"Deleted {last_user}")

#         # Remove the last user from the encoding and names lists
#         known_face_encodings = known_face_encodings[:-1]
#         known_face_names = known_face_names[:-1]
#         print(f"User {last_user} has been removed.")
#     else:
#         print("No users to delete.")

# # Open webcam
# video_capture = cv2.VideoCapture(0)

# if not video_capture.isOpened():
#     print("Error: Unable to access the camera.")
#     exit()

# # Initialize ID counter for new users, starting from ID 3
# user_id_counter = 3

# # To track the time when an unknown face is first detected
# unknown_faces = {}

# # Start hand tracking
# with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
#     while True:
#         ret, frame = video_capture.read()
#         if not ret:
#             break

#         # Flip the frame for a mirror effect
#         frame = cv2.flip(frame, 1)

#         # Convert BGR to RGB for face recognition
#         rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

#         # Process frame and detect hands
#         results = hands.process(rgb_frame)

#         if results.multi_hand_landmarks:
#             for hand_landmarks in results.multi_hand_landmarks:
#                 # Draw hand landmarks on the frame
#                 mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

#                 # Count the number of fingers up
#                 num_fingers = count_fingers(hand_landmarks)

#                 # If the index finger is raised, delete the last user
#                 if num_fingers == 1:  # Index finger raised
#                     delete_last_user()

#                 # Display the number of fingers
#                 cv2.putText(frame, f"Fingers: {num_fingers}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

#         # Process the frame for face recognition
#         face_locations = face_recognition.face_locations(rgb_frame)
#         face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

#         for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
#             name = "Unknown"
#             matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
#             face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

#             if len(face_distances) > 0:
#                 best_match_index = np.argmin(face_distances)
#                 if matches[best_match_index]:
#                     name = known_face_names[best_match_index]

#             if name == "Unknown":
#                 current_time = time.time()
#                 if (top, right, bottom, left) not in unknown_faces:
#                     unknown_faces[(top, right, bottom, left)] = current_time
#                     print("Unknown face detected!")

#                 if current_time - unknown_faces[(top, right, bottom, left)] > 3:
#                     new_user_image_path = os.path.join(KNOWN_FACES_DIR, f"user{user_id_counter}.jpg")
#                     cv2.imwrite(new_user_image_path, frame[top:bottom, left:right])

#                     known_face_encodings.append(face_encoding)
#                     known_face_names.append(f"User{user_id_counter}")

#                     user_id_counter += 1
#                     name = f"User{user_id_counter - 1}"

#                     del unknown_faces[(top, right, bottom, left)]
#                     print(f"New user added as {name}")

#             # Extract the detected face for emotion analysis
#             face_frame = frame[top:bottom, left:right]
#             emotion = "Unknown"
#             try:
#                 if face_frame.shape[0] > 0 and face_frame.shape[1] > 0:  # Ensure the face is valid
#                     # Resize face to be more suitable for DeepFace
#                     face_frame_resized = cv2.resize(face_frame, (224, 224))

#                     # Analyze the emotion of the resized face
#                     analysis = DeepFace.analyze(face_frame_resized, actions=["emotion"], enforce_detection=False)
#                     emotion = analysis[0]["dominant_emotion"]
#             except Exception as e:
#                 print(f"Emotion analysis error: {e}")
#                 emotion = "Error"

#             # Draw a rectangle around the face
#             cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

#             # Display the name and emotion
#             cv2.putText(frame, f"{name}, {emotion}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

#         # Display the frame with results
#         cv2.imshow("Hand Gesture + Face Recognition + Emotion", frame)

#         # Exit the program when 'q' is pressed
#         if cv2.waitKey(1) & 0xFF == ord('q'):
#             break

# # Release the camera and close windows
# video_capture.release()
# cv2.destroyAllWindows()








# ###############################
# ################################
# # name , emotion , add after unknown by gesture (pinky), delete by gesture (1) 


import cv2
import face_recognition
import numpy as np
import os
import time
import mediapipe as mp
from deepface import DeepFace  # For emotion analysis

# Directory to store known faces
KNOWN_FACES_DIR = "known_faces"
if not os.path.exists(KNOWN_FACES_DIR):
    os.makedirs(KNOWN_FACES_DIR)

# Initialize MediaPipe Hands
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

# Load known users' images
known_face_encodings = []
known_face_names = []

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

def delete_last_user():
    """Deletes the last added user image and updates the lists."""
    global known_face_encodings, known_face_names

    if len(known_face_names) > 0:
        # Remove the last user from the known_faces directory
        last_user = known_face_names[-1]
        last_user_image_path = os.path.join(KNOWN_FACES_DIR, f"{last_user}.jpg")
        if os.path.exists(last_user_image_path):
            os.remove(last_user_image_path)
            print(f"Deleted {last_user}")

        # Remove the last user from the encoding and names lists
        known_face_encodings = known_face_encodings[:-1]
        known_face_names = known_face_names[:-1]
        print(f"User {last_user} has been removed.")
    else:
        print("No users to delete.")

# Open webcam
video_capture = cv2.VideoCapture(0)

if not video_capture.isOpened():
    print("Error: Unable to access the camera.")
    exit()

# Initialize ID counter for new users, starting from ID 3
user_id_counter = 3

# To track the time when an unknown face is first detected
unknown_faces = {}

# Start hand tracking
with mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7) as hands:
    while True:
        ret, frame = video_capture.read()
        if not ret:
            break

        # Flip the frame for a mirror effect
        frame = cv2.flip(frame, 1)

        # Convert BGR to RGB for face recognition
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Process frame and detect hands
        results = hands.process(rgb_frame)

        # Only check for fingers if hands are detected
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                # Draw hand landmarks on the frame
                mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

                # Count the number of fingers up
                num_fingers = count_fingers(hand_landmarks)

                # If the index finger is raised, delete the last user
                if num_fingers == 1:  # Index finger raised
                    delete_last_user()

                # Display the number of fingers
                cv2.putText(frame, f"Fingers: {num_fingers}", (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

                # Check if pinky is raised for user registration
                pinky_up = hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_TIP].y < hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_PIP].y
                if pinky_up:
                    print("Pinky raised! Adding new user.")

        # Process the frame for face recognition
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            name = "Unknown"
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)

            if len(face_distances) > 0:
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]

            if name == "Unknown":
                current_time = time.time()
                if (top, right, bottom, left) not in unknown_faces:
                    unknown_faces[(top, right, bottom, left)] = {"time": current_time, "pinky_raised": False}
                    print("Unknown face detected!")

                if current_time - unknown_faces[(top, right, bottom, left)]["time"] > 3 and not unknown_faces[(top, right, bottom, left)]["pinky_raised"]:
                    # Wait for the user to raise their pinky before adding them
                    if pinky_up:
                        # Save the new user's image and add them to the list
                        new_user_image_path = os.path.join(KNOWN_FACES_DIR, f"user{user_id_counter}.jpg")
                        cv2.imwrite(new_user_image_path, frame[top:bottom, left:right])

                        known_face_encodings.append(face_encoding)
                        known_face_names.append(f"User{user_id_counter}")

                        user_id_counter += 1
                        name = f"User{user_id_counter - 1}"

                        unknown_faces[(top, right, bottom, left)]["pinky_raised"] = True  # Mark pinky raised
                        print(f"New user added as {name}")

            # Extract the detected face for emotion analysis
            face_frame = frame[top:bottom, left:right]
            emotion = "Unknown"
            try:
                if face_frame.shape[0] > 0 and face_frame.shape[1] > 0:  # Ensure the face is valid
                    # Resize face to be more suitable for DeepFace
                    face_frame_resized = cv2.resize(face_frame, (224, 224))

                    # Analyze the emotion of the resized face
                    analysis = DeepFace.analyze(face_frame_resized, actions=["emotion"], enforce_detection=False)
                    emotion = analysis[0]["dominant_emotion"]
            except Exception as e:
                print(f"Emotion analysis error: {e}")
                emotion = "Error"

            # Draw a rectangle around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)

            # Display the name and emotion
            cv2.putText(frame, f"{name}, {emotion}", (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

        # Display the frame with results
        cv2.imshow("Hand Gesture + Face Recognition + Emotion", frame)

        # Exit the program when 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

# Release the camera and close windows
video_capture.release()
cv2.destroyAllWindows()