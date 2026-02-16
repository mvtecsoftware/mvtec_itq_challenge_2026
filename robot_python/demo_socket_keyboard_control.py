import keyboard
import time

from robot_api_socket_client import RobotAPISocketClient

ROBOT_IP = "192.168.178.22"
ROBOT_PORT = 3000

speed = 0.8  # normalized speed (0.0 … 1.0)

print("W/A/S/D = move | R/F = speed +/- | Q = quit")

robot = RobotAPISocketClient(ROBOT_IP, ROBOT_PORT)

try:
    while True:

        # Speed control
        if keyboard.is_pressed('r'):
            speed = min(1.0, speed + 0.05)
            print(f"Speed: {speed:.2f}")
            time.sleep(0.2)

        if keyboard.is_pressed('f'):
            speed = max(0.0, speed - 0.05)
            print(f"Speed: {speed:.2f}")
            time.sleep(0.2)

        # Motion
        if keyboard.is_pressed("w"):
            robot.set_wheel_speeds(speed, speed)

        elif keyboard.is_pressed("s"):
            robot.set_wheel_speeds(-speed, -speed)

        elif keyboard.is_pressed("a"):
            robot.set_wheel_speeds(-speed, speed)

        elif keyboard.is_pressed("d"):
            robot.set_wheel_speeds(speed, -speed)

        elif keyboard.is_pressed("q"):
            robot.stop()
            print("Exiting...")
            break

        else:
            robot.stop()

        time.sleep(0.02)

finally:
    robot.stop()
    robot.close()
