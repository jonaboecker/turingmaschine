"""
This module contains the Functions to control the Color Sensor.
"""

# pylint: todo: disable=fixme

import time
import platform

# Import RPi.GPIO (just supported on RPi) or fake_rpi.RPi.GPIO based on the platform
import importlib
from random import randrange

import assets

if platform.system() == "Linux":
    GPIO = importlib.import_module("RPi.GPIO")
else:
    GPIO = importlib.import_module("fake_rpi.RPi.GPIO")

def get_color():
    """
    Get the color from the color sensor.

    Returns:
        Enum: The detected color Enum('Color', [('RED', 1), ('BLUE', 2), ('BLANK', 3)]) from assets.
    """
    # todo: implement the color detection
    # return random color for testing
    random_color = assets.IO_BAND_COLORS(randrange(3))
    print(f"Random detected and returned color: {random_color}")
    return random_color

# GPIO Pins
S2 = 22
S3 = 23
SIGNAL = 18

# Constants
NUM_CYCLES = 25

# Color thresholds
RED_THRESHOLD = 1500
BLUE_THRESHOLD = 1500


def setup():
    """Setup GPIO pins for the color sensor."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SIGNAL, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(S2, GPIO.OUT)
    GPIO.setup(S3, GPIO.OUT)
    print("GPIO setup completed.")


def measure_channel(s2_val, s3_val):
    """
    Measure the frequency for a specific color channel.

    Args:
        s2_val (bool): Value to set for the S2 pin (LOW or HIGH).
        s3_val (bool): Value to set for the S3 pin (LOW or HIGH).

    Returns:
        float: The frequency measured for the specified channel.
    """
    GPIO.output(S2, s2_val)
    GPIO.output(S3, s3_val)
    time.sleep(0.3)  # Short delay to stabilize the sensor
    start = time.time()  # Record the start time for measurement
    for _ in range(NUM_CYCLES):
        GPIO.wait_for_edge(SIGNAL, GPIO.FALLING)  # Wait for a falling edge signal
    duration = time.time() - start  # Calculate the duration of the measurement
    return NUM_CYCLES / duration  # Calculate the frequency


def determine_color(red, blue):
    """
    Determine the dominant color based on measured frequencies.

    Args:
        red (float): Frequency of the red channel..
        blue (float): Frequency of the blue channel.
        temp (int): State variable to track object placement.

    Returns:
        tuple: (string, int) - Detected color and updated temp value.
    """
    if red > blue and red > RED_THRESHOLD:
        return "red", 1
    if blue > red  and blue > BLUE_THRESHOLD:
        return "blue", 1
    return "blank", 0


def loop():
    """
    Main loop to measure the color channels and detect the color.
    """
    while True:
        # Measure all color channels
        red = measure_channel(GPIO.LOW, GPIO.LOW)
        blue = measure_channel(GPIO.LOW, GPIO.HIGH)

        # Detect color
        color = determine_color(red, blue)

        # Output detected color and frequencies
        print(f"Detected color: {color} (R: {red:.2f}, B: {blue:.2f})")


def endprogram():
    """Cleanup GPIO settings before exiting."""
    GPIO.cleanup()
    print("GPIO cleanup completed.")


if __name__ == '__main__':
    setup()
    try:
        loop()
    except KeyboardInterrupt:
        endprogram()
