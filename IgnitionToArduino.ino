#include <SPI.h>
#include <Ethernet.h>
#include <Arduino_JSON.h>

// MAC + static IP for Arduino
byte mac[] = { 0xA8, 0x61, 0x0A, 0xAE, 0x1A, 0x42 };
IPAddress ip(192,168,137,50);

// Start server on port 80
EthernetServer server(80);

// JSON Object
JSONVar jsonObj;

// Updates the json file
void updateJson();

void setup() {
  pinMode(LED_BUILTIN, OUTPUT);

  Serial.begin(9600);
  Ethernet.begin(mac, ip);
  server.begin();

  Serial.print("Server running at: ");
  Serial.println(Ethernet.localIP());

  updateJson();
}

void loop() {
  EthernetClient client = server.available();
  if (client) {

    // Wait for request
    while (!client.available()) delay(1);

    // Read and discard request
    while (client.available()) client.read();

    // Update JSON
    updateJson();

    // Send JSON response
    client.println("HTTP/1.1 200 OK");
    client.println("Content-Type: application/json");
    client.println("Connection: close");
    client.println();

    client.print(JSON.stringify(jsonObj));

    delay(5);   // flush
    client.stop();
  }
}

// Update JSON with sensor readings
void updateJson() {
  // Digital outputs (avoid pins 0 & 1)
  jsonObj["Arduino Output Values"]["Digital"]["D0"] = digitalRead(2);
  jsonObj["Arduino Output Values"]["Digital"]["D1"] = digitalRead(3);
  jsonObj["Arduino Output Values"]["Digital"]["D2"] = digitalRead(4);
  jsonObj["Arduino Output Values"]["Digital"]["D3"] = digitalRead(5);
  jsonObj["Arduino Output Values"]["Digital"]["D4"] = digitalRead(6);

  // Analog outputs
  jsonObj["Arduino Output Values"]["Analog"]["A0"] = analogRead(A0);
  jsonObj["Arduino Output Values"]["Analog"]["A1"] = analogRead(A1);
  jsonObj["Arduino Output Values"]["Analog"]["A2"] = analogRead(A2);
  jsonObj["Arduino Output Values"]["Analog"]["A3"] = analogRead(A3);
  jsonObj["Arduino Output Values"]["Analog"]["A4"] = analogRead(A4);
  jsonObj["Arduino Output Values"]["Analog"]["A5"] = analogRead(A5);

  // Digital inputs (example static values)
  jsonObj["Arduino Input Values"]["Digital"]["D0"] = 6;
  jsonObj["Arduino Input Values"]["Digital"]["D1"] = 6;
  jsonObj["Arduino Input Values"]["Digital"]["D2"] = 6;
  jsonObj["Arduino Input Values"]["Digital"]["D3"] = 6;
  jsonObj["Arduino Input Values"]["Digital"]["D4"] = 6;
}
