"""
This file is used to provide NTC derating test interface to test case. (LDM12A/B/C)

Refer to LDM12FNV3_SYSQTS 10.5: Power derating Function.

@Author: Yujie.shi
@Date: 2023.02.21
"""
import time

from Core import parse_yaml_case
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import (
    dataset,
    canoe_app,
    read_curr_vol,
    battery,
    parameter_def, msg_sig_env_def, bin_set, cdd_qualifier_def, battery_KL31
)

yaml_case = parse_yaml_case.YamlCaseHandler("./test_profile/test_case/ford_test_case/tc_ntc_derating.yaml")


def ntc_test_step(function: str, TD_value: int):
    """
    NTC test step.
    because test case
    TD_value=1: input tem < TD1,TD_value=[2,3,4,5,6] : input TD-1< tem < TD,TD_value=7:input tem > TD max
    @param function: test function
    @param TD_value:
    @return: current_bef_derating, current_af_derating, derating_value, function_cal
    """
    set_all_function_no_ntc_derating()
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Foreground_LB.value[0], 0)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Foreground_LB.value[1], 0)

    battery.power_reset()
    time.sleep(1)
    fun_ch_info_dict, function_name = get_function_data(function)
    function_cal = function_name[0]
    req_dict = get_start_stop_req_value(function_cal)
    battery.set_default_status()
    battery_KL31.set_default_status()

    set_bin_function(function_cal, 6)  # configure BIN 5 current is 500 mA
    send_function_req(function_cal, req_dict["req"])

    time.sleep(4)
    current_bef_derating = read_test_function_current(fun_ch_info_dict)
    print("step 1: measure current={}mA".format(current_bef_derating))

    ntc_R, ntc_R_AD, channel, source_value = get_tem_R_derating_source(fun_ch_info_dict, TD_value)
    bin_set.set_vol_base_on_resistor(int(source_value), ntc_R)
    time.sleep(1)
    power_reset()
    time.sleep(3)

    current_af_derating = read_test_function_current(fun_ch_info_dict)
    actual_derating = round((1 - sum(current_af_derating) / sum(current_bef_derating)) * 100, 2)
    print(
        "step 2: Set {} ohm to analog {} "
        "set derating then measure current={}mA and actual derating is {} %"
        .format(ntc_R, source_value, current_af_derating, actual_derating)
    )
    return current_bef_derating, current_af_derating, channel, function_cal


def expect_current(current_bef_derating: list, channel: int, function: str):
    """
    cal expect current
    @param current_bef_derating:
    @param channel:
    @param function:
    @return:
    """
    expect_list = []
    current_ad = read_ntc_ad(channel)
    tem = dataset.get_ntc_tem(current_ad)
    TD_list = dataset.get_ntc_info(channel)['ch_TD']
    BD_list = dataset.get_ntc_info(channel)['ch_BD']
    derating = 0
    for i in range(6):
        if tem < TD_list[0]:
            derating = BD_list[0]
        elif tem > TD_list[5]:
            derating = BD_list[5]
        elif TD_list[i] < tem < TD_list[i + 1]:
            derating = round(linear_relation(tem, TD_list[i], BD_list[i], TD_list[i + 1], BD_list[i + 1]), 1)
        elif TD_list[i] == tem:
            derating = BD_list[i]

    for current in current_bef_derating:
        if abs(current) < 1:
            expect_list.append(0)
        else:
            expect_list.append(round((current * (1 - derating / 100)), 2))

    send_function_req(function, 0)
    print("The chanel temperature is {} Deg C,the expect derating is {} % and current = {} mA"
          .format(tem, derating, expect_list))
    return expect_list


def power_reset():
    if battery_KL31.read_output_voltage() == 0:
        battery.set_output('OFF')
        battery_KL31.set_output('off')
        time.sleep(1)
        battery.set_output('ON')
    else:
        battery.set_output('OFF')
        battery_KL31.set_output('off')
        time.sleep(1)
        battery.set_output('ON')
        battery_KL31.set_output('on')


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
        source_list.append(ntc_info_dict["ch_NTC_source"][13:])
    for value in source_list:
        if source_min_list.count(value) < 1 and value != '':
            source_min_list.append(value)
    for values in source_min_list:
        bin_set.set_vol_base_on_resistor(int(values), 20)
        time.sleep(1)
    print("set all function no ntc derating !")


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


def get_function_data(function: str):
    """

    @param function:test function    @return:  channel(the first one )
    """
    ch_info_dict = dataset.get_ch_func_chip_dict()
    fun_ch_info_dict = {}
    function_name = []
    if function == "SML":  # dataset has no sml
        sml_dict = {'CH_13': {'function': 'SML'}}
        fun_ch_info_dict.update(sml_dict)
        function_name.append("SML")

    elif function == "HB":  # pixel HB/matrix HB and return static HB to send hb req
        for key, value in ch_info_dict.items():
            if "Pixel" == value["function"] or function in value["function"]:
                function_name.append("Static_HB")
                fun_ch_info_dict.update({key: ch_info_dict[key]})
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
    ch_info_dict = dataset.get_ch_func_chip_dict()
    fun_ch_info_dict = {}
    channel_info = []
    resistor_list = []
    addr_list = []
    i = 0

    for key, value in ch_info_dict.items():
        if function in value["function"]:
            fun_ch_info_dict.update({key: ch_info_dict[key]})

    for keys, values in fun_ch_info_dict.items():
        channel_info.append(keys[3:])

    for channel in channel_info:
        resistor = dataset.get_bin_info_by_channel(channel)['ch_bin'][bin_x - 1] / 1000
        chx_analog_input = dataset.get_bin_info_by_channel(channel)['ch_analog_input']
        addr = int(chx_analog_input.split()[-1])
        resistor_list.append(resistor)
        addr_list.append(addr)

    for resistors in resistor_list:
        time.sleep(1)
        bin_set.set_vol_base_on_resistor(addr_list[i], resistors)
        i += 1
    battery.power_reset()
    print("set {} bin {} ok !".format(function, bin_x))


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


def read_ntc_ad(ch_x: int):
    """
    Read fd 35 channel NTC value
    @param ch_x:
    @return:
    """
    ad_list = []
    for i in range(4):
        result = canoe_app.send_diag_req(cdd_qualifier_def.SubFunctions.Binning_NTC_AD_Read.value)
        if ch_x > 6:
            ntc_value = result[2 * ch_x + 3] * 0x100 + result[2 * ch_x + 4]
        else:
            ntc_value = result[2 * ch_x + 1] * 0x100 + result[2 * ch_x + 2]
        ad_list.append(ntc_value)
        time.sleep(0.3)
    current_ad = round(sum(ad_list) / len(ad_list), 0)
    return current_ad


def linear_relation(X: int, X1: int, Y1: int, X2: int, Y2: int):
    """
    Calculation of bivariate linear equation
    Y = aX + b
    @param X: need cal Y value
    @param X1: Y1 = aX1 + b
    @param Y1: Y1 = aX1 + b
    @param X2: Y2 = aX2 + b
    @param Y2: Y2 = aX2 + b
    @return: Y
    """
    a = (Y1 - Y2) / (X1 - X2)
    b = Y1 - a * X1
    value = a * X + b
    return value


def get_tem_R_derating_source(fun_ch_info_dict: dict, TD: int):
    """
    Get the resistance value and AD corresponding to the temperature
    and tem is between both TD -1  and TD when TD = 2 - 6
    tem is TD 1 -20 when TD=1
    tem is TD max + 20 when TD=7
    @param TD:
    @return: ntc_R, ntc_R_AD
    """
    ch_list = []
    tem_list = []
    derating_list = []
    source_list = []
    channel = 0
    tem_value = 0
    source_value = 0
    for key, values in fun_ch_info_dict.items():
        if key != "CH_6 LS":
            ch_list.append(int(key[3:]))
    for ch in ch_list:
        ntc_info_dict = dataset.get_ntc_info(ch)
        source_list.append(ntc_info_dict["ch_NTC_source"][13:])
        if TD == 1:
            tem = ntc_info_dict['ch_TD'][0] - 20
            derating = ntc_info_dict['ch_BD'][0]
        elif TD == 7:
            tem = ntc_info_dict['ch_TD'][5] + 20
            derating = ntc_info_dict['ch_BD'][5]
        else:
            tem = round((ntc_info_dict['ch_TD'][TD - 2] + ntc_info_dict['ch_TD'][TD - 1]) / 2, 0)
            derating = linear_relation(
                tem, ntc_info_dict['ch_TD'][TD - 2], ntc_info_dict['ch_BD'][TD - 2],
                ntc_info_dict['ch_TD'][TD - 1], ntc_info_dict['ch_BD'][TD - 1]
            )
        tem_list.append(tem)
        derating_list.append(derating)
        derating_value = max(derating_list)
        tem_value = tem_list[derating_list.index(derating_value)]
        source_value = source_list[derating_list.index(derating_value)]
        channel = ch_list[derating_list.index(derating_value)]
    ntc_R, ntc_R_AD = dataset.get_ntc_R_AD(tem_value)

    return ntc_R, ntc_R_AD, channel, source_value


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


def get_start_stop_req_value(function: str):
    """

    @param function:
    @return: dict
    """
    for item in parameter_def.derating_req:
        if item.name in function:
            return parameter_def.derating_req[item.name].value


def set_TI_chip_bin(ch_x: int, bin_x: int):
    """
    TI matrix chip set BIN level
    :param ch_x:
    :param bin_x:
    :return:
    """
    channel_info_dict = dataset.get_TI_matrix_info(ch_x)
    set_ad_value = round((channel_info_dict['min_ad'][bin_x - 1] + channel_info_dict['max_ad'][bin_x - 1]) / 2, 0)
    bin_set.set_vol_base_on_TI_matrix_ad(7, set_ad_value)
    time.sleep(1)
    power_reset()


def cal_function_set_ad(ch_list: list, TD):
    """
    select the max derating value ad
    :param ch_list:
    :param TD:
    :return:
    """
    derating_list = []
    ad_list = []
    for ch_x in ch_list:
        channel_info_dict = dataset.get_ntc_info(ch_x)
        if TD == 1:
            set_ad_value = channel_info_dict['ch_TD'][0] + 3
            derating = channel_info_dict['ch_BD'][0]
        elif TD == 7:
            set_ad_value = channel_info_dict['ch_TD'][5] - 3
            derating = channel_info_dict['ch_BD'][5]
        else:
            set_ad_value = round((channel_info_dict['ch_TD'][TD - 2] + channel_info_dict['ch_TD'][TD - 1]) / 2, 0)
            derating = linear_relation(set_ad_value,
                                       channel_info_dict['ch_TD'][TD - 2], channel_info_dict['ch_BD'][TD - 2],
                                       channel_info_dict['ch_TD'][TD - 1], channel_info_dict['ch_BD'][TD - 1])
        derating_list.append(derating)
        ad_list.append(set_ad_value)

    derating_max = max(derating_list)
    ad = ad_list[derating_list.index(derating_max)]
    return ad


def set_TI_chip_TD(ad: int):
    """
    set TI ntc
    :param ch_x:
    :param TD:
    :return:
    """
    bin_set.set_vol_base_on_TI_matrix_ad(8, ad)
    time.sleep(1)
    power_reset()


def TI_matrix_chip_NTC_test_step(function: str, TD: int):
    ch_list = []
    battery.set_default_status()
    battery_KL31.set_default_status()
    time.sleep(1)
    bin_set.send_vol_output(8, 4.5)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Foreground_LB.value[0], 0)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Foreground_LB.value[1], 0)

    time.sleep(1)
    fun_ch_info_dict, function_name = get_function_data(function)
    for key, values in fun_ch_info_dict.items():
        if key != "CH_6 LS":
            ch_list.append(int(key[3:]))
    set_TI_chip_bin(ch_list[0], 5)
    function_cal = function_name[0]
    req_dict = get_start_stop_req_value(function_cal)
    time.sleep(1)
    power_reset()
    time.sleep(1)

    send_function_req(function_cal, req_dict["req"])

    time.sleep(3)
    current_bef_derating = read_test_function_current(fun_ch_info_dict)
    print("step 1: measure current={}mA".format(current_bef_derating))
    ad = cal_function_set_ad(ch_list, TD)
    set_TI_chip_TD(ad)
    time.sleep(1)
    function_req_reset(function_cal)
    time.sleep(3)

    current_af_derating = read_test_function_current(fun_ch_info_dict)
    actual_derating = round((1 - sum(current_af_derating) / sum(current_bef_derating)) * 100, 2)
    print(
        "Step 2: set AD = {} then measure current={}mA and actual derating is {} %"
        .format(ad, current_af_derating, actual_derating)
    )
    return current_bef_derating, current_af_derating, ch_list, function_cal


def function_req_reset(function: str):
    """
    resend function req off -> on
    :param function:
    :return:
    """
    req_dict = get_start_stop_req_value(function)
    send_function_req(function, 0)
    time.sleep(1)
    send_function_req(function, req_dict["req"])
    time.sleep(1)


def cal_ad_derating(ch_x: int, ad):
    """
    cal expect derating value
    :param ch_x:
    :param ad:
    :return: derating
    """
    channel_info_dict = dataset.get_ntc_info(ch_x)
    td_list = channel_info_dict['ch_TD']
    bd_list = channel_info_dict['ch_BD']
    for i in range(6):
        if td_list[i + 1] <= ad <= td_list[i]:
            derating = linear_relation(ad, td_list[i + 1], bd_list[i + 1], td_list[i], bd_list[i])
            return derating
        elif ad < td_list[5]:
            return bd_list[5]
        elif ad > td_list[0]:
            return bd_list[0]


def matrix_expect_current(ch_list: list, current_bef_derating: list, function: str):
    derating_list = []
    _expect_current = []
    for ch in ch_list:
        ad = read_ntc_ad(ch)
        derating_list.append(1 - cal_ad_derating(ch, ad) / 100)
    derating_max = max(derating_list)
    for current in current_bef_derating:
        _expect_current.append(round(current * derating_max, 2))
    expect_derating = round((1 - sum(_expect_current) / sum(current_bef_derating)) * 100, 2)
    print("The expect current is {} mA, the expect deraing is {} %".format(_expect_current, expect_derating))
    send_function_req(function, 0)
    bin_set.send_vol_output(8, 4.5)
    time.sleep(1)
    power_reset()
    return _expect_current


def set_NTC_ad(ad):
    """
    set NXP ad
    :param ad:
    :return:
    """
    bin_set.set_vol_base_on_NXP_matrix_ad(8, ad)
    time.sleep(1)
    power_reset()


def NXP_matrix_chip_NTC_test_step(function: str, TD: int):
    """
    NXP ntc test step,
    BIN_SET channel 7 to set bin level, all function bin source should configure the same matrix chip
    BIN_SET channel 8 to set NTC level, all function NTC source should configure the same matrix chip
    :param function:
    :param TD:
    :return:
    """
    ch_list = []
    battery.set_default_status()
    battery_KL31.set_default_status()
    time.sleep(1)
    bin_set.send_vol_output(8, 4.5)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Foreground_LB.value[0], 0)
    canoe_app.set_EnvVar(parameter_def.FunMapToENV.Foreground_LB.value[1], 0)

    time.sleep(1)
    fun_ch_info_dict, function_name = get_function_data(function)
    for key, values in fun_ch_info_dict.items():
        if key != "CH_6 LS":
            ch_list.append(int(key[3:]))
    bin_set.send_vol_output(7, parameter_def.NXP_BIN_Level_vol.BIN5.value)  # 使用第7通道来设置bin值
    function_cal = function_name[0]
    req_dict = get_start_stop_req_value(function_cal)

    send_function_req(function_cal, req_dict["req"])
    power_reset()

    time.sleep(3)
    current_bef_derating = read_test_function_current(fun_ch_info_dict)
    ad = cal_function_set_ad(ch_list, TD)
    print("step 1: measure current={}mA".format(current_bef_derating))
    set_NTC_ad(ad)
    time.sleep(2)
    function_req_reset(function_cal)
    time.sleep(3)

    current_af_derating = read_test_function_current(fun_ch_info_dict)
    actual_derating = round((1 - sum(current_af_derating) / sum(current_bef_derating)) * 100, 2)
    print(
        "Step 2: set AD = {} then measure current={}mA and actual derating is {} %"
        .format(ad, current_af_derating, actual_derating)
    )
    return current_bef_derating, current_af_derating, ch_list, function_cal

# current_bef_derating, current_af_derating, ch_list, function_cal = NXP_matrix_chip_NTC_test_step("TI", 7)
# matrix_expect_current(ch_list, current_bef_derating, function_cal)
# list = []
# for i in range(4, 104, 4):
#     bin = i/10
#     bin_set.set_vol_base_on_resistor(2, bin)
#     current_ad = read_ntc_ad(1)
#     print('set',bin)
#     re = (102300-5090*current_ad)/(current_ad-1023)/1000
#     re_1 = round(re,4)
#     print(re_1)
#     list.append(re_1)
#     time.sleep(1)
# print(list)