# SPDX-FileCopyrightText: 2020 Bryan Siepert, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import time
import board
import busio
'''
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)
'''
from adafruit_bno08x.i2c import BNO08X_I2C

i2c = busio.I2C(board.D3, board.D2, frequency=400000)
bno = BNO08X_I2C(i2c)
print("initialized!")

# Print BNO085 calibration status.
#sys_cal, gyro_cal, accel_cal, mag_cal = bno.calibration_status
#print(f'System: {sys_cal}, Gyro: {gyro_cal}, Accel: {accel_cal}, Mag: {mag_cal}')

# Configure the BNO085 sensor.
bno.accelerometer_enabled = True
bno.gyro_enabled = True
bno.magnetometer_enabled = True
bno.orientation_enabled = True
bno.linear_acceleration_enabled = True
bno.gravity_enabled = True
bno.tap_detection_enabled = True
bno.step_detection_enabled = True
bno.wrist_wakeup_enabled = True
bno.pickup_enabled = True

# Enable quaternion reporting.
bno.report_quaternion = True

# Print BNO085 sensor data.
while True:
    # Get BNO085 sensor data.
    quat = bno.quaternion
    euler = bno.euler

    # Print sensor data.
    print(f'Quaternion: {quat}, Euler: {euler}')

    # Delay for a second.
    time.sleep(1)
