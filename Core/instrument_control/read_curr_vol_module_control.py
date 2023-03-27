"""
This file is used to connect read_current/voltage_module(KV_AMP) via serial port.

Refer to KV_AMPxxx系列微电流表头-用户手册V1.0.pdf and KV_DVMxxx系列电压表头-用户手册V1.1.pdf
for the relevant calculation formulae.

@Author: Siwei.Lu
@Date: 2022.11.27
"""
import sys

import time

from Core import parse_config
from Core.instrument_control import serial_control


class ReadCurrVolModuleControl:
    def __init__(self, config: parse_config.ConfigHandler):
        self.__config = config
        self.__kv_config = self.__config.get_config_by_inst('read_current_voltage_module')
        self.__baud = self.__config.get_baud_rate('read_current_voltage_module')
        self.__com = self.__config.get_com('read_current_voltage_module')

        try:
            self.__serialHandler = serial_control.SerialHandler(self.__com, self.__baud)
        except BaseException as err:
            print("read_current_voltage_module({}) open failed! \n{}".format(self.__com, err))
            serial_control.logger.error("read_current_voltage_module({}) open failed! \n{}".format(self.__com, err))
            sys.exit()

    def read_current(self, addr):
        Resolution = 0.1
        cur_cmd = self.__kv_config['read_req'].copy()
        cur_cmd[0] = addr

        current = self._send_and_rec(cur_cmd)

        if (current[3] == 0xFF) and (current[4] == 0xFF):
            return -round((0xFFFF - current[5] * 0x100 - current[6]) * Resolution * Resolution, 3)  # mA

        return round((current[5] * 0x100 + current[6]), 3) * Resolution  # mA

    def read_voltage(self, addr):
        Resolution = 1  # 1mV
        vol_cmd = self.__kv_config['read_req'].copy()
        vol_cmd[0] = addr

        voltage = self._send_and_rec(vol_cmd)

        if (voltage[3] == 0xFF) and (voltage[4] == 0xFF):
            return -round((0xFFFF - voltage[5] * 0x100 - voltage[6]) * Resolution * Resolution * 0.001, 3)  # mV 转 V

        return round((voltage[5] * 0x100 + voltage[6]), 3) * Resolution * 0.001  # mV 转 V

    def _send_and_rec(self, request_cmd: list):
        for i in range(2):  # 发2次命令，避免接收数据不对
            cmd = request_cmd.copy()
            self.__serialHandler.send_req(self.__serialHandler.get_array_after_crc16(cmd))
            data = self.__serialHandler.rec_data()
            time.sleep(0.5)

        while True:
            if len(data) == 9:  # 判断接收数据长度是否为指定长度
                break
            else:
                cmd = request_cmd.copy()
                self.__serialHandler.send_req(self.__serialHandler.get_array_after_crc16(cmd))
                data = self.__serialHandler.rec_data()

        return data
