"""
This module executes color_sensor.cpp to determine the detected color.
"""

import subprocess
import os
import platform
from random import randrange

import assets

def compile_cpp():
    """Compiles the C++ program using the Makefile."""
    compile_command = ["g++", "color_sensor.cpp", "-o", "color_sensor", "-lwiringPi"]
    try:
        subprocess.run(compile_command, capture_output=True, text=True, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print("❌ Kompilierung fehlgeschlagen:", e.stderr)
        return False

def run_cpp():
    """Runs the compiled C++ program and returns the detected color."""
    try:
        result = subprocess.run([assets.EXE_FILE], capture_output=True, text=True, check=True)
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
    # If not running on Linux, return a random color for testing purposes
    if platform.system() != "Linux":
        random_color = assets.IO_BAND_COLORS(randrange(3))
        print(f"Random detected and returned color: {random_color}")
        return random_color
    # Check if the compiled executable exists, otherwise compile it
    if not os.path.exists(assets.EXE_FILE):
        compile_cpp()
    detected_color = run_cpp()
    return assets.IO_BAND_COLORS[detected_color]  # Example: assets.IO_BAND_COLORS['RED']
