"""
This file is used to provide DRL test interface to test case. (LDM12A/B/C)

Refer to LDM12FNV3_SYSQTS 10.5: DRL, Park/Position and Auxiliary Signature Light Function.

@Author: Siwei.Lu
@Date: 2022.12.11
"""

import time

from Core import parse_yaml_case
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import \
    dataset, canoe_app, calc, parameter_def


yaml_case = parse_yaml_case.YamlCaseHandler('./test_profile/test_case/ford_test_case/tc_drl_po.yaml')


def drl_test_step(drl_request: int, drl_x: int):
    print("step 1: send DRL/PO_{} can request = {}".format(drl_x, drl_request))

    canoe_app.set_EnvVar(parameter_def.FunMapToENV['DRL{}'.format(drl_x)].value[0], drl_request)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV['DRL{}'.format(drl_x)].value[1], drl_request)

    time.sleep(0.5)  # Waiting
    drl_int_config = calc.get_drl_int(drl_x)
    drl_ch_info_dict, drl_po_int = get_function_channel_info_dict(drl_int_config, 'DRL{}'.format(drl_x))

    return drl_ch_info_dict, drl_po_int


def po_with_ti_test_step(drl_x: int, ti_request: int):
    drl_request = 0x01

    print("step 1: send DRL/PO_{} can request = {}(po)".format(drl_x, drl_request))
    canoe_app.set_EnvVar(parameter_def.FunMapToENV['DRL{}'.format(drl_x)].value[0], drl_request)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV['DRL{}'.format(drl_x)].value[1], drl_request)

    print("step 2: send TI can request = {}".format(ti_request))
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_TI.value[0], ti_request)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_TI.value[1], ti_request)

    time.sleep(0.5)  # Waiting
    drl_int_config = calc.get_drl_int(drl_x)

    drl_ch_info_dict, drl_po_int = get_function_channel_info_dict(drl_int_config, 'DRL{}'.format(drl_x))

    return drl_ch_info_dict, drl_po_int


def aux_test_step(drl_request: int, aux_x: int):
    print("step 1: send DRL/PO_{} can request = {}".format(aux_x, drl_request))

    canoe_app.set_EnvVar(parameter_def.FunMapToENV['Auxiliary_Signature_Light_{}'.format(aux_x)].value[0], drl_request)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV['Auxiliary_Signature_Light_{}'.format(aux_x)].value[1], drl_request)

    time.sleep(0.5)  # Waiting
    aux_int_config = calc.get_aux_int(aux_x)
    aux_ch_info_dict, aux_int = get_function_channel_info_dict(aux_int_config,
                                                               'Auxiliary_Signature_Light_{}'.format(aux_x))

    return aux_ch_info_dict, aux_int


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

    return did_result


def get_function_channel_info_dict(drl_int_config: int, function: str):
    ch_info_dict = dataset.get_ch_func_chip_dict()
    fun_ch_info_dict = {}
    for key, value in ch_info_dict.items():
        if value['function'] == function:
            fun_ch_info_dict.update({key: ch_info_dict[key]})

    function_int = []
    for key, values in fun_ch_info_dict.items():
        if values['matrix_chip'] == 'NU':
            # No_matrix channel
            function_int.append(drl_int_config)
        else:
            # Matrix channel
            for switch in range(1, 13):
                if drl_int_config == 0:
                    function_int.append(0)
                else:
                    if switch not in values['x01~x12']:
                        function_int.append(0)  # The intensity of 'NU' is 0%
                    else:
                        function_int.append(drl_int_config)

    return fun_ch_info_dict, function_int


def get_tc_data(tc_type: str):
    return yaml_case.get_tc_data()[tc_type]


