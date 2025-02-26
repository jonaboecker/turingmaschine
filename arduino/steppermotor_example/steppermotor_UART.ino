#include <Arduino.h>
#include <string.h>
#include <stdlib.h>
#include "A4988.h"

// ----- Pin Assignments for Main Stepper Motor -----
int Step    = 3;    // STEP pin
int Dire    = 2;    // DIRECTION pin
int Sleep   = 4;    // SLEEP pin
int MS1     = 5;    // Microstep setting
int MS2     = 6;    // Microstep setting
int MS3     = 7;    // Microstep setting

// ----- Pin Assignments for Arm Stepper Motor -----
int Step_Arm   = 9;    // STEP pin
int Dire_Arm   = 8;    // DIRECTION pin
int Sleep_Arm  = 10;   // SLEEP pin
int MS1_Arm    = 11;   // Microstep setting
int MS2_Arm    = 12;   // Microstep setting
int MS3_Arm    = 13;   // Microstep setting

// ----- Motor Specifications -----
const int spr = 200;      // Steps per revolution
int RPM = 20;             // Rotations per minute
int Microsteps = 8;       // Microstepping (e.g., 8 = 1:8 microstepping)
int Microsteps_Arm = 8;

// ----- Motor Instantiation -----
// Ensure the parameter order matches your library specifications!
A4988 stepper(spr, Dire, Step, MS1, MS2, MS3);
A4988 stepper2(spr, Dire_Arm, Step_Arm, MS1_Arm, MS2_Arm, MS3_Arm);

// Function prototypes for command handlers
void toggleHandler(char* args);
void setupHandler(char* args);
void cleanupHandler(char* args);
void rotateHandler(char* args);
void moveHandler(char* args);

// Function pointer type for command handlers
typedef void (*CommandHandler)(char* args);

// Command structure
struct Command {
  const char* name;
  CommandHandler handler;
};

// Command dispatch table
Command commands[] = {
  {"TOGGLE",  toggleHandler},
  {"SETUP",   setupHandler},
  {"CLEANUP", cleanupHandler},
  {"ROTATE",  rotateHandler},
  {"MOVE",    moveHandler},
};

const int numCommands = sizeof(commands) / sizeof(Command);

//
// --- Functions for parsing and dispatching serial input ---
//

/**
 * Reads a line from the serial interface, parses it,
 * and dispatches it to the appropriate handler function.
 */
void processSerialInput() {
  if (Serial.available() > 0) {
    // Read incoming command until newline character
    String commandStr = Serial.readStringUntil('\n');
    commandStr.trim(); // Remove leading and trailing spaces
    if (commandStr.length() == 0) return;
    
    Serial.print("Received command: ");
    Serial.println(commandStr);
    
    // Copy string into a buffer (C-string) for further processing
    char commandBuffer[64];
    commandStr.toCharArray(commandBuffer, sizeof(commandBuffer));
    
    // First token = command
    char* token = strtok(commandBuffer, " ");
    if (token == NULL) return;
    
    // The rest of the line (parameters) is passed to the handler function
    char* args = strtok(NULL, "\n");  // Everything until end of line
    if (args == NULL) {
      static char empty[] = "";
      args = empty;
    }
    
    // Dispatch: Search for the command in the table
    bool found = false;
    for (int i = 0; i < numCommands; i++) {
      if (strcmp(token, commands[i].name) == 0) {
        commands[i].handler(args);
        found = true;
        break;
      }
    }
    if (!found) {
      Serial.println("Unknown command.");
    }
  }
}

//
// --- Handler functions for parsing parameters ---
//

void toggleHandler(char* args) {
  // No parameters needed
  handleToggle();
}

void setupHandler(char* args) {
  handleSetup();
}

void cleanupHandler(char* args) {
  handleCleanup();
}

void rotateHandler(char* args) {
  // Expected format: <steps> <direction> <delayInSec>
  char* token = strtok(args, " ");
  if(token == NULL) { Serial.println("ROTATE: missing steps"); return; }
  int steps = atoi(token);
  
  token = strtok(NULL, " ");
  if(token == NULL) { Serial.println("ROTATE: missing direction"); return; }
  const char* direction = token;
  
  token = strtok(NULL, " ");
  if(token == NULL) { Serial.println("ROTATE: missing delay"); return; }
  float delaySec = atof(token);
  
  handleRotate(steps, direction, delaySec);
}

void moveHandler(char* args) {
  // Expected format: <direction> <speed> <steps>
  char* token = strtok(args, " ");
  if(token == NULL) { Serial.println("MOVE: missing direction"); return; }
  const char* direction = token;
  
  token = strtok(NULL, " ");
  if(token == NULL) { Serial.println("MOVE: missing speed"); return; }
  int speed = atoi(token);
  
  token = strtok(NULL, " ");
  if(token == NULL) { Serial.println("MOVE: missing steps"); return; }
  int steps = atoi(token);
  
  handleMove(direction, speed, steps);
}

//
// --- Functions for executing commands ---
//

void handleToggle() {
  Serial.println("TOGGLE command received: Simulating keypress.");
  digitalWrite(Sleep_Arm, HIGH);
  stepper2.rotate(20);
  delay(100);
  stepper2.rotate(-20);
  Serial.println("Pressed");
  digitalWrite(Sleep_Arm, LOW);
}

void handleSetup() {
  Serial.println("SETUP command received: Re-initializing hardware.");
  
  // Configure pins as outputs
  pinMode(Step, OUTPUT);
  pinMode(Dire, OUTPUT);
  pinMode(Sleep, OUTPUT);
  pinMode(Step_Arm, OUTPUT);
  pinMode(Dire_Arm, OUTPUT);
  pinMode(Sleep_Arm, OUTPUT);
  
  // Set initial state
  digitalWrite(Step, LOW);
  digitalWrite(Dire, LOW);
  digitalWrite(Step_Arm, LOW);
  digitalWrite(Dire_Arm, LOW);
  
  // Reinitialize stepper motors
  stepper.begin(RPM, Microsteps);
  stepper2.begin(RPM, Microsteps_Arm);
  
  // Activate motors
  digitalWrite(Sleep, HIGH);
  digitalWrite(Sleep_Arm, HIGH);
  
  Serial.println("Setup complete.");
}

void handleCleanup() {
  Serial.println("CLEANUP command received: Putting motors into sleep mode.");
  digitalWrite(Sleep, LOW);
  digitalWrite(Sleep_Arm, LOW);
  Serial.println("Motors put into sleep mode.");
}

void handleRotate(int steps, const char* direction, float delaySec) {
  digitalWrite(Sleep, HIGH);
  unsigned long delayTime = delaySec * 1000;  // Convert to milliseconds
  
  if (strcmp(direction, "LEFT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(1);
      delay(delayTime);
    }
  }
  else if (strcmp(direction, "RIGHT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(-1);
      delay(delayTime);
    }
  }
  digitalWrite(Sleep, LOW);
}

void handleMove(const char* direction, int delay_ms, int steps) {
  digitalWrite(Sleep, HIGH);
  
  if (strcmp(direction, "LEFT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(1);
      delay(delay_ms);
    }
  }
  else if (strcmp(direction, "RIGHT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(-1);
      delay(delay_ms);
    }
  }
  digitalWrite(Sleep, LOW);
}

//
// --- Main program ---
//

void setup() {
  Serial.begin(9600);
  Serial.println("Serial command interface started. Enter commands:");
  handleSetup();
}

void loop() {
  processSerialInput();
}
#include <Arduino.h>
#include <string.h>
#include <stdlib.h>
#include "A4988.h"

// ----- Pin Assignments for Main Stepper Motor -----
int Step    = 3;    // STEP pin
int Dire    = 2;    // DIRECTION pin
int Sleep   = 4;    // SLEEP pin
int MS1     = 5;    // Microstep setting
int MS2     = 6;    // Microstep setting
int MS3     = 7;    // Microstep setting

// ----- Pin Assignments for Arm Stepper Motor -----
int Step_Arm   = 9;    // STEP pin
int Dire_Arm   = 8;    // DIRECTION pin
int Sleep_Arm  = 10;   // SLEEP pin
int MS1_Arm    = 11;   // Microstep setting
int MS2_Arm    = 12;   // Microstep setting
int MS3_Arm    = 13;   // Microstep setting

// ----- Motor Specifications -----
const int spr = 200;      // Steps per revolution
int RPM = 20;             // Rotations per minute
int Microsteps = 8;       // Microstepping (e.g., 8 = 1:8 microstepping)
int Microsteps_Arm = 8;

// ----- Motor Instantiation -----
// Ensure the parameter order matches your library specifications
A4988 stepper(spr, Dire, Step, MS1, MS2, MS3);
A4988 stepper2(spr, Dire_Arm, Step_Arm, MS1_Arm, MS2_Arm, MS3_Arm);

// Function prototypes for command handlers
void toggleHandler(char* args);
void setupHandler(char* args);
void cleanupHandler(char* args);
void rotateHandler(char* args);
void moveHandler(char* args);

// Function pointer type for command handlers
typedef void (*CommandHandler)(char* args);

// Command structure
struct Command {
  const char* name;
  CommandHandler handler;
};

// Command dispatch table
Command commands[] = {
  {"TOGGLE",  toggleHandler},
  {"SETUP",   setupHandler},
  {"CLEANUP", cleanupHandler},
  {"ROTATE",  rotateHandler},
  {"MOVE",    moveHandler},
};

const int numCommands = sizeof(commands) / sizeof(Command);

//
// --- Functions for parsing and dispatching serial input ---
//

/**
 * Reads a line from the serial interface, parses it,
 * and dispatches it to the appropriate handler function.
 */
void processSerialInput() {
  if (Serial.available() > 0) {
    String commandStr = Serial.readStringUntil('\n');
    commandStr.trim();
    if (commandStr.length() == 0) return;
    
    Serial.print("Received command: ");
    Serial.println(commandStr);
    
    char commandBuffer[64];
    commandStr.toCharArray(commandBuffer, sizeof(commandBuffer));
    
    // First token = command
    char* token = strtok(commandBuffer, " ");
    if (token == NULL) return;
    
    // The rest of the line (parameters) is passed to the handler function
    char* args = strtok(NULL, "\n");  // Everything until end of line
    if (args == NULL) {
      static char empty[] = "";
      args = empty;
    }
    
    // Dispatch: Search for the command in the table
    bool found = false;
    for (int i = 0; i < numCommands; i++) {
      if (strcmp(token, commands[i].name) == 0) {
        commands[i].handler(args);
        found = true;
        break;
      }
    }
    if (!found) {
      Serial.println("Unknown command.");
    }
  }
}

//
// --- Handler functions for parsing parameters ---
//

void toggleHandler(char* args) {
  // No parameters needed
  handleToggle();
}

void setupHandler(char* args) {
  handleSetup();
}

void cleanupHandler(char* args) {
  handleCleanup();
}

void rotateHandler(char* args) {
  // Expected format: <steps> <direction> <delayInSec>
  char* token = strtok(args, " ");
  if(token == NULL) { Serial.println("ROTATE: missing steps"); return; }
  int steps = atoi(token);
  
  token = strtok(NULL, " ");
  if(token == NULL) { Serial.println("ROTATE: missing direction"); return; }
  const char* direction = token;
  
  token = strtok(NULL, " ");
  if(token == NULL) { Serial.println("ROTATE: missing delay"); return; }
  float delaySec = atof(token);
  
  handleRotate(steps, direction, delaySec);
}

void moveHandler(char* args) {
  // Expected format: <direction> <speed> <steps>
  char* token = strtok(args, " ");
  if(token == NULL) { Serial.println("MOVE: missing direction"); return; }
  const char* direction = token;
  
  token = strtok(NULL, " ");
  if(token == NULL) { Serial.println("MOVE: missing speed"); return; }
  int speed = atoi(token);
  
  token = strtok(NULL, " ");
  if(token == NULL) { Serial.println("MOVE: missing steps"); return; }
  int steps = atoi(token);
  
  handleMove(direction, speed, steps);
}

//
// --- Functions for executing commands ---
//

void handleToggle() {
  Serial.println("TOGGLE command received: Simulating keypress.");
  digitalWrite(Sleep_Arm, HIGH);
  stepper2.rotate(20);
  delay(100);
  stepper2.rotate(-20);
  Serial.println("Pressed");
  digitalWrite(Sleep_Arm, LOW);
}

void handleSetup() {
  Serial.println("SETUP command received: Re-initializing hardware.");
  
  // Configure pins as outputs
  pinMode(Step, OUTPUT);
  pinMode(Dire, OUTPUT);
  pinMode(Sleep, OUTPUT);
  pinMode(Step_Arm, OUTPUT);
  pinMode(Dire_Arm, OUTPUT);
  pinMode(Sleep_Arm, OUTPUT);
  
  // Set initial state
  digitalWrite(Step, LOW);
  digitalWrite(Dire, LOW);
  digitalWrite(Step_Arm, LOW);
  digitalWrite(Dire_Arm, LOW);
  
  // Reinitialize stepper motors
  stepper.begin(RPM, Microsteps);
  stepper2.begin(RPM, Microsteps_Arm);
  
  // Activate motors
  digitalWrite(Sleep, HIGH);
  digitalWrite(Sleep_Arm, HIGH);
  
  Serial.println("Setup complete.");
}

void handleCleanup() {
  Serial.println("CLEANUP command received: Putting motors into sleep mode.");
  digitalWrite(Sleep, LOW);
  digitalWrite(Sleep_Arm, LOW);
  Serial.println("Motors put into sleep mode.");
}

void handleRotate(int steps, const char* direction, float delaySec) {
  digitalWrite(Sleep, HIGH);
  unsigned long delayTime = delaySec * 1000;  // Convert to milliseconds
  
  if (strcmp(direction, "LEFT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(1);
      delay(delayTime);
    }
  }
  else if (strcmp(direction, "RIGHT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(-1);
      delay(delayTime);
    }
  }
  digitalWrite(Sleep, LOW);
}

void handleMove(const char* direction, int delay_ms, int steps) {
  digitalWrite(Sleep, HIGH);
  
  if (strcmp(direction, "LEFT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(1);
      delay(delay_ms);
    }
  }
  else if (strcmp(direction, "RIGHT") == 0) {
    for (int i = 0; i < abs(steps); i++) {
      stepper.rotate(-1);
      delay(delay_ms);
    }
  }
  digitalWrite(Sleep, LOW);
}

//
// --- Main program ---
//

void setup() {
  Serial.begin(9600);
  handleSetup();
}

void loop() {
  processSerialInput();
}

