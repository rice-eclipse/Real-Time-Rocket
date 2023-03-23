from radio_launch_test import Radio
import time

trx = Radio("example_config.yaml", None)

while True:
    example_data = {'latitude': 29.72, 'longitude': -95.41, 'fix_quality': 2}
    trx.send(example_data)
    # time.sleep(1)
