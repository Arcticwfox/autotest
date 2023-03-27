"""
This file provides a method of connecting to the instrument via the serial port.

@Author: Siwei.Lu
@Date: 2022.11.27
"""

import time
import numpy as np
import serial

from Core.log_handler import LogHandler

logger = LogHandler.get_log_handler(__name__, "info")


class SerialHandler:
    def __init__(self, com, baud):
        """设定COM口和波特率"""
        self.com = serial.Serial(com, baud)

    def send_req(self, command):
        """
        Send given command
        :param command: str or list
        :return:
        """
        # print("type = ", type(command), command)

        if type(command) == str:
            command_data = np.fromstring(command, dtype=np.uint8)
        else:
            command_data = command

        self.com.write(command_data)

    def rec_data(self):
        flag = 0
        while True:
            count = self.com.inWaiting()  # 缓冲区字节长度
            flag = flag + 1
            # print("count = {}".format(count))
            if count > 0:
                time.sleep(0.3)
                data = self.com.read(count)  # 读取缓冲区字节
                break
            elif flag == 30000:
                raise RuntimeWarning("Serial port ({}) timeout".format(self.com.port))

        return data

    @staticmethod
    def _crc16_calc(list_data: list):
        """CRC计算"""
        crc16 = 0xFFFF
        poly = 0xA001
        for i in range(0, len(list_data)):
            a = int(list_data[i])
            '''^ 异或运算：如果两个位为“异”（值不同），则该位结果为1，否则为0'''
            crc16 = a ^ crc16
            for i in range(8):
                # 对于每一个data，都需要右移8次，可以简单理解为对每一位都完成了校验
                if 1 & crc16 == 1:
                    # crc16与上1 的结果(16位二进制)只有第0位是1或0，其他位都是0
                    # & 与运算：都是1才是1，否则为0
                    crc16 = crc16 >> 1
                    # >>表示右移，即从高位向低位移出，最高位补0
                    crc16 = crc16 ^ poly
                else:
                    crc16 = crc16 >> 1

        crc16_2 = int(crc16 / 0x100)
        crc16_1 = crc16 - (int(crc16 / 0x100) << 8)

        return crc16_1, crc16_2

    def get_array_after_crc16(self, input_array: list):
        crc16_1, crc16_2 = self._crc16_calc(input_array)
        input_array.append(crc16_1)
        input_array.append(crc16_2)

        return input_array
