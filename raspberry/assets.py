"""
The file contains the configuration of the project.
"""
from enum import Enum

# folder where uploaded files are stored
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'txt'}

# possible program languages
PROGRAM_LANGUAGES = Enum('Language',
                         [
                             ('COM', 'turingmachinesimulator.com'),
                             ('IO', 'turingmachine.io')
                         ])

# colors of the io band
IO_BAND_COLORS = Enum('Color', [('RED', 0), ('BLUE', 1), ('BLANK', 2)])

# LEDs
LED_AMOUNT = 60
STEPS_BETWEEN_LEDS = 13
STEPS_BETWEEN_HOME_TO_FIRST_LED = 20

# directions the robot can move
ROBOT_DIRECTIONS = Enum('Direction', [('LEFT', 1), ('RIGHT', 2), ('HOLD', 3)])

# the amount of retries for the robot to toggle the io band before giving up
TOGGLE_IO_BAND_RETRYS = 10
