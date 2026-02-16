from robot_api_serial import RobotAPISerial
import time

robot = RobotAPISerial("/dev/ttyUSB0")

try:
    robot.drive_for(1.0, 1.0, 2.0)
    robot.stop()
    time.sleep(1)

    robot.drive_for(-0.5, 0.5, 2.0)
    robot.stop()
    time.sleep(1)

    robot.servo_1(130)
    time.sleep(1)

    robot.servo_1(160)
    time.sleep(1)

finally:
    robot.close()
