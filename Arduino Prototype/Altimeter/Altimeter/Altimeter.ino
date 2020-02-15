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

#define T_REF 20



int C1;
int C2; 
int C3; 
int C4;
int C5;
int C6;


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
  int d1 = read_data(CONVERT_D1_4096);//uncorrected pressure data
  int d2 = read_data(CONVERT_D2_4096);//uncorrected temp data

  Serial.println(d1);

  float dT = d2 - (C5 * 256);
  Serial.println(dT);
  float temp = 2000 + ((dT * 28312) / 8388608.0);
  Serial.print("Temperature is: ");
  Serial.println(temp);

  delay(500);
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

int read_prom(int command){
  
  Wire.beginTransmission(ALT_ADDR);
  Wire.write(command);
  Wire.endTransmission();

  
  delay(100);
  


  Wire.requestFrom(ALT_ADDR, 2);

  delay(100);
  // wait for the bytes to become available
  while (Wire.available() < 1);

  unsigned int reading;
  reading |= Wire.read();
  reading << 8;
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

  uint32_t reading;
  reading |= (uint32_t) Wire.read();
  reading << 8;
  reading |= (uint32_t) Wire.read();
  reading << 8;
  reading |= (uint32_t) Wire.read();
  return reading;
}
