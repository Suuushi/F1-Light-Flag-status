#include <SoftwareSerial.h>
#include <Adafruit_NeoPixel.h>
#include <math.h>

#define NUM_PIXELS 60
#define LED_STRIP_PIN 6

#define PULSE_LENGTH 2000

boolean on = true;

float brightness = -1;

float a = 0;
Adafruit_NeoPixel strip(NUM_PIXELS, LED_STRIP_PIN, NEO_GRB + NEO_KHZ800);
uint32_t yellow, red, green, white;

void setup() {
  Serial.begin(57600);
  strip.begin();
  strip.show();
  yellow = strip.Color(255, 255, 0);
  green = strip.Color(0, 255, 0);
  white = strip.Color(255, 255, 255);
  red = strip.Color(255, 0, 0);            
  strip.setBrightness((255 * brightness));  // 0 - 255
}

void loop() {
  if (Serial.available() > 0) {
    if (brightness <= a) {
      String brightnessdata = Serial.readStringUntil('\n');
      brightness = brightnessdata.toFloat();
      ////Serial.println("bright set");

      delay(100);
    } else {
      String lapcountdata = Serial.readStringUntil('\n');
      Serial.println("AL: " + lapcountdata);

      String state = Serial.readStringUntil('\n');
      Serial.println("AS: " + state);
      // String state = String("5");

      strip.setBrightness((255 * brightness));
      if (state == "0" or state == "-1") {
        setAll(255, 255, 255, brightness);
      } else if (state == "1") {
        lapcount(0, 255, 0, brightness, lapcountdata);
      } else if (state == "2") {
        setAll(255, 255, 0, brightness);
        strip.show();
      } else if (state == "3" or state == "4") {  // FLASHING YELLOW
        Flash(255, 255, 0);
      } else if (state == "5") {
        setAll(255, 0, 0, brightness);
      } else if (state == "6") {
        Flash(255, 255, 255);
        //CHEKERED FLAG
        // maybe black/white worms or white/black flashing
      } else if (state == "7") {  // Fade Yellow
        Fade(255, 255, 0);
      } else {
        Serial.println("NO MODE");
        Serial.println("NO MODE");
        strip.fill();
        strip.show();
      }
    }
  }
}

void setAll(int r, int g, int b, float brightness) {
  uint32_t color = strip.Color((int)(r * brightness), int(g * brightness), int(b * brightness));
  for (int ledID = 0; ledID < NUM_PIXELS; ledID++)
    strip.setPixelColor(ledID, color);
  strip.show();
}

void Fade(int r, int g, int b) {    // color pulsing
  long lm = millis();
  while (millis() - lm < 5000) {
    float pulseBrightness = brightness * (0.5 + 0.5 * sin(2.0 * PI * (millis() / (float)PULSE_LENGTH)));
    setAll(r, g, b, pulseBrightness);
  }
}

void Flash(int r, int g, int b) {
  long lm = millis();
  while (millis() - lm < 5000) {
    setAll(r, g, b, brightness);
    delay(200);
    strip.clear();
    strip.show();
    delay(200);
  }
}

void lapcount(int r, int g, int b, float brightness, String lapcountdata) {
  uint32_t color = strip.Color((int)(r * brightness), int(g * brightness), int(b * brightness));
  float lapcounter = lapcountdata.toFloat();

  float lap = fmod(lapcounter, 1); //Fade last LED : lapcounter = 1.2 -> LED(0) = brightness 1; LED(1) = brightness 0.2
  uint32_t color2 = strip.Color((int)(r * brightness * lap), int(g * brightness * lap), int(b * brightness * lap));
  int lapint = (int)lapcounter;

  for (int i = 0; i < lapint; i++) {
    strip.setPixelColor(i, color);
  }
  strip.setPixelColor(((int)lapint), color2);
  strip.show();
}
