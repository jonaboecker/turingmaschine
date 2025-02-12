#include <Wire.h>
#include <Arduino.h>
#include <string.h>
#include <stdlib.h>
#include "A4988.h"

// ----- Pin Assignments -----
// Pins for the Stepper Motor (A4988)
int Step = 3;    // STEP Pin
int Dire = 2;    // DIRECTION Pin
int Sleep = 4;   // SLEEP Pin
int MS1 = 5;     // Microstep Setting
int MS2 = 6;     // Microstep Setting
int MS3 = 7;     // Microstep Setting

// ----- Pin Assignments -----
// Pins for the Stepper Motor (A4988) Arm
int Step_Arm = 9;    // STEP Pin
int Dire_Arm = 8;    // DIRECTION Pin
int Sleep_Arm = 10;  // SLEEP Pin
int MS1_Arm = 11;    // Microstep Setting
int MS2_Arm = 12;    // Microstep Setting
int MS3_Arm = 13;    // Microstep Setting

// ----- Motor Specifications -----
const int spr = 200;        // Steps per revolution
int RPM = 20;               // RPM (revolutions per minute)
int Microsteps = 1;         // Microsteps (e.g., 8 = 1:8 Microstepping)
int Microsteps_Arm = 8;

// ----- Motor Instantiation -----
A4988 stepper(spr, Dire, Step, MS1, MS2, MS3);
A4988 stepper2(spr, Dire_Arm, Step_Arm, MS1_Arm, MS2_Arm, MS3_Arm);

// Default delay (in milliseconds) for rotate (can be adjusted)
const unsigned long DEFAULT_DELAY = 10;

#define I2C_ADDRESS 0x08  // This address MUST match the address of your Python program

// Function prototypes
void receiveEvent(int howMany);
void handleToggle();
void handleSetup();
void handleCleanup();
void handleRotate(int steps, const char* direction, float delaySec);
void handleMove(const char* direction, int speed, int steps);

void setup() {
  Serial.begin(9600);
  
  // Initialize I²C as Slave
  Wire.begin(I2C_ADDRESS);
  Wire.onReceive(receiveEvent);
  Serial.println("I2C Slave started. Waiting for commands...");

  // Configure pins as outputs
  pinMode(Step, OUTPUT);
  pinMode(Dire, OUTPUT);
  pinMode(Sleep, OUTPUT);

  pinMode(Step_Arm, OUTPUT);
  pinMode(Dire_Arm, OUTPUT);
  pinMode(Sleep_Arm, OUTPUT);
  
  // Set initial state of signals
  digitalWrite(Step, LOW);
  digitalWrite(Dire, LOW);

  digitalWrite(Step_Arm, LOW);
  digitalWrite(Dire_Arm, LOW);
  
  // Initialize the stepper motor with desired RPM and microstepping setting
  stepper.begin(RPM, Microsteps);
  stepper2.begin(RPM, 8);
  
  // Ensure the motor is active (not in sleep mode)
  digitalWrite(Sleep, HIGH);
  digitalWrite(Sleep_Arm, HIGH);
  
  Serial.println("Setup complete.");
}

void loop() {
  // The main loop remains empty – all actions are handled in receiveEvent().
}

// This function is called when data is received via I²C.
void receiveEvent(int howMany) {
  // It is assumed that the first byte is the transmitted "dummy" register value.
  if (howMany < 2) return; // If only the dummy is sent, nothing is there.
  char commandBuffer[64];  // Buffer for the received command
  int i = 0;
  
  // Discard the first byte (register/dummy):
  Wire.read();
  // Read the remaining bytes until the buffer is full or no more data is available
  while (Wire.available() && i < 63) {
    commandBuffer[i++] = Wire.read();
  }
  commandBuffer[i] = '\0';  // Null-terminate
  
  // Print the received command for debugging
  Serial.print("Received command: ");
  Serial.println(commandBuffer);

  // Split the command into individual tokens (words)
  char *token = strtok(commandBuffer, " ");
  if (token == NULL) return;
  
  if (strcmp(token, "TOGGLE") == 0) {
    handleToggle();
  }
  else if (strcmp(token, "SETUP") == 0) {
    handleSetup();
  }
  else if (strcmp(token, "CLEANUP") == 0) {
    handleCleanup();
  }
  else if (strcmp(token, "ROTATE") == 0) {
    // Expected format: ROTATE <steps> <direction> <delayInSec>
    char *stepsStr = strtok(NULL, " ");
    char *direction = strtok(NULL, " ");
    char *delayStr = strtok(NULL, " ");
    if (stepsStr != NULL && direction != NULL && delayStr != NULL) {
      int steps = atoi(stepsStr);
      float delaySec = atof(delayStr);
      handleRotate(steps, direction, delaySec);
    }
  }
  else if (strcmp(token, "MOVE") == 0) {
    // Expected format: MOVE <direction> <speed> <steps>
    char *direction = strtok(NULL, " ");
    char *speedStr = strtok(NULL, " ");
    char *stepsStr = strtok(NULL, " ");
    if (direction != NULL && speedStr != NULL && stepsStr != NULL) {
      int speed = atoi(speedStr);
      int steps = atoi(stepsStr);
      handleMove(direction, speed, steps);
    }
  }
}

//
// Function to handle the TOGGLE command
//
void handleToggle() {
  Serial.println("TOGGLE command received: Simulating keypress.");
  digitalWrite(Sleep_Arm, HIGH);

  stepper2.rotate(20);
  delay(100);
  stepper2.rotate(-20);
  Serial.print("Pressed");

  digitalWrite(Sleep_Arm, LOW);
}

//
// Function to handle the SETUP command
//
void handleSetup() {
  Serial.println("SETUP command received: Re-initializing hardware.");
  pinMode(Step, OUTPUT);
  pinMode(Dire, OUTPUT);
  pinMode(Sleep, OUTPUT);

  pinMode(Step_Arm, OUTPUT);
  pinMode(Dire_Arm, OUTPUT);
  pinMode(Sleep_Arm, OUTPUT);
  
  // Set initial state of signals
  digitalWrite(Step, LOW);
  digitalWrite(Dire, LOW);

  digitalWrite(Step_Arm, LOW);
  digitalWrite(Dire_Arm, LOW);
  
  // Initialize the stepper motor with desired RPM and microstepping setting
  stepper.begin(RPM, Microsteps);
  stepper2.begin(RPM, 8);
  
  // Ensure the motor is active (not in sleep mode)
  digitalWrite(Sleep, HIGH);
  digitalWrite(Sleep_Arm, HIGH);
}

//
// Function to handle the CLEANUP command
//
void handleCleanup() {
  Serial.println("CLEANUP command received: Putting motors into sleep mode.");
  digitalWrite(Sleep, LOW);
  digitalWrite(Sleep_Arm, LOW);
  Serial.println("cleanup: Motor put into sleep mode.");
}

//
// Function to handle the ROTATE command
// Expects: Number of steps, direction (e.g., LEFT/RIGHT), delay in seconds per step
//
void handleRotate(int steps, const char* direction, float delaySec) {
  unsigned long delayTime = delaySec * 1000;  // Convert seconds to milliseconds
  
  // Set the rotation direction
  if (strcmp(direction, "LEFT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(1);  // Perform one step
      delay(delayTime);
    }
  }
  else if (strcmp(direction, "RIGHT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(-1);  // Perform one step
      delay(delayTime);
    }
  }
}

//
// Function to handle the MOVE command
// Expects: Direction (e.g., LEFT/RIGHT), speed (as number), steps
//
void handleMove(const char* direction, int speed, int steps) {
  //Serial.print("MOVE command received: Direction = ");
  //Serial.print(direction);
  //Serial.print(", Speed = ");
  //Serial.print(speed);
  //Serial.print(", Steps = ");
  //Serial.println(steps);
  
  unsigned long stepDelay = 1000 / speed;
  if (strcmp(direction, "LEFT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(1); 
      delay(stepDelay);
    }
  }
  else if (strcmp(direction, "RIGHT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(-1);  // Perform one step
      delay(stepDelay);
    }
  }
}