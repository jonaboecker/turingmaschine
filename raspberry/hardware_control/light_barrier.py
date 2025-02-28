"""
This module contains the functions to control the Light Barrier.
"""

import platform

if platform.system() == "Linux":
    import gpiod
    from gpiod.line import Direction
else:
    GPIOD = None

# gpiod pin for the light barrier
SENSOR_PIN = 17
CHIP = "/dev/gpiochip4"  # Standard GPIO-Chip auf dem Raspberry Pi 5

# Initialize gpiod
if platform.system() == "Linux":
    line_request = gpiod.request_lines(
        CHIP,
        consumer="light_barrier",
        config={SENSOR_PIN: gpiod.LineSettings(direction=Direction.INPUT)},
    )

def get_state():
    """
    Get the state of the light barrier.

    Returns:
        bool: state The of the light barrier (True if blocked, False if not blocked).
    """
    if platform.system() == "Linux":
        return line_request.get_value(SENSOR_PIN) == 1
    return True  # Simulierter Wert für Nicht-Raspberry-Pi-Systeme
