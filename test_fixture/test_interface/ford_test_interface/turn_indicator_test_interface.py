"""
This file is used to provide TI test interface to test case. (LDM12A/B/C)

Refer to LDM12FNV3_SYSQTS 10.6: Turn Indicator Function.

@Author: Li.Wang
@Date:2023.1.12
"""

import time

from Core import parse_yaml_case
from Core.project.ford import parameter_def
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import \
    dataset, canoe_app, calc, msg_sig_env_def

yaml_case = parse_yaml_case.YamlCaseHandler('./test_profile/test_case/ford_test_case/tc_turn_indicator.yaml')


def turn_indicator_step(ti_request: int, function: list, drl_x: int):
    print("step 1: send TI can request = {}".format(ti_request))

    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_TI.value[0], ti_request)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_TI.value[1], ti_request)

    time.sleep(0.5)  # Waiting
    ti_config, ti_delay, wait = calc.get_turn_indicator_int(function[0], drl_x)
    ti_ch_info_dict, ti_expect_int = get_function_channel_info_dict(ti_config, function)

    if ti_request == 3 and wait == 1:
        time.sleep(ti_delay/ 1000)
    else:
        pass
    ti_actual_int = send_did_to_read_ch_intensity(ti_ch_info_dict)
    time.sleep(0.5)

    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_TI.value[0], 0)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_TI.value[1], 0)
    time.sleep(0.5)

    return ti_expect_int, ti_actual_int


def ti_with_po_step(ti_request: int, function: list, drl_x: int, drl_request: int):
    print("step 1: send TI can request = {}".format(ti_request))
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_TI.value[0], ti_request)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_TI.value[1], ti_request)

    print("step 2: send DRL/PO_{} can request = {}".format(drl_x, drl_request))
    canoe_app.set_EnvVar(parameter_def.FunMapToENV['DRL{}'.format(drl_x)].value[0], drl_request)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV['DRL{}'.format(drl_x)].value[1], drl_request)

    time.sleep(0.5)  # Waiting

    ti_config, ti_delay, wait = calc.get_turn_indicator_int(function[0], drl_x)
    ti_ch_info_dict, ti_expected_int = get_function_channel_info_dict(ti_config, function)

    if ti_request == 3 and wait == 1:
        time.sleep(ti_delay)
    else:
        pass

    ti_actual_int = send_did_to_read_ch_intensity(ti_ch_info_dict)
    time.sleep(0.5)

    canoe_app.set_EnvVar(parameter_def.FunMapToENV['DRL{}'.format(drl_x)].value[0], 0)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV['DRL{}'.format(drl_x)].value[1], 0)
    time.sleep(0.5)  # Waiting

    return ti_expected_int, ti_actual_int


def ti_with_animation_step(ti_request: int, function: list, drl_x: int, animation_request: int):
    print("step 1: send animation can request = {}".format(ti_request), " 0:farewell, 1:welcome, 2:prepare")
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLampLoFlOn_B_Stat_1.value, 0)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLampLoFrOn_B_Stat_1.value, 0)

    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.Ignition_Status_4.value, 1)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.PwPckTq_D_Stat_2.value, 0)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLghtSwtch_D_Stat_2.value, 0)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLghtHi_D_Rq.value, 0)
    # 'welcome' command
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.WfSuperstate_D_Stat_2.value, 2)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.WfSubstate_D_Stat_3.value, animation_request)

    print("step 2: send TI can request = {}".format(ti_request))
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_TI.value[0], ti_request)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_TI.value[1], ti_request)

    time.sleep(0.5)  # Waiting

    ti_config, ti_delay, wait = calc.get_turn_indicator_int(function[0], drl_x)
    ti_ch_info_dict, ti_expected_int = get_function_channel_info_dict(ti_config, function)

    if ti_request == 3 and wait == 1:
        time.sleep(ti_delay / 1000)
    else:
        pass
    ti_actual_int = send_did_to_read_ch_intensity(ti_ch_info_dict)

    print("step 3: animation command reset")
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.Ignition_Status_4.value, 4)
    time.sleep(0.5)

    return ti_actual_int, ti_expected_int


def send_did_to_read_ch_intensity(ch_info_dict: dict):
    """
    Read DID to get actual result
    @param ch_info_dict: dict
    @return: list
    """
    did_result = []
    read_did_len = 3

    for key, values in ch_info_dict.items():
        if values['matrix_chip'] == 'NU':
            # No_matrix channel: DID FD50~FD61
            stream = canoe_app.send_diag_req(parameter_def.CHxDIDx_map[key][1])

            did_result.append(round(float(100 / 255 * stream[read_did_len])))  # 按CDD 换算
            # print('RESULT = ', did_result, values['function'])
        else:
            # Matrix channel: DID FD11~FD22
            stream = canoe_app.send_diag_req(parameter_def.CHxDIDx_map[key][0])

            for i in range(len(stream) - read_did_len):  # 需要的数据长度
                did_result.append(round(float(100 / 255 * stream[i + read_did_len])))  # 按CDD 换算

        time.sleep(0.5)

    return did_result


def get_function_channel_info_dict(ti_int_config: int, function: list):
    ch_info_dict = dataset.get_ch_func_chip_dict()
    fun_ch_info_dict = {}
    for key, value in ch_info_dict.items():
        if value['function'] in function:
            fun_ch_info_dict.update({key: ch_info_dict[key]})

    function_int = []
    for key, values in fun_ch_info_dict.items():
        if values['matrix_chip'] == 'NU':
            # No_matrix channel
            function_int.append(ti_int_config)
        else:
            # Matrix channel
            for switch in range(1, 13):
                if ti_int_config == 0:
                    function_int.append(0)
                else:
                    if switch not in values['x01~x12']:
                        function_int.append(0)  # The intensity of 'NU' is 0%
                    else:
                        function_int.append(ti_int_config)

    return fun_ch_info_dict, function_int


def get_tc_data(tc_type: str):
    return yaml_case.get_tc_data()[tc_type]
