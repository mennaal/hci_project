import cv2
import mediapipe as mp
import numpy as np
import csv
from datetime import datetime

# Initialize MediaPipe Face Mesh
mp_face_mesh = mp.solutions.face_mesh

# Screen dimensions (adjust these to match your screen)
screen_width = 1920
screen_height = 1080

# Create a log file for gaze tracking
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
csv_filename = f"gaze_tracking_{timestamp}.csv"
with open(csv_filename, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(["Frame", "Screen_X", "Screen_Y"])  # CSV header

def normalize_eye_coordinates(iris, eye_corners, frame_width, frame_height):
    """
    Normalize iris coordinates relative to eye bounding box.
    Args:
    - iris: Landmark of the iris center (x, y).
    - eye_corners: Eye region corners (landmarks for left/right eye corners).
    - frame_width, frame_height: Dimensions of the video frame.

    Returns:
    - Normalized (x, y) in range [0, 1].
    """
    eye_min_x = min(eye_corners[0].x, eye_corners[1].x) * frame_width
    eye_max_x = max(eye_corners[0].x, eye_corners[1].x) * frame_width
    eye_min_y = min(eye_corners[0].y, eye_corners[1].y) * frame_height
    eye_max_y = max(eye_corners[0].y, eye_corners[1].y) * frame_height

    iris_x = iris.x * frame_width
    iris_y = iris.y * frame_height

    normalized_x = (iris_x - eye_min_x) / (eye_max_x - eye_min_x)
    normalized_y = (iris_y - eye_min_y) / (eye_max_y - eye_min_y)

    return normalized_x, normalized_y

def map_to_screen(normalized_x, normalized_y, screen_width, screen_height):
    """
    Map normalized gaze coordinates to screen space.
    Args:
    - normalized_x, normalized_y: Normalized coordinates in range [0, 1].
    - screen_width, screen_height: Dimensions of the screen.

    Returns:
    - Screen coordinates (x, y).
    """
    screen_x = int(normalized_x * screen_width)
    screen_y = int(normalized_y * screen_height)
    return screen_x, screen_y

# Start video capture
cap = cv2.VideoCapture(0)

gaze_points = []  # Store gaze points for heatmap
frame_counter = 0

with mp_face_mesh.FaceMesh(
    max_num_faces=1,
    refine_landmarks=True,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
) as face_mesh:
    while cap.isOpened():
        success, frame = cap.read()
        if not success:
            print("Ignoring empty frame.")
            break

        frame_counter += 1
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_height, frame_width = frame.shape[:2]

        results = face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                # Get landmarks for left and right iris
                left_iris = face_landmarks.landmark[468]  # Adjust index if needed
                right_iris = face_landmarks.landmark[473]

                # Get landmarks for eye corners
                left_eye_corners = [face_landmarks.landmark[33], face_landmarks.landmark[133]]
                right_eye_corners = [face_landmarks.landmark[362], face_landmarks.landmark[263]]

                # Normalize gaze points for both eyes
                left_normalized = normalize_eye_coordinates(left_iris, left_eye_corners, frame_width, frame_height)
                right_normalized = normalize_eye_coordinates(right_iris, right_eye_corners, frame_width, frame_height)

                # Average normalized gaze points
                normalized_x = (left_normalized[0] + right_normalized[0]) / 2
                normalized_y = (left_normalized[1] + right_normalized[1]) / 2

                # Map to screen coordinates
                screen_x, screen_y = map_to_screen(normalized_x, normalized_y, screen_width, screen_height)
                gaze_points.append((screen_x, screen_y))

                # Log gaze point to CSV
                with open(csv_filename, mode="a", newline="") as file:
                    writer = csv.writer(file)
                    writer.writerow([frame_counter, screen_x, screen_y])

                # Visualize gaze point on frame
                cv2.circle(frame, (screen_x, screen_y), 5, (0, 255, 0), -1)
                cv2.putText(
                    frame, f"Gaze: ({screen_x}, {screen_y})",
                    (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2
                )

        # Display the frame
        cv2.imshow("Gaze Tracking", frame)

        # Exit on ESC
        if cv2.waitKey(5) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()

# Generate Heatmap
heatmap = np.zeros((screen_height, screen_width), dtype=np.uint32)
for x, y in gaze_points:
    if 0 <= x < screen_width and 0 <= y < screen_height:
        heatmap[y, x] += 1

heatmap = heatmap.astype(np.float32)

# Normalize and save heatmap
heatmap = cv2.normalize(heatmap, None, 0, 255, cv2.NORM_MINMAX)
heatmap = np.uint8(heatmap)
heatmap_color = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)

cv2.imwrite("gaze_heatmap.png", heatmap_color)
cv2.imshow("Gaze Heatmap", heatmap_color)
cv2.waitKey(0)
cv2.destroyAllWindows()