import radio_launch_test as radio

trx = radio.Radio("example_config.yaml", "log.yaml")
# trx.set_amp_mode(radio.AmpMode.RECEIVE)

while True:
    packet_data = trx.receive_and_log()
    print(packet_data)
