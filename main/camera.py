import cv2
import numpy as np

def capture_image(camera_index=0):
    """Capture a single image from the specified camera."""
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        raise ValueError("Could not open camera.")

    ret, frame = cap.read()
    cap.release()
    frame = np.array(frame)

    if not ret:
        raise ValueError("Could not read frame from camera.")

    #downsize image for performance
    frame = cv2.resize(frame, (0, 0), fx=1.0, fy=1.0)
    return frame
