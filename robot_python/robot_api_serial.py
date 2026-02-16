import serial
import time
import threading


class RobotAPISerial:
    """
    Robot API for direct serial communication with the Arduino.

    Features:
    - Motor control (ML / MR)
    - Servo control (S1–S4)
    - Automatic watchdog handling in a background thread
    """

    def __init__(
        self,
        port="/dev/ttyUSB0",
        baudrate=9600,
        watchdog_interval=0.2,
        auto_watchdog=True,
    ):
        """
        Initialize the serial connection and optionally start the watchdog.

        :param port: Serial device (e.g. /dev/ttyUSB0)
        :param baudrate: Baudrate, must match Arduino (9600)
        :param watchdog_interval: Time between watchdog updates in seconds
        :param auto_watchdog: Start watchdog thread automatically
        """
        self.ser = serial.Serial(port, baudrate, timeout=1)

        # Give the Arduino time to reset after opening the serial port
        time.sleep(2)

        self._running = True
        self._lock = threading.Lock()
        self._wd_val = 0
        self._watchdog_interval = watchdog_interval

        if auto_watchdog:
            self._watchdog_thread = threading.Thread(
                target=self._watchdog_loop, daemon=True
            )
            self._watchdog_thread.start()

    # ------------------------------------------------------------------
    # Low-level communication
    # ------------------------------------------------------------------

    def _send(self, cmd: str):
        """
        Send a raw command string to the Arduino.
        """
        with self._lock:
            self.ser.write(cmd.encode())

    def _watchdog_loop(self):
        """
        Periodically toggle the watchdog value.

        The Arduino requires the watchdog value to change at least every
        500 ms, otherwise it will stop the motors.
        """
        while self._running:
            self._wd_val = 0 if self._wd_val == 1 else 1
            self._send(f":WD={self._wd_val}!")
            time.sleep(self._watchdog_interval)

    @staticmethod
    def _speed_to_val(speed: float) -> int:
        """
        Convert a normalized speed (-1.0 .. 1.0) to the Arduino value (0 .. 310).

        155 corresponds to stop.
        """
        if abs(speed) < 0.05:
            return 155
        return int((speed + 1.0) * 155)

    # ------------------------------------------------------------------
    # Motor API
    # ------------------------------------------------------------------

    def set_left_speed(self, speed: float):
        """
        Set left motor speed.

        :param speed: -1.0 (full backward) .. 1.0 (full forward)
        """
        val = self._speed_to_val(speed)
        self._send(f":ML={val}!")

    def set_right_speed(self, speed: float):
        """
        Set right motor speed.

        :param speed: -1.0 (full backward) .. 1.0 (full forward)
        """
        val = self._speed_to_val(speed)
        self._send(f":MR={val}!")

    def set_wheel_speeds(self, left: float, right: float):
        """
        Set both wheel speeds.

        :param left: Left motor speed (-1.0 .. 1.0)
        :param right: Right motor speed (-1.0 .. 1.0)
        """
        self.set_left_speed(left)
        time.sleep(0.01)
        self.set_right_speed(right)
        time.sleep(0.12)

    def drive_for(self, left, right, duration):
        """
        Drive for a fixed duration and send command to Arduino continuously.

        :param left: Left motor speed (-1.0 .. 1.0)
        :param right: Right motor speed (-1.0 .. 1.0)
        :param duration: Duration in seconds.
        """
        t_end = time.time() + duration
        while time.time() < t_end:
            self.set_wheel_speeds(left, right)
            time.sleep(0.1)

    def stop(self):
        """
        Stop both motors.
        """
        for _ in range(3):
            self.set_wheel_speeds(0.0, 0.0)
            time.sleep(0.12)

    # ------------------------------------------------------------------
    # Servo API
    # ------------------------------------------------------------------

    def set_servo(self, servo_id: int, value: int):
        """
        Set a servo position.

        :param servo_id: Servo index (1..4)
        :param value: Servo target value (angle or raw value)
        """
        if servo_id not in (1, 2, 3, 4):
            raise ValueError("servo_id must be between 1 and 4")

        self._send(f":S{servo_id}={int(value)}!")
        time.sleep(0.12)

    def servo_1(self, value: int):
        self.set_servo(1, value)

    def servo_2(self, value: int):
        self.set_servo(2, value)

    def servo_3(self, value: int):
        self.set_servo(3, value)

    def servo_4(self, value: int):
        self.set_servo(4, value)

    # ------------------------------------------------------------------
    # Cleanup
    # ------------------------------------------------------------------

    def close(self):
        """
        Stop the watchdog, stop the motors and close the serial connection.
        """
        self._running = False
        time.sleep(0.2)
        self.stop()
        self.ser.close()
