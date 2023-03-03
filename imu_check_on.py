import smbus
import time

# Define the I2C address of the BNO085 IMU
BNO085_ADDR = 0x4B

# Define the register address of the chip ID
BNO_CHIP_ID_ADDR = 0x00

# Initialize the I2C bus with a timeout of 1 second
bus = smbus.SMBus(1, timeout=1)

# Read the chip ID from the BNO085 IMU
chip_id = bus.read_byte_data(BNO085_ADDR, BNO_CHIP_ID_ADDR)

# Print the chip ID
print(f"Chip ID: 0x{chip_id:02X}")
