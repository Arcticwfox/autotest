"""
This file is used to provide Bending test interface to test case. (LDM12A/B/C)

Refer to LDM12FNV3_SYSQTS 10.5: Bending Light Function.

@Author: Yujie.shi
@Date: 2023.01.10
"""

import time
from Core import parse_yaml_case
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import \
    dataset, canoe_app, parameter_def, msg_sig_env_def

yaml_case = parse_yaml_case.YamlCaseHandler('./test_profile/test_case/ford_test_case/tc_bending.yaml')


def segment_Bending_test_step(addr: int, intensity: int):
    """
    @param addr: matrix bending address
    @param intensity: intensity
    @return: bending data and intensity
    """
    print("step1: send Bending_{} intensity = {}".format(addr, intensity))
    send_bending_req(addr, intensity)
    time.sleep(0.5)  # Waiting
    send_seq = bending_req()
    bending_ch_info_dict, bending_intensity = get_function_channel_info_dict('Segment_Bending', send_seq)
    time.sleep(1)  # Waiting
    send_bending_req(addr, 0)
    return bending_ch_info_dict, bending_intensity


def static_Bending_test_step(intensity: int):
    """

    @param intensity: output intensity
    @return: bending data and intensity
    """
    print("step1: send static bending intensity = {}".format(intensity))
    send_bending_req(1, intensity)
    time.sleep(0.5)  # Waiting
    send_seq = bending_req()
    bending_ch_info_dict, bending_inten = get_function_channel_info_dict('Static_Bending', send_seq)
    return bending_ch_info_dict, bending_inten


def get_function_channel_info_dict(function: str, send_req: list):
    """
    the bending intensity is displayed by physical address
    @param function: static bending or segment bending
    @param send_req: bending send req
    @return: the bending intensity is displayed by physical address
    """
    ch_info_dict = dataset.get_ch_func_chip_dict()
    fun_ch_info_dict = {}

    for key, value in ch_info_dict.items():
        if value['function'] == function:
            fun_ch_info_dict.update({key: ch_info_dict[key]})

    function_int = []
    for key, values in fun_ch_info_dict.items():
        if values['matrix_chip'] == 'NU':
            if key == 'CH_6 LS':
                if 0 < send_req[0] <= 5:
                    function_int.append(5)
                else:
                    function_int.append(send_req[0])
            else:
                function_int.append(send_req[0])
            # No_matrix channel

        else:
            for switch in range(1, 13):
                if switch not in values['x01~x12']:
                    function_int.append(0)  # The intensity of 'NU' is 0%
                else:
                    index = values['x01~x12'].index(switch)
                    print(index)
                    function_int.append(send_req[index])

    return fun_ch_info_dict, function_int


def send_bending_req(bending_x: int, intensity: int):
    """
    send bending intensity
    @param bending_x: bending 1-5
    @param intensity: bending intensity
    """
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName['Slght{}BrghtRight_Pc_Rq_8'.format(bending_x)].value, intensity)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName['Slght{}BrghtLeft_Pc_Rq_8'.format(bending_x)].value, intensity)


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
        else:
            # Matrix channel: DID FD11~FD22

            stream = canoe_app.send_diag_req(parameter_def.CHxDIDx_map[key][0])

            for i in range(len(stream) - read_did_len):  # 需要的数据长度
                did_result.append(round(float(100 / 255 * stream[i + read_did_len])))  # 按CDD 换算

    time.sleep(0.5)
    send_bending_req(1, 0)
    print("step2: read Bending intensity = {}".format(did_result))

    return did_result


def bending_req():
    """
    read bending req
    @return: bending 1-5 req
    """
    send_req = []
    for bending_x in range(1, 6):
        intensity = canoe_app.get_EnvVar(msg_sig_env_def.EnvName['Slght{}BrghtLeft_Pc_Rq_8'.format(bending_x)].value)
        if 0 < intensity <= 2:
            intensity = 2
        if intensity >= 100:
            intensity = 100
        send_req.append(intensity)
    return send_req


def bending_expected_intensity_logical():
    """
    cal logical intensity
    @return: bending logical intensity
    """
    expected_intensity_logical = []
    for bending_x in range(1, 6):
        intensity = canoe_app.get_EnvVar(msg_sig_env_def.EnvName['Slght{}BrghtLeft_Pc_Rq_8'.format(bending_x)].value)
        if 0 < intensity <= 2:
            intensity = 2
        if intensity >= 100:
            intensity = 100
        expected_intensity_logical.append(intensity)
    for i in range(7):
        expected_intensity_logical.append(0)
    return expected_intensity_logical


def get_tc_data(tc_type: str):
    """
    @param tc_type: bending
    @return: data
    """
    return yaml_case.get_tc_data()[tc_type]
