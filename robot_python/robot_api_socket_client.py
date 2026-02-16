import socket
import time


class RobotAPISocketClient:
    """
    Client-side Robot API.
    Can be run on the robot or on your own laptop.
    """

    def __init__(self, ip, port=3000):
        self.ip = ip
        self.port = port

    # --------------------------------------------------
    # Low-level send
    # --------------------------------------------------

    def _send(self, msg: str):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            sock.connect((self.ip, self.port))
            sock.sendall(msg.encode())
        finally:
            sock.close()

    # --------------------------------------------------
    # Speed mapping
    # --------------------------------------------------

    @staticmethod
    def _speed_to_percent(speed: float) -> int:
        """
        Convert -1.0..1.0 → -100..100
        """
        speed = max(-1.0, min(1.0, speed))
        return int(speed * 100)

    # --------------------------------------------------
    # Motion API (same semantics as serial)
    # --------------------------------------------------

    def set_wheel_speeds(self, left: float, right: float):
        l = self._speed_to_percent(left)
        r = self._speed_to_percent(right)

        if l == r:
            if l > 0:
                self._send("F")
            elif l < 0:
                self._send("B")
            else:
                self._send("S")
        else:
            if l < r:
                self._send("L")
            else:
                self._send("R")

    def set_speed(self, speed: int):
        speed = max(0, min(100, speed))
        self._send(f"S{speed}")

    def stop(self):
        self._send("S")

    # --------------------------------------------------
    # Servo control
    # --------------------------------------------------

    def servo_1(self, value: int):
        self._send(f":S1={value}!")

    def servo_2(self, value: int):
        self._send(f":S2={value}!")

    def servo_3(self, value: int):
        self._send(f":S3={value}!")

    def servo_4(self, value: int):
        self._send(f":S4={value}!")

    def close(self):
        # nothing persistent to close
        pass
