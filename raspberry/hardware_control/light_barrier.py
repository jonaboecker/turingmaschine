"""
This module contains the functions to control the Light Barrier.
"""

import platform

if platform.system() == "Linux":
    import gpiod
else:
    GPIOD = None

# GPIO pin for the light barrier
SENSOR_PIN = 17
CHIP = "/dev/gpiochip4"  # Standard GPIO-Chip auf dem Raspberry Pi 5

# Initialize GPIO
if platform.system() == "Linux":
    chip = gpiod.Chip(CHIP)
    line = chip.get_line(SENSOR_PIN)
    line.request(consumer="light_barrier", type=gpiod.LINE_REQ_DIR_IN)

def get_state():
    """
    Get the state of the light barrier.

    Returns:
        bool: state The of the light barrier (True if blocked, False if not blocked).
    """
    if platform.system() == "Linux":
        return line.get_value() == 1
    return True  # Simulierter Wert für Nicht-Raspberry-Pi-Systeme
