"""
This file is used to provide eEZL test interface to test case. (LDM12A/B/C)

Refer to LDM12FNV3_SYSQTS 10.12 Enhanced Zone Lighting Feature Configuration

@Author: Li.Wang
@Date:2023.2.16
"""

import time

from Core import parse_yaml_case
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import \
    dataset, canoe_app, calc
from Core.project.ford.parameter_def import DiagRequest, CHxDIDx_map, FunMapToENV
from Core.project.ford import cdd_qualifier_def
from Core.project.ford.msg_sig_env_def import EnvName

yaml_case = parse_yaml_case.YamlCaseHandler('./test_profile/test_case/ford_test_case/tc_ezl.yaml')
para_value = ['EZLenable_cfg', 'EZLch1_cfg', 'EZLch2_cfg', 'EZLch3_cfg', 'EZLch4_cfg', 'EZLch5_cfg', 'EZLch6_cfg',
              'EZLch7_cfg', 'EZLch8_cfg', 'EZLch9_cfg', 'EZLch10_cfg', 'EZLch11_cfg', 'EZLch12_cfg',
              'EZLSection0_cfg', 'EZLSection1_cfg', 'EZLSection2_cfg', 'EZLSection3_cfg', 'EZLSection4_cfg',
              'EZLSection5_cfg']


def ezl_request_test_step(ezl_request: int, did_para: list):
    # print(stream)
    print("step 1: send ezl can request = {}".format(ezl_request))

    canoe_app.send_diag_req(DiagRequest.DE04_write_DID.value, para_value, did_para)
    time.sleep(0.5)
    stream = canoe_app.send_diag_req(DiagRequest.DE04_read_DID.value)

    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, ezl_request)
    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, ezl_request)
    canoe_app.set_EnvVar(EnvName.HeadLampLoFlOn_B_Stat_1.value, 0)
    canoe_app.set_EnvVar(EnvName.HeadLampLoFrOn_B_Stat_1.value, 0)

    time.sleep(0.5)  # Waiting
    ezl_config, pixel_int = calc.get_ezl_int(stream, stream[26])
    ch_info_dict, ezl_expect_int = get_function_channel_info_dict(ezl_config)
    # for key, value in ezl_expect_int.items():

    for keys, values in pixel_int.items():
        ezl_expect_int[keys] = values
    # print('ezl_expect_int = ', ezl_expect_int)

    ezl_actual_int = send_did_to_read_ch_intensity(ch_info_dict)
    # print('ezl_actual_int', ezl_actual_int)
    # print(ezl_expect_int)
    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, 0)
    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, 0)
    time.sleep(0.5)
    return ezl_expect_int, ezl_actual_int


def po_interrupt_ezl_step(ezl_request: int, did_para: list, drl_x: int):
    # print(stream)
    print("step 1: send ezl can request = {}".format(ezl_request))

    canoe_app.send_diag_req(DiagRequest.DE04_write_DID.value, para_value, did_para)
    time.sleep(0.5)

    print("step 2: send DRL/PO_{} can request = {}".format(drl_x, 1))
    canoe_app.set_EnvVar(FunMapToENV['DRL{}'.format(drl_x)].value[0], 1)
    canoe_app.set_EnvVar(FunMapToENV['DRL{}'.format(drl_x)].value[1], 1)

    stream = canoe_app.send_diag_req(DiagRequest.DE04_read_DID.value)
    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, ezl_request)
    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, ezl_request)

    time.sleep(0.5)  # Waiting
    ezl_config = calc.get_po_interrupt_ezl_int(stream, drl_x)
    # print('ezl_config =  ', ezl_config)
    ch_info_dict, ezl_expect_int = get_function_channel_info_dict(ezl_config)

    # print('ch_info_dict = ', ch_info_dict)
    ezl_ch_cfg = {}
    for key, value in ch_info_dict.items():
        for key_ezl, value_ezl in ezl_config.items():
            if key == key_ezl:
                ezl_ch_cfg[key] = value
    # print('ezl_ch_cfg = ', ezl_ch_cfg)

    ezl_actual_int = send_did_to_read_ch_intensity(ezl_ch_cfg)

    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, 0)
    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, 0)
    time.sleep(0.5)
    return ezl_expect_int, ezl_actual_int


def iocontrol_ezl_step(ezl_request: int, fun: str, iocontrol_request: int):
    # print(stream)
    # para_value = ['EZLenable_cfg', 'EZLch1_cfg', 'EZLch2_cfg', 'EZLch3_cfg', 'EZLch4_cfg', 'EZLch5_cfg', 'EZLch6_cfg',
    #               'EZLch7_cfg', 'EZLch8_cfg', 'EZLch9_cfg', 'EZLch10_cfg', 'EZLch11_cfg', 'EZLch12_cfg']

    print("step 1: send ezl can request = {}".format(ezl_request))
    iocontrol_fun_did = {'lb': [cdd_qualifier_def.SubFunctions.Left_Front_Low_Beam_Output_Control_Status_Read.value,
                                cdd_qualifier_def.SubFunctions.Left_Front_Low_Beam_Output_Control_Status_Short_Term_Adjustment.value,
                                cdd_qualifier_def.SubFunctions.Left_Front_Low_Beam_Output_Control_Status_Return_Control.value],
                         'hb': [cdd_qualifier_def.SubFunctions.Headlamp_High_Beam_Output_Control_Read.value,
                                cdd_qualifier_def.SubFunctions.Headlamp_High_Beam_Output_Control_Short_Term_Adjustment.value,
                                cdd_qualifier_def.SubFunctions.Headlamp_High_Beam_Output_Control_Return_Control.value],
                         'drl': [cdd_qualifier_def.SubFunctions.Daytime_Running_Light_Output_Read.value,
                                 cdd_qualifier_def.SubFunctions.Daytime_Running_Light_Output_Short_Term_Adjustment.value,
                                 cdd_qualifier_def.SubFunctions.Daytime_Running_Light_Output_Return_Control.value],
                         'ti': [cdd_qualifier_def.SubFunctions.Left_Turn_Lamps_Output_Read.value,
                                cdd_qualifier_def.SubFunctions.Left_Turn_Lamps_Output_Short_Term_Adjustment.value,
                                cdd_qualifier_def.SubFunctions.Left_Turn_Lamps_Output_Return_Control.value],
                         'bending': [cdd_qualifier_def.SubFunctions.Left_Front_Static_Bending_Lamp_Read.value,
                                     cdd_qualifier_def.SubFunctions.Left_Front_Static_Bending_Lamp_Short_Term_Adjustment.value,
                                     cdd_qualifier_def.SubFunctions.Left_Front_Static_Bending_Lamp_Return_Control.value],
                         'aux': [cdd_qualifier_def.SubFunctions.Front_Signature_Lamps_Output_Read.value,
                                 cdd_qualifier_def.SubFunctions.Front_Signature_Lamps_Output_Short_Term_Adjustment.value,
                                 cdd_qualifier_def.SubFunctions.Front_Signature_Lamps_Output_Return_Control.value]}

    iocontrol_did = {'Left_Front_Low_Beam_Output_Control_Status_Short_Term_Adjustment': 'Left_Front_Low_Beam_Output_Control_Status',
                     'Headlamp_High_Beam_Output_Control_Short_Term_Adjustment': 'Headlamp_High_Beam_Output_Control',
                     'Daytime_Running_Light_Output_Short_Term_Adjustment': 'Daytime_Running_Light_Output',
                     'Left_Turn_Lamps_Output_Short_Term_Adjustment': 'Left_Turn_Lamps_Output',
                     'Left_Front_Static_Bending_Lamp_Short_Term_Adjustment': 'Left_Front_Static_Bending_Lamp',
                     'Front_Signature_Lamps_Output_Short_Term_Adjustment': 'Front_Signature_Lamps_Output'}

    canoe_app.send_diag_req(DiagRequest.DE04_write_DID.value, para_value, [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
    time.sleep(0.5)
    canoe_app.set_EnvVar(EnvName.HeadLampLoFlOn_B_Stat_1.value, 0)
    canoe_app.set_EnvVar(EnvName.HeadLampLoFrOn_B_Stat_1.value, 0)

    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, ezl_request)
    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, ezl_request)
    time.sleep(0.5)
    # set ezl enable
    print("step 2: send ", fun, " function IOcontrol requeset = {}".format(iocontrol_request))
    for key, value in iocontrol_fun_did.items():
        for keys, values in iocontrol_did.items():
            if key == fun:
                if value[1] == keys:
                    # print(value[1])
                    canoe_app.send_diag_req(value[1], values, iocontrol_request)
    time.sleep(0.5)

    # Waiting
    ezl_config, pixel_int = calc.get_iocontrol_ezl_int(fun, iocontrol_request)
    # print('ezl_config =  ', ezl_config)

    ch_info_dict, ezl_expect_int = get_function_channel_info_dict(ezl_config)

    for keys, values in pixel_int.items():
        ezl_expect_int[keys] = values

    # print('ezl_expect_int = ', ezl_expect_int)
    ezl_ch_cfg = {}
    for key, value in ch_info_dict.items():
        for key_ezl, value_ezl in ezl_config.items():
            if key == key_ezl:
                ezl_ch_cfg[key] = value
    # print('ezl_ch_cfg = ', ezl_ch_cfg)

    ezl_actual_int = send_did_to_read_ch_intensity(ezl_ch_cfg)
    # print('ezl_actual_int = ', ezl_actual_int)
    time.sleep(0.5)
    for key, value in iocontrol_fun_did.items():
        if key == fun:
            if value[1] == key:
                canoe_app.send_diag_req(value[2])
                time.sleep(0.5)

    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, 0)
    canoe_app.set_EnvVar(EnvName.ExtLghtFront_D_RqBody_2.value, 0)
    time.sleep(0.5)

    return ezl_expect_int, ezl_actual_int


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


def get_function_channel_info_dict(ezl_int_config: dict):
    ch_info_dict = dataset.get_ch_func_chip_dict()
    fun_ch_info_dict = {}
    function = ['DRL1', 'DRL2', 'DRL3', 'DRL4', 'Auxiliary_Signature_Light_1', 'Auxiliary_Signature_Light_2',
                'Auxiliary_Signature_Light_3', 'Auxiliary_Signature_Light_4', 'Segment_Bending', 'Static_Bending',
                'Static_HB', 'Sequential_TI_Section_10', 'Sequential_TI_Section_11', 'Sequential_TI_Section_13',
                'Channel_Sequential_TI_1', 'Channel_Sequential_TI_2', 'Channel_Sequential_TI_3', 'Static_TI', 'Pixel',
                'Matrix_HB_Section_4', 'Matrix_HB_Section_5', 'Foreground_LB']
    for key, value in ch_info_dict.items():
        if value['function'] in function:
            fun_ch_info_dict.update({key: ch_info_dict[key]})

    function_int = []
    function_expect_int = {}
    # if drl_x == 0:
    for key_ezl, value_ezl in ezl_int_config.items():
        for key, values in fun_ch_info_dict.items():
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

    return fun_ch_info_dict, function_expect_int


def get_tc_data(tc_type: str):
    return yaml_case.get_tc_data()[tc_type]




