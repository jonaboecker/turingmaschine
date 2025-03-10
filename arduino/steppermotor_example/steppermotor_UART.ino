  #include <Arduino.h>
#include <string.h>
#include <stdlib.h>
#include "A4988.h"

// ----- Makro zur bedingten Nutzung von Serial1 -----
#ifdef Serial1
  #define WRITE_SERIAL1(val) Serial1.println("ACK:" val)
#else
  #define WRITE_SERIAL1(val) Serial.println("ACK:" val)
#endif
// ----- Pin-Zuweisungen für den Haupt-Schrittmotor -----
const int Step    = 3;    // STEP-Pin
const int Dire    = 2;    // DIRECTION-Pin
const int Sleep   = 4;    // SLEEP-Pin
const int MS1     = 7;    // Microstep-Einstellung
const int MS2     = 6;    // Microstep-Einstellung
const int MS3     = 5;    // Microstep-Einstellung

// ----- Pin-Zuweisungen für den Arm-Schrittmotor -----
const int Step_Arm   = 9;   // STEP-Pin
const int Dire_Arm   = 8;   // DIRECTION-Pin
const int Sleep_Arm  = 10;  // SLEEP-Pin
const int MS1_Arm    = 13;  // Microstep-Einstellung
const int MS2_Arm    = 12;  // Microstep-Einstellung
const int MS3_Arm    = 11;  // Microstep-Einstellung

// ----- Motor-Spezifikationen -----
const int spr = 200;      // Schritte pro Umdrehung
int RPM = 20;             // Drehzahl (Umdrehungen pro Minute)
int Microsteps = 8;       // Microstepping (z. B. 8 = 1:8)
int Microsteps_Arm = 8;

// ----- Motor-Instanzen -----
A4988 stepper(spr, Dire, Step, MS1, MS2, MS3);
A4988 stepper2(spr, Dire_Arm, Step_Arm, MS1_Arm, MS2_Arm, MS3_Arm);

// Prototypen der Handler-Funktionen für die einzelnen Befehle
void toggleHandler(char* args);
void setupHandler(char* args);
void cleanupHandler(char* args);
void moveHandler(char* args);

// Funktionszeiger-Typ für Kommandohandler
typedef void (*CommandHandler)(char* args);

// Struktur für ein Kommando
struct Command {
  const char* name;
  CommandHandler handler;
};

// Dispatch-Tabelle für Befehle
Command commands[] = {
  {"TOGGLE",  toggleHandler},
  {"SETUP",   setupHandler},
  {"CLEANUP", cleanupHandler},
  {"MOVE",    moveHandler},
};

const int numCommands = sizeof(commands) / sizeof(Command);

//
// --- Funktion zum Parsen und Dispatchen der seriellen Eingabe ---
//
void processSerialInput() {
  digitalWrite(Sleep, LOW);
  if (Serial.available() > 0) {
    // Lese den eingehenden Befehl bis zum Newline-Zeichen
    String commandStr = Serial.readStringUntil('\n');
    commandStr.trim(); // Entferne überflüssige Leerzeichen
    if (commandStr.length() == 0) return;
    
    Serial.print("Received command: ");
    Serial.println(commandStr);
    
    // Kopiere den String in einen Puffer (C-String)
    char commandBuffer[64];
    commandStr.toCharArray(commandBuffer, sizeof(commandBuffer));
    
    // Erster Token = Kommando
    char* token = strtok(commandBuffer, " ");
    if (token == NULL) return;
    
    // Rest der Zeile als Argumente
    char* args = strtok(NULL, "\n");  
    if (args == NULL) {
      static char empty[] = "";
      args = empty;
    }
    
    // Suche in der Dispatch-Tabelle nach dem passenden Befehl
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
// --- Handler-Funktionen ---
//
void toggleHandler(char* args) {
  // Keine Parameter benötigt
  handleToggle();
}

void setupHandler(char* args) {
  handleSetup();
}

void cleanupHandler(char* args) {
  handleCleanup();
}

void moveHandler(char* args) {
  digitalWrite(Sleep, LOW);
  // Erwartetes Format: <direction> <delay_ms> <steps>
  char* token = strtok(args, " ");
  if (token == NULL) { 
    Serial.println("MOVE: missing direction"); 
    return; 
  }
  const char* direction = token;

  token = strtok(NULL, " ");
  if (token == NULL) { 
    Serial.println("MOVE: missing delay"); 
    return; 
  }
  int delay_ms = atoi(token);

  token = strtok(NULL, " ");
  if (token == NULL) { 
    Serial.println("MOVE: missing steps"); 
    return; 
  }
  int steps = atoi(token);

  Serial.print("MOVE: direction: ");
  Serial.print(direction);
  Serial.print(", delay_ms: ");
  Serial.print(delay_ms);
  Serial.print(", steps: ");
  Serial.println(steps);
  handleMove(direction, delay_ms, steps);
}

//
// --- Funktionen zur Ausführung der Befehle ---
//
void handleToggle() {
  Serial.println("TOGGLE command received: Simuliere Tastendruck.");
  digitalWrite(Sleep_Arm, HIGH);
  stepper2.rotate(-20);
  delay(100);
  stepper2.rotate(20);
  Serial.println("Tastendruck simuliert.");
  digitalWrite(Sleep_Arm, LOW);
  WRITE_SERIAL1("1");
}

void handleSetup() {
  Serial.println("SETUP command received: Hardware wird neu initialisiert.");
  
  // Konfiguriere die Pins als Outputs
  pinMode(Step, OUTPUT);
  pinMode(Dire, OUTPUT);
  pinMode(Sleep, OUTPUT);
  pinMode(Step_Arm, OUTPUT);
  pinMode(Dire_Arm, OUTPUT);
  pinMode(Sleep_Arm, OUTPUT);
  
  // Setze Anfangszustand
  digitalWrite(Step, LOW);
  digitalWrite(Dire, LOW);
  digitalWrite(Step_Arm, LOW);
  digitalWrite(Dire_Arm, LOW);
  
  // Initialisiere die Schrittmotoren
  stepper.begin(RPM, Microsteps);
  stepper2.begin(RPM, Microsteps_Arm);
  
  digitalWrite(Sleep, LOW);
  digitalWrite(Sleep_Arm, LOW);
  
  Serial.println("Setup abgeschlossen.");
  WRITE_SERIAL1("1");
}

void handleCleanup() {
  Serial.println("CLEANUP command received: Motoren werden in den Schlafmodus versetzt.");
  digitalWrite(Sleep, LOW);
  digitalWrite(Sleep_Arm, LOW);
  Serial.println("Motoren im Schlafmodus.");
  WRITE_SERIAL1("1");
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
  } else { WRITE_SERIAL1("0");}
  digitalWrite(Sleep, LOW);
  WRITE_SERIAL1("1");
}

//
// --- Hauptprogramm ---
//
void setup() {
  Serial.begin(9600);
  
  // Falls verfügbar, initialisiere Serial1
  #ifdef Serial1
    Serial1.begin(9600);
  #endif
  
  handleSetup();
}

void loop() {
  processSerialInput();
}
