import time
import board
import busio
import adafruit_bno08x
from adafruit_bno08x.i2c import BNO08X_I2C

i2c = busio.I2C(board.D3, board.D2, frequency=800000)
bno = BNO08X_I2C(i2c)
print("initialized!")

bno.enable_feature(adafruit_bno08x.BNO_REPORT_ROTATION_VECTOR)
print("enabled!")