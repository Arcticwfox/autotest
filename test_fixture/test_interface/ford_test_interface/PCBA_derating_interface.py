"""
This file is used to provide Power derating test interface to test case. (LDM12A/B/C)

Refer to LDM12FNV3_SYSQTS 10.5: Power derating Function.

@Author: Yujie.shi
@Date: 2023.3.06
"""

import time

from Core import parse_yaml_case
from Core.project.ford import cdd_qualifier_def
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import (
    dataset, canoe_app, read_curr_vol, battery, parameter_def, msg_sig_env_def, bin_set, battery_KL31
)

yaml_case = parse_yaml_case.YamlCaseHandler("./test_profile/test_case/ford_test_case/tc_PCBA_derating.yaml")


def cal_expect_result(function: str, current_bef_derating: list):
    """
    CAL expect result
    different functions have different derating value and PCBA derating is Nonlinear
    :param function:
    :param current_bef_derating:
    :return: current before derating * expect derating value
    """
    expect_result = []
    PCBA_data = get_derating_req_value(function)["PCBA"]
    PCBA_tem = canoe_app.send_diag_req(cdd_qualifier_def.SubFunctions.PCBA_Temperature_Read.value)[3]

    if PCBA_tem < 95:
        derating = 0
    elif 95 <= PCBA_tem < 105:
        derating = PCBA_data[0]
    elif 105 <= PCBA_tem < 115:
        derating = PCBA_data[1]
    else:
        derating = PCBA_data[2]

    for current in current_bef_derating:
        expect_result.append(round(current * (100 - derating) / 100, 2))

    print("Read the current PCBA temperature = {} deg and the expect derating is {} %, the expect result is {} mA"
          .format(PCBA_tem, derating, expect_result))

    send_function_req(function, 0)
    bin_set.set_vol_base_on_PCBA_Tem(6, 50)
    time.sleep(1)

    return expect_result


def PCBA_derating_test_step(function: str, tem: int):
    """
    test step
    precondition : set bin 5 (500mA), no NTC derating
    step1 : send test function on and measure current
    step2 : set PCBA derating then measure current
    :param function:
    :param tem:
    :return: current before and after derating, one of test function name
    """
    power_reset()
    req = get_derating_req_value(function)["req"]
    fun_ch_info_dict, function_name = get_function_data(function)
    function_cal = function_name[0]
    battery.set_default_status()
    battery_KL31.set_default_status()
    time.sleep(1)
    set_all_function_no_ntc_derating()
    time.sleep(1)
    set_bin_function(function_cal, 5)

    send_function_req(function_cal, req)
    time.sleep(2)

    current_bef_derating = read_test_function_current(fun_ch_info_dict)
    print("step 1: send test function on and measure current={}mA".format(current_bef_derating))
    time.sleep(1)
    bin_set.set_vol_base_on_PCBA_Tem(6, tem)
    power_reset()
    time.sleep(2)

    current_af_derating = read_test_function_current(fun_ch_info_dict)
    print(
        "step 2: Set PCBA temperature = {} deg then measure current={}mA".format(tem, current_af_derating)
    )

    return current_bef_derating, current_af_derating, function_cal


def send_function_req(function: str, req: int):
    """
    send_function_req
    @param function: function
    @param req: req on
    """

    if function == 'SML':
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SideMarker_Actv_Rq_1.value, req)

    else:
        canoe_app.set_EnvVar(
            parameter_def.FunMapToENV[function].value[0], req)
        canoe_app.set_EnvVar(
            parameter_def.FunMapToENV[function].value[1], req)
        if function in ['Pixel', 'Foreground_LB']:
            if req == 0:
                battery_req = 'off'
            else:
                battery_req = 'on'
            battery_KL31.set_output(battery_req)


def get_function_data(function: str):
    """

    @param function: function
    @return: function channel(the first one )
    """
    ch_info_dict = dataset.get_ch_func_chip_dict()
    fun_ch_info_dict = {}
    function_name = []
    if function == "SML":  # dataset has no sml
        sml_dict = {'CH_13': {'function': 'SML'}}
        fun_ch_info_dict.update(sml_dict)
        function_name.append("SML")
    else:
        for key, value in ch_info_dict.items():
            if function in value["function"]:
                function_name.append(value["function"])
                fun_ch_info_dict.update({key: ch_info_dict[key]})
    if not fun_ch_info_dict:
        print("Test function = {} can not be found in this dataset!".format(function))
    else:
        print("test function = {}".format(function))
    return fun_ch_info_dict, function_name


def set_bin_function(function: str, bin_x: int):
    """
    find function all channel and set bin level
    @param function:
    @param bin_x:
    @return:
    """
    matrix_config = dataset.get_row_column_array(parameter_def.UsedSheet.basic.value, [10, 10, 8, 8])
    ch_info_dict = dataset.get_ch_func_chip_dict()
    fun_ch_info_dict = {}
    channel_info = []
    resistor_list = []
    addr_list = []
    i = 0

    for key, value in ch_info_dict.items():
        if function in value["function"] and key != 'CH_6 LS':
            fun_ch_info_dict.update({key: ch_info_dict[key]})

    for keys, values in fun_ch_info_dict.items():
        channel_info.append(keys[3:])

    for channel in channel_info:
        bin_source = dataset.get_bin_info_by_channel(channel)['ch_analog_input']
        if "TI" in matrix_config and "Matrix Controller" in bin_source:
            channel_info_dict = dataset.get_TI_matrix_info(int(channel))
            set_ad_value = round((channel_info_dict['min_ad'][bin_x - 1] + channel_info_dict['max_ad'][bin_x - 1]) / 2,
                                 0)
            bin_set.set_vol_base_on_TI_matrix_ad(7, set_ad_value)
            time.sleep(1)
            power_reset()
            return print("TI set {} bin {} ok !".format(function, bin_x))

        elif "NXP" in matrix_config:
            bin_set.send_vol_output(7, parameter_def.NXP_BIN_Level_vol["BIN{}".format(bin_x)].value)
            return print("NXP set {} bin {} ok !".format(function, bin_x))
        else:
            resistor = dataset.get_bin_info_by_channel(channel)['ch_bin'][bin_x - 1] / 1000
            chx_analog_input = dataset.get_bin_info_by_channel(channel)['ch_analog_input']
            addr = int(chx_analog_input.split()[-1])
            resistor_list.append(resistor)
            addr_list.append(addr)

    for resistors in resistor_list:
        time.sleep(1)
        bin_set.set_vol_base_on_resistor(addr_list[i], resistors)
        i += 1
    power_reset()
    return print("Analog set {} bin {} ok !".format(function, bin_x))


def set_all_function_no_ntc_derating():
    """
    set all channel no ntc derating
    @return:
    """
    ch_list = []
    source_list = []
    source_min_list = []
    ch_info_dict = dataset.get_ch_func_chip_dict()
    for key, values in ch_info_dict.items():
        if key != "CH_6 LS":
            ch_list.append(int(key[3:]))
    for ch in ch_list:
        ntc_info_dict = dataset.get_ntc_info(ch)
        if "Matrix Controller" in ntc_info_dict["ch_NTC_source"]:
            source_list.append(8)
        else:
            source_list.append(ntc_info_dict["ch_NTC_source"][13:])
    for value in source_list:
        if source_min_list.count(value) < 1 and value != '':
            source_min_list.append(value)
    for values in source_min_list:
        bin_set.set_vol_base_on_resistor(int(values), 25)
        time.sleep(1)
    print("set all function no ntc derating !")


def get_derating_req_value(function: str):
    """

    @param function:
    @return: dict
    """
    for item in parameter_def.derating_req:
        if item.name in function:
            return parameter_def.derating_req[item.name].value


def read_test_function_current(fun_ch_info_dict: dict):
    """
    read
    @param fun_ch_info_dict:
    @return:
    """
    function_current = []
    if fun_ch_info_dict is None:
        function_current = []
    else:
        for key, values in fun_ch_info_dict.items():
            if key != "CH_6 LS":
                measure_current = round(read_curr_vol.read_current(int(key[3:])), 2)
                function_current.append(measure_current)
    return function_current


def power_reset():
    if battery_KL31.read_output_voltage() == 0:
        battery.set_output('OFF')
        time.sleep(0.5)
        battery_KL31.set_output('off')
        time.sleep(1.5)
        battery.set_output('ON')
    else:
        battery.set_output('OFF')
        time.sleep(0.5)
        battery_KL31.set_output('off')
        time.sleep(1.5)
        battery.set_output('ON')
        battery_KL31.set_output('on')


def check_result_if_match_requirement(expect_result, actual_result, margin):
    i = 0
    for result in expect_result:
        if result == 0:
            if abs((result - actual_result[i])) <= 2:
                i += 1
            else:
                return False
        else:
            if abs((result - actual_result[i]) / result) <= margin \
                    or abs((result - actual_result[i])) <= 25:
                i += 1
            else:
                return False
    return True


def get_tc_data(tc_type: str):
    """
    get yaml data
    @param tc_type:
    @return:
    """
    return yaml_case.get_tc_data()[tc_type]

# function = "LB"
# current_bef_derating, current_af_derating, function_cal = PCBA_derating_test_step(function,110)
# expect = cal_expect_result(function_cal,current_bef_derating)
# result = check_result_if_match_requirement(expect,current_af_derating,0.08)
# print(result)
