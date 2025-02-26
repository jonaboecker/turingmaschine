"""
This module executes color_sensor.cpp to determine the detected color.
"""

import subprocess
import os
import platform
from random import randrange

import assets

# Name of the C++ source file and the executable
CPP_FILE = "color_sensor.cpp"
EXE_FILE = "./color_sensor"

def compile_cpp():
    """Compiles the C++ program using the Makefile."""
    try:
        subprocess.run(["make"], capture_output=True, text=True, check=True)
        # Compilation successful, return True
        return True
    except subprocess.CalledProcessError as e:
        # Print the error output if compilation fails
        print("❌ Compilation failed:", e.stderr)
        return False

def run_cpp():
    """Runs the compiled C++ program and returns the detected color."""
    try:
        result = subprocess.run([EXE_FILE], capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print("Error while executing the C++ program:", e.stderr)
        return None

def get_color():
    """
    Retrieves the detected color from the color sensor.

    Returns:
        IO_BAND_COLORS: The detected color as an Enum ('RED', 'BLUE', or 'BLANK'),
                        or None in case of an error.
    """
    if platform.system() != "Linux":
        random_color = assets.IO_BAND_COLORS(randrange(3))
        print(f"Random detected and returned color: {random_color}")
        return random_color
    # Check if the compiled executable exists, otherwise compile it
    if not os.path.exists(EXE_FILE):
        if not compile_cpp():
            return None

    detected_color = run_cpp()

    try:
        return assets.IO_BAND_COLORS[detected_color]  # Example: assets.IO_BAND_COLORS['RED']
    except KeyError:
        # Handle invalid color values
        print(f"Invalid color detected: {detected_color}")
        return None

# Test function call
#if __name__ == "__main__":
#    color = get_color()
#    if color:
#        print(f"Detected color: {color.name}")
#    else:
#        print("No valid color detected.")
