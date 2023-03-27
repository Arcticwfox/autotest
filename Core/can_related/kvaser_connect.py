"""
This file is used to create CAN communication by kvaser.
Note: This file is mainly used for CCE PTR Test

@Author: Siwei.Lu
@Date: 2023.2.24
"""

import can

import math
import sys

from Core.project.ford.parameter_def import DiagRequest
from Core.log_handler import LogHandler

logger = LogHandler.get_log_handler(__name__, "info")


class KvaserMsg:
    def __init__(self, can_fd=True):
        """
        Connect the specified hardware.
        :param can_fd: Enable CAN FD
        :return:
        """
        self.__is_fd = can_fd

        try:
            self.bus = can.Bus(bustype='kvaser',
                               fd=self.__is_fd,  # CNA FD
                               receive_own_messages=True,
                               channel=0
                               )
        except BaseException as err:
            print("kvaser hardware connect failed! \n{}".format(err))
            logger.critical("kvaser hardware connect failed! \n{}".format(err))
            sys.exit()

        self.__diag_send_msg_id = 0x74E
        self.__diag_rec_msg_id = 0x7CE
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

    def __output_message(self, msg_id, msg_data):
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

    def send_msg(self, side_info: int, msg_id, msg_data):
        """
        Note: This function is used for CCE PTR Test
        """
        msg_data.insert(0, side_info)

        if (len(msg_data) > 8) and (msg_data[1] != 0):  # 多帧
            msg_ff_data = msg_data[:8]
            print("msg_ff_data = ", msg_ff_data)
            self.__output_message(msg_id, msg_ff_data)  # 发送首帧
            self.__output_message(msg_id, DiagRequest.FC.value)  # 发送流控帧
            while True:
                if self.bus.recv(1).data[0] == 0x30:  # 等待 流控帧
                    """每帧报文对应7个字节data"""
                    for i in range(math.ceil((msg_data[1] + ((msg_data[0] - 0x10) << 8) - 8) / 7)):
                        j = i % 15
                        msg_cf_data_1 = msg_data[1 + 7 * (i + 1):7 * (i + 2) + 1]  # [15:22] Data
                        msg_cf_data = [0x20 + j + 1]  # CF  连续帧
                        msg_cf_data.extend(msg_cf_data_1)
                        print("msg_cf_data {} = {}".format(i + 1, msg_cf_data))
                        self.__output_message(msg_id, msg_cf_data)
                    break
                else:
                    # print("Wait for FC ")
                    pass
        else:

            self.__output_message(msg_id, msg_data)

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
                self.__output_message(self.__diag_send_msg_id, DiagRequest.FC.value)  # 使用诊断ID， 发送流控帧
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

    def get_did_resp(self, side_info: int, did_list: list):
        """
        Note: This function is used for CCE PTR Test

        @param side_info: Left or Right
        @param did_list: Defined in DiagRequest. eg: [0x22, 0xFD, 0X11]
        :return: Response data
        """
        count = 1
        first_byte = len(did_list)
        did_list.insert(0, first_byte)

        self.send_msg(side_info, self.__diag_send_msg_id, did_list)

        while True:
            count += count
            is_sf, rec_data_len, rec_data, pos_resp_byte = self.rec_message(self.__diag_rec_msg_id)

            if pos_resp_byte == did_list[1] + 0x40:  # Positive Response
                for i in range(is_sf + 1):
                    rec_data.pop(0)
                break

            if count == 50000:
                raise Exception("DID {} has no response".format(did_list))

        return rec_data


# msg1 = KvaserMsg(False)
# msg1.send_msg(0x10, 0x74e, [0x10, 0x12, 0x03, 0X05, 0x03, 0x05, 0x03, 0x05,0x03, 0x05,0x03, 0x05])
# r = msg1.get_did_resp(0x00, [0x22, 0x03, 0x05, 0xF1, 0x89, 0x03, 0x05, 0x03, 0x05, 0x03, 0x05, 0x03, 0x05])
# for i in r:
#     print(hex(i))

