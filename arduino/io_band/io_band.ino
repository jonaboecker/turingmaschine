#include <Adafruit_NeoPixel.h>
#ifdef __AVR__
#include <avr/power.h>  // Required for 16 MHz Adafruit Trinket
#endif

#define PIN_WS2812B 4  // Arduino pin that connects to WS2812B
#define NUM_PIXELS 60  // The number of LEDs (pixels) on WS2812B

#define DELAY_INTERVAL 250  // 250ms pause between each pixel

Adafruit_NeoPixel WS2812B(NUM_PIXELS, PIN_WS2812B, NEO_GRB + NEO_KHZ800);

void setup() {
  WS2812B.begin();  // INITIALIZE WS2812B strip object (REQUIRED)
}

void loop() {
  WS2812B.clear();  // set all pixel colors to 'off'. It only takes effect if pixels.show() is called
  WS2812B.setBrightness(100); // a value from 0 to 255

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
