import camera
import numpy as np
import cv2
import math

threshold_value = 70
#detect line center of mass in image
def detect_line_center_of_mass(image):
    """Detect the center of mass of a line in the given image."""
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    contrast = cv2.convertScaleAbs(gray, alpha=2.0, beta=0)
    # Apply Gaussian blur
    blurred = cv2.GaussianBlur(contrast, (5, 5), 0)

    # Threshold the image to get a binary image
    _, binary = cv2.threshold(blurred, threshold_value, 255, cv2.THRESH_BINARY_INV)

    # Find contours
    contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if not contours:
        return None  # No line detected

    # Assume the largest contour is the line
    largest_contour = max(contours, key=cv2.contourArea)

    # Calculate moments of the largest contour
    M = cv2.moments(largest_contour)

    if M["m00"] == 0:
        return None  # Avoid division by zero

    # Calculate center of mass
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])

    return (cX, cY)


def line_angle(x1, y1, x2, y2):
    return math.degrees(math.atan2(y2 - y1, x2 - x1))

def intersection_point(L1, L2):
    # L1 = (x1,y1,x2,y2), L2 = (x3,y3,x4,y4)
    x1,y1,x2,y2 = L1
    x3,y3,x4,y4 = L2

    denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
    if denom == 0:
        return None

    px = ((x1*y2 - y1*x2)*(x3-x4) - (x1-x2)*(x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2)*(y3-y4) - (y1-y2)*(x3*y4 - y3*x4)) / denom

    return int(px), int(py)


    # New blank mask
    filtered_edges = np.zeros_like(edges)

    min_len = 200  # minimum edge size in pixels

    for label in range(1, num_labels):  # skip 0, the background
        component = (labels == label)
        length = np.count_nonzero(component)

        if length >= min_len:
            filtered_edges[component] = 255
    edges = filtered_edges

    # Detect straight line segments
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi/180,
        threshold=50,
        minLineLength=30,
        maxLineGap=10
    )

    if lines is None:
        return []

    lines = [tuple(l[0]) for l in lines]  # unpack

    crossings = []

    # Compare every line with every other
    for i in range(len(lines)):
        for j in range(i+1, len(lines)):
            L1 = lines[i]
            L2 = lines[j]

            # Compute angles
            angle1 = line_angle(*L1)
            angle2 = line_angle(*L2)
            angle_diff = abs(angle1 - angle2)
            angle_diff = min(angle_diff, 180-angle_diff)

            # If lines are too parallel → skip
            if angle_diff < min_angle_deg:
                continue

            # Compute intersection
            point = intersection_point(L1, L2)
            if point is None:
                continue

            x, y = point


            # Check intersection is inside image
            h, w = gray.shape
            if 0 <= x < w and 0 <= y < h:
                crossings.append((x, y))

    return crossings
