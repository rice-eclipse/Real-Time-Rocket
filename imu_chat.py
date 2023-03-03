import smbus
import time

# BNO085 I2C address
BNO085_ADDR = 0x4A

# I2C bus number on Raspberry Pi Zero
I2C_BUS_NUM = 1

# Register addresses
BNO_CHIP_ID_ADDR = 0x00
BNO_QUATERNION_ADDR = 0x01
BNO_EULER_ADDR = 0x0D

# Initialize I2C bus
bus = smbus.SMBus(I2C_BUS_NUM, timeout=1)

# Read chip ID
chip_id = bus.read_byte_data(BNO085_ADDR, BNO_CHIP_ID_ADDR)
print("BNO085 chip ID: 0x{:02X}".format(chip_id))

# Enable sensors
bus.write_byte_data(BNO085_ADDR, 0x7F, 0x00) # set command register
bus.write_byte_data(BNO085_ADDR, 0x08, 0x01) # enable accelerometer
bus.write_byte_data(BNO085_ADDR, 0x08, 0x02) # enable gyroscope
bus.write_byte_data(BNO085_ADDR, 0x08, 0x04) # enable magnetometer
bus.write_byte_data(BNO085_ADDR, 0x08, 0x10) # enable rotation vector

# Read quaternion values
while True:
    quat_data = bus.read_i2c_block_data(BNO085_ADDR, BNO_QUATERNION_ADDR, 16)
    w = (quat_data[0] << 8) | quat_data[1]
    x = (quat_data[2] << 8) | quat_data[3]
    y = (quat_data[4] << 8) | quat_data[5]
    z = (quat_data[6] << 8) | quat_data[7]
    print("Quaternion: w={:.3f}, x={:.3f}, y={:.3f}, z={:.3f}".format(w/16384.0, x/16384.0, y/16384.0, z/16384.0))
    time.sleep(0.1)

# Read Euler angles
while True:
    euler_data = bus.read_i2c_block_data(BNO085_ADDR, BNO_EULER_ADDR, 6)
    heading = (euler_data[0] << 8) | euler_data[1]
    roll = (euler_data[2] << 8) | euler_data[3]
    pitch = (euler_data[4] << 8) | euler_data[5]
    print("Heading: {:.3f} deg, Roll: {:.3f} deg, Pitch: {:.3f} deg".format(heading/16.0, roll/16.0, pitch/16.0))
    time.sleep(0.1)
