import board
import busio
import digitalio
import adafruit_rfm9x
from collections.abc import Iterable
import struct
import yaml
import time

# Unified class for sending and receiving data
# Much from:
# https://learn.adafruit.com/adafruit-rfm69hcw-and-rfm96-rfm95-rfm98-lora-packet-padio-breakouts/circuitpython-for-rfm9x-lora


class Radio:
    def __init__(self, config_dict):
        """
        Constructs a Radio object with a given configuration

        Parameters:
            config_dict: a dictionary loaded from a configuration file with such fields as frequency, callsign, data_types, etc.

        Returns:
            The newly-constructed Radio object
        """
        # NOTICE: Configuration loading moved to __init__
        # I could have just called load_config, but I've heard it's better form to initialize all variables in __init__

        # Loading Basics
        self.radio_freq_mhz = config_dict["frequency_mhz"]

        self.callsign = config_dict["callsign"]

        self.packets_per_transmit = config_dict["packets_per_transmit"]
        self.transmit_per_second = config_dict["transmit_per_second"]

        # Loading Connections and Radio
        self.cs = digitalio.DigitalInOut(getattr(board, config_dict["cs_pin"]))
        self.reset = digitalio.DigitalInOut(getattr(board, config_dict["reset_pin"]))
        self.spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)

        # NARWAL RF Switch
        self.enable_amps = config_dict["enable_amps"]
        if self.enable_amps:
            self.CTRL1A = digitalio.DigitalInOut(getattr(board, config_dict["ctrl1A_pin"]))
            self.CTRL2A = digitalio.DigitalInOut(getattr(board, config_dict["ctrl2A_pin"]))
            self.CTRL1A.direction = digitalio.Direction.OUTPUT
            self.CTRL2A.direction = digitalio.Direction.OUTPUT

            self.CTRL1B = digitalio.DigitalInOut(getattr(board, config_dict["ctrl1B_pin"]))
            self.CTRL2B = digitalio.DigitalInOut(getattr(board, config_dict["ctrl2B_pin"]))
            self.CTRL1B.direction = digitalio.Direction.OUTPUT
            self.CTRL2B.direction = digitalio.Direction.OUTPUT

        self.enable_bypass = config_dict["enable_bypass"]

        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.radio_freq_mhz, baudrate=10_000_000)
        # Optional parameter baudrate of connection between rfm9x and SPI (baudrate is equal to bitrate)
        # Default baud rate is 10MHz but that may be too fast
        # If issues arise, decrease to 1MHz

        # Loading Data Structure
        self.data_types = config_dict["data_types"]
        self.packet_size_bytes = 6
        for val in self.data_types:
            self.packet_size_bytes += struct.calcsize(list(val.values())[0])

        if self.packet_size_bytes >= 252:
            raise Exception("Radio packet size too large (must be under 252 bytes)")

        print(f"Radio configuration loaded! Now configured for {self.packet_size_bytes}-byte packets!")

    def send(self, data):
        """
        Sends data through the RFM9X radio.

        Parameters:
            data: a list of numbers conforming to the order and types described in the loaded config file

        Returns:
            None
        """
        print(f"Time at start of radio.send: {time.time()}")  # Timestamps for debugging
        # Bitrate Budget:
        # https://docs.google.com/spreadsheets/d/1BNU0LOl0tzaBlsRqHiAFNp9Y_h9E01Kwud-uezHMNdA/edit#gid=1938337728

        # The length of each value in data is determined by its position and the config
        # Remember, packets can't be longer than 252 bytes!

        # If data is shorter than self.data_order refuse to send packet
        if len(self.data_types) != len(data):
            print("Send data is not the appropriate length; check the config")
            return

        # 6-Byte FCC License Callsign - required for every packet
        # Callsign is not in data_order because it is required for every packet
        callsign = bytes(self.callsign, 'utf-8')

        data_bytearray = bytearray()
        data_bytearray.extend(callsign)

        for data_type, val in zip(self.data_types, data):
            data_bytearray.extend(struct.pack(f">{list(data_type.values())[0]}", val))

        # For NARWAL we need to change the RF switches send
        if self.enable_amps:
            if self.enable_bypass:
                self.CTRL1A.value = False
                self.CTRL2A.value = True

                self.CTRL1B.value = False
                self.CTRL2B.value = True
            else:
                self.CTRL1A.value = True
                self.CTRL2A.value = False

                self.CTRL1B.value = True
                self.CTRL2B.value = True

        # To send a message, call send()
        print(f"Time at rfm9x.send: {time.time()}")
        self.rfm9x.send(bytes(data_bytearray))
        print(f"Time at end of radio.send: {time.time()}")

    def send_flight_data(self, acceleration, gyro, magnetic, altitude, gps, temperature):
        """
        Helper for send() function, designed to ensure that flight data is sent in the correct order.

        Parameters:
            acceleration: 3-tuple of floats
            gyro: 3-tuple of floats
            magnetic: 3-tuple of loats
            altitude: float
            gps: 2-tuple of floats
            temperature: float

        Returns:
            None
        """
        # TODO: Decide whether this function is actually necessary. Will require communication with Flight Instruments

        data = (acceleration, gyro, magnetic, altitude, gps, temperature)
        flat_data = []
        for item in data:
            if isinstance(item, Iterable):
                flat_data.extend(item)
            else:
                flat_data.append(item)
        self.send(flat_data)

    def receive(self):
        """
        Receives data through the RFM9X radio and returns it as a dictionary,
        including signal-to-noise ratio and last received signal strength

        Parameters:
            None

        Returns:
            Dictionary w/ all keys in the config data_types, along with 'rssi' and 'snr'
        """
        print(f"Time at start of radio.receive: {time.time()}")
        # For NARWAL we need to change the RF switches to receive
        if self.enable_amps:
            if self.enable_bypass:
                self.CTRL1A.value = False
                self.CTRL2A.value = True

                self.CTRL1B.value = False
                self.CTRL2B.value = True
            else:
                self.CTRL1A.value = True
                self.CTRL2A.value = True

                self.CTRL1B.value = True
                self.CTRL2B.value = False

        # Optionally change the receive timeout (how long until it gives up) from its default of 0.5 seconds:
        print(f"Time before rfm9x.receive: {time.time()}")
        packet = self.rfm9x.receive(timeout=1/self.transmit_per_second)
        print(f"Time after rfm9x.receive: {time.time()}")
        # If no packet was received during the timeout then None is returned.
        if packet is None:
            # Packet has not been received
            print(f"Time at end of radio.receive (failure): {time.time()}")
            return None
        else:
            # Received a packet!

            # Check to see if it has the right number of bytes to be ours
            if len(packet) != self.packet_size_bytes:
                print(f"Received packet is not the right size! ({len(packet)}, should be {self.packet_size_bytes})")
                return None

            # Check to see if it's our packet using the callsign
            callsign = str(packet[:6], 'utf-8')
            if callsign != self.callsign:
                print(f"Received packet has incorrect callsign! ({callsign}, should be {self.callsign})")
                return None

            encoded_data = packet[6:]

            # Build a list of all the data we've received
            return_dict = {}
            for data_type in self.data_types:
                dt = list(data_type.values())[0]  # have to do this funky thing because of how YAML is organized
                data_name = list(data_type.keys())[0]

                bytes_size = struct.calcsize(dt)
                this_data = encoded_data[:bytes_size]
                encoded_data = encoded_data[bytes_size:]

                unpacked_data = struct.unpack(f">{dt}", this_data)[0]
                return_dict[data_name] = unpacked_data

            # Also read the RSSI (signal strength) of the last received message, in dB
            return_dict["rssi"] = self.rfm9x.last_rssi

            # Also read the SNR (Signal-to-Noise Ratio) of the last message
            return_dict["snr"] = self.rfm9x.last_snr

            print(f"Time at end of radio.receive (success): {time.time()}")
            return return_dict

    def load_config(self, config_dict):
        """
        Takes a dictionary of config values and applies them to the current radio object
        Data types are in the format of struct - https://docs.python.org/3/library/struct.html

        Parameters:
            config_dict - a dictionary of configuration information, likely from a config YAML file

        Returns:
            None
        """

        self.radio_freq_mhz = config_dict["frequency_mhz"]
        self.callsign = config_dict["callsign"]
        self.packets_per_transmit = config_dict["packets_per_transmit"]
        self.transmit_per_second = config_dict["transmit_per_second"]
        self.cs = digitalio.DigitalInOut(getattr(board,config_dict["cs_pin"]))
        self.reset = digitalio.DigitalInOut(getattr(board,config_dict["reset_pin"]))
        self.rfm9x = adafruit_rfm9x.RFM9x(self.spi, self.cs, self.reset, self.radio_freq_mhz, baudrate=10_000_000)

        # NARWAL RF Switch
        self.enable_amps = config_dict["enable_amps"]
        if self.enable_amps:
            self.CTRL1A = digitalio.DigitalInOut(getattr(board, config_dict["ctrl1A_pin"]))
            self.CTRL2A = digitalio.DigitalInOut(getattr(board, config_dict["ctrl2A_pin"]))
            self.CTRL1A.direction = digitalio.Direction.OUTPUT
            self.CTRL2A.direction = digitalio.Direction.OUTPUT

            self.CTRL1B = digitalio.DigitalInOut(getattr(board, config_dict["ctrl1B_pin"]))
            self.CTRL2B = digitalio.DigitalInOut(getattr(board, config_dict["ctrl2B_pin"]))
            self.CTRL1B.direction = digitalio.Direction.OUTPUT
            self.CTRL2B.direction = digitalio.Direction.OUTPUT

        self.enable_bypass = config_dict["enable_bypass"]

        self.data_types = config_dict["data_types"]
        self.packet_size_bytes = 6
        for val in self.data_types:
            self.packet_size_bytes += struct.calcsize(list(val.values())[0])

        if self.packet_size_bytes >= 252:
            raise Exception("Radio packet size too large (must be under 252 bytes)")

        print(f"Radio configuration loaded! Now configured for {self.packet_size_bytes}-byte packets!")
