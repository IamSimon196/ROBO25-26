import threading
import socketserver
import http.server
import time
import cv2

# Shared latest frame set by the main loop. Handlers will serve this frame.
latest_frame = None


class MJPEGHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path != "/":
            self.send_error(404)
            return

        self.send_response(200)
        self.send_header('Age', '0')
        self.send_header('Cache-Control', 'no-cache, private')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=--jpgboundary')
        self.end_headers()

        boundary = "--jpgboundary"
        try:
            while True:
                frame = latest_frame
                if frame is None:
                    time.sleep(0.05)
                    continue

                # encode to JPEG
                ret, jpg = cv2.imencode('.jpg', frame)
                if not ret:
                    time.sleep(0.05)
                    continue

                data = jpg.tobytes()

                self.wfile.write((boundary + '\r\n').encode())
                self.wfile.write(b'Content-Type: image/jpeg\r\n')
                self.wfile.write(f'Content-Length: {len(data)}\r\n\r\n'.encode())
                self.wfile.write(data)
                self.wfile.write(b'\r\n')

                # small sleep to limit frame rate
                time.sleep(0.05)
        except Exception:
            # client disconnected or other error — just exit
            return


class ThreadedHTTPServer(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def start_server(host='0.0.0.0', port=8080):
    server = ThreadedHTTPServer((host, port), MJPEGHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread


if __name__ == '__main__':
    srv, th = start_server()
    print(f'MJPEG stream started at http://0.0.0.0:8080/')
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        srv.shutdown()

