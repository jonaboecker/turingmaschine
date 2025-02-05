#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>  // Required for 16 MHz Adafruit Trinket
#endif

#include <Wire.h>

#include <Arduino.h>
#include "A4988.h"

#include <Adafruit_MCP23X17.h>

// ---------- ---------- RGB-LED Stripe ---------- ----------

#define PIN_WS2812B 4  // Arduino pin that connects to WS2812B
#define NUM_PIXELS 60  // The number of LEDs (pixels) on WS2812B

#define DELAY_INTERVAL 250  // 250ms pause between each pixel

#define BRIGHTNESS 255  // a value from 0 to 255

#define BLANK strip.Color(0, 0, 0)
#define SYMBOL_1 strip.Color(255, 0, 0)
#define SYMBOL_2 strip.Color(0, 255, 0)


// ---------- ---------- I²C ---------- ----------

#define IODIRA 0x00 // I/O Direction Register für Port A
#define IODIRB 0x01 // I/O Direction Register für Port B
#define GPIOA  0x12 // GPIO Register für Port A
#define GPIOB  0x13 // GPIO Register für Port B


// ---------- ---------- BUTTON-MATRIX ---------- ----------

#define MCP23017_ADDRESS_MATRIX 0x20   // I2C-Adresse des MCP23017 (Standard: 0x20, anpassbar durch A0, A1, A2)


// ---------- ---------- STEPPER-MOTOR ---------- ----------

#define MCP23017_ADDRESS_STEPPER 0x21   // I2C-Adresse des MCP23017 (Standard: 0x20, anpassbar durch A0, A1, A2)

#define STEP_A 1
#define DIRE_A 2
#define SLEEP_A 3
#define MS1_A 4
#define MS2_A 5
#define MS3_A 6

#define STEP_B 8
#define DIRE_B 9
#define SLEEP_B 10
#define MS1_B 11
#define MS2_B 12
#define MS3_B 13

// ---------- ---------- RGB-LED Stripe ---------- ----------

Adafruit_NeoPixel strip = Adafruit_NeoPixel(NUM_PIXELS, PIN_WS2812B, NEO_GRB + NEO_KHZ800);

struct LedData {
  int pos;    // Key
  int state;  // State
};

LedData led_state_dict[60];


// ---------- ---------- I²C ---------- ----------

void writeMCP23017(uint8_t mcpAddress, uint8_t reg, uint8_t value) {
  Wire.beginTransmission(mcpAddress);
  Wire.write(reg);
  Wire.write(value);
  Wire.endTransmission();
}

uint8_t readMCP23017(uint8_t mcpAddress, uint8_t reg) {
  Wire.beginTransmission(mcpAddress);
  Wire.write(reg);
  Wire.endTransmission();

  Wire.requestFrom(mcpAddress, (uint8_t)1);
  if (Wire.available()) {
    return Wire.read();
  }
  return 0;
}

Adafruit_MCP23X17 mcp_stepper;


// ---------- ---------- STEPPER-MOTOR ---------- ----------

//Motor Specs
const int spr = 200; //Steps per revolution
int RPM = 20; //Motor Speed in revolutions per minute
int Microsteps = 8; //Stepsize (1 for full steps, 2 for half steps, 4 for quarter steps, etc)

//Providing parameters for motor control
A4988 stepper_button(spr, DIRE_A, STEP_A, MS1_A, MS2_A, MS3_A);
A4988 stepper_rail(spr, DIRE_B, STEP_B, MS1_B, MS2_B, MS3_B);

// ---------- ---------- SETUP ---------- ----------

void setup() {
  
  // ---------- SERIAL SETUP ----------
  Serial.begin(9600);
  while (!Serial) {
    ; // Warte, bis die serielle Verbindung aktiv ist
  }


  // ---------- I²C SETUP ----------
  if (!mcp_stepper.begin_I2C(MCP23017_ADDRESS_STEPPER)) {
    Serial.println("Error.");
    while (1);
  }


  // ---------- STEPPER SETUP ----------
  // Set A0 to A5 as outputs
  for (uint8_t pin = 0; pin <= 5; pin++) {
      mcp_stepper.pinMode(pin, OUTPUT);
  }
  
  // Set B0 to B5 (8-13) as outputs
  for (uint8_t pin = 8; pin <= 13; pin++) {
      mcp_stepper.pinMode(pin, OUTPUT);
  }
  
  mcp_stepper.digitalWrite(STEP_A, LOW);
  mcp_stepper.digitalWrite(DIRE_A, LOW);

  mcp_stepper.digitalWrite(STEP_B, LOW);
  mcp_stepper.digitalWrite(DIRE_B, LOW);

  stepper_button.begin(RPM, Microsteps);
  stepper_rail.begin(RPM, Microsteps);


  // ---------- RGB-LED SETUP ----------
  for(int i = 0; i < 60; i++) {
      led_state_dict[i] = {i, 0};
  }
  strip.begin();  // INITIALIZE WS2812B strip object
  strip.clear();  // SET all LED to OFF
  strip.setBrightness(BRIGHTNESS);  // Set LED brightness to "BRIGHTNESS"
  strip.show(); // adopt changes


  // ---------- BUTTON-MATRIX SETUP ----------
  Wire.begin();     // Initialisiere die I2C-Schnittstelle
  // Konfiguriere alle Pins von Port A und Port B als Eingänge
  writeMCP23017(MCP23017_ADDRESS_MATRIX, IODIRA, 0xFF); // 0xFF: Alle Pins von Port A als Eingang
  writeMCP23017(MCP23017_ADDRESS_MATRIX, IODIRB, 0xFF); // 0xFF: Alle Pins von Port B als Eingang
}


// ---------- ---------- LOOP ---------- ----------

void loop() {
  int result = calculateResult();
  if (result != -1) {
    Serial.print("Result,");
    Serial.println(result);
    
    set_RGB_LED(result);
  }
  delay(50);
}


// ---------- ---------- MAIN-METHODS ---------- ----------

// BUTTON-MATRIX Initialisierung und Berechnung
int calculateResult() {
  static uint8_t lastInputsA = 0xFF;
  static uint8_t lastInputsB = 0xFF;

  // Lese die Eingänge von Port A und Port B
  uint8_t inputsA = readMCP23017(MCP23017_ADDRESS_MATRIX, GPIOA);
  uint8_t inputsB = readMCP23017(MCP23017_ADDRESS_MATRIX, GPIOB);

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


// RGB-LED Stripe farbe setzen
void set_RGB_LED(int new_pos) {
  strip.clear();
  strip.setBrightness(BRIGHTNESS);

  for(LedData &led : led_state_dict) {
    int pos = led.pos;
    int state = led.state;
    
    if (pos == new_pos) {
      state += 1;
      state %= 3;
      if (state == 0){
        strip.setPixelColor(0, BLANK);
      } else if (state == 1){
        strip.setPixelColor(0, SYMBOL_1);
      } else if (state == 2){
        strip.setPixelColor(0, SYMBOL_2);
      }
    } else {
      if (state == 0){
        strip.setPixelColor(0, BLANK);
      } else if (state == 1){
        strip.setPixelColor(0, SYMBOL_1);
      } else if (state == 2){
        strip.setPixelColor(0, SYMBOL_2);
      }
    }
  }
  strip.show(); // adopt changes
  Serial.println("LED_set");
}


// Stepper Motor Button Press
void stepper_press_button() {
  stepper_button.rotate(20);
  delay(100);
  stepper_button.rotate(-20);
  Serial.print("Button_pressed");
}



// ---------- ---------- DEMO ---------- ----------

void led_demo() {
  strip.clear();  // set all pixel colors to 'off'. It only takes effect if pixels.show() is called
  strip.setBrightness(BRIGHTNESS); // a value from 0 to 255

  // turn pixels to green one by one with delay between each pixel
  for (int pixel = 0; pixel < NUM_PIXELS; pixel++) {         // for each pixel
    strip.setPixelColor(pixel, strip.Color(0, 255, 0));  // it only takes effect if pixels.show() is called
    
    if(pixel >= 1) {
      strip.setPixelColor((pixel-1), strip.Color(0, 0, 255));
    }

    if(pixel >= 2) {
      strip.setPixelColor((pixel-2), strip.Color(255, 0, 0));
    }

    if(pixel >= 3) {
      strip.setPixelColor((pixel-3), strip.Color(0, 0, 0));
    }

    strip.show();

    delay(DELAY_INTERVAL);  // pause between each pixel
  }
}

void led_3(){
  strip.clear();  // set all pixel colors to 'off'. It only takes effect if pixels.show() is called
  strip.setBrightness(BRIGHTNESS); // a value from 0 to 255

  strip.setPixelColor(0, strip.Color(255, 0, 0));  // it only takes effect if pixels.show() is called
  strip.setPixelColor(1, strip.Color(0, 255, 0));  // it only takes effect if pixels.show() is called
  strip.setPixelColor(2, strip.Color(0, 0, 255));  // it only takes effect if pixels.show() is called

  strip.show();
}