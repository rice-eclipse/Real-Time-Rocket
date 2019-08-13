// LoRa 9x_TX
// -*- mode: C++ -*-
// Example sketch showing how to create a simple messaging client (transmitter)
// with the RH_RF95 class. RH_RF95 class does not provide for addressing or
// reliability, so you should only use RH_RF95 if you do not need the higher
// level messaging abilities.
// It is designed to work with the other example LoRa9x_RX

#include <SPI.h>
#include <RH_RF95.h>
#include <Adafruit_MPL3115A2.h>

#define RFM95_CS 4
#define RFM95_RST 5
#define RFM95_INT 3

// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 915.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);
Adafruit_MPL3115A2 baro = Adafruit_MPL3115A2();

void setup() 
{
pinMode(RFM95_RST, OUTPUT);
pinMode(8, OUTPUT);
digitalWrite(8, LOW);
digitalWrite(RFM95_RST, HIGH);

while (!Serial);
Serial.begin(9600);
delay(100);

Serial.println("Arduino LoRa TX Test!");

// manual reset
digitalWrite(RFM95_RST, LOW);
delay(10);
digitalWrite(RFM95_RST, HIGH);
delay(10);

while (!rf95.init()) {
  Serial.println("LoRa radio init failed");
  while (1);
}
Serial.println("LoRa radio init OK!");

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

if (!baro.begin()) {
    Serial.println("Couldn't find sensor.");
    return;
  }
}

int16_t packetnum = 0;  // packet counter, we increment per xmission

void loop()
{
//Serial.println("Sending to rf95_server");
// Send a message to rf95_server

// Gets pressure in inch Mercury
char presData[10] = "Pre      ";
float pres = baro.getPressure() / 3377.0;
itoa(pres, presData + 4, 10);

// Get altitude in meters
char altData[10] = "Alt      ";
float alt = baro.getAltitude();
itoa(alt, altData + 4, 10);

// Gets temp in C
char tempData[10] = "Temp     ";
float temp = baro.getTemperature();
itoa(temp, tempData + 5, 10);

char timestamp[13] = "Time        ";
itoa(millis()/1000, timestamp+5, 10);
timestamp[12] = 0;
char number[10] = "#        ";
itoa(packetnum++, number+1, 10);
number[9] = 0;


Serial.print("Sending timestamp: "); Serial.println(timestamp);
Serial.print("Sending number: "); Serial.println(number);

Serial.print("Sending pressure: "); Serial.println(presData);
Serial.print("Sending altitude: "); Serial.println(altData);
Serial.print("Sending temp (C): "); Serial.println(tempData);

//Serial.println("Sending..."); delay(10);
rf95.send((uint8_t *)timestamp, 13);
rf95.send((uint8_t *)number, 10);
rf95.send((uint8_t *)presData, 10);
rf95.send((uint8_t *)altData, 10);
rf95.send((uint8_t *)tempData, 10);

//Serial.println("Waiting for packet to complete..."); delay(10);
//rf95.waitPacketSent();
//// Now wait for a reply
//uint8_t buf[RH_RF95_MAX_MESSAGE_LEN];
//uint8_t len = sizeof(buf);

//Serial.println("Waiting for reply..."); delay(10);
//if (rf95.waitAvailableTimeout(1000))
//{ 
//  // Should be a reply message for us now   
//  if (rf95.recv(buf, &len))
// {
//    Serial.print("Got reply: ");
//    Serial.println((char*)buf);
//    Serial.print("RSSI: ");
//    Serial.println(rf95.lastRssi(), DEC);    
//  }
//  else
//  {
//    Serial.println("Receive failed");
//  }
//}
//else
//{
//  Serial.println("No reply, is there a listener around?");
//}
//delay(1000);
}
