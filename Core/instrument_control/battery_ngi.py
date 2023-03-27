"""
This file is used to connect battery(NGI) via serial port.

@Author: Chengyu.Liu Yujie.Shi
@Date: 2022.12.6
"""
import sys

from Core import parse_config
from Core.instrument_control import serial_control


class VbatControlNGI:

    def __init__(self, config: parse_config.ConfigHandler):
        self.__config = config
        self.__vbat_config = self.__config.get_config_by_inst('power_supply_NGI')
        self.__baud = self.__config.get_baud_rate('power_supply_NGI')
        self.__com = self.__config.get_com('power_supply_NGI')

        try:
            self.__serialHandler = serial_control.SerialHandler(self.__com, self.__baud)
        except BaseException as err:
            print("power_supply_ngi({}) open failed! \n{}".format(self.__com, err))
            serial_control.logger.error("power_supply_ngi({}) open failed! \n{}".format(self.__com, err))
            sys.exit()

    def send(self, data):
        # 通过串口下发字符串，通常用于对下位机下发字符串指令
        self.__serialHandler.send_req(data)

    def set_input_voltage(self, input_vol: float):
        vol_cmd = 'SOURce:VOLTage ' + str(input_vol) + ' \n'
        self.send(vol_cmd)

    def set_input_current(self, input_cur: float):
        vol_cmd = 'SOURce:CURRent ' + str(input_cur) + ' \n'
        self.send(vol_cmd)

    def set_output(self, status: str):
        output_cmd = 'OUTPut:ONOFF ' + str(status) + ' \n'
        self.send(output_cmd)

    def read_output_voltage(self):
        cmd = 'MEASure:VOLTage? \n'
        self.send(cmd)
        data = self.__serialHandler.rec_data()

        while True:
            if len(data) == 8:  # 判断接收数据长度是否为指定长度
                break
            else:
                self.send(cmd)
                data = self.__serialHandler.rec_data()

        return data.decode()

    def read_output_current(self):
        cmd = 'MEASure:CURRent? \n'
        self.send(cmd)
        data = self.__serialHandler.rec_data()

        while True:
            if len(data) == 9:  # 判断接收数据长度是否为指定长度
                break
            else:
                self.send(cmd)
                data = self.__serialHandler.rec_data()

        return data.decode()

    def set_default_status(self):
        voltage = self.__vbat_config['default_input_voltage']
        current = self.__vbat_config['default_input_current']
        status = self.__vbat_config['default_status']

        self.set_input_current(current)
        self.set_input_voltage(voltage)
        self.set_output(status)
