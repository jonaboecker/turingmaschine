"""
This module contains the functions to control the Light Barrier.
"""

import platform

# Import RPi.GPIO (just supported on RPi) or fake_rpi.RPi.GPIO based on the platform
import importlib

if platform.system() == "Linux":
    GPIO = importlib.import_module("RPi.GPIO")
else:
    GPIO = None

# GPIO pin for the light barrier
SENSOR_PIN = 17

# Initialize GPIO
if platform.system() == "Linux":
    GPIO.setmode(GPIO.BCM)  # Use BCM pin numbering
    GPIO.setup(SENSOR_PIN, GPIO.IN)  # Configure the pin as an input

def get_state():
    """
    Get the state of the light barrier.

    Returns:
        bool: state The of the light barrier (True if blocked, False if not blocked).
    """
    if platform.system() == "Linux":
        return GPIO.input(SENSOR_PIN) == 1
    else:
        return True # Return True for testing on non-Raspberry Pi platforms
