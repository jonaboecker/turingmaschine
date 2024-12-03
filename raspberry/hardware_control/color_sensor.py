"""
This module contains the Functions to control the Color Sensor.
"""
import time
from RPi import GPIO

# GPIO Pins
S2 = 23
S3 = 24
SIGNAL = 25

# Constants
NUM_CYCLES = 10

# Color thresholds
RED_THRESHOLD = 12000
GREEN_THRESHOLD = 12000
BLUE_THRESHOLD = 12000


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


def determine_color(red, green, blue):
    """
    Determine the dominant color based on measured frequencies.

    Args:
        red (float): Frequency of the red channel.
        green (float): Frequency of the green channel.
        blue (float): Frequency of the blue channel.

    Returns:
        tuple: (string, int) - Detected color and updated temp value.
    """
    if red > green and red > blue and red > RED_THRESHOLD:
        return "red", 1
    if green > red and green > blue and green > GREEN_THRESHOLD:
        return "green", 1
    if blue > red and blue > green and blue > BLUE_THRESHOLD:
        return "blue", 1
    return "unknown", 0


def detect_color(red, green, blue, temp):
    """
    Determine the color based on the measured frequencies.

    Args:
        red (float): Frequency of the red channel.
        green (float): Frequency of the green channel.
        blue (float): Frequency of the blue channel.
        temp (int): State variable to track object placement.

    Returns:
        tuple: (string, int) - Detected color and updated temp value.
    """
    if green < 7000 and blue < 7000 and red > 12000:
        return "red", 1
    if red < 12000 and blue < 12000 and green > 12000:
        return "green", 1
    if green < 7000 and red < 7000 and blue > 12000:
        return "blue", 1
    if red > 10000 and green > 10000 and blue > 10000 and temp == 1:
        return "place the object.....", 0
    return "unknown", temp


def loop():
    """
    Main loop to measure the color channels and detect the color.
    """
    temp = 1
    while True:
        # Measure all color channels
        red = measure_channel(GPIO.LOW, GPIO.LOW)
        green = measure_channel(GPIO.HIGH, GPIO.HIGH)
        blue = measure_channel(GPIO.LOW, GPIO.HIGH)

        # Detect color
        color, temp = detect_color(red, green, blue, temp)

        # Output detected color and frequencies
        print(f"Detected color: {color} (R: {red:.2f}, G: {green:.2f}, B: {blue:.2f})")


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
