/*
  ESP32 -> Flask patient monitoring API (educational prototype)

  Arduino IDE library:
    - SparkFun MAX3010x Sensor Library

  Wiring for a common MAX30102 breakout:
    VIN -> 3V3 (check your breakout board specifications)
    GND -> GND
    SDA -> GPIO 21
    SCL -> GPIO 22

  IMPORTANT:
  The example uses the SparkFun library's example heart-rate algorithm.
  SpO2 is a placeholder here, not a validated clinical measurement.
  Temperature is also a placeholder until you add and validate a temperature
  sensor. Do not use these values for diagnosis or emergency care.
*/
#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include "MAX30105.h"
#include "heartRate.h"

const char* WIFI_SSID = "YOUR_WIFI_NAME";
const char* WIFI_PASSWORD = "YOUR_WIFI_PASSWORD";
const char* SERVER_URL = "http://192.168.1.10:5000/api/readings";
const char* API_KEY = "CHANGE_TO_THE_API_KEY_FROM_DOT_ENV";
const int PATIENT_ID = 1;

MAX30105 particleSensor;
const byte RATE_SIZE = 4;
byte rates[RATE_SIZE];
byte rateSpot = 0;
long lastBeat = 0;
float beatsPerMinute = 0;
int beatAvg = 0;

unsigned long lastSend = 0;
const unsigned long SEND_INTERVAL_MS = 5000;

void connectWiFi() {
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to Wi-Fi");
  unsigned long started = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - started < 20000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Connected. ESP32 IP: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("Wi-Fi connection failed; will retry.");
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);
  connectWiFi();

  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println("MAX30102 not found. Check wiring and power.");
    while (true) delay(1000);
  }

  // Configuration adapted from common SparkFun MAX3010x examples.
  particleSensor.setup();
  particleSensor.setPulseAmplitudeRed(0x0A);
  particleSensor.setPulseAmplitudeGreen(0);
  Serial.println("Sensor initialized.");
}

void sendReading(float heartRate, float spo2, float temperature) {
  if (WiFi.status() != WL_CONNECTED) {
    connectWiFi();
    if (WiFi.status() != WL_CONNECTED) return;
  }

  HTTPClient http;
  http.begin(SERVER_URL);
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-API-Key", API_KEY);

  String body = "{\"patient_id\":" + String(PATIENT_ID) +
                ",\"heart_rate\":" + String(heartRate, 1) +
                ",\"spo2\":" + String(spo2, 1) +
                ",\"temperature\":" + String(temperature, 1) + "}";

  int status = http.POST(body);
  Serial.print("POST status: ");
  Serial.println(status);
  Serial.println(http.getString());
  http.end();
}

void loop() {
  long irValue = particleSensor.getIR();

  if (checkForBeat(irValue)) {
    long delta = millis() - lastBeat;
    lastBeat = millis();
    beatsPerMinute = 60.0 / (delta / 1000.0);

    if (beatsPerMinute > 20 && beatsPerMinute < 255) {
      rates[rateSpot++] = (byte)beatsPerMinute;
      rateSpot %= RATE_SIZE;
      int total = 0;
      for (byte i = 0; i < RATE_SIZE; i++) total += rates[i];
      beatAvg = total / RATE_SIZE;
    }
  }

  if (millis() - lastSend >= SEND_INTERVAL_MS) {
    lastSend = millis();

    // Replace these placeholders with validated sensor outputs.
    // MAX30102 IR pulse data alone does NOT provide clinically reliable SpO2.
    float demoSpO2 = 98.0;
    float demoTemperature = 36.8;

    if (irValue > 50000 && beatAvg > 0) {
      Serial.printf("IR=%ld HR=%d (demo SpO2/temp)\n", irValue, beatAvg);
      sendReading((float)beatAvg, demoSpO2, demoTemperature);
    } else {
      Serial.println("Finger/sensor signal not detected; no reading sent.");
    }
  }
  delay(20);
}
