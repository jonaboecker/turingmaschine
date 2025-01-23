"""
This module contains the functions to control the stepper motors.
"""

# pylint: todo: disable=fixme
import time
import platform

# Import RPi.GPIO (just supported on RPi) or fake_rpi.RPi.GPIO based on the platform
import importlib
from time import sleep

import assets

if platform.system() == "Linux":
    GPIO = importlib.import_module("RPi.GPIO")
else:
    GPIO = None

# Pin Configuration
STEP_PIN = 19  # STEP-Pin of A4988 on GPIO19 (Pin 35)
DIR_PIN = 20  # DIR-Pin of A4988 on GPIO20 (Pin 38)
ENABLE_PIN = 26  # ENABLE-Pin of A4988 on GPIO26 (Pin 37)

STEPS_PER_REV = 200  # Steps per revolution (e.g., 1.8° stepper motor)
DEFAULT_DELAY = 0.01  # Default delay between pulses (controls speed)


class StepperMotorController:
    """
    This class is used to control the stepper motors.
    """

    def __init__(self):
        self.current_position = 0
        if platform.system() == "Linux":
            self.setup_pins()

    @staticmethod
    def setup_pins():
        """Sets up the GPIO pins for the stepper motor."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(STEP_PIN, GPIO.OUT)
        GPIO.setup(DIR_PIN, GPIO.OUT)
        GPIO.setup(ENABLE_PIN, GPIO.OUT)

        GPIO.output(ENABLE_PIN, GPIO.LOW)  # Enable the motor driver

    @staticmethod
    def cleanup():
        """Cleans up the GPIO pins."""
        GPIO.output(ENABLE_PIN, GPIO.HIGH)
        GPIO.cleanup()

    def rotate(self, steps, direction, delay=DEFAULT_DELAY):
        """
        Rotates the motor by a specified number of steps in the given direction.

        Args:
            steps (int): Number of steps to move.
            direction (str): "LEFT" or "RIGHT" to set rotation direction.
            delay (float): Delay between each step (controls speed).
        """
        GPIO.output(
            DIR_PIN,
            GPIO.HIGH if direction == assets.ROBOT_DIRECTIONS.RIGHT else GPIO.LOW,
        )

        for _ in range(steps):
            GPIO.output(STEP_PIN, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(STEP_PIN, GPIO.LOW)
            time.sleep(delay)

        self.current_position += (
            steps if direction == assets.ROBOT_DIRECTIONS.RIGHT else -steps
        )

    def move_robot(self, direction: assets.ROBOT_DIRECTIONS, speed=1, steps=1):
        """
        Moves the robot in the specified direction by the specified amount of steps.
        :return: False if the robot would move out of the LED strip.

        Args:
            direction (Enum): The direction in which the robot should move
            Enum('Direction', [('LEFT', 1), ('RIGHT', 2)]).
            speed (int): The speed of the robot.
            steps (int): The amount of steps the robot should move.
        """
        if direction == assets.ROBOT_DIRECTIONS.LEFT:
            self.current_position -= steps
        elif direction == assets.ROBOT_DIRECTIONS.RIGHT:
            self.current_position += steps
        if self.current_position < 0 or self.current_position > assets.LED_AMOUNT:
            return False
        # todo: implement the movement with correct speed

        if platform.system() == "Linux":
            self.rotate(steps, direction.name)
        else:
            sleep(5 / speed)
        print(f"Moving the robot {direction} by {steps} steps with speed {speed}")
        return True

    @staticmethod
    def toggle_io_band():
        """Toggles the IO band state."""
        # TODO: Implement the toggle functionality
        print("Toggling the IO band")


# if __name__ == "__main__":
#    try:
#       motor = StepperMotorController()
#        print("Motor rotating one full revolution...")
#        motor.rotate(STEPS_PER_REV, "RIGHT", DEFAULT_DELAY)
#        print("Rotation completed.")
#    except KeyboardInterrupt:
#        print("Operation interrupted by user.")
#    finally:
#        motor.cleanup()
