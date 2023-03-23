import eclipse_radio_v1 as eradio
import time

NUM_SENDS = 5

bandwidth = float(input("Enter bandwidth (500, 250, 125, 62.5): "))
spreading = int(input("Enter spreading factor (7-12): "))
tx_power = int(input("Enter transmit power (23, 20, 15, 10): "))

trx = eradio.Radio("stadium_config.yaml", None)
trx.trx.signal_bandwidth = bandwidth * 10**3
trx.trx.spreading_factor = spreading
trx.trx.tx_power = tx_power

for i in range(NUM_SENDS):
    data = {'bandwidth': bandwidth, 'spreading': spreading, 'tx_power': tx_power}
    trx.send(data)
    time.sleep(0.5)
