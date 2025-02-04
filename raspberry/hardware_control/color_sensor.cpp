/*
 * color_sensor.cpp - Module to control the color sensor.
 * 
 * This program initializes the sensor, measures the color frequency, 
 * and determines whether the detected color is red, blue, or blank.
 */

#include <iostream>
#include <wiringPi.h>
#include <time.h>
#include <string>

using namespace std;

// GPIO pin definitions
#define S0_PIN 4      // Connected to GPIO 23
#define S1_PIN 5      // Connected to GPIO 24
#define S2_PIN 2      // Connected to GPIO 27
#define S3_PIN 3      // Connected to GPIO 22
#define SIGNAL_PIN 0  // Connected to GPIO 17
#define NUM_CYCLES 20 // Number of signal cycles used for measurement

// Threshold values for color detection
#define RED_THRESHOLD 50000
#define BLUE_THRESHOLD 50000

// Function declarations
void setup();
double measure_color(int s2_state, int s3_state);
string determine_color();

int main() {
    setup();

    // Measure the color once and print the detected result
    string detected_color = determine_color();
    cout << detected_color << endl;

    return 0;  // Exit the program
}

/**
 * Initializes GPIO pins and sets up the color sensor.
 * The sensor's frequency is set to 100%.
 */
void setup() {
    wiringPiSetup();
    pinMode(SIGNAL_PIN, INPUT);
    pinMode(S0_PIN, OUTPUT);
    pinMode(S1_PIN, OUTPUT);
    pinMode(S2_PIN, OUTPUT);
    pinMode(S3_PIN, OUTPUT);

    // Set frequency to 100%
    digitalWrite(S0_PIN, HIGH);
    digitalWrite(S1_PIN, HIGH);
}

/**
 * Measures the frequency of the selected color filter.
 * 
 * @param s2_state - State of the S2 pin (LOW or HIGH).
 * @param s3_state - State of the S3 pin (LOW or HIGH).
 * @return The measured signal frequency (in Hz).
 */
double measure_color(int s2_state, int s3_state) {
    // Activate the selected color filter
    digitalWrite(S2_PIN, s2_state);
    digitalWrite(S3_PIN, s3_state);
    delay(200);  // Allow the sensor to stabilize

    struct timespec start, end;
    clock_gettime(CLOCK_MONOTONIC, &start);

    for (int i = 0; i < NUM_CYCLES; i++) {
        while (digitalRead(SIGNAL_PIN) == HIGH); // Wait for LOW signal
        while (digitalRead(SIGNAL_PIN) == LOW);  // Wait for HIGH signal
    }

    clock_gettime(CLOCK_MONOTONIC, &end);
    double duration = (end.tv_sec - start.tv_sec) + (end.tv_nsec - start.tv_nsec) / 1e9;

    return NUM_CYCLES / duration; // Convert cycles to frequency
}

/**
 * Determines the dominant color by measuring red and blue intensity.
 * 
 * @return "RED" if red is dominant, "BLUE" if blue is dominant, otherwise "BLANK".
 */
string determine_color() {
    double red = measure_color(LOW, LOW);
    double blue = measure_color(LOW, HIGH);

    // Debug output (uncomment if needed)
    // cout << "DEBUG: Red: " << red << ", Blue: " << blue << endl;

    if (red > blue && red > RED_THRESHOLD) {
        return "RED";
    } 
    else if (blue > red && blue > BLUE_THRESHOLD) {
        return "BLUE";
    } 
    else {
        return "BLANK"; // No dominant color detected
    }
}
