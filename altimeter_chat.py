import smbus
import time

# Define MS5803 constants
MS5803_ADDRESS = 0x76  # Address of the MS5803 altimeter
MS5803_RESET = 0x1E  # Reset command
MS5803_CONVERT_D1_256 = 0x40  # Start pressure conversion, OSR=256
MS5803_CONVERT_D2_256 = 0x50  # Start temperature conversion, OSR=256
MS5803_ADC_READ = 0x00  # ADC read command

# Define I2C bus
bus = smbus.SMBus(0)  # Use I2C bus 1 on Raspberry Pi

# Reset MS5803
bus.write_byte(MS5803_ADDRESS, MS5803_RESET)
time.sleep(0.05)

while True:
    # Start pressure conversion
    bus.write_byte(MS5803_ADDRESS, MS5803_CONVERT_D1_256)
    time.sleep(0.05)

    # Read ADC value for pressure
    adc = bus.read_i2c_block_data(MS5803_ADDRESS, MS5803_ADC_READ, 3)
    d1 = (adc[0] << 16) | (adc[1] << 8) | adc[2]

    # Start temperature conversion
    bus.write_byte(MS5803_ADDRESS, MS5803_CONVERT_D2_256)
    time.sleep(0.05)

    # Read ADC value for temperature
    adc = bus.read_i2c_block_data(MS5803_ADDRESS, MS5803_ADC_READ, 3)
    d2 = (adc[0] << 16) | (adc[1] << 8) | adc[2]

    # Calculate temperature
    dT = d2 - 8388608
    TEMP = 2000 + (dT * 5) / 8388608

    # Calculate pressure
    OFF = 0
    SENS = 0
    if TEMP < 2000:
        T2 = (dT * dT) / 2147483648
        OFF2 = 61 * ((TEMP - 2000) ** 2) / 16
        SENS2 = 2 * ((TEMP - 2000) ** 2)
        if TEMP < -1500:
            OFF2 += 15 * ((TEMP + 1500) ** 2)
            SENS2 += 8 * ((TEMP + 1500) ** 2)
    else:
        T2 = 0
        OFF2 = 0
        SENS2 = 0

    OFF = (2953 * 2 ** 21) + ((SENS2 * dT) / 2 ** 24) - OFF2
    SENS = (1100 * 2 ** 21) + ((SENS2 * dT) / 2 ** 25)

    P = (((d1 * SENS) / 2 ** 21) - OFF) / 2 ** 15

    print("Pressure: %.2f mbar" % P)
    print("Temperature: %.2f C" % TEMP)
    time.sleep(1)
