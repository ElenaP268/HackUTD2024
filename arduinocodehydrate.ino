#define USE_ARDUINO_INTERRUPTS true
#include <LiquidCrystal.h>
#include <math.h>

const int rs = 12, en = 11, d4 = 5, d5 = 4, d6 = 3, d7 = 2;
LiquidCrystal lcd(rs, en, d4, d5, d6, d7);
const int buzzerPin = 9;
const int B = 4275;     // B value of the thermistor
const int R0 = 100000;  // R0 = 100k
const int pinTempSensor = A0;
const int pinTouch = 8;

void setup() {
  Serial.begin(9600);
  pinMode(buzzerPin, OUTPUT);
  pinMode(pinTouch, INPUT);
  lcd.begin(16, 2);
  lcd.clear();
}

void loop() {
  int sensorValue = digitalRead(pinTouch);
  int a = analogRead(pinTempSensor);

  float R = 1023.0 / a - 1.0;
  R = R0 * R;
  float temperature = 1.0 / (log(R / R0) / B + 1 / 298.15) - 273.15;

 String data = "<T=" + String(temperature) + ", P=" + String(sensorValue) + ">";
  Serial.println(data);  // Send data over serial

  if (temperature < 25 && sensorValue == 1) {
    tone(buzzerPin, 3000);
    delay(600);
    noTone(buzzerPin);
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Hydrate Formation!");
    lcd.setCursor(0, 1);
    lcd.print("High P & Low T!");
  } else if (sensorValue == 0 && temperature > 25) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("No Hydrate Formation!");
    lcd.setCursor(0, 1);
    lcd.print("Low P & High T!");
  } else if (sensorValue == 1 && temperature > 25) {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("No Hydrate Formation!");
    lcd.setCursor(0, 1);
    lcd.print("High P & High T!");
  } else {
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("No Hydrate Formation!");
    lcd.setCursor(0, 1);
    lcd.print("Low P & Low T!");
  }

  delay(500);  // Adjust delay as needed
}



