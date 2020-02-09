#include <Wire.h>

#define ALT_ADDR 0x77
#define CONVERT_D1_256 0x40
#define CONVERT_D2_256 0x50 


void setup() {
  // put your setup code here, to run once:
  Wire.begin();
  Serial.begin(9600);

  // reset the altimeter
  Wire.beginTransmission(ALT_ADDR);
  Wire.write(0x1e);
  Wire.endTransmission();

  delay(500);
  Serial.println("Device reset");
}

void loop() {
  //tell the altimeter to convert d1 (not quite sure what it does)
  /*Serial.println("Converting to D1");
  Wire.beginTransmission(ALT_ADDR);
  Wire.write(CONVERT_D1_256);
  Wire.endTransmission();*/

  Serial.println("Converting to D2");
  Wire.beginTransmission(ALT_ADDR);
  Wire.write(CONVERT_D2_256);
  Wire.endTransmission();

  delay(100);
  
  // tell the altimeter to perform an ADC read
  Wire.beginTransmission(ALT_ADDR);
  Wire.write(0x00);
  Wire.endTransmission();

  // wait a bit for the read to go through
  delay(100);

  // returned read is 24 bits (3 bytes)
  Wire.requestFrom(ALT_ADDR, 3);

  Serial.println("Waiting for 3 bytes...");

  // wait for the bytes to become available
  while (Wire.available() < 3);

  int reading;
  reading |= Wire.read();
  reading << 8;
  reading |= Wire.read();
  reading << 8;
  reading |= Wire.read();
  Serial.print("Read: ");
  Serial.println(reading);

  delay(500);
}
