"""
This file is used to connect battery(KORAD) via serial port.

@Author: Bo.Li
@Date: 2022.12.09
"""
import sys

from Core import parse_config
from Core.instrument_control import serial_control


class BatKoradControl:
    def __init__(self, config: parse_config.ConfigHandler):
        self.__config = config
        self.__vbat_config = self.__config.get_config_by_inst('power_supply_korad')
        self.__baud = self.__config.get_baud_rate('power_supply_korad')
        self.__com = self.__config.get_com('power_supply_korad')

        try:
            self.__serialHandler = serial_control.SerialHandler(self.__com, self.__baud)
        except BaseException as err:
            print("power_supply_korad({}) open failed! \n{}".format(self.__com, err))
            serial_control.logger.error("power_supply_korad({}) open failed! \n{}".format(self.__com, err))
            sys.exit()

    def set_input_voltage(self, input_vol: float):
        vol_cmd = "VSET1:{}\n".format(str(input_vol))
        self.__serialHandler.send_req(vol_cmd)

    def set_input_current(self, input_cur: float):
        cur_cmd = "ISET1:{}\n".format(str(input_cur))
        self.__serialHandler.send_req(cur_cmd)

    def set_output(self, output: str):
        if output.lower() == "on":
            req = 1
        else:
            req = 0
        cur_cmd = "OUT{}\n".format(req)
        self.__serialHandler.send_req(cur_cmd)

    def read_output_voltage(self):
        req_cmd = "VOUT1?:"
        self.__serialHandler.send_req(req_cmd)
        data = self.__serialHandler.rec_data()

        # print(float(str(data.decode())))
        return float(str(data.decode()))

    def set_default_status(self):
        voltage = self.__vbat_config['default_input_voltage']
        current = self.__vbat_config['default_input_current']
        status = self.__vbat_config['default_status']

        self.set_input_current(current)
        self.set_input_voltage(voltage)
        self.set_output(status)


# config = parse_config.ConfigHandler()
#
# power = BatKoradControl(config)
# power.set_input_voltage(14)
# power.set_output(0)
# power.read_output_voltage()
