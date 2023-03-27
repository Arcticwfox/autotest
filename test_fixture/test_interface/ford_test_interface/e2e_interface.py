"""
This file is used to provide E2E test interface to test case. (LDM12A/B/C)

Refer to LDM12FNV3_SYSQTS 10.31 E2E Requirement

@Author: Li.Wang
@Date:2023.2.21
"""

import time

from Core import parse_yaml_case
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import \
    dataset, canoe_app, calc
from Core.project.ford.msg_sig_env_def import EnvName
from test_fixture.test_interface.ford_test_interface import faultinjection
from Core.project.ford.parameter_def import CHxDIDx_map
from Core.project.ford import parameter_def


yaml_case = parse_yaml_case.YamlCaseHandler('./test_profile/test_case/ford_test_case/tc_e2e.yaml')


def e2e_test_step(e2e_error: int, e2e_type: int):
    # print(stream)
    dtc_expect = []
    e2e_cfg = dataset.get_e2e_config()
    print("step 0: E2E_configuration = ", e2e_cfg)
    canoe_app.send_diag_req(parameter_def.DiagRequest.clear_dtc.value)
    time.sleep(0.2)

    if e2e_type == 1:
        print("step 1: set", EnvName.Env_Var_Mes320Bz.value, " = {}".format(e2e_error))
        canoe_app.set_EnvVar(EnvName.Env_Var_Mes320Bz.value, e2e_error)
        time.sleep(3.5)  # Waiting
        dtc_test = faultinjection.check_dtc(parameter_def.DTC.e2e_82.value)
        dtc_expect = parameter_def.DTC.e2e_82.value
    elif e2e_type == 2:
        print("step 1: set", EnvName.Env_Var_Mes320Crc.value, " = {}".format(e2e_error))
        canoe_app.set_EnvVar(EnvName.Env_Var_Mes320Crc.value, e2e_error)
        time.sleep(3.5)  # Waiting
        dtc_test = faultinjection.check_dtc(parameter_def.DTC.e2e_83.value)
        dtc_expect = parameter_def.DTC.e2e_83.value

    time.sleep(0.5)
    if e2e_error == 1 or e2e_cfg == "Disable":
        dtc_expect = [1]

    # print(dtc_expect)
    # print(dtc_test)
    canoe_app.set_EnvVar(EnvName.Env_Var_Mes320Bz.value, 1)
    canoe_app.set_EnvVar(EnvName.Env_Var_Mes320Crc.value, 1)
    time.sleep(0.5)
    # for key, value in ezl_expect_int.items():
    return dtc_test, dtc_expect


def e2e_light_test_step(e2e_error: int, e2e_type: int):
    # print(stream)
    dtc_expect = []
    e2e_cfg = dataset.get_e2e_config()
    print("step 0: E2E_configuration = ", e2e_cfg)
    canoe_app.send_diag_req(parameter_def.DiagRequest.clear_dtc.value)
    canoe_app.set_EnvVar(EnvName.TurnLghtLeft_D_Rq_2.value, 2)
    canoe_app.set_EnvVar(EnvName.TurnLghtRight_D_Rq_2.value, 2)
    canoe_app.set_EnvVar(EnvName.HeadLampLoFlOn_B_Stat_1.value, 0)
    canoe_app.set_EnvVar(EnvName.HeadLampLoFrOn_B_Stat_1.value, 0)
    time.sleep(0.2)

    if e2e_type == 1:
        print("step 1: set", EnvName.Env_Var_Mes320Bz.value, " = {}".format(e2e_error))
        canoe_app.set_EnvVar(EnvName.Env_Var_Mes320Bz.value, e2e_error)
        time.sleep(3.5)  # Waiting
        dtc_test = faultinjection.check_dtc(parameter_def.DTC.e2e_82.value)
        dtc_expect = parameter_def.DTC.e2e_82.value
    elif e2e_type == 2:
        print("step 1: set", EnvName.Env_Var_Mes320Crc.value, " = {}".format(e2e_error))
        canoe_app.set_EnvVar(EnvName.Env_Var_Mes320Crc.value, e2e_error)
        time.sleep(3.5)  # Waiting
        dtc_test = faultinjection.check_dtc(parameter_def.DTC.e2e_83.value)
        dtc_expect = parameter_def.DTC.e2e_83.value

    time.sleep(0.5)
    if e2e_error == 1 or e2e_cfg == "Disable":
        dtc_expect = [1]

    e2e_config, pixel_int = calc.get_e2e_int(dtc_expect)
    ch_info_dict, e2e_expect_int = get_function_channel_info_dict(e2e_config)

    if pixel_int != {}:
        for keys, values in pixel_int.items():
            e2e_expect_int[keys] = values
    # print(pixel_int)
    # print(e2e_expect_int)
    ezl_ch_cfg = {}
    for key, value in ch_info_dict.items():
        for key_e2e, value_e2e in e2e_expect_int.items():
            if key == key_e2e:
                ezl_ch_cfg[key] = value

    ezl_actual_int = send_did_to_read_ch_intensity(ezl_ch_cfg)
    # print(dtc_expect)
    # print(dtc_test)
    canoe_app.set_EnvVar(EnvName.Env_Var_Mes320Bz.value, 1)
    canoe_app.set_EnvVar(EnvName.Env_Var_Mes320Crc.value, 1)
    canoe_app.set_EnvVar(EnvName.TurnLghtLeft_D_Rq_2.value, 0)
    canoe_app.set_EnvVar(EnvName.TurnLghtRight_D_Rq_2.value, 0)
    time.sleep(0.5)
    # for key, value in ezl_expect_int.items():
    return dtc_test, dtc_expect,  ezl_actual_int, e2e_expect_int


def get_function_channel_info_dict(e2e_int_config: dict):
    ch_info_dict = dataset.get_ch_func_chip_dict()
    # fun_ch_info_dict = {}
    # function = ['DRL1', 'DRL2', 'DRL3', 'DRL4', 'Auxiliary_Signature_Light_1', 'Auxiliary_Signature_Light_2',
    #             'Auxiliary_Signature_Light_3', 'Auxiliary_Signature_Light_4', 'Segment_Bending', 'Static_Bending',
    #             'Static_HB', 'Sequential_TI_Section_10', 'Sequential_TI_Section_11', 'Sequential_TI_Section_13',
    #             'Channel_Sequential_TI_1', 'Channel_Sequential_TI_2', 'Channel_Sequential_TI_3', 'Static_TI', 'Pixel',
    #             'Matrix_HB_Section_4', 'Matrix_HB_Section_5', 'Foreground_LB']
    # for key, value in ch_info_dict.items():
    #     if value['function'] in function:
    #         fun_ch_info_dict.update({key: ch_info_dict[key]})

    function_int = []
    function_expect_int = {}
    # if drl_x == 0:
    for key_ezl, value_ezl in e2e_int_config.items():
        for key, values in ch_info_dict.items():
            if key == key_ezl:
                if values['matrix_chip'] == 'NU':
                    # No_matrix channel
                    function_int = value_ezl
                else:
                    # Matrix channel
                    for switch in range(1, 13):
                        if value_ezl == 0:
                            function_int.append(0)
                        else:
                            if switch not in values['x01~x12']:
                                function_int.append(0)  # The intensity of 'NU' is 0%
                            else:
                                function_int.append(value_ezl)
                function_expect_int[key] = function_int
                function_int = []

    return ch_info_dict, function_expect_int


def send_did_to_read_ch_intensity(ch_info_dict: dict):
    """
    Read DID to get actual result
    @param ch_info_dict: dict
    @return: list
    """
    did_result = []
    read_did_len = 3
    did_result_int = {}
    for key, values in ch_info_dict.items():
        if values['matrix_chip'] == 'NU':
            # No_matrix channel: DID FD50~FD61
            stream = canoe_app.send_diag_req(CHxDIDx_map[key][1])

            did_result = round(float(100 / 255 * stream[read_did_len]))  # 按CDD 换算
            # print('RESULT = ', did_result, values['function'])
        else:
            # Matrix channel: DID FD11~FD22
            stream = canoe_app.send_diag_req(CHxDIDx_map[key][0])

            for i in range(len(stream) - read_did_len):  # 需要的数据长度
                did_result.append(round(float(100 / 255 * stream[i + read_did_len])))  # 按CDD 换算

        did_result_int[key] = did_result
        did_result = []
        time.sleep(0.5)

    return did_result_int


def get_tc_data(tc_type: str):
    return yaml_case.get_tc_data()[tc_type]
