"""
This file is used to provide SML test interface to test case. (LDM12A/B/C)

Refer to LDM12FNV3_SYSQTS 10.5: SML Light Function.

@Author: Yujie.shi
@Date: 2023.01.10
"""

import time
from Core.project.ford import parameter_def, security_access
from Core import parse_yaml_case
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import (
    canoe_app,
    read_curr_vol, can_msg, msg_sig_env_def, cdd_qualifier_def
)

yaml_case = parse_yaml_case.YamlCaseHandler(
    "./test_profile/test_case/ford_test_case/tc_sml.yaml"
)


def sml_test_step(current: int, num: int, vol: int, hs2_status: int, sml_request: int):
    sml_req = sml_request
    write_sml_config(current, num, vol, hs2_status)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Foreground_LB.value[0], 0)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Foreground_LB.value[1], 0)

    print("step1: write sml config: "
          "sml current = {} mA,sml_number = {},sml_voltage = {} V, sml_hss2_status = {}".
          format(current, num, vol, hs2_status)
          )
    time.sleep(1)
    send_sml_req(sml_req)
    time.sleep(1)

    actual_current = read_sml_current()

    sml_hss2_status, sml_hss2_current = read_sml_hss2_Status_current()
    print(
        "step2: send sml = {},measure sml current = {} mA and read sml hss2 status = {}, sml hss2 current = {} mA"
        .format(sml_req, actual_current, sml_hss2_status, sml_hss2_current)
    )
    time.sleep(1)

    sml_req = 0x00
    send_sml_req(sml_req)

    return actual_current, sml_hss2_status, sml_hss2_current


def read_sml_current():
    """
    measure address 13 current
    @return: sm actual current
    """
    sm_actual_current = round(read_curr_vol.read_current(13), 1)
    return sm_actual_current


def read_sml_hss2_Status_current():
    """
    read hss2 status and current
    @return: hss2 status and current
    """
    result = canoe_app.send_diag_req(parameter_def.DiagRequest.FD08_DID.value)
    status = result[6]
    if status == 1:
        sm_hss2_status = 1
    else:
        sm_hss2_status = 0
    sm_hss2_current = round((result[7] * 256 + result[8]) * 2000 / 65535, 0)
    return sm_hss2_status, sm_hss2_current


def send_sml_req(req: int):
    """
    send sm on/off
    @param req: 0:off,1:on
    """
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SideMarker_Actv_Rq_1.value, req)


def read_sm_config():
    """
    read sm config about configuration sm current / sm number / sm voltage / sm hss2 status
    @return: sm current / sm number / sm voltage / sm hss2 status
    """
    result = canoe_app.send_diag_req(cdd_qualifier_def.SubFunctions.Method_2_Data_Type_1_Read.value)
    sml_config_current = round(result[32] * 230 / 255 + 25, 0)
    sml_config_number = result[33]
    sml_config_vol = round((result[34] * 256 + result[35]) * 5000 / 65535, 0)
    sml_hs2_config = result[31]
    return sml_config_current, sml_config_number, sml_config_vol, sml_hs2_config


def check_result_if_match_requirement(expect_result: float, actual_result: float, margin: float):
    if expect_result == 0:
        return abs(expect_result - actual_result) <= 2
    else:
        return abs((expect_result - actual_result) / expect_result) <= margin


def write_sml_config(current: int, num: int, vol: int, hs2_status: int):
    """
    write sm config: current num vol
    @param current: mA
    @param num:
    @param vol: mV
    @param hs2_status: 0:deactivate,1:active
    """
    write_data = [((current * 255) - 6375) / 230, num, (65535 * vol) / 5000, hs2_status]
    parameter = [
        "SideMarker_Output_Current",
        "SideMarker_Led_Number",
        "SideMarker_Led_Uf",
        "HS2_SM_Function_Assigh_Cfg",
    ]
    canoe_app.send_diag_req(
        cdd_qualifier_def.SubFunctions.Method_2_Data_Type_1_Write.value, parameter, write_data
    )


def get_tc_data(tc_type: str):
    return yaml_case.get_tc_data()[tc_type]


def sml_hss2_expect():
    """
    cal sml hss 2 expect
    only if sml req = on and hss2 status = 1(active), sml hss2 expect is 1
    @return: hss2 expect
    """
    sml_req = canoe_app.get_EnvVar(msg_sig_env_def.EnvName.SideMarker_Actv_Rq_1.value)
    result = canoe_app.send_diag_req(cdd_qualifier_def.SubFunctions.Method_2_Data_Type_1_Read.value)
    sml_hss2_status = result[31]

    if sml_req == 1 and sml_hss2_status == 1:
        hss2_expect = 1
    else:
        hss2_expect = 0
    return hss2_expect


def sml_expect():
    """
    cal expect sml current
    if sml off,expect current = 0
    if sml on,expect current = sml config current
    @return: expect current
    """
    sml_req = canoe_app.get_EnvVar(msg_sig_env_def.EnvName.SideMarker_Actv_Rq_1.value)
    result = canoe_app.send_diag_req(cdd_qualifier_def.SubFunctions.Method_2_Data_Type_1_Read.value)
    sml_config_current = round(result[32] * 230 / 255 + 25, 0)

    if sml_req == 0x00:
        sml_expect_result = 0
    else:
        sml_expect_result = sml_config_current
    return sml_expect_result
