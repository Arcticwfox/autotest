"""
This file is used to provide Class Level test (Only for Ford) interface to test case.

@Author: Siwei.Lu
@Date: 2022.12.5
"""

import time

from Core import parse_config, parse_yaml_case
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import \
    canoe_app, calc, parameter_def, msg_sig_env_def

config = parse_config.ConfigHandler()
yaml_case = parse_yaml_case.YamlCaseHandler('./test_profile/test_case/ford_test_case/tc_class_lvl.yaml')


def ClassTest(class_lvl, hb_req):
    ch_int = []

    print("step 1: Send LB CAN request = {}".format(class_lvl))
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassL_D_Rq_4.value, class_lvl)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassR_D_Rq_4.value, class_lvl)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLghtHi_D_Rq.value, hb_req)
    time.sleep(0.5)

    print("Step 2: Calculate the actual intensity")
    calc.get_pixel_class_intensity()
    class_result = calc.get_pixel_ch_int_dict()
    print(class_result.values())

    for value in class_result.values():
        for i in range(12):
            ch_int.append(value[i + 1])

    return class_result.keys(), ch_int


def FLBIntensityTest(ClassLvl, HBReq):
    ch_int = []
    # step 1: Send CAN request : DBL/ClassLvl/HB
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassL_D_Rq_4.value, ClassLvl)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassR_D_Rq_4.value, ClassLvl)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLghtHi_D_Rq.value, HBReq)
    time.sleep(0.5)
    # Step 2: Calculate the actual intensity
    ch_flb_dict, flb_int = calc.get_flb_class_intensity()

    for key in ch_flb_dict.keys():
        ch_int.append(flb_int)

    return ch_flb_dict.keys(), ch_int


def ClassChangeTest(class_lvl_1, class_lvl_2, hb_req):
    ch_int = []

    print("step 1: Send LB CAN request from {} to {}".format(class_lvl_1, class_lvl_2))
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassL_D_Rq_4.value, class_lvl_1)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassR_D_Rq_4.value, class_lvl_1)
    time.sleep(1)
    # step 2: Send CAN request : DBL/ClassLvl/HB
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassL_D_Rq_4.value, class_lvl_2)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassR_D_Rq_4.value, class_lvl_2)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLghtHi_D_Rq.value, hb_req)
    time.sleep(0.5)

    # Step 3: Calculate the actual intensity
    calc.get_pixel_class_intensity()
    class_result = calc.get_pixel_ch_int_dict()

    for value in class_result.values():
        for i in range(12):
            ch_int.append(value[i + 1])

    return class_result.keys(), ch_int


def TrafficChangeTest(traffic_1, traffic_2, class_lvl, hb_req):
    ch_int = []

    print("step 1: Send traffic_style CAN request from {} to {}".format(traffic_1, traffic_2))
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.Traffic_Style_Rq_1.value, traffic_1)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassL_D_Rq_4.value, class_lvl)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassR_D_Rq_4.value, class_lvl)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLghtHi_D_Rq.value, hb_req)
    time.sleep(1)
    # step 2: Send CAN request : DBL/ClassLvl/HB
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.Traffic_Style_Rq_1.value, traffic_2)
    time.sleep(0.5)

    # Step 3: Calculate the actual intensity
    calc.get_pixel_class_intensity()
    pixel_result = calc.get_pixel_ch_int_dict()

    for value in pixel_result.values():
        for i in range(12):
            ch_int.append(value[i + 1])

    return pixel_result.keys(), ch_int


def read_matrix_ch_did(ch_x):
    did_result = []
    read_did_len = 3

    for key in ch_x:
        stream = canoe_app.send_diag_req(parameter_def.CHxDIDx_map[key][0])
        for i in range(len(stream) - read_did_len):  # 需要的数据长度
            did_result.append(round(float(100 / 255 * stream[i + read_did_len])))  # 按CDD 换算
        time.sleep(0.5)

    return did_result


def read_static_ch_did(ch_x):
    did_result = []
    read_did_len = 3

    for key in ch_x:
        stream = canoe_app.send_diag_req(parameter_def.CHxDIDx_map[key][1])
        did_result.append(round(float(100 / 255 * stream[read_did_len])))  # 按CDD 换算
        time.sleep(0.5)

    return did_result


def get_tc_data(test_info: str):
    return yaml_case.get_tc_data()[test_info]


# def get_tc_class_lvl_change_data():
#     return yaml_case.get_tc_data()['class_change_test_case']
# print(FLBIntensityTest(0, 0))
