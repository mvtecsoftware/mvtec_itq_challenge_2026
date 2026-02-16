import socket
import serial
import threading
import time


class RobotAPISocket:
    """
    Robot API that bridges TCP socket commands to Arduino serial commands.
    Run this on the robot.
    """

    def __init__(
        self,
        listen_ip="0.0.0.0",
        listen_port=3000,
        serial_port="/dev/ttyUSB0",
        baudrate=9600,
        watchdog_interval=0.2,
        motor_interval=0.1,
    ):
        # --- Serial connection ---
        self.ser = serial.Serial(serial_port, baudrate, timeout=1)
        time.sleep(2)  # Arduino reset

        self._lock = threading.Lock()
        self.running = True

        # --- Motion state ---
        self.speed = 80  # 0–100
        self.left = 0
        self.right = 0

        # --- Socket server ---
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((listen_ip, listen_port))
        self.server.listen(1)

        # --- Watchdog ---
        self._wd_val = 0
        self._watchdog_interval = watchdog_interval

        threading.Thread(
            target=self._watchdog_loop, daemon=True
        ).start()

        # --- Motor refresh ---
        self._motor_interval = motor_interval
        threading.Thread(
            target=self._motor_loop, daemon=True
        ).start()

    # --------------------------------------------------
    # Low-level serial
    # --------------------------------------------------

    def _send_serial(self, cmd: str):
        with self._lock:
            self.ser.write(cmd.encode())

    @staticmethod
    def _speed_to_val(speed: int) -> int:
        speed = max(-100, min(100, speed))
        return int((speed + 100) * 310 / 200)

    # --------------------------------------------------
    # Background loops
    # --------------------------------------------------

    def _watchdog_loop(self):
        while self.running:
            self._wd_val ^= 1
            self._send_serial(f":WD={self._wd_val}!")
            time.sleep(self._watchdog_interval)

    def _motor_loop(self):
        while self.running:
            self._send_serial(f":ML={self._speed_to_val(self.left)}!")
            self._send_serial(f":MR={self._speed_to_val(self.right)}!")
            time.sleep(self._motor_interval)

    # --------------------------------------------------
    # Command handling
    # --------------------------------------------------

    def handle_command(self, cmd: str):
        cmd = cmd.strip()

        if cmd.startswith("S") and len(cmd) > 1:
            try:
                self.speed = max(0, min(100, int(cmd[1:])))
            except ValueError:
                pass
            return

        if cmd == "F":
            self.left = self.speed
            self.right = self.speed

        elif cmd == "B":
            self.left = -self.speed
            self.right = -self.speed

        elif cmd == "L":
            self.left = -self.speed
            self.right = self.speed

        elif cmd == "R":
            self.left = self.speed
            self.right = -self.speed

        elif cmd == "S":
            self.left = 0
            self.right = 0

        # Servo passthrough
        elif cmd.startswith(":S"):
            self._send_serial(cmd)

    # --------------------------------------------------
    # Socket server loop
    # --------------------------------------------------

    def serve_forever(self):
        print("Robot API socket server running...")
        while self.running:
            conn, _ = self.server.accept()
            try:
                data = conn.recv(1024).decode()
                if data:
                    self.handle_command(data)
            finally:
                conn.close()

    # --------------------------------------------------
    # Cleanup
    # --------------------------------------------------

    def close(self):
        self.running = False
        time.sleep(0.3)
        self.left = 0
        self.right = 0
        time.sleep(0.2)
        self.ser.close()
        self.server.close()


if __name__ == "__main__":
    server = RobotAPISocket()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server.close()
