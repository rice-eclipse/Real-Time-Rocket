// LoRa 9x_TX
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client (transmitter)
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example LoRa9x_RX

#include <SPI.h>
#include <RH_RF95.h>

#define RFM95_CS 4
#define RFM95_RST 5
#define RFM95_INT 3

// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 915.0
#define JOYPIN 1
#define JOYSWPIN 0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

void setup() 
{
  pinMode(RFM95_RST, OUTPUT);
  pinMode(8, OUTPUT);
  pinMode(JOYSWPIN, INPUT);
  digitalWrite(8, LOW);
  digitalWrite(RFM95_RST, HIGH);

  while (!Serial);
  Serial.begin(9600);
  delay(100);
  
  Serial.println("Arduino LoRa TX Servo Test");
  
  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);
  
  while (!rf95.init()) {
    Serial.println("LoRa radio init failed");
    Serial.println("Trying again...");
    delay(1000);
  }
  Serial.println("LoRa radio initialized.");

  // Defaults after init are 434.0MHz, modulation GFSK_Rb250Fd250, +13dbM
  if (!rf95.setFrequency(RF95_FREQ)) {
    Serial.println("setFrequency failed");
    while (1);
  }
  Serial.print("Set Freq to: "); Serial.println(RF95_FREQ);

  // Defaults after init are 434.0MHz, 13dBm, Bw = 125 kHz, Cr = 4/5, Sf = 128chips/symbol, CRC on
  
  // The default transmitter power is 13dBm, using PA_BOOST.
  // If you are using RFM95/96/97/98 modules which uses the PA_BOOST transmitter pin, then 
  // you can set transmitter powers from 5 to 23 dBm:
  rf95.setTxPower(23, false);
  Serial.println("Set power to 23");

}

void loop()
{
  String joy_message;
  String test_message = "bee movie";
  /*if (digitalRead(JOYSWPIN) == LOW) {
    joy_message = "LOW";
    Serial.println(joy_message);
  }
  else {
    float joy_val = analogRead(JOYPIN);
    joy_message = String(joy_val);
    Serial.println(joy_val);
  }*/
  char joy_message_chars[50];
  char test_message_chars[252];


  
  //joy_message.toCharArray(joy_message_chars, sizeof(joy_message_chars));
  test_message.toCharArray(test_message_chars, sizeof(test_message_chars));
  //rf95.send((uint8_t *)joy_message_chars, sizeof(joy_message_chars));
  rf95.send((uint8_t *) test_message_chars, sizeof(test_message_chars));


  Serial.print("Just sent a message ");
  Serial.println(test_message_chars);

  delay(500);
}
