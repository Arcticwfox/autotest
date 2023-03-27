"""
This file is used to create CAN/LIN communication by hardware.

@Author: Siwei.Lu
@Date: 2022.11.26
"""

import can
import math
import sys

from Core import parse_config
from Core.project.ford.parameter_def import DiagRequest
from Core.log_handler import LogHandler

logger = LogHandler.get_log_handler(__name__, "info")


class Msg:
    def __init__(self, config: parse_config.ConfigHandler, can_fd=True):
        """
        Connect the specified hardware.
        :param serial: Vector Hardware Config-->Hardware, choose the correct Serial number
        :param channel: channel = Hardware used channel
        :param can_fd: Enable CAN FD
        :return:
        """

        serial = config.get_config_by_name('vector_hardware')['serial_number']
        channel = config.get_config_by_name('vector_hardware')['channel']
        self.__is_fd = can_fd

        try:
            self.bus = can.Bus(bustype='vector',
                               # app_name='CANoe',  # Vector Hardware Config --> Application 里进行配置
                               channel=channel - 1,
                               # bitrate=500000,
                               # data_bitrate=2000000,
                               fd=self.__is_fd,  # CNA FD
                               receive_own_messages=True,
                               serial=serial,
                               )
        except BaseException as err:
            print("Vector hardware connect failed! \n{}".format(err))
            logger.critical("Vector hardware connect failed! \n{}".format(err))
            sys.exit()

        self.__diag_send_msg_id = 0x6f6
        self.__diag_rec_msg_id = 0x6fe
        self.__dlc = 8
        self.__is_extended_id = False

    @property
    def diag_send_msg_id(self):
        return self.__diag_send_msg_id

    @diag_send_msg_id.setter
    def diag_send_msg_id(self, send_id):
        self.__diag_send_msg_id = send_id

    @property
    def diag_rec_msg_id(self):
        return self.__diag_rec_msg_id

    @diag_rec_msg_id.setter
    def diag_rec_msg_id(self, recv_id):
        self.__diag_rec_msg_id = recv_id

    @property
    def is_extended_id(self):
        return self.__is_extended_id

    @is_extended_id.setter
    def is_extended_id(self, value):
        """
        :param value: True or False
        :return:
        """
        self.__is_extended_id = value

    @property
    def dlc(self):
        return self.__dlc

    @dlc.setter
    def dlc(self, value):
        """
        :param value: True or False
        :return:
        """
        self.__dlc = value

    def disconnect_bus(self):
        """
        Disconnect the specified hardware.
        :return:
        """
        self.bus.shutdown()

    def _output_message(self, msg_id, msg_data):
        """
        Output a message without CF
        :param msg_data: Message to be sent
        :return:
        """
        msg = can.Message(arbitration_id=msg_id,
                          data=msg_data,
                          is_extended_id=self.__is_extended_id,
                          dlc=self.__dlc,
                          is_fd=self.__is_fd)
        # print(msg)
        try:
            self.bus.send(msg)
        except can.CanError:
            print("Msg Not Send: {}".format(can.CanError))

    def send_msg(self, msg_id, msg_data):
        if (len(msg_data) > 8) and (msg_data[0] != 0):
            # if MsgData[0] >> 4 == 0x1:  # 多帧
            msg_ff_data = msg_data[:8]
            print("msg_ff_data = ", msg_ff_data)
            self._output_message(msg_id, msg_ff_data)  # Send first frame
            self._output_message(msg_id, DiagRequest.FC.value)  # 发送流控帧
            while True:
                if self.bus.recv(1).data[0] == 0x30:  # Wait for FC
                    """每帧报文对应7个字节data"""
                    for i in range(math.ceil((msg_data[1] + ((msg_data[0] - 0x10) << 8) - 8) / 7)):
                        j = i % 15
                        msg_cf_data_1 = msg_data[1 + 7 * (i + 1):7 * (i + 2) + 1]  # [15:22] Data
                        msg_cf_data = [0x20 + j + 1]  # CF
                        msg_cf_data.extend(msg_cf_data_1)
                        print("msg_cf_data {} = {}".format(i + 1, msg_cf_data))
                        self._output_message(msg_id, msg_cf_data)
                    break
                else:
                    # print("Wait for FC ")
                    pass
        else:
            self._output_message(msg_id, msg_data)

    def rec_message(self, rec_msg_id):
        data_len = 0
        pos_resp_byte = 0
        is_sf = 0  # 单帧： 0， 多帧： 1

        msg = self.bus.recv(rec_msg_id)
        rec_data = msg.data
        msg_ff = msg

        if rec_msg_id == msg.arbitration_id:
            if msg.data[0] >> 4 == 0x1:
                data_len = msg.data[1] + ((msg.data[0] - 0x10) << 8)
                pos_resp_byte = msg_ff.data[2]
                is_sf = 1
                self._output_message(self.__diag_send_msg_id, DiagRequest.FC.value)  # 使用诊断ID， 发送流控帧
                while True:
                    msg = self.bus.recv()
                    if msg.data[0] == 0x30:
                        for i in range(math.ceil((data_len - 6) / 7)):
                            msg = self.bus.recv()
                            if msg.data[0] >> 4 == 0x2:
                                rec_data.extend(msg.data)
                                rec_data.remove(0x20 + i + 1)
                        break
            elif msg.data[0] == 0:  # CANFD dlc:64
                data_len = msg.data[1]
                pos_resp_byte = msg.data[2]

            else:
                data_len = msg.data[0]
                pos_resp_byte = msg.data[1]

        return is_sf, data_len, rec_data, pos_resp_byte

    def get_did_resp(self, did_list: list):
        """
        This function is used to get the response of [22 XX XX]
        :param did_list: Defined in DiagRequest.  eg: [0x22, 0xFD, 0X11]
        :return: Response data
        """
        first_byte = len(did_list)
        did_list.insert(0, first_byte)

        self.send_msg(self.__diag_send_msg_id, did_list)
        while True:
            is_sf, rec_data_len, rec_data, pos_resp_byte = self.rec_message(self.__diag_rec_msg_id)
            if pos_resp_byte == did_list[1] + 0x40:  # Positive Response
                for i in range(is_sf + 1):
                    rec_data.pop(0)
                break

        return rec_data

