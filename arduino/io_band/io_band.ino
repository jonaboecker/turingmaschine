#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>  // Required for 16 MHz Adafruit Trinket
#endif

#define PIN_WS2812B 4  // Arduino pin that connects to WS2812B
#define NUM_PIXELS 60  // The number of LEDs (pixels) on WS2812B

#define DELAY_INTERVAL 250  // 250ms pause between each pixel

struct SensorData {
  int sensor_val; // Key
  int pos;        // Position
  int state;      // State
};

const int VOLTAGE_SENSOR_PIN = A0;

float voltage = 0;

const int delta = 100;

int flag = 0;

SensorData stripe_dict[] = {
  {700, 0, 0},
  {200, 1, 0},
  {700, 2, 0},
  {200, 3, 0},
  {700, 4, 0},
  {200, 5, 0},
  {700, 6, 0},
  {200, 7, 0},
  {700, 8, 0}
};

const int dictSize = sizeof(stripe_dict) / sizeof(stripe_dict[0]);

Adafruit_NeoPixel WS2812B(NUM_PIXELS, PIN_WS2812B, NEO_GRB + NEO_KHZ800);

void setup() {
  WS2812B.begin();  // INITIALIZE WS2812B strip object (REQUIRED)

  Serial.begin(9600);
}

void loop() {
  //int sensor_val = read_voltage();
  //Serial.println(sensor_val);
  //connect_led_demo(sensor_val);
  //led_demo();
  if (flag == 0){
    flag++;
    led_3();
  }
}

void led_demo() {
  WS2812B.clear();  // set all pixel colors to 'off'. It only takes effect if pixels.show() is called
  WS2812B.setBrightness(255); // a value from 0 to 255

  // turn pixels to green one by one with delay between each pixel
  for (int pixel = 0; pixel < NUM_PIXELS; pixel++) {         // for each pixel
    WS2812B.setPixelColor(pixel, WS2812B.Color(0, 255, 0));  // it only takes effect if pixels.show() is called
    
    if(pixel >= 1) {
      WS2812B.setPixelColor((pixel-1), WS2812B.Color(0, 0, 255));
    }

    if(pixel >= 2) {
      WS2812B.setPixelColor((pixel-2), WS2812B.Color(255, 0, 0));
    }

    if(pixel >= 3) {
      WS2812B.setPixelColor((pixel-3), WS2812B.Color(0, 0, 0));
    }

    WS2812B.show();

    delay(DELAY_INTERVAL);  // pause between each pixel
  }
}

void led_3(){
  WS2812B.clear();  // set all pixel colors to 'off'. It only takes effect if pixels.show() is called
  WS2812B.setBrightness(255); // a value from 0 to 255

  WS2812B.setPixelColor(0, WS2812B.Color(255, 0, 0));  // it only takes effect if pixels.show() is called
  WS2812B.setPixelColor(1, WS2812B.Color(0, 255, 0));  // it only takes effect if pixels.show() is called
  WS2812B.setPixelColor(2, WS2812B.Color(0, 0, 255));  // it only takes effect if pixels.show() is called

  WS2812B.show();
}

int read_voltage() {
  int sensorValue = analogRead(VOLTAGE_SENSOR_PIN);
  /*
  float voltage = sensorValue * (5/1024);
  Serial.print("Spannung: ");
  Serial.println(voltage);
  */
  delay(50);
  return sensorValue;
}

void connect_led_demo(int val) {
  WS2812B.setBrightness(255); // a value from 0 to 255

  for (int i = 0; i < dictSize; i++) {
    int threshold = stripe_dict[i].sensor_val;
    if (val >= threshold - delta && val <= threshold + delta) {

      /*
      Serial.print("Threashold ");
      Serial.print(stripe_dict[i].sensor_val);
      Serial.print(" is greater or equal to ");
      Serial.println(val);
      */

      int state = stripe_dict[i].state;
      int pixel = stripe_dict[i].pos;
      if (state == 0){
        WS2812B.setPixelColor(pixel, WS2812B.Color(255, 0, 0));
      } else if (state == 1){
        WS2812B.setPixelColor(pixel, WS2812B.Color(0, 255, 0));
      } else if (state == 2){
        WS2812B.setPixelColor(pixel, WS2812B.Color(0, 0, 255));
      } else if (state == 3){
        WS2812B.setPixelColor(pixel, WS2812B.Color(0, 0, 0));
      }

      
      Serial.print("Set Pixel ");
      Serial.print(pixel);
      Serial.print(" to state ");
      Serial.println(state);

      
      stripe_dict[i].state += 1;
      stripe_dict[i].state = stripe_dict[i].state % 4;
      WS2812B.show();
      delay(100);
    }
  }
}