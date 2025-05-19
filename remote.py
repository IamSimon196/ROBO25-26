import curses
import os
from gpiozero import PWMOutputDevice, DigitalOutputDevice
from time import sleep

ENA = PWMOutputDevice(8)  # Left motor speed
ENB = PWMOutputDevice(7)  # Right motor speed

IN1 = DigitalOutputDevice(14)  # Left motor forward
IN2 = DigitalOutputDevice(15)  # Left motor backward
IN3 = DigitalOutputDevice(18)  # Right motor forward
IN4 = DigitalOutputDevice(23)  # Right motor backward

print("Motor system initialized")

def move_forward():
    print("Moving Forward")
    ENA.value = 0.8
    ENB.value = 0.8
    IN1.on()
    IN2.off()
    IN3.on()
    IN4.off()

def move_backward():
    print("Moving Backward")
    ENA.value = 0.8
    ENB.value = 0.8
    IN1.off()
    IN2.on()
    IN3.off()
    IN4.on()

def turn_right():
    print("Turning Left")
    ENA.value = 0.6
    ENB.value = 0.8
    IN1.off()
    IN2.on()
    IN3.on()
    IN4.off()

def turn_left():
    print("Turning Right")
    ENA.value = 0.8
    ENB.value = 0.6
    IN1.on()
    IN2.off()
    IN3.off()
    IN4.on()

def stop():
    print("Stopping")
    ENA.value = 0
    ENB.value = 0
    IN1.off()
    IN2.off()
    IN3.off()
    IN4.off()

screen = curses.initscr()
curses.noecho()
curses.cbreak()
curses.halfdelay(3)
screen.keypad(True)

try:
    while True:
        char = screen.getch()
        screen.addstr(2, 0, f"Key pressed: {char}")
        screen.refresh()

        if char == ord('q'):
            stop()
            break
        elif char == ord('p'):
            stop()
            curses.nocbreak()
            screen.keypad(0)
            curses.echo()
            curses.endwin()
            os.system('sudo halt')
        elif char == curses.KEY_UP: 
            move_forward()
        elif char == curses.KEY_DOWN: 
            move_backward()
        elif char == curses.KEY_LEFT:  
            turn_left()
        elif char == curses.KEY_RIGHT:  
            turn_right()
        else:
            stop()

finally:
    curses.nocbreak()
    screen.keypad(0)
    curses.echo()
    curses.endwin()
    stop()
