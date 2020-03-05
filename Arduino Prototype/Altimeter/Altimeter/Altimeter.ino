#include <Wire.h>

#define ALT_ADDR 0x77

#define RESET_ALT 0x1E

#define CONVERT_D1_256 0x40
#define CONVERT_D2_256 0x50 
#define CONVERT_D1_4096 0x48
#define CONVERT_D2_4096 0x58


#define PROM_C0 0xA0
#define PROM_C1 0xA2
#define PROM_C2 0xA4
#define PROM_C3 0xA6
#define PROM_C4 0xA8
#define PROM_C5 0xAA
#define PROM_C6 0xAC



uint16_t C1;
uint16_t C2; 
uint16_t C3; 
uint16_t C4;
uint16_t C5;
uint16_t C6;


void setup() {
  // put your setup code here, to run once:
  Wire.begin();
  Serial.begin(9600);

  // reset the altimeter
  Wire.beginTransmission(ALT_ADDR);
  Wire.write(ALT_ADDR);
  Wire.endTransmission();

  delay(500);
  Serial.println("Device reset");
  Serial.println("Reading PROM");
  update_prom();

}

void loop() {
  uint32_t d1 = read_data(CONVERT_D1_4096);//uncorrected pressure data
  uint32_t d2 = read_data(CONVERT_D2_4096);//uncorrected temp data

  int32_t tRef = C5;
  tRef = tRef << 8;

  int32_t dT = d2 - tRef;

  long long longtemp = ((long long) dT) * ((long long) C6);//need 64 bits because of overflow errors
  longtemp = longtemp >> 23;
  longtemp = longtemp + 2000;
  int32_t inttemp = (int32_t) longtemp;
  double temp = ((float) inttemp) / 100;
  Serial.print("Temperature is: ");
  Serial.println(temp);

  int64_t off = ((int64_t) C2) << 16;//offset at actual temperature
  
  off += (C4*dT) >> 7; 
  
  //OLD MATH - has overflows out the wazoo
  int64_t sens = ((int64_t) C1) << 15;
  sens += (C3 * dT) >> 8;

  long long longpressure = d1 * sens >> 21;
  longpressure -= off;
  longpressure = longpressure >> 15;

  int32_t intpressure = (int32_t) longpressure;
  //
  double pressure = ((double) intpressure) / 100;
  
  Serial.print("Pressure is: ");
  Serial.println(pressure);

  delay(1000);
}


/*
 * Read the PROM memory from the altimeter.
 */
void update_prom(){
  C1 = read_prom(PROM_C1);
  C2 = read_prom(PROM_C2);
  C3 = read_prom(PROM_C3);
  C4 = read_prom(PROM_C4);
  C5 = read_prom(PROM_C5);
  C6 = read_prom(PROM_C6);
  Serial.print("C6 is: ");
  Serial.println(C6);
}

uint16_t read_prom(int command){
  
  Wire.beginTransmission(ALT_ADDR);
  Wire.write(command);
  Wire.endTransmission();

  delay(100);
  
  Wire.requestFrom(ALT_ADDR, 2);

  delay(100);
  // wait for the bytes to become available
  while (Wire.available() < 1);

  uint16_t reading;
  reading |= Wire.read();
  reading = reading << 8;
  reading |= Wire.read();
  return reading;
}

uint32_t read_data(int command) {
  Wire.beginTransmission(ALT_ADDR);
  Wire.write(command);
  Wire.endTransmission();

  
  delay(100);
  
  // tell the altimeter to perform an ADC read
  Wire.beginTransmission(ALT_ADDR);
  Wire.write(0x00);
  Wire.endTransmission();

  Wire.requestFrom(ALT_ADDR, 3);
  
  // wait for the bytes to become available
  while (Wire.available() < 3);

  //read off 3x 8-bit numbers
  uint32_t reading;
  reading = (uint32_t) 0;
  uint32_t a = Wire.read();
  a = a << 16;
  
  uint32_t b = Wire.read();
  b = b << 8;

  uint32_t c = Wire.read();
  
  c = c << 0;

  reading |= a;
  reading |= b;
  reading |= c;
  return reading;
}
