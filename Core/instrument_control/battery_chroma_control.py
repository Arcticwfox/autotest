"""
This file is used to connect battery(chroma) visa.

@Author: Yujie.shi
@Date: 2022.12.09
"""

import sys
import time

import pyvisa as visa
from Core import parse_config
from Core.instrument_control import serial_control


class BatChromaControl:
    def __init__(self, config: parse_config.ConfigHandler):
        self.__config = config
        self.__vbat_config = self.__config.get_config_by_inst('power_supply_chroma')
        self.__visa = self.__vbat_config['visa_resource']
        rm = visa.ResourceManager("C:/Windows/System32/visa32.dll")

        try:
            self._inst = rm.open_resource(self.__visa)
        except BaseException as err:
            print("power_supply_chroma({}) open failed! \n{}".format(self.__visa, err))
            serial_control.logger.error("power_supply_chroma({}) open failed! \n{}".format(self.__visa, err))
            sys.exit()

    def set_output(self, status):
        self._inst.write("CONFigure:OUTPut {}\n".format(status))

    def set_input_voltage(self, input_vol: float):
        self._inst.write("SOUR:VOLT " + str(input_vol) + "\n")

    def set_input_current(self, input_cur: float):
        self._inst.write("SOUR:CURR " + str(input_cur) + "\n")

    def read_output_voltage(self):
        data = self._inst.query("FETC:VOLT?")
        return eval(data)

    def read_output_current(self):
        data = self._inst.query("FETCH:CURRent?")
        return eval(data)

    def power_reset(self):
        self._inst.write("CONFigure:OUTPut OFF\n")
        time.sleep(1)
        self._inst.write("CONFigure:OUTPut ON\n")

    def set_default_status(self):
        voltage = self.__vbat_config['default_input_voltage']
        current = self.__vbat_config['default_input_current']
        status = self.__vbat_config['default_status']

        self.set_input_current(current)
        self.set_input_voltage(voltage)
        self.set_output(status)
