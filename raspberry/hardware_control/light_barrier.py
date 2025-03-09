"""
This module contains the functions to control the Light Barrier.
"""

import platform

if platform.system() == "Linux":
    import gpiod
    from gpiod.line import Direction
    import assets
else:
    GPIOD = None

# Initialize gpiod
if platform.system() == "Linux":
    line_request = gpiod.request_lines(
        assets.CHIP,
        consumer="light_barrier",
        config={assets.SENSOR_PIN: gpiod.LineSettings(direction=Direction.INPUT)},
    )

def get_state():
    """
    Get the state of the light barrier.

    Returns:
        bool: state The of the light barrier (True if blocked, False if not blocked).
    """
    if platform.system() == "Linux":
        return line_request.get_value(assets.SENSOR_PIN) == 1
    return True  # simulated value for non-Raspberry-Pi-Systems
