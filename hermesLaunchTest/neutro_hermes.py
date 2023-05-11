import time
from ms5803 import MS5803 as Altimeter
import eclipse_radio_v1 as eradio
import yaml

P0 = 1018.3  # Approximate sea level pressure in mbar at Galveston
CONFIG_FILENAME = "/home/pi/Neutro/hermesLaunchTest/neutro_config_hermes.yaml"
LOG_FILENAME = "/home/pi/Neutro/hermesLaunchTest/neutro_log_hermes.yaml"

trx = eradio.Radio(CONFIG_FILENAME, None)

altimeter = Altimeter(0)

packets_sent = 0

while True:
    pressure, temp = altimeter.read()
    altitude = ((P0 / (pressure + 1E-10)) ** (1 / 5.257) - 1) * (temp + 273.15) / 0.0065

    data = {'pressure': pressure, 'temperature': temp, 'altitude': altitude}
    trx.send(data)

    data['packetnum'] = packets_sent
    packets_sent += 1

    data['time'] = time.time_ns()

    with open(LOG_FILENAME, 'a', buffering=1) as logfile:
        yaml.dump([data], logfile)
        logfile.flush()

    print(data)
    time.sleep(2.05)
