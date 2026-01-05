import cv2
import os
import socket
import mjpeg_stream
import time
import motor
import PID
import camera
import line_detection

BASE_SPEED = 0.3
# store last commanded speeds so we can ramp down
last_left_speed = BASE_SPEED
last_right_speed = BASE_SPEED


def map_value(x, in_min, in_max, out_min, out_max):
    try:
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    except ZeroDivisionError:
        return out_min


def move(correction, motor_l, motor_r):
    base_speed = BASE_SPEED
    max_correction = 400

    scaled = map_value(correction, -max_correction, max_correction, -base_speed, base_speed)

    # compute target speeds in [0, 1]
    right_speed = base_speed - scaled
    left_speed = base_speed + scaled

    right_speed = max(0.0, min(1.0, right_speed))
    left_speed = max(0.0, min(1.0, left_speed))

    # set via motor objects (they handle direction)
    motor_r.set_speed(right_speed)
    motor_l.set_speed(left_speed)

    # remember last speeds for ramping down
    global last_left_speed, last_right_speed
    last_left_speed = left_speed
    last_right_speed = right_speed

    print(f"Correction: {correction}, Right Speed: {right_speed:.3f}, Left Speed: {left_speed:.3f}")


def main():
    prev_error = 0
    integral = 0
    n_crossings = 0
    crossing_cooldown = cv2.getTickFrequency() * 5
    time_of_crossing = -crossing_cooldown

    motor_r = motor.Motor(7, 23, 18)
    motor_l = motor.Motor(8, 14, 15)

    # determine local IP (Raspberry Pi IP) to bind the MJPEG server to
    def get_local_ip(fallback='0.0.0.0'):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # doesn't have to be reachable - 8.8.8.8 is used to determine the outbound iface
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return fallback

    port = int(os.environ.get('MJPEG_PORT', '8080'))
    local_ip = get_local_ip()
    try:
        mjpeg_stream.start_server(host=local_ip, port=port)
        print(f"MJPEG stream available at http://{local_ip}:{port}/")
    except Exception as e:
        print(f"Failed to start MJPEG stream on {local_ip}:{port}: {e}")

    running = True
    try:
        while running:
            try:
                frame = camera.capture_image()
            except Exception as e:
                print(f"Camera read error: {e}")
                time.sleep(0.1)
                continue

            if frame is None:
                time.sleep(0.01)
                continue

            cm = line_detection.detect_line_center_of_mass(frame)
            crossings = line_detection.detect_line_crossings(frame)
            # publish frame for MJPEG stream
            try:

                stream_frame = frame.copy()
                if crossings:
                    for crossing in crossings:
                        cv2.circle(stream_frame, crossing, 10, (0,0,255), 2)
                if cm is not None:
                    cv2.circle(stream_frame, cm, 5, (0,255,0), -1) if cm is not None else None
                mjpeg_stream.latest_frame = stream_frame

            except Exception:
		pass


            now = cv2.getTickCount()
            if crossings and (now - time_of_crossing) > crossing_cooldown:
                n_crossings += 1
                time_of_crossing = now
                print(f"Line crossing detected! Total crossings: {n_crossings}")


            if n_crossings ==6 or n_crossings ==7:
                # continue for 1 second, then slowly ramp down motors
                motor_l.set_speed(BASE_SPEED)
                motor_r.set_speed(BASE_SPEED)
                time.sleep(0.5)




            if cm is not None:
                cx, cy = cm
                correction, prev_error, integral = PID.pid(cx, prev_error, integral)
                move(correction, motor_l, motor_r)
            else:
                # No line detected → drive slowly forward
                motor_l.set_speed(BASE_SPEED)
                motor_r.set_speed(BASE_SPEED)

            # small sleep to avoid busy loop
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Interrupted, stopping motors")
    finally:
        motor_l.set_speed(0)
        motor_r.set_speed(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    # Optionally start the MJPEG stream: set environment variable ENABLE_MJPEG_STREAM=1
    if os.environ.get('ENABLE_MJPEG_STREAM') == '1':
        try:
            import mjpeg_stream
            port = int(os.environ.get('MJPEG_PORT', '8080'))
            mjpeg_stream.start_server(host='0.0.0.0', port=port)
            print(f"MJPEG stream available at http://0.0.0.0:{port}/")
        except Exception as e:
            print(f"Failed to start MJPEG stream: {e}")

    main()
