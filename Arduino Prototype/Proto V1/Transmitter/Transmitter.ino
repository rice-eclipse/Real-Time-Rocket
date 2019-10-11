#include <Wire.h> // for I2C communication
#include <RH_RF95.h>

#define RFM95_CS 4
#define RFM95_RST 5
#define RFM95_INT 3

// Change to 434.0 or other frequency, must match RX's freq!
#define RF95_FREQ 915.0

// Singleton instance of the radio driver
RH_RF95 rf95(RFM95_CS, RFM95_INT);

#define ALTBASIS 18 //start altitude to calculate mean sea level pressure in meters

const int SENSORADDRESS = 0x60; // address specific to the MPL3115A1, value found in datasheet
byte IICdata[5] = {0,0,0,0,0}; //buffer for sensor data
int16_t packetnum = 0;
float altsmooth = 0; //for exponential smoothing

void setup(){
  Wire.begin(); // join i2c bus
  Serial.begin(9600); // start serial for output
  Serial.println("Setup");
  if(IIC_Read(0x0C) == 196); //checks whether sensor is readable (who_am_i bit)
  else Serial.println("i2c bad");

  // Radio initialization
  pinMode(RFM95_RST, OUTPUT);
  digitalWrite(RFM95_RST, HIGH);
  Serial.println("here0");
  // manual reset
  digitalWrite(RFM95_RST, LOW);
  delay(10);
  digitalWrite(RFM95_RST, HIGH);
  delay(10);
  Serial.println("here1");
  
  //accel setup               
  //adxl.powerOn();                     // Power on
  //adxl.setRangeSetting(8);            //2,4,8 or 16 - Higher Values = Wider Measurement Range - Lower Values = Greater Sensitivity
  //adxl.setSpiBit(0);                  //set to 0 for some reason
  
  //accel calibration, DO NOT MOVE module during startup, or calibration values will be inaccurate
  //adxl.readAccel(&cx, &cy, &cz);
  Serial.println("here2");
  
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
 
  IIC_Write(0x2D,0); //write altitude offset=0 (because calculation below is based on offset=0)
  //calculate sea level pressure by averaging a few readings
  Serial.println("Pressure calibration...");
  float buff[4];
  for (byte i=0;i<4;i++){
    IIC_Write(0x26, 0b00111011); //bit 2 is one shot mode, bits 4-6 are 128x oversampling
    IIC_Write(0x26, 0b00111001); //must clear oversampling (OST) bit, otherwise update will be once per second
    delay(550); //wait for sensor to read pressure (512ms in datasheet)
    IIC_ReadData(); //read sensor data
    buff[i] = Baro_Read(); //read pressure
    Serial.println(buff[i]);
  }
  float currpress=(buff[0]+buff[1]+buff[2]+buff[3])/4; //average over two seconds
 
  Serial.print("Current pressure: "); Serial.print(currpress); Serial.println(" Pa");
  //calculate pressure at mean sea level based on a given altitude
  float seapress = currpress/pow(1-ALTBASIS*0.0000225577,5.255877);
  Serial.print("Sea level pressure: "); Serial.print(seapress); Serial.println(" Pa");
  Serial.print("Temperature: ");
  Serial.print(IICdata[3]+(float)(IICdata[4]>>4)/16); Serial.println(" C");
 
  // This configuration option calibrates the sensor according to
  // the sea level pressure for the measurement location (2 Pa per LSB)
  IIC_Write(0x14, (unsigned int)(seapress / 2)>>8);//IIC_Write(0x14, 0xC3); // BAR_IN_MSB (register 0x14):
  IIC_Write(0x15, (unsigned int)(seapress / 2)&0xFF);//IIC_Write(0x15, 0xF3); // BAR_IN_LSB (register 0x15):
 
  //one reading seems to take 4ms (datasheet p.33);
  //oversampling 32x=130ms interval between readings seems to be best for 10Hz; slightly too slow
  //first bit is altitude mode (vs. barometer mode)
 
  //Altitude mode
  IIC_Write(0x26, 0b10111011); //bit 2 is one shot mode //0xB9 = 0b10111001
  IIC_Write(0x26, 0b10111001); //must clear oversampling (OST) bit, otherwise update will be once per second
  delay(550); //wait for measurement
  IIC_ReadData(); //
  altsmooth=Alt_Read();
  Serial.print("Altitude now: "); Serial.println(altsmooth);
  Serial.println("Done.");
}

void loop() {
  char timestamp[13] = "Time        ";
  itoa(millis()/1000, timestamp+5, 10);
  char number[10] = "#        ";
  itoa(packetnum++, number+1, 10);

  Serial.println("altimeter reading:");
  float pressure = read_pressure();
  Serial.print(pressure);
  Serial.println(" pascals");
  
  float height = read_height();
  Serial.print(height);
  Serial.println(" meters");
  
  float temp = read_tempature();
  Serial.print(temp);
  Serial.println("*C");
  
  Serial.println(timestamp);
  Serial.println(number);
  rf95.send((uint8_t *)timestamp, 13);
  rf95.send((uint8_t *)number, 10);
}

char altbaro_send[13] = "baro:       ";
char alt1_send[13] = "alt1:       ";
char alt2_send[13] = "alt2:       ";
char x_accel_read[13] = "            ";
char y_accel_read[13] = "            ";
char z_accel_read[13] = "            ";
//char temp_send[13] = "temp:       ";


/*
 * INTERNAL FUNCTIONS
 */

float read_pressure() {
  //
  float pres;
  IIC_Write(0x26, 0b00111011); //bit 2 is one shot mode //0xB9 = 0b10111001
  IIC_Write(0x26, 0b00111001); //must clear oversampling (OST) bit, otherwise update will be once per second
  delay(550); //wait for sensor to read pressure (512ms in datasheet)
  IIC_ReadData(); //read sensor data
  pres = Baro_Read();
  return pres;
}

float read_height() {
  //
  float alt;
  IIC_Write(0x26, 0b10111011); //bit 2 is one shot mode //0xB9 = 0b10111001
  IIC_Write(0x26, 0b10111001); //must clear oversampling (OST) bit, otherwise update will be once per second
  delay(550); //wait for sensor to read pressure (512ms in datasheet)
  IIC_ReadData(); //read sensor data
  alt = Alt_Read();
  return alt;
}

float read_tempature() {
  //
  int m_temp;
  float l_temp;
  float temp;
  m_temp = IICdata[3]; //temperature, degrees
  l_temp = (float)(IICdata[4]>>4)/16.0; //temperature, fraction of a degree
  temp = (float)(m_temp + l_temp);
  return temp;
}
 
float Baro_Read(){
  //this function takes values from the read buffer and converts them to pressure units
  unsigned long m_altitude = IICdata[0];
  unsigned long c_altitude = IICdata[1];
  float l_altitude = (float)(IICdata[2]>>4)/4; //dividing by 4, since two lowest bits are fractional value
  return((float)(m_altitude<<10 | c_altitude<<2)+l_altitude); //shifting 2 to the left to make room for LSB
}
 
float Alt_Read(){
  //Reads altitude data (if CTRL_REG1 is set to altitude mode)
  int m_altitude = IICdata[0];
  int c_altitude = IICdata[1];
  float l_altitude = (float)(IICdata[2]>>4)/16;
  return((float)((m_altitude << 8)|c_altitude) + l_altitude);
}
 
byte IIC_Read(byte regAddr){
  // This function reads one byte over I2C
  Wire.beginTransmission(SENSORADDRESS);
  Wire.write(regAddr); // Address of CTRL_REG1
  Wire.endTransmission(false); // Send data to I2C dev with option for a repeated start. Works in Arduino V1.0.1
  Wire.requestFrom(SENSORADDRESS, 1);
  return Wire.read();
}
 
void IIC_ReadData(){  //Read Altitude/Barometer and Temperature data (5 bytes)
  //This is faster than reading individual register, as the sensor automatically increments the register address,
  //so we just keep reading...
  byte i=0;
  Wire.beginTransmission(SENSORADDRESS);
  Wire.write(0x01); // Address of CTRL_REG1
  Wire.endTransmission(false);
  Wire.requestFrom(SENSORADDRESS,5); //read 5 bytes: 3 for altitude or pressure, 2 for temperature
  while(Wire.available()) IICdata[i++] = Wire.read();
}
 
void IIC_Write(byte regAddr, byte value){
  // This function writes one byto over I2C
  Wire.beginTransmission(SENSORADDRESS);
  Wire.write(regAddr);
  Wire.write(value);
  Wire.endTransmission(true);
}

