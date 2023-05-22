import time
from ms5803 import MS5803
from radio_launch_test import Radio

P0 = 1010.837  # Approximate sea level pressure in mbar at Galveston

#trx = Radio("/home/pi/Neutro/neutro_config_32523.yaml", None)

altimeter = MS5803(0)


while True:
    pressure, temp = altimeter.read()
    h = ((P0 / pressure) ** (1 / 5.257) - 1) * (temp + 273.15) / 0.0065
    data = {'pressure': pressure, 'temperature': temp, 'altitude': h}
    #trx.send(data)
    print(data)
    time.sleep(1.0)
