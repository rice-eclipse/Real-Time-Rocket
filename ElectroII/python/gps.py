<<<<<<< HEAD
# Simple GPS module demonstration.
# Will print NMEA sentences received from the GPS, great for testing connection
# Uses the GPS to send some commands, then reads directly from the GPS
import time
import board
#import busio
import adafruit_gps
import digitalio

# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
#uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
# for a computer, use the pyserial library for uart access
import serial

import os
permission_command = "sudo chmod 777 /dev/ttyS0"
sudoPassword = "raspberry"
os.system('echo %s|sudo -S %s' % (sudoPassword, permission_command))


reset = digitalio.DigitalInOut(board.D1)
reset.direction = digitalio.Direction.OUTPUT
fix = digitalio.DigitalInOut(board.D5)
fix.direction = digitalio.Direction.INPUT

reset.value = True #set reset pin to high, pin is active low

uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
# If using I2C, we'll create an I2C interface to talk to using default pins
# i2c = board.I2C()
# Create a GPS module instance.
gps = adafruit_gps.GPS(uart)  # Use UART/pyserial
# gps = adafruit_gps.GPS_GtopI2C(i2c)  # Use I2C interface
# Initialize the GPS module by changing what data it sends and at what rate.
# These are NMEA extensions for PMTK_314_SET_NMEA_OUTPUT and
# PMTK_220_SET_NMEA_UPDATERATE but you can send anything from here to adjust
# the GPS module behavior:
#   https://cdn-shop.adafruit.com/datasheets/PMTK_A11.pdf
# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# Turn on just minimum info (RMC only, location):
# gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn off everything:
# gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn on everything (not all of it is parsed!)
# gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b"PMTK220,1000")
# Or decrease to once every two seconds by doubling the millisecond value.
# Be sure to also increase your UART timeout above!
# gps.send_command(b'PMTK220,2000')
# You can also speed up the rate, but don't go too fast or else you can lose
# data during parsing.  This would be twice a second (2hz, 500ms delay):
# gps.send_command(b'PMTK220,500')
# Main loop runs forever printing data as it comes in
timestamp = time.monotonic()
while True:
    #os.system('echo %s|sudo -S %s' % (sudoPassword, permission_command))
    gps.update()
    
    if uart.inWaiting:
        print("in waiting")
    else:
        print("not in waiting")
    
    
    if fix.value:
        print("fix pin is HIGH")
    else:
        print("fix pin is LOW")

    if gps.has_fix:
        print("gps.has_fix")
    else:
        print("gps_does_not_have_fix")
    
    recieved = uart.read()
    print(recieved)
    
    
    try:
        data = gps.read(32)  # read up to 32 bytes
        print(data)  # this is a bytearray type
        if data is not None:
            # convert bytearray to string
            data_string = "".join([chr(b) for b in data])
            print(data_string, end="")
        if time.monotonic() - timestamp > 5:
            # every 5 seconds...
            gps.send_command(b"PMTK605")  # request firmware version
            timestamp = time.monotonic()
    except Exception as e:
        print("Exception Caught: " + str(e))
   
=======
# Simple GPS module demonstration.
# Will print NMEA sentences received from the GPS, great for testing connection
# Uses the GPS to send some commands, then reads directly from the GPS
import time
import board
#import busio
import adafruit_gps
import digitalio

# Create a serial connection for the GPS connection using default speed and
# a slightly higher timeout (GPS modules typically update once a second).
# These are the defaults you should use for the GPS FeatherWing.
# For other boards set RX = GPS module TX, and TX = GPS module RX pins.
#uart = busio.UART(board.TX, board.RX, baudrate=9600, timeout=10)
# for a computer, use the pyserial library for uart access
import serial

import os
permission_command = "sudo chmod 777 /dev/ttyS0"
sudoPassword = "raspberry"
os.system('echo %s|sudo -S %s' % (sudoPassword, permission_command))


reset = digitalio.DigitalInOut(board.D17)
reset.direction = digitalio.Direction.OUTPUT
standby = digitalio.DigitalInOut(board.D5)
standby.direction = digitalio.Direction.OUTPUT
fix = digitalio.DigitalInOut(board.D22)
fix.direction = digitalio.Direction.INPUT

reset.value = True #set reset pin to high, pin is active low
standby.value = True  #set standby pin to high, pin is active low

uart = serial.Serial("/dev/ttyS0", baudrate=9600, timeout=1)
# If using I2C, we'll create an I2C interface to talk to using default pins
# i2c = board.I2C()
# Create a GPS module instance.
gps = adafruit_gps.GPS(uart)  # Use UART/pyserial
# gps = adafruit_gps.GPS_GtopI2C(i2c)  # Use I2C interface
# Initialize the GPS module by changing what data it sends and at what rate.
# These are NMEA extensions for PMTK_314_SET_NMEA_OUTPUT and
# PMTK_220_SET_NMEA_UPDATERATE but you can send anything from here to adjust
# the GPS module behavior:
#   https://cdn-shop.adafruit.com/datasheets/PMTK_A11.pdf
# Turn on the basic GGA and RMC info (what you typically want)
gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
# Turn on just minimum info (RMC only, location):
# gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn off everything:
# gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Turn on everything (not all of it is parsed!)
gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')
# Set update rate to once a second (1hz) which is what you typically want.
gps.send_command(b"PMTK220,1000")
# Or decrease to once every two seconds by doubling the millisecond value.
# Be sure to also increase your UART timeout above!
# gps.send_command(b'PMTK220,2000')
# You can also speed up the rate, but don't go too fast or else you can lose
# data during parsing.  This would be twice a second (2hz, 500ms delay):
# gps.send_command(b'PMTK220,500')
# Main loop runs forever printing data as it comes in
timestamp = time.monotonic()
while True:
    #os.system('echo %s|sudo -S %s' % (sudoPassword, permission_command))
    gps.update()
    
    if uart.inWaiting:
        print("in waiting")
    else:
        print("not in waiting")
    
    
    if fix.value:
        print("fix pin is HIGH")
    else:
        print("fix pin is LOW")
    
    try:
        data = gps.read(32)  # read up to 32 bytes
        print(data)  # this is a bytearray type
        if data is not None:
            # convert bytearray to string
            data_string = "".join([chr(b) for b in data])
            print(data_string, end="")
        if time.monotonic() - timestamp > 5:
            # every 5 seconds...
            gps.send_command(b"PMTK605")  # request firmware version
            timestamp = time.monotonic()
    except Exception as e:
        print("Exception Caught: " + str(e))
   
>>>>>>> 7f8bc5da2294e1b557f413def0b7f7284d5253ad
