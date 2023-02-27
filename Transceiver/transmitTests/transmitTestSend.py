import yaml
import time
import sys
import os.path

# If git doesn't cooperate:
# git add .\code\transmitTests\transmitTestSend.py

# Get the file Radio.py into PATH
full_path = os.path.realpath(__file__)
projectdir = os.path.dirname(os.path.dirname(full_path))
radiodir = os.path.join(projectdir, "radio")
sys.path.insert(0, radiodir)

tests_per_config = 3

from radio import Radio
print("Radio.py located")

with open("transmitTestConfig.yaml", "r") as stream:
    config_dict = yaml.safe_load(stream)
radio = Radio(config_dict)

test_cases = []
# each test case is a 3-tuple (bandwidth, spreading factor, transmission power)
for spreading_factor in range(7, 13):
    for bandwidth in (500000, 250000, 125000, 62500):
        for tx_power in (23, 20, 17):
            for i in range(tests_per_config):
                test_cases.append((bandwidth, spreading_factor, tx_power))

print("Tests loaded")

test_attempts = 0
c_idx = 0
with open("log.yaml", 'a', buffering=1) as file:
    while c_idx < len(test_cases):

        if c_idx % tests_per_config == 0:
            print(f"Tests {int(100 * (c_idx / len(test_cases)))}% completed")

        config = test_cases[c_idx]

        radio.rfm9x.signal_bandwidth = config[0]
        radio.rfm9x.spreading_factor = config[1]
        radio.rfm9x.tx_power = config[2]

        print(f"Radio now configured for: Bandwidth {config[0]}, Spreading Factor {config[1]}, Tx Power {config[2]}")

        # Attempt to conduct test successfully
        attempts = 0
        ack_success = False
        ack_pack = None
        while attempts < 2 and not ack_success:
            # Configure for send

            # Send packet
            send_time = time.time_ns()
            radio.send((send_time, 0, config[0], config[1], config[2], c_idx, 0, 0))

            # Configure for receive

            # Receive acknowledgement
            ack_pack = radio.receive()

            time.sleep(0.05)

            if ack_pack is not None:
                ack_success = True
                break
            else:
                print(f"No acknowledgement received for test {c_idx} ({config})")
                attempts += 1

        print(f"Attempts: {attempts}, Success: {ack_success}")
        print(f"Packet: {ack_pack}")

        if ack_success:
            print("Ack Success; recording and moving on to the next test")
            ack_pack["final_time"] = time.time_ns() - ack_pack["ping_time"]
            # Update the file immediately so that we keep this data
            yaml.dump([ack_pack], file)
            # Putting ack_pack into a little list helps keep the different tests separate in the yaml
            file.flush()
            c_idx += 1
        else:
            print("Test Failed, Moving On")
            c_idx += 1

# log.yaml should have all the info
print("Tests completed successfully")
