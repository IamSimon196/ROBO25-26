import gpiozero as gpio

class Motor:
    def __init__(self, en_pin, in1_pin, in2_pin):
        self.en = gpio.PWMOutputDevice(en_pin)
        self.in1 = gpio.OutputDevice(in1_pin)
        self.in2 = gpio.OutputDevice(in2_pin)

    def set_speed(self, speed):
        """Set motor speed.

        Args:
            speed (float): Speed value between -1.0 (full reverse) and 1.0 (full forward).
        """
        if speed > 0:
            self.in1.on()
            self.in2.off()
            self.en.value = min(speed, 1.0)
        elif speed < 0:
            self.in1.off()
            self.in2.on()
            self.en.value = min(-speed, 1.0)
        else:
            self.in1.off()
            self.in2.off()
            self.en.value = 0.0
