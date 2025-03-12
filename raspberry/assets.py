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

# the amount of retries for the robot to toggle the io band before giving up
TOGGLE_IO_BAND_RETRYS = 10

# Path to the configuration file for dynamically changing the configuration
CONFIG_PATH = 'static/config.json'

# directions the robot can move
ROBOT_DIRECTIONS = Enum('Direction', [('LEFT', 1), ('RIGHT', 2), ('HOLD', 3)])

# Light barrier configuration
SENSOR_PIN = 18 # gpiod pin for the light barrier
CHIP = "/dev/gpiochip0"  # Standard GPIO-Chip auf dem Raspberry Pi 5

# arduino communication configuration
SERIAL_PORT = "/dev/ttyACM0"
BAUDRATE = 9600
TIMEOUT = 30
