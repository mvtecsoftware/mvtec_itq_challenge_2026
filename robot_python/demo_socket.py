from robot_api_socket_client import RobotAPISocketClient
import time

robot = RobotAPISocketClient(ip="192.168.178.22", port=3000)

try:
    robot.set_speed(80)

    robot.set_wheel_speeds(1.0, 1.0)
    time.sleep(2)

    robot.stop()
    time.sleep(1)

    robot.set_wheel_speeds(-0.5, 0.5)
    time.sleep(2)

    robot.stop()
    time.sleep(1)

    robot.servo_1(130)
    time.sleep(1)

    robot.servo_1(160)
    time.sleep(1)

finally:
    robot.stop()
