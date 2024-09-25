//Reciever End (Arduino)

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

// Pin connections
#define CE_PIN 9
#define CSN_PIN 10

// Initialize the radio object with CE and CSN pins
RF24 radio(CE_PIN, CSN_PIN);

const byte address[6] = "00001";  // Must match the address used in the transmitter

// Buffer to store received data
char receivedData[32] = "";  // 32 bytes max payload size

void setup() {
  Serial.begin(9600);
  
  // Initialize the radio communication
  radio.begin();
  radio.openReadingPipe(0, address);  // Open a reading pipe on the receiver
  radio.setPALevel(RF24_PA_MIN);      // Set power level (can adjust based on range needed)
  radio.startListening();             // Start listening for data
}

void loop() {
  // Check if data is available to be received
  if (radio.available()) {
    // Read the data into the buffer
    radio.read(&receivedData, sizeof(receivedData));
    
    // Display the received data on the serial monitor
    Serial.print("Received Data: ");
    Serial.println(receivedData);
    
    // Clear the buffer after reading the data
    memset(receivedData, 0, sizeof(receivedData));
  }
}