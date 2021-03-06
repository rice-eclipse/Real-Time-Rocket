import busio
import time
import board
import array
from utils import big_endian_add
import struct

meters_per_foot = 0.3048
standard_atm_mbar = 1013.25
class Altimeter:
    """
    A class defined to interface with the MS5803 altimeter for Real-Time-Rocket.
    """

    def __init__(self):
        """
        Create an altimeter object.
        """
        #PROM values
        self._c = [
            0,
            0,
            0,
            0,
            0,
            0,
            0
        ]
        self._address = 0x76  # Hardware address on the altimeter. 0x76 for hi CS
        #and 0x77 for low CS
        self._prom_commands = [
            0xA0,
            0xA2,
            0xA4,
            0xA6,
            0xA8,
            0xAA,
            0xAC
        ]
        self._i2c = busio.I2C(board.SCL, board.SDA)
        self._reset_command = 0x1E
        self._convert_d1_256 = 0x40
        self._convert_d1_4096 = 0x48
        self._convert_d2_4096 = 0x58
        self._adc_command = 0x00

    def initialize(self):
        """
        Initialize the altimeter. Called once at the start of using this altimeter.
        """
        print("Scanning devices")
        print(self._i2c.scan())
        print("Resetting device")
        self.reset()
        print("Reading PROM")
        self.update_prom()
        print("PROM is", self._c)

    def reset(self):
        while not self._i2c.try_lock():  # lock the i2c
            pass
        self._i2c.writeto(address=self._address,
                          buffer=bytearray([self._reset_command]))
        self._i2c.unlock()

    def update_prom(self):
        """
        Update the information in self._c to reflect the values in PROM.
        """
        for i in range(len(self._prom_commands)):
            self._c[i] = self.read_prom(self._prom_commands[i])

    def read_prom(self, command):
        """
        Read a value from the PROM memory of the altimeter.
        Inputs:
            - command - hex command for which byte to read
        Returns int equal to value encoded at that memory slot
        """

        while not self._i2c.try_lock():  # lock the i2c
            pass
        self._i2c.writeto(address=self._address, buffer=bytearray([command]))
        output_buffer = bytearray(2)
        self._i2c.readfrom_into(address=self._address, buffer=output_buffer)
        self._i2c.unlock()  # free the i2c
        return big_endian_add(output_buffer)

    def read_raw(self, command):
        """
        Read a raw data value off of the altimeter.
        """

        while not self._i2c.try_lock():  # lock the i2c
            pass

        self._i2c.writeto(address=self._address, buffer=bytearray([command]))
        time.sleep(0.05)  # have to wait for conversion to be complete
        self._i2c.writeto(
            address=self._address,
            buffer=bytearray([self._adc_command]))
        output_buffer = bytearray(3)
        self._i2c.readfrom_into(address=self._address, buffer=output_buffer)
        print(output_buffer)
        self._i2c.unlock()  # free the i2c
        return big_endian_add(output_buffer)

    def get_data(self):
        """
        Get data off of the altimeter! 
        Returns a mapping {"temp": tempval, "pressure": pressure}
        """
        d1 = self.read_raw(self._convert_d1_256)
        print("D1 is", d1)
        d2 = self.read_raw(self._convert_d2_4096)
        print("D2 is", d2)

        d_t = d2 - (self._c[5] << 8)  # temperature offset from reference
        print("DT is", d_t)

        int_temp = ((d_t * self._c[6]) >> 23) + 2000
        temp = float(int_temp) / 100

        off = self._c[2] << 16  # offset at actual temperature
        off += (self._c[4]*d_t) >> 7

        print("OFF is", off)

        sens = (self._c[1] << 15) + ((self._c[3] * d_t) >> 8)  # sensitivity

        print("SENS is", sens)

        intpressure = ((d1 * sens >> 21) - off) >> 15
        pressure = float(intpressure) / 100

        altitude = meters_per_foot * 145366.45 * (1 - (pressure / standard_atm_mbar) ** 0.190284)

        output = {
            "temp": temp,
            "pressure": pressure,
            "altitude": altitude
        }

        return output


alt = Altimeter()
alt.initialize()
print(alt.get_data())
