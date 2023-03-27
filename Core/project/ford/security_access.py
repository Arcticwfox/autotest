"""
This file provide the function for 2703 unlock of LDM12/12A/12C/12FNV3.

Please check the DLL dependency before use this file.
Tool: https://dependencywalker.com/

@Author: Siwei.Lu
@Date: 2023.2.2
"""

from ctypes import *
import ctypes
import time
import os

from Core.can_related.can_control import Msg
from Core.can_related.canoe_connect import CanoeSync
from Core.project.ford.parameter_def import DiagRequest

key_len_2703 = 16
wait_time_for_msg_send = 0.1

seed_2703 = (c_ubyte * key_len_2703)()
key_2703 = (c_ubyte * key_len_2703)()

dll_path = os.path.dirname(os.path.abspath(__file__)) + r'\FordUnlockKBD.dll'


def ford_security_access_03(msg: Msg, can_app: CanoeSync, is_12b=True):
    req_2704 = [0x00, 0x12, 0x27, 0x04]
    if not is_12b:
        req_2704 = [0x10, 0x12, 0x27, 0x04]

    can_app.send_diag_req("Tester_Present_Send", 'zeroSubFunction', 1)

    # DLL文件和python位数要匹配
    dll = CDLL(dll_path)
    msg_send_id = msg.diag_send_msg_id
    msg_recv_id = msg.diag_rec_msg_id
    msg.send_msg(msg_send_id, DiagRequest.session_03.value)
    time.sleep(wait_time_for_msg_send)
    msg.send_msg(msg_send_id, DiagRequest.req_2703.value)

    while True:
        is_sf, data_len, rec_data, pos_resp_byte = msg.rec_message(msg_recv_id)
        # time.sleep(wait_time_for_msg_send)
        if pos_resp_byte == 0x67:  # 27+40 0x67
            for i in range(4):  # remove byte 0~3 [00 12 67 03] [10 12 67 03]
                rec_data.pop(0)
            break

    for i in range(key_len_2703):
        # print(hex(rec_data[i]))
        seed_2703[i] = ctypes.c_ubyte(rec_data[i])

    dll.GetFordKeyL3_2703(seed_2703, key_2703)

    for key in key_2703:
        req_2704.append(key)

    if is_12b:
        msg.dlc = len(req_2704)

    msg.send_msg(msg_send_id, req_2704)


# config = parse_config.ConfigHandler()
# can_msg = Msg(config)
# ford_security_access_03(can_msg)
