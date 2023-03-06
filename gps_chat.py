import serial

# Set up the serial port
ser = serial.Serial('/dev/ttyS0', 9600, timeout=1)
print("serial opened")

# Send command to enable NMEA output
ser.write(b'$PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0*29\r\n')
#ser.write(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')
print("enabled NMEA output")

# Read and print GPS data
while True:
    data = ser.readline().decode('utf-8').strip()
    if data.startswith('$GPGGA'):
        # Parse the GGA sentence
        parts = data.split(',')
        if parts[6] != '0':
            # If fix quality is not 0, print fix message
            print('GPS fix achieved!')
        else:
            print('GPS not fixed')
        # Print the full GGA sentence
        print(data)