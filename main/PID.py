Kp = 1.2
Ki = 0.5
Kd = 0.6


def pid(cx, prev_error, integral, setpoint=320):
    """Simple PID that returns (correction, error, integral).

    The correction is clamped to +/-400 and negated (keeps previous behavior).
    """
    error = (cx - setpoint) * 2
    integral += error

    # anti-windup
    integral = max(-1000, min(1000, integral))

    derivative = error - prev_error

    correction = Kp * error + Ki * integral + Kd * derivative

    # clamp and invert sign to match original behavior
    correction = -max(-400, min(400, correction))

    return correction, error, integral
