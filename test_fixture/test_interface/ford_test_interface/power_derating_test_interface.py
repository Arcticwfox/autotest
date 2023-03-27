"""
This file is used to provide Power derating test interface to test case. (LDM12A/B/C)

Refer to LDM12FNV3_SYSQTS 10.5: Power derating Function.

@Author: Yujie.shi
@Date: 2023.01.10
"""

import time
from Core.project.ford import security_access
from Core import parse_yaml_case
from Core.project.ford import cdd_qualifier_def
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import (
    dataset,
    canoe_app,
    read_curr_vol,
    battery,
    calc, parameter_def, msg_sig_env_def, bin_set, battery_KL31, can_msg
)
from test_fixture.test_interface.ford_test_interface import sml_test_interface

yaml_case = parse_yaml_case.YamlCaseHandler("./test_profile/test_case/ford_test_case/tc_power_derating.yaml")


def set_start_stop_derating(function: str, vo: int):
    """
    read current before derating
    set derating then read again

    @param function: function
    @param vo: start stop derating voltage
    @return: current before derating and after derating
    """
    set_all_function_no_ntc_derating()
    # set_bin_function(function, 3)
    power_reset()
    time.sleep(1)
    fun_ch_info_dict, function_name = get_function_data(function)
    derating_dict = get_derating_req_value(function)
    if fun_ch_info_dict is None:
        current_bef_derating = []
        current_af_derating = []
        function_cal = []
    else:
        function_cal = function_name[0]
        battery.set_default_status()

        if function_cal == 'Pixel':
            # canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLghtHi_D_Rq.value, 1)  # send HB on 12B
            canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HBHL_Beam_D_Rq_3.value, 1)  # 12C
        else:
            send_function_req(function, derating_dict["req"])

        time.sleep(3)
        current_bef_derating = read_test_function_current(fun_ch_info_dict)
        print("step 1: measure current={}mA".format(current_bef_derating))

        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.ElPw_D_Stat_3.value, 0x02)
        set_input_vol_slow(vo)
        time.sleep(2)

        current_af_derating = read_test_function_current(fun_ch_info_dict)
        actual_derating = round((1 - (sum(current_af_derating) / sum(current_bef_derating))) * 100, 2)
        print(
            "step 2: Set input voltage = {} V and "
            "set start stop derating then measure current={}mA,actual_derating = {} %"
            .format(vo, current_af_derating, actual_derating)
        )

    return current_bef_derating, current_af_derating, function_cal


def set_low_vol_derating(test_function: str, vo: int):
    """
    read current before derating
    set derating then read again
    if test function == pixel or HB , read DID about intensity and measure current

    @param test_function: function
    @param vo: derating voltage
    @return: current before derating and after derating
    """
    # set_all_function_no_ntc_derating()
    # set_bin_function(test_function, 3)
    # power_reset()
    # time.sleep(1)
    fun_ch_info_dict, function_name = get_function_data(test_function)
    function = function_name[0]
    derating_dict = get_derating_req_value(function)
    send_function_req('Foreground_LB', 0)  # close LB to reduce power,only test function is on
    if fun_ch_info_dict is None:
        current_bef_derating = []
        actual_result = []
    else:
        battery.set_default_status()
        battery_KL31.set_default_status()
        send_function_req(test_function, derating_dict['req'])
        time.sleep(3)

        if function == 'Pixel' or 'HB' in function:
            canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassL_D_Rq_4.value, 13)
            canoe_app.set_EnvVar(msg_sig_env_def.EnvName.LowBeamLightClassR_D_Rq_4.value, 13)
            send_function_req('Foreground_LB', 1)
            time.sleep(1)
            if vo > 9:
                current_bef_derating = read_test_function_current(fun_ch_info_dict)
            else:
                set_input_vol_slow(9)
                current_bef_derating = read_test_function_current(fun_ch_info_dict)
        else:
            current_bef_derating = read_test_function_current(fun_ch_info_dict)
        print("step 1: measure current={}mA before derating".format(current_bef_derating))

        set_input_vol_slow(vo)
        time.sleep(2)

        if function == 'Pixel' or 'HB' in function:
            actual_result = send_did_to_read_ch_intensity(fun_ch_info_dict)
            current = read_test_function_current(fun_ch_info_dict)
            actual_result.extend(current)
        else:
            actual_result = read_test_function_current(fun_ch_info_dict)
        print("step 2: Set input voltage = {} V and actual result is {} ".format(vo, actual_result))
    return current_bef_derating, actual_result, function


def set_low_vol_animation_derating(test_function: str, vo: float):
    """
    read current before derating
    set derating then read again

    @param test_function: function
    @param vo: derating voltage
    @return: current before derating and after derating
    """
    battery.set_default_status()
    battery_KL31.set_default_status()
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SwitchOnOff.value, 0x00)

    time.sleep(1)

    fun_ch_info_dict, function_name = get_function_data(test_function)
    function = function_name[0]

    if fun_ch_info_dict is None:
        current_bef_derating = []
        current_af_derating = []
    else:
        # security_access.ford_security_access_03(can_msg, canoe_app, False)
        enter_animation()

        type_num = get_derating_req_value(test_function)['type_num']
        write_animation_type(type_num)

        time.sleep(2)
        current_bef_derating = read_test_function_current(fun_ch_info_dict)
        print("step 1:enter animation and measure current={}mA".format(current_bef_derating))
        time.sleep(1)
        set_input_vol_slow(vo)
        time.sleep(2)

        current_af_derating = read_test_function_current(fun_ch_info_dict)
        actual_derating = round((1 - (sum(current_af_derating) / sum(current_bef_derating))) * 100, 2)
        print(
            "step 2: Set input voltage = {} V and "
            "set derating then measure current={}mA actual derating = {} %".format(vo, current_af_derating,
                                                                                   actual_derating)
        )

    return current_bef_derating, current_af_derating, function


def set_total_power_derating(bin_x: int, vo: float, main_Power: str):
    """
    set total power derating, change output power by setting different bin,set LB off and
    TI DRL(reduce the impact of low power derating) on, read DID about ecu voltage to reach expect voltage
    measure current output power
    @param bin_x: configure bin 1 : low output power, bin 7 : max output power in dataset
    @param vo: expect ecu voltage
    @return: current output power
    """
    test_function = ["TI", "DRL", "Pixel"]
    for function in test_function:
        set_bin_function(function, bin_x)

    if main_Power == "on":
        send_function_req("Static_TI", 2)
        send_function_req("DRL", 2)
        send_function_req("Foreground_LB", 1)
        time.sleep(1)
        battery_KL31.set_output('off')
        print("step1: set bin to control output power and set low Beam power = 0V")
        set_ecu_vol(vo)
    else:
        battery.set_output('off')
        battery_KL31.set_output('on')
        battery_KL31.set_input_voltage(13.5)
        print("step1: set bin to control output power and set main power = 0V")

    power = cal_current_output_power()
    print("step2: measure current output power = {} w !".format(power))

    return power


def total_power_expect_result(main_power_status: str):
    """
    cal total power expect result
    @return:
    """
    ecu_vol = read_ECU_vol()
    if main_power_status == "on":

        expect_max = linear_relation(
            ecu_vol, parameter_def.total_power["start_vol"], parameter_def.total_power["start_power"],
            parameter_def.total_power["stop_vol"], parameter_def.total_power["stop_power"])

        if expect_max > parameter_def.total_power["start_power"]:
            expect_max = parameter_def.total_power["start_power"]
    else:
        expect_max = 40

    battery.set_default_status()
    battery_KL31.set_default_status()
    print("step3: The expected max power is {} w !".format(expect_max))
    send_function_req("Static_TI", 0)
    send_function_req("DRL", 0)
    send_function_req("Foreground_LB", 0)
    return expect_max


def animation_expect_result(current_bef_derating: list, function: str):
    """

    @param current_bef_derating:
    @param function:
    @return: expect current
    """
    expect_result = []
    derating_value = []
    ch = []
    ecu_vol = read_ECU_vol()
    i = 0
    fun_ch_info_dict, function_name = get_function_data(function)
    if current_bef_derating is None:
        expect_result = []
    else:
        for key, values in fun_ch_info_dict.items():
            if key != "CH_6 LS":
                ch.append(int(key[3:]) + 49)
                result = canoe_app.send_diag_req(parameter_def.DiagRequest["FD{}_DID".format(str(ch[0]))].value)
                derating = int(round(result[8] * 100 / 255, 2))
                if "HB" in values['function'] and ecu_vol < 9:  # HB 9v off
                    derating = 0
                # if ecu_vol < 8:  # if voltage <8, all function off in animation mode
                #     derating = 0
                derating_value.append(derating)

        for channel in current_bef_derating:
            expect_result.append(round((channel * derating_value[i] / 100), 2))
            i += 1

        time.sleep(1)
        expect_derating = round((1 - (sum(expect_result) / sum(current_bef_derating))) * 100, 2)
        battery.set_default_status()
        battery_KL31.set_default_status()
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SwitchOnOff.value, 0X01)
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.Ignition_Status_4.value, 0x04)
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.WfSubstate_D_Stat_3.value, 0x00)
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.WfSuperstate_D_Stat_2.value, 0x00)
        # canoe_app.set_EnvVar(msg_sig_env_def.EnvName.ExLghtAnmtn_D_Rq.value, 0x00)
        print("The expect result is {} and expect derating = {} %".format(expect_result, expect_derating))
        time.sleep(1)
    return expect_result


def cal_expect_current_by_DID(current_bef_derating: list, function: str):
    """
    cal expect current (get class C intensity) by DID
    @param current_bef_derating:
    @param function: test function
    @return: expect result (pixel / HB : class C intensity + current; the others : current)
    """
    expect_result = []
    ch = []
    current = []
    fun_ch_info_dict, function_name = get_function_data(function)
    cal_function = function_name[0]
    ecu_vol = read_ECU_vol()
    if fun_ch_info_dict is None:
        expect_result = []

    else:
        for key, values in fun_ch_info_dict.items():
            if key != "CH_6 LS":
                ch.append(int(key[3:]) + 49)
        result = canoe_app.send_diag_req(parameter_def.DiagRequest["FD{}_DID".format(str(ch[0]))].value)
        derating = int(round(result[8] * 100 / 255, 2))  # one function has the same derate in different channels
        if ecu_vol < 6:  # if voltage <6, all function off
            derating = 0

        if function == 'Pixel' or 'HB' in cal_function:
            cal_result = expect_pixel_intensity()  # get pixel intensity from dataset
            if ecu_vol < 6:  # if voltage <6, all function off
                for intensity in cal_result:
                    expect_result.append(intensity * 0)
            else:
                expect_result.extend(cal_result)
            for channel in current_bef_derating:
                if abs(channel) < 1:
                    current.append(0)
                else:
                    current.append(round(channel * derating / 100))
            expect_result.extend(current)

        elif function == 'SML':  # read sml cfg current if vol < 6 current =0
            sml_current_cfg = canoe_app.send_diag_req(parameter_def.DiagRequest.DE00_read_DID.value)
            expect_current = round(sml_current_cfg[32] * 230 / 255 + 25, 0)
            if ecu_vol < 6:
                expect_current = 0
            expect_result.append(expect_current)

        else:
            for channel in current_bef_derating:
                expect_result.append(round(channel * derating / 100))

    time.sleep(1)
    battery.set_default_status()
    battery_KL31.set_default_status()
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.ElPw_D_Stat_3.value, 0x00)
    if function == 'Pixel':
        # canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLghtHi_D_Rq.value, 0)  # 12B
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HBHL_Beam_D_Rq_3.value, 0)  # 12C
    else:
        send_function_req(function, 0)
    print("The expect result is {}".format(expect_result))
    return expect_result


def start_stop_expect_current(current_bef_derating: list, function: str):
    """
    Calculation of expect value
    @param current_bef_derating: the current before start stop derating
    @param function: test function
    @return: expect current after start stop derating
    """
    expect_current = []
    derating_dict = get_derating_req_value(function)
    if current_bef_derating is None:
        expect_current = []
    else:
        expect_derating = startstop_derating_cal(derating_dict["Start"], derating_dict["Stop"])

        for channel in current_bef_derating:
            expect_current.append(round((channel * (100 - expect_derating) / 100), 2))
        print("expect_derating = {} % and expect current = {} mA".format(expect_derating, expect_current))

        time.sleep(1)
        battery.set_default_status()
        battery_KL31.set_default_status()
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.ElPw_D_Stat_3.value, 0x00)
        send_function_req(function, 0)

    return expect_current


def check_total_power_result(expect_max_power: float, actual_result: float):
    """
    check total power derating result, the actual result should less than expect max power or within the margin of error
    @param expect_max_power:
    @param actual_result:
    @return: check result Ture or False
    """
    if actual_result < expect_max_power:
        return True
    elif abs((expect_max_power - actual_result) / expect_max_power) <= 0.08:  # the current error is 8%
        return True
    else:
        return False


def check_result_if_match_requirement(expect_result: list, actual_result: list, margin: float):
    """
    check result
    if expect_current = 0, actual current should in [-2,2]
    when the expect current matrix channel about 100mA,it would have large error
    @param expect_result: cal intensity
    @param actual_result: measure intensity
    @param margin:
    @return:
    """
    i = 0
    if expect_result is None:
        return False
    else:
        for expect_current in expect_result:
            if expect_current == 0:  # read actual current would be [-2,2] even if channel is off
                if abs((expect_current - actual_result[i])) <= 2:
                    i += 1
                else:
                    return False
            else:
                if abs((expect_current - actual_result[i]) / expect_current) <= margin \
                        or abs((expect_current - actual_result[i])) <= 20:
                    # the error range is 8% but matrix channel would have large error when current = 100mA
                    i += 1
                else:
                    print(expect_current, actual_result[i])
                    return False
        return True


def get_tc_data(tc_type: str):
    """
    get yaml data
    @param tc_type:
    @return:
    """
    return yaml_case.get_tc_data()[tc_type]


def expect_pixel_intensity():
    """
    cal expect matrix class intensity(include class lb and hb,left/right ecu,different mode and ecu voltage)
    @return: matrix intensity
    """
    pixel_intensity = []
    calc.get_pixel_class_intensity()
    pixel_result_dict = calc.get_pixel_ch_int_dict()
    for key, value in pixel_result_dict.items():
        for switch in range(1, 13):
            pixel_intensity.append(pixel_result_dict[key][switch])
    return pixel_intensity


def send_did_to_read_ch_intensity(ch_info_dict: dict):
    """
    Read DID to get actual result
    @param ch_info_dict: dict
    @return: list
    """
    did_result = []
    read_did_len = 3

    for key, values in ch_info_dict.items():
        if values['function'] != 'Static_HB':
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


def enter_animation():
    """
    enter welcome
    @return:
    """
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SwitchOnOff.value, 0X01)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.Ignition_Status_4.value, 0x01)
    send_function_req('Foreground_LB', 0)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.WfSubstate_D_Stat_3.value, 0x02)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.WfSuperstate_D_Stat_2.value, 0x01)


def choose_animation_type(type_num: int):
    """
    choose animation type
    @param type_num: 0 - 15
    """
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.ExLghtAnmtn_D_Rq.value, type_num)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.Ignition_Status_4.value, 0x04)
    time.sleep(0.5)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.Ignition_Status_4.value, 0x01)


def read_channel_current():
    """
    read FD 33
    @return: CH1-12 current
    """
    result = canoe_app.send_diag_req(parameter_def.DiagRequest.FD33_DID.value)[3:15]
    current = []
    for cu in result:
        current.append(round(cu * 1200 / 255, 1))
    return current


def cal_current_output_power():
    """
    cal output power
    @return: power
    """
    current_list = []
    voltage_list = []
    vol_addr = 0
    power = 0
    for i in range(1, 14):
        current = round(read_curr_vol.read_current(i) / 1000, 2)
        if current < 0:
            current = 0
        current_list.append(current)
    for j in range(14, 27):
        voltage = round(read_curr_vol.read_voltage(j), 2)
        voltage_list.append(voltage)

    for current in current_list:
        power = round(power + current * voltage_list[vol_addr], 2)
        vol_addr += 1
    return power


def set_all_function_bin(bin_x: int):
    """
    find function all channel and set bin level
    @param function:
    @param bin_x:
    @return:
    """
    matrix_config = dataset.get_row_column_array(parameter_def.UsedSheet.basic.value, [10, 10, 8, 8])
    ch_info_dict = dataset.get_ch_func_chip_dict()
    ch_bin_info_dict = {}
    channel_info = []
    resistor_list = []
    addr_list = []
    i = 0

    for keys, values in ch_info_dict.items():
        if keys != 'CH_6 LS':
            ch_bin_info_dict.update({keys: ch_info_dict[keys]})

    for keys, values in ch_bin_info_dict.items():
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
            return print("set all function bin {} ok !".format(bin_x))

        elif "NXP" in matrix_config:
            bin_set.send_vol_output(7, parameter_def.NXP_BIN_Level_vol["BIN{}".format(bin_x)].value)
            return print("set all function bin {} ok !".format(bin_x))
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
    return print("set all function bin {} ok !".format(bin_x))


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
        if "TI" in matrix_config and "Matrix Controller" in bin_source:  # 使用TI 芯片设置bin
            channel_info_dict = dataset.get_TI_matrix_info(int(channel))
            set_ad_value = round((channel_info_dict['min_ad'][bin_x - 1] + channel_info_dict['max_ad'][bin_x - 1]) / 2,
                                 0)
            bin_set.set_vol_base_on_TI_matrix_ad(7, set_ad_value)
            time.sleep(1)
            power_reset()
            return print("set {} bin {} ok !".format(function, bin_x))

        elif "NXP" in matrix_config and "Matrix Controller" in bin_source:  # NXP 芯片
            bin_set.send_vol_output(7, parameter_def.NXP_BIN_Level_vol["BIN{}".format(bin_x)].value)
            return print("set {} bin {} ok !".format(function, bin_x))
        else:
            resistor = dataset.get_bin_info_by_channel(channel)['ch_bin'][bin_x - 1] / 1000  # analog
            chx_analog_input = dataset.get_bin_info_by_channel(channel)['ch_analog_input']
            addr = int(chx_analog_input.split()[-1])
            resistor_list.append(resistor)
            addr_list.append(addr)

    for resistors in resistor_list:
        time.sleep(1)
        bin_set.set_vol_base_on_resistor(addr_list[i], resistors)
        i += 1
    power_reset()
    return print("set {} bin {} ok !".format(function, bin_x))


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
        bin_set.set_vol_base_on_resistor(int(values), 16)
        time.sleep(1)
    print("set all function no ntc derating !")


def read_ECU_vol():
    """
    DID read ECU vol
    @return: vol .V
    """
    data = []
    if calc.side == parameter_def.ecu_side.right.value:
        data = canoe_app.send_diag_req(parameter_def.DiagRequest.Right_Headlamp_Power_Supply_Read.value)
    elif calc.side == parameter_def.ecu_side.left.value:
        data = canoe_app.send_diag_req(parameter_def.DiagRequest.Left_Headlamp_Power_Supply_Read.value)
    ECU_vol = round(data[3] / 4, 2)
    return ECU_vol


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


def set_ecu_vol(vo: float):
    time.sleep(1)
    while True:
        ecu_vol = read_ECU_vol()
        vo_battery = battery.read_output_voltage()
        time.sleep(0.5)
        if abs(ecu_vol - vo) <= 0.5:
            print("DID read ecu voltage = {} v".format(ecu_vol))
            break
        elif ecu_vol - vo > 0.5:
            battery.set_input_voltage(vo_battery - 0.5)
        else:
            battery.set_input_voltage(vo_battery + 0.5)


def startstop_derating_cal(start: int, stop: int):
    """
    Read the current voltage and calculate the theoretical derating
    @param start:start derating value
    @param stop:stop derating value
    @return:theoretical derating
    """
    ecu_vol = read_ECU_vol()
    print("DID read ecu_voltage = {} V".format(ecu_vol))
    derating = linear_relation(ecu_vol, 10, start, 6, stop)
    if derating < start:
        derating = start
    return derating


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


def low_vol_derating_cal(start_vol: int, start_derating: int, stop_vol: int, stop_derating: int):
    """
    cal low vol derating
    @param start_vol: v
    @param start_derating: %
    @param stop_vol: v
    @param stop_derating: %
    @return: expect derating
    """
    ecu_vol = read_ECU_vol()
    print("DID read ecu_voltage = {} V".format(ecu_vol))
    derating = linear_relation(ecu_vol, start_vol, start_derating, stop_vol, stop_derating)

    if ecu_vol > start_vol:
        derating = 0
    if ecu_vol < stop_vol:
        derating = stop_derating
    if stop_derating == 0:
        derating = 0

    return derating


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


def send_function_req(function: str, req: int):
    """
    send_function_req
    @param function: function
    @param req: req on
    """
    enver_list = []
    for item in parameter_def.FunMapToENV:
        if function in item.name:
            for i in range(2):
                if parameter_def.FunMapToENV[item.name].value[i] not in enver_list:
                    enver_list.append(parameter_def.FunMapToENV[item.name].value[i])

    if function == 'SML':
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SideMarker_Actv_Rq_1.value, req)

    else:
        for enver in enver_list:
            canoe_app.set_EnvVar(enver, req)
        if function in ['Pixel', 'Foreground_LB']:
            if req == 0:
                battery_req = 'off'
            else:
                battery_req = 'on'
            battery_KL31.set_output(battery_req)


def set_input_vol_slow(vo: float):
    """
    set output voltage with 1s
    @param vo: output voltage
    @return:
    """
    voltage = battery.read_output_voltage()
    battery_KL31.set_output('off')
    step = abs(voltage - vo) / 10
    for i in range(10):
        time.sleep(0.1)
        voltage = voltage - step
        battery.set_input_voltage(voltage)
    time.sleep(1)


def cal_channel_output_power(channel: int):
    """
    cal channel output power
    matrix channel : channel_current * channel_led_num * channel_bin_vol * average_intensity_pwm +
                          channel_current * channel_current * 2 * (1 - average_intensity_pwm)

    no_matrix channel : channel_current * channel_voltage * average pwm

    @param channel: test channel
    @return: channel power : int
    """
    did_result = []
    read_did_len = 3
    power = 0
    channel_current = round(read_curr_vol.read_current(channel) / 1000, 2)
    channel_voltage = read_curr_vol.read_voltage(channel + 13)
    if channel == 13:
        power = round(channel_current * channel_voltage, 2)
    else:
        channel_info_dict = dataset.get_ch_func_chip_dict()['CH_{}'.format(channel)]
        if channel < 7:
            channel_led_num = dataset.get_row_column_array(
                parameter_def.UsedSheet.ch_output.value, [channel + 1, channel + 1, 8, 8])
        else:
            channel_led_num = dataset.get_row_column_array(
                parameter_def.UsedSheet.ch_output.value, [channel + 2, channel + 2, 8, 8])
        channel_bin_vol = dataset.get_row_column_array(parameter_def.UsedSheet.bin_ntc.value,
                                                       [11 * channel - 1, 11 * channel - 1, 11, 11]) / 1000

        if channel_info_dict['matrix_chip'] == 'NU':
            stream = canoe_app.send_diag_req(parameter_def.CHxDIDx_map['CH_{}'.format(channel)][1])

            did_result.append(round(float(100 / 255 * stream[read_did_len])))
            power = round(channel_current * channel_voltage * did_result[0] / 100, 2)
        else:
            # Matrix channel: DID FD11~FD22

            stream = canoe_app.send_diag_req(parameter_def.CHxDIDx_map['CH_{}'.format(channel)][0])

            for i in range(len(stream) - read_did_len):  # 需要的数据长度
                did_result.append(round(float(100 / 255 * stream[i + read_did_len])))  # 按CDD 换算
                average_intensity_pwm = round(sum(did_result) / len(did_result) / 100, 3)
                power = round(channel_current * channel_led_num * channel_bin_vol * average_intensity_pwm +
                              channel_current * channel_current * 2 * (1 - average_intensity_pwm), 2)

    return power


def channel_derating_test_step(channel: int):
    if channel == 13:
        function = 'SML'
        channel_info_dict = {"function": "SML", "matrix_chip": "NU"}

    else:
        channel_info_dict = dataset.get_ch_func_chip_dict()['CH_{}'.format(channel)]
        function = channel_info_dict['function']
        set_bin_function(function, 7)
        set_all_function_no_ntc_derating()

    send_req_channel_derating(channel_info_dict, get_derating_req_value(function)['req'])
    battery.power_reset()
    time.sleep(3)
    actual_power = cal_channel_output_power(channel)
    print("step 1: send {} on and measure channel {} output power is {} w".format(function, channel, actual_power))
    time.sleep(1)
    send_req_channel_derating(channel_info_dict, 0)
    return actual_power


def send_req_channel_derating(fun_info_dict: dict, req: int):
    """
    Distinguish between Pixel LB and Pixel HB
    both Pixel LB and HB turned on together, ECU would total power derating,the single channel derating would error
    @param fun_info_dict:
    @param req:
    @return:
    """
    pixel_addr_list = dataset.get_row_column_array(parameter_def.UsedSheet.pixel.value, [10, 105, 4, 4])
    if fun_info_dict['function'] == 'Pixel':
        addr_index = pixel_addr_list.index(fun_info_dict['matrix_chip'])
        if addr_index >= 64:
            canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_HB.value[0], req)
            canoe_app.set_EnvVar(parameter_def.FunMapToENV.Static_HB.value[1], req)
        else:
            canoe_app.set_EnvVar(parameter_def.FunMapToENV.Foreground_LB.value[0], req)
            canoe_app.set_EnvVar(parameter_def.FunMapToENV.Foreground_LB.value[1], req)
    elif fun_info_dict['function'] == 'SML':
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SideMarker_Actv_Rq_1.value, req)
    else:
        canoe_app.set_EnvVar(
            parameter_def.FunMapToENV[fun_info_dict['function']].value[0], req)
        canoe_app.set_EnvVar(
            parameter_def.FunMapToENV[fun_info_dict['function']].value[1], req)


def get_derating_req_value(function: str):
    """

    @param function:
    @return: dict
    """
    for item in parameter_def.derating_req:
        if item.name in function:
            return parameter_def.derating_req[item.name].value


def write_animation_type(type_num: int):
    """
    write animation config
    :param type_num:
    """
    # security_access.ford_security_access_03(can_msg, canoe_app, False)  # Ture: 12B False: 12C
    time.sleep(2)
    canoe_app.send_diag_req(cdd_qualifier_def.SubFunctions.Method_2_Data_Type_5_Write.value,
                            [cdd_qualifier_def.SubParameter.WelcomeSelect_Cfg.value,
                             cdd_qualifier_def.SubParameter.FarewellSelect_Cfg.value], [type_num + 1, type_num + 1])
    # power_reset()
# security_access.ford_security_access_03(can_msg, canoe_app, False)
# function = 'DRL'
# current_bef_derating, actual_result, function_cal = set_low_vol_derating(function, 7)
# cal_expect_current_by_DID(current_bef_derating, function)
# print(dataset.get_bin_info_by_channel(1)['ch_analog_input'])
# test_function = 'Pixel'
# set_vol = 9
# test_function = 'DRL'
# type_num = get_derating_req_value(test_function)['type_num']
# print(type_num)
# write_animation_type(type_num)

# current_bef_derating, actual_result, function_cal = set_low_vol_animation_derating(
#     test_function, set_vol)
# expect_result = animation_expect_result(current_bef_derating, test_function)
# battery_KL31.set_output('off')
# battery_KL31.set_input_voltage(13)