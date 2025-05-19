import cv2
import numpy as np
from gpiozero import DigitalOutputDevice, PWMOutputDevice
import time

# Define motor control pins using gpiozero
IN1 = DigitalOutputDevice(18)  # Right motor forward
IN2 = DigitalOutputDevice(23)  # Right motor backward
IN3 = DigitalOutputDevice(14)  # Left motor forward
IN4 = DigitalOutputDevice(15)  # Left motor backward
ENA = PWMOutputDevice(13)  # Right motor speed
ENB = PWMOutputDevice(12)  # Left motor speed

# PID constants
Kp = 0.02  # Proportional gain
Ki = 0.001  # Integral gain
Kd = 0.07  # Derivative gain

prev_error = 0
integral = 0

cap = cv2.VideoCapture(0)
cap.set(3, 160)
cap.set(4, 120)

while True:
    ret, frame = cap.read()
    low_b = np.array([5, 5, 5], dtype=np.uint8)
    high_b = np.array([0, 0, 0], dtype=np.uint8)
    mask = cv2.inRange(frame, high_b, low_b)

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if contours:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        if M["m00"] != 0:
            cx = int(M['m10'] / M['m00'])
            cy = int(M['m01'] / M['m00'])

            error = cx - 80  # 80 is the center of the frame
            integral += error
            derivative = error - prev_error

            correction = Kp * error + Ki * integral + Kd * derivative
            prev_error = error

            # Adjust motor speeds using PID output
            right_speed = max(0, min(1, 0.5 - correction))
            left_speed = max(0, min(1, 0.5 + correction))

            ENA.value = right_speed
            ENB.value = left_speed

            print(f"CX: {cx}, Error: {error}, Correction: {correction}")
            print(f"Right Speed: {right_speed}, Left Speed: {left_speed}")

            # Movement logic updated
            if error > 5:
                print("Turn Right")
                IN1.on()
                IN2.off()
                IN3.off()
                IN4.on()
            elif -5 <= error <= 5:
                print("On Track!")
                IN1.on()
                IN2.off()
                IN3.on()
                IN4.off()
            else:
                print("Turn Left")
                IN1.off()
                IN2.on()
                IN3.on()
                IN4.off()

    else:
        print("I don't see the line")
        IN1.off()
        IN2.off()
        IN3.off()
        IN4.off()

    if cv2.waitKey(1) & 0xFF == ord('q'):
        IN1.off()
        IN2.off()
        IN3.off()
        IN4.off()
        break

cap.release()
cv2.destroyAllWindows()
