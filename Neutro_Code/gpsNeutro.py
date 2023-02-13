# SPDX-FileCopyrightText: 2021 ladyada for Adafruit Industries
# SPDX-License-Identifier: MIT

# Simple GPS module demonstration.
# Will wait for a fix and print a message every second with the current location
import time
import board
import busio
import digitalio
import adafruit_gps
import serial
import os
# No reset for neturo, only fix and hw_s
fix = digitalio.DigitalInOut(board.D19)
fix.direction = digitalio.Direction.INPUT
hws = digitalio.DigitalInOut(board.D26)
hws.direction = digitalio.Direction.OUTPUT

# find out what this part does
permission_command = "sudo chmod 777 /dev/ttyS0"
sudoPassword = "realtimerocket" #"raspberry"
os.system('echo %s|sudo -S %s' % (sudoPassword, permission_command))

# Create a serial connection for the GPS connection using default speed and timeout of once per second
uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)

# Create a GPS module instance through the uart interface
gps = adafruit_gps.GPS(uart)

# activate standby mode
gps.send_command(b"PMTK161")
# wake up from standby mode
hws.value = True

