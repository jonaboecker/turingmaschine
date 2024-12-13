"""
This module contains the Functions to control the Stepper Motors.
"""
# pylint: todo: disable=fixme

import assets


class StepperMotorController:
    """
    This class is used to control the Stepper Motors.
    """
    def __init__(self):
        self.current_position = 0

    @staticmethod
    def toggle_io_band():
        """Toggles the io_band to toggle state (color)."""
        # todo: implement the toggle
        print("Toggling the band")

    def move_robot(self, direction: assets.ROBOT_DIRECTIONS, speed = 1, steps=1):
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
        print(f"Moving the robot {direction} by {steps} steps with speed {speed}")
        return True
