"""
This file is used to provide DBL test (Only for Ford) interface to test case.

@Author: Siwei.Lu
@Date: 2022.11.27
"""

import time

from Core import parse_config, parse_yaml_case
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import \
    canoe_app, calc, msg_sig_env_def, parameter_def

config = parse_config.ConfigHandler()
yaml_case = parse_yaml_case.YamlCaseHandler('./test_case/ford_test_case/tc_dbl.yaml')


def DBLTest(dbl_move_ang, class_lvl, hb_req):
    ch_int = []
    print("Step 1: send LB class level = {}, DBL move ang = {}".format(class_lvl, dbl_move_ang))
    # step 1: Send CAN request : DBL/ClassLvl/HB
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SwvlTrgtLeft_An_Rq_11, dbl_move_ang)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SwvlTrgtRight_An_Rq_11, dbl_move_ang)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassL_D_Rq_4.value, class_lvl)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassL_D_Rq_4.value, class_lvl)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLghtHi_D_Rq.value, hb_req)
    time.sleep(0.5)

    print("Step 2: Calculate the actual DBL move angle")
    # Step 2: Calculate the actual DBL move angle
    calc.get_status_after_dbl()
    DBL_result = calc.get_pixel_ch_int_dict()
    for value in DBL_result.values():
        # print(value)
        for i in range(12):
            ch_int.append(value[i + 1])

    return DBL_result.keys(), ch_int


def read_ch_did(ch_x: dict):
    did_result = []
    read_did_len = 3

    for key in ch_x:
        stream = canoe_app.send_diag_req(parameter_def.CHxDIDx_map[key][0])
        for i in range(len(stream) - read_did_len):  # 需要的数据长度
            did_result.append(round(float(100 / 255 * stream[i + read_did_len])))  # 按CDD 换算
        time.sleep(0.5)

    return did_result


def get_tc_data():
    return yaml_case.get_tc_data()['dbl_test_case']
