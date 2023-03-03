import serial
import time

# Initialize the serial port
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)

# Send a command to the GPS module to check its status
ser.write("$PMTK605\r\n".encode())
time.sleep(1)

# Read the response from the GPS module
response = ser.readline().decode('utf-8').strip()

# Check the response to see if the GPS module is turned on
if "PMTK605" in response:
    if "PMTK605,0" in response:
        print("GPS module is powered off")
    elif "PMTK605,1" in response:
        print("GPS module is powered on")
else:
    print("Invalid response from GPS module")

# Close the serial port
ser.close()
