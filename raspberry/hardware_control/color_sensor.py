"""
This module contains the Functions to control the Color Sensor.
"""
import RPi.GPIO as GPIO
import time

s2 = 23
s3 = 24
signal = 25
NUM_CYCLES = 10

# Color thresholds
RED_THRESHOLD = 12000
GREEN_THRESHOLD = 12000
BLUE_THRESHOLD = 12000
    
def setup():
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(signal,GPIO.IN, pull_up_down=GPIO.PUD_UP)
  GPIO.setup(s2,GPIO.OUT)
  GPIO.setup(s3,GPIO.OUT)
  print("\n")
  
def measure_channel(s2_val, s3_val):
    """Measure the frequency for a specific color channel.
        The s2 and s3 values determine the color channel being measured:
            - s2=LOW, s3=LOW: Measure red channel (600–750 nm, ~10,000–20,000 Hz).
            - s2=LOW, s3=HIGH: Measure blue channel (450–495 nm, ~10,000–20,000 Hz).
            - s2=HIGH, s3=HIGH: Measure green channel (495–570 nm, ~10,000–20,000 Hz).
            - s2=HIGH, s3=LOW: Measure clear channel (no filter, ~20,000–30,000 Hz).
    """
    GPIO.output(s2, s2_val)
    GPIO.output(s3, s3_val)
    time.sleep(0.3)  # Short delay to stabilize the sensor
    start = time.time()  # Record the start time for measurement
    for impulse_count in range(NUM_CYCLES):  # Count the number of impulses
        GPIO.wait_for_edge(signal, GPIO.FALLING)  # Wait for a falling edge signal
    # Time-out modus
    #if not GPIO.wait_for_edge(signal, GPIO.FALLING, timeout=1000):  # Timeout in ms
    #print("No signal detected!")
    #return 0 
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
    elif green > red and green > blue and green > GREEN_THRESHOLD:
        return "green", 1
    elif blue > red and blue > green and blue > BLUE_THRESHOLD:
        return "blue", 1
    else:
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
    elif red < 12000 and blue < 12000 and green > 12000:
        return "green", 1
    elif green < 7000 and red < 7000 and blue > 12000:
        return "blue", 1
    elif red > 10000 and green > 10000 and blue > 10000 and temp == 1:
        return "place the object.....", 0
    else:
        return "unknown", temp

def loop():
  temp = 1
  while(1):  
     # Measure all color channels
    red = measure_channel(GPIO.LOW, GPIO.LOW)
    green = measure_channel(GPIO.HIGH, GPIO.HIGH)
    blue = measure_channel(GPIO.LOW, GPIO.HIGH)
    
    
    #color, temp = determine_color(red, green, blue) # try this 
    color, temp = detect_color(red, green, blue, temp)
    print(f"Detected color: {color} (R: {red:.2f}, G: {green:.2f}, B: {blue:.2f})")
      

def endprogram():
    GPIO.cleanup()

if __name__=='__main__':
    
    setup()

    try:
        loop()

    except KeyboardInterrupt:
        endprogram()
