#include <WiFi.h>
#include <ESP32Servo.h>

#define GREEN 15
#define RED 4
#define SERVO 13

// Update these with values suitable for your network.
const char* ssid = "Kien";
const char* password = "(@ddk1912@)";

WiFiServer server(80);

Servo myServo;

void setup() {
  Serial.begin(115200);
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);

  myServo.attach(SERVO);

  WiFi.begin(ssid, password);
  Serial.println("Connecting to WiFi...");
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("Connected to WiFi");
  Serial.print("IP address: ");
  Serial.println(WiFi.localIP());
  server.begin();
}

void loop() {
  WiFiClient client = server.available();

  if (client) {
    Serial.println("New client connected");

    while (client.connected()) {
      if (client.available()) {
        String command = client.readStringUntil('\n');
        command.trim();
        if (command == "open") {
          digitalWrite(GREEN, HIGH);
          digitalWrite(RED, LOW);
          myServo.write(90);
          delay(10000);
        } else {
          digitalWrite(GREEN, LOW);
          digitalWrite(RED, HIGH);
          myServo.write(0);
        }
      } else {
        digitalWrite(GREEN, LOW);
        digitalWrite(RED, HIGH);
        myServo.write(0);
      }
    }
    client.stop();
    Serial.println("Client disconnected");
  } else {
    digitalWrite(GREEN, LOW);
    digitalWrite(RED, HIGH);
    myServo.write(0);
  }
}