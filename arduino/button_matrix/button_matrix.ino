#include <Wire.h>

// I2C-Adresse des MCP23017 (Standard: 0x20, anpassbar durch A0, A1, A2)
#define MCP23017_ADDRESS 0x20

// Register-Adressen des MCP23017
#define IODIRA 0x00 // I/O Direction Register für Port A
#define IODIRB 0x01 // I/O Direction Register für Port B
#define GPIOA  0x12 // GPIO Register für Port A
#define GPIOB  0x13 // GPIO Register für Port B

void writeMCP23017(uint8_t reg, uint8_t value) {
  Wire.beginTransmission(MCP23017_ADDRESS);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

uint8_t readMCP23017(uint8_t reg) {
  Wire.beginTransmission(MCP23017_ADDRESS);
  Wire.write(reg);
  Wire.endTransmission();

  Wire.requestFrom(MCP23017_ADDRESS, 1);
  if (Wire.available()) {
    return Wire.read();
  }
  return 0;
}

// Funktion zur Initialisierung und Berechnung des Ergebnisses
int calculateResult() {
  static uint8_t lastInputsA = 0xFF;
  static uint8_t lastInputsB = 0xFF;

  // Lese die Eingänge von Port A und Port B
  uint8_t inputsA = readMCP23017(GPIOA);
  uint8_t inputsB = readMCP23017(GPIOB);


    // Überprüfe, ob es Änderungen gab
  if (inputsA == lastInputsA && inputsB == lastInputsB) {
    return -1; // Keine Änderung
  }

  // Funktion zum Verarbeiten der Eingänge und Rückgabe des Index der Änderung
  auto processInputs = [](uint8_t current, uint8_t last) -> int {
    int lowIndex = -1;
    int lowCount = 0;

    for (int i = 0; i < 8; i++) {
      uint8_t mask = 1 << i;
      bool currentState = !(current & mask);
      bool lastState = !(last & mask);

      if (currentState) {
        lowIndex = i;
        lowCount++;
      }
    }

    if (lowCount == 1) {
      return lowIndex; // Rückgabe des Index der 0
    } else {
      return -1; // Keine oder mehrere 0en, verwerfen
    }
  };

  // Verarbeite die Eingänge und überprüfe Änderungen
  int changeA = processInputs(inputsA, lastInputsA);
  int changeB = processInputs(inputsB, lastInputsB);

  // Aktualisiere die letzten Zustände
  lastInputsA = inputsA;
  lastInputsB = inputsB;

  // Berechne und gebe den neuen Wert nur aus, wenn es Änderungen gibt
  if (changeA != -1 && changeB != -1) {
    return changeA + 8 * changeB;
  }

  return -1; // Kein gültiges Ergebnis
}

void setup() {
  // Starte die serielle Kommunikation für Debugging
  Serial.begin(9600);
  while (!Serial) {
    ; // Warte, bis die serielle Verbindung aktiv ist
  }

  // Initialisiere die I2C-Schnittstelle
  Wire.begin();

  // Konfiguriere alle Pins von Port A und Port B als Eingänge
  writeMCP23017(IODIRA, 0xFF); // 0xFF: Alle Pins von Port A als Eingang
  writeMCP23017(IODIRB, 0xFF); // 0xFF: Alle Pins von Port B als Eingang

  Serial.println("MCP23017 initialisiert.");
}

void loop() {
  int result = calculateResult();
  if (result != -1) {
    Serial.print("Result,");
    Serial.println(result);
  }
  delay(100); // Abfrage alle 100 ms
}