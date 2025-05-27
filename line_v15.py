import cv2
import numpy as np
from gpiozero import DigitalOutputDevice, PWMOutputDevice
import time

IN1 = DigitalOutputDevice(18)  # Right motor forward
IN2 = DigitalOutputDevice(23)  # Right motor backward
IN3 = DigitalOutputDevice(14)  # Left motor forward
IN4 = DigitalOutputDevice(15)  # Left motor backward
ENA = PWMOutputDevice(8)  # Right motor speed
ENB = PWMOutputDevice(7)  # Left motor speed

Kp = 1.4
Ki = 0.1
Kd = 0.7

prev_error = 0
integral = 0

cap = cv2.VideoCapture(0)
cap.set(3, 1280) 
cap.set(4, 720)   



def map_value(x, in_min, in_max, out_min, out_max):
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min

def pid(cx, prev_error, integral):
    setpoint = 640 
    error = cx - setpoint
    integral += error

    integral = max(-1000, min(1000, integral)) 
    derivative = error - prev_error


    correction = Kp * error + Ki * integral + Kd * derivative
    correction = max(-400, min(400, correction))

    return correction, error, integral

def move(correction):
    base_speed = 0.7  
    max_correction = 400 

    scaled = map_value(correction, -max_correction, max_correction, -base_speed, base_speed)

    right_speed = base_speed - scaled
    left_speed = base_speed + scaled


    right_speed = max(0, min(1, right_speed))
    left_speed = max(0, min(1, left_speed))

    ENA.value = right_speed
    ENB.value = left_speed

    IN1.on()
    IN2.off()
    IN3.on()
    IN4.off()

    print(f"Correction: {correction}, Right Speed: {right_speed}, Left Speed: {left_speed}")

while True:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame")
        continue
    
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    _, mask = cv2.threshold(gray, 60, 255, cv2.THRESH_BINARY_INV)  

    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    if contours:
        c = max(contours, key=cv2.contourArea)
        M = cv2.moments(c)

        if M["m00"] != 0:
            cx = int(M['m10'] / M['m00'])
            correction, prev_error, integral = pid(cx, prev_error, integral)
            move(correction)
            
    else:
        print("No line detected")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        IN1.off()
        IN2.off()
        IN3.off()
        IN4.off()
        break

cap.release()
cv2.destroyAllWindows()
