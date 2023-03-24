from enum import Enum
import yaml
import busio
import digitalio
from digitalio import DigitalInOut as dIO
import board
import adafruit_rfm9x
import struct
import time


class AmpMode(Enum):
	DISABLED = 'D'
	BYPASS	 = 'B'
	TRANSMIT = 'T'
	RECEIVE  = 'R'


class Radio:

	DATA_TYPES = {'int8':'b', 'int16':'h', 'int32':'i', 'int64':'q',
	  'uint8':'B', 'uint16':'H', 'uint32':'I', 'uint64':'Q',
	  'float32':'f', 'float64':'d', 'bool':'?'}


	'''
	Constructs a Radio object with the given configuration.
	
	Parameters:
		config_filename:	the path to a valid LaunchTest-format radio config file
		log_filename:		the path to a YAML file to write received data to

	Returns:
		None
	'''
	def __init__(self, config_filename, log_filename):

		print("Radio initializing...")

		# Import configuration from config file
		with open(config_filename, 'r') as stream:
			self.config = yaml.safe_load(stream)

		# Save configuration info
		self.frequency = self.config['frequency']
		self.bandwidth = self.config['bandwidth'] * 10**3
		self.spreading = self.config['spreading']
		self.tx_power = self.config['tx_power']
		self.amp_mode = AmpMode(self.config['amp_mode'])
		self.timeout = self.config['timeout']
		self.coding_rate = self.config['coding_rate']
		self.baudrate = self.config['baudrate'] * 10**6
		self.callsign = self.config['callsign']
		self.send_packet_n = self.config['send_packet_n']
		self.send_time = self.config['send_time']
		self.magic = self.config['magic']
		self.pins_trx = self.config['pins']['transceiver']
		self.pins_swA = self.config['pins']['switch_A']
		self.pins_swB = self.config['pins']['switch_B']
		self.packetdef = self.config['packetdef']

		self.log_filename = log_filename

		# Declare transceiver
		cs = dIO(getattr(board, self.pins_trx['cs']))
		reset = dIO(getattr(board, self.pins_trx['reset']))
		sck_id = getattr(board, self.pins_trx['sck'])
		mosi_id = getattr(board, self.pins_trx['mosi'])
		miso_id = getattr(board, self.pins_trx['miso'])
		spi = busio.SPI(clock=sck_id, MOSI=mosi_id, MISO=miso_id)

		# Initialize transceiver
		self.trx = adafruit_rfm9x.RFM9x(spi, cs, reset, self.frequency, baudrate=self.baudrate)
		self.trx.signal_bandwidth = self.bandwidth
		self.trx.spreading_factor = self.spreading
		self.trx.tx_power = self.tx_power
		self.trx.coding_rate = self.coding_rate

		# Initialize RF switches
		self.set_amp_mode(AmpMode(self.amp_mode))

		# Calculate packet size
		self.packet_size = 0

		if self.callsign != None:
			self.packet_size += len(bytes(self.callsign, 'ascii'))
		if self.send_packet_n:
			self.packet_size += struct.calcsize(Radio.DATA_TYPES['uint32'])
		if self.send_time:
			self.packet_size += struct.calcsize(Radio.DATA_TYPES['uint64'])
		if self.magic != None:
			self.packet_size += struct.calcsize(Radio.DATA_TYPES['uint8'])

		for vardef in self.packetdef:
			var_type = list(vardef.values())[0]
			self.packet_size += struct.calcsize(Radio.DATA_TYPES[var_type])

		if self.packet_size >= 252:
			raise Exception(f"Packet size too large: {self.packet_size} > 252 bytes")
		
		# Initialize sent packet count
		self.packets_sent = 0
		self.packets_received = 0

		print("Radio initialization complete")


	'''
	Switches the amplifier mode to the given mode.

	Parameters:
		mode: the AmpMode to switch to. It is not possible to switch from a non-Disabled mode
			  to the disabled mode

	Returns:
		None
	'''
	def set_amp_mode(self, mode):

		if mode == AmpMode.DISABLED:
			if self.amp_mode != AmpMode.DISABLED:
				print("Cannot switch non-disabled amplifier mode to disabled")
			return
		
		self.amp_mode = mode

		swA_ctrl1 = dIO(getattr(board, self.pins_swA['ctrl1']))
		swA_ctrl2 = dIO(getattr(board, self.pins_swA['ctrl2']))
		swB_ctrl1 = dIO(getattr(board, self.pins_swB['ctrl1']))
		swB_ctrl2 = dIO(getattr(board, self.pins_swB['ctrl2']))

		swA_ctrl1.direction = digitalio.Direction.OUTPUT
		swA_ctrl2.direction = digitalio.Direction.OUTPUT
		swB_ctrl1.direction = digitalio.Direction.OUTPUT
		swB_ctrl2.direction = digitalio.Direction.OUTPUT

		ctrls = {}
		ctrls[AmpMode.BYPASS] = [False, True, False, True]
		ctrls[AmpMode.TRANSMIT] = [True, False, True, True]
		ctrls[AmpMode.RECEIVE] = [True, True, True, False]

		swA_ctrl1.value, swA_ctrl2.value, swB_ctrl1.value, swB_ctrl2.value = ctrls[self.amp_mode]


	'''
	Transmits a packet containing the given data.
	
	Parameters:
		data: a dictionary formatted according to the packet definition specified by the config 
		  file provided on init
		
	Returns:
		None
	'''
	def send(self, data):
		
		data_bytes = bytearray()

		if self.callsign != None:
			data_bytes.extend(bytes(self.callsign, 'ascii'))
		if self.send_packet_n:
			data_bytes.extend(struct.pack(f">{Radio.DATA_TYPES['uint32']}", self.packets_sent))
		if self.send_time:
			data_bytes.extend(struct.pack(f">{Radio.DATA_TYPES['uint64']}", time.time_ns()))

		for vardef in self.packetdef:
			var_name = list(vardef.keys())[0]
			var_type = list(vardef.values())[0]
			val = data[var_name]
			packed_val = struct.pack(f">{Radio.DATA_TYPES[var_type]}", val)
			data_bytes.extend(packed_val)

		if self.magic != None:
			data_bytes.extend(struct.pack(f">{Radio.DATA_TYPES['uint8']}", self.magic))

		if len(data_bytes) != self.packet_size:
			print(f"Packet of size {len(data_bytes)} is invalid for config with size {self.packet_size}")
			return

		self.trx.send(bytes(data_bytes))
		self.packets_sent += 1
		print("Packet transmitted successfully")
	

	'''
	Receives a single packet and returns its interpreted contents.
	
	Parameters:
		None

	Returns:
		A dictionary with keys adhering to the packet definition specified by the config file
		provided on init, plus '_rssi', '_snr', and possibly '_callsign', '_packet_n',
		'_send_time', and/or '_magic' as appropriate, and with values extracted from the received 
		packet.
	'''
	def receive(self):

		packet = self.trx.receive(timeout=self.timeout)

		if packet is None:
			print("No packets received")
			return None
		
		if len(packet) != self.packet_size:
			print(f"Received packet of size {len(packet)} is invalid for config with size {self.packet_size}")
			return None
		
		data = {}

		if self.callsign != None:
			callsign = str(packet[:len(bytes(self.callsign, 'ascii'))], 'ascii')
			if callsign != self.callsign:
				print(f"Received packet with callsign {callsign} is invalid for config with callsign {self.callsign}")
				return None
			data['_callsign'] = callsign
			packet = packet[len(bytes(self.callsign, 'ascii')):]

		if self.send_packet_n:
			packet_n_raw = packet[:struct.calcsize(Radio.DATA_TYPES['uint32'])]
			data['_packet_n'] = struct.unpack(f">{Radio.DATA_TYPES['uint32']}", packet_n_raw)[0]
			packet = packet[struct.calcsize(Radio.DATA_TYPES['uint32']):]

		if self.send_time:
			send_time_raw = packet[:struct.calcsize(Radio.DATA_TYPES['uint64'])]
			data['_send_time'] = struct.unpack(f">{Radio.DATA_TYPES['uint64']}", send_time_raw)[0]
			packet = packet[struct.calcsize(Radio.DATA_TYPES['uint64']):]
			
		if self.magic != None:
			magic_raw = packet[-struct.calcsize(Radio.DATA_TYPES['uint8']):]
			magic = struct.unpack(f">{Radio.DATA_TYPES['uint8']}", magic_raw)[0]
			if magic != self.magic:
				print(f"Received packet with magic {magic} is invalid for config with magic {self.magic}")
				return None
			data['_magic'] = magic
			packet = packet[:-struct.calcsize(Radio.DATA_TYPES['uint8'])]

		for vardef in self.packetdef:
			var_name = list(vardef.keys())[0]
			var_type = list(vardef.values())[0]
			size = struct.calcsize(Radio.DATA_TYPES[var_type])
			packed_val = packet[:size]
			data[var_name] = struct.unpack(f">{Radio.DATA_TYPES[var_type]}", packed_val)[0]
			packet = packet[size:]

		data['_rssi'] = self.trx.last_rssi
		data['_snr'] = self.trx.last_snr

		self.packets_received += 1
		print("Packet received successfully")

		return data
	

	'''
	Receives a single packet, writes its contents to the log file provided on init, and returns 
	the contents.
	
	Parameters:
		None

	Returns:
		A dictionary with keys adhering to the packet definition specified by the config file
		provided on init, plus '_rssi', '_snr', and possibly '_callsign', '_packet_n',
		'_send_time', and/or '_magic' as appropriate, and with values extracted from the received 
		packet.
	'''
	def receive_and_log(self):

		data = self.receive()

		if self.log_filename != None:
			with open(self.log_filename, 'a', buffering=1) as log_file:
				yaml.dump([data], log_file)
				log_file.flush()
			print("Data successfully written to log file")
		else:
			print("No log filename provided on init, cannot write to log file")

		return data
