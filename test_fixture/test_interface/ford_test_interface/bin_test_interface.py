"""
This file is used to provide BIN test interface to test case.

@Author: Siwei.Lu
@Date: 2022.11.27
"""

import time

from Core import parse_yaml_case
from Core.project.ford import parameter_def, msg_sig_env_def

from test_fixture.test_interface.ford_test_interface.precondition_test_interface import \
    dataset, bin_set, battery, read_curr_vol, canoe_app, battery_KL31

yaml_case = parse_yaml_case.YamlCaseHandler("/test_profile/test_case/ford_test_case/tc_bin.yaml")


# todo: Add test case of out of range value.

def BINTest_expect_result(ch_x: int, bin_x: int):
    """
    Only for normal BIN testcase.
    """
    # step1: get a dict based on channel and bin(DatasetHandler)
    current = dataset.get_bin_info_by_channel(ch_x)['ch_current'][bin_x - 1]
    if current != 'NU':
        return current
    else:
        """
        When the current is set to 'NU', the output current should be the minimum current.
        """
        current = dataset.get_bin_info_by_channel(ch_x)['ch_current']
        current.remove('NU')  # remove 'NU'
        current.sort()  # 从小到大排序
        return current[0]


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


def get_derating_req_value(function: str):
    """

    @param function:
    @return: dict
    """
    for item in parameter_def.derating_req:
        if item.name in function:
            return parameter_def.derating_req[item.name].value


def BINTest_step(ch_x: int, bin_x: int):
    print("step 1: Set bin resistor in range BIN{} (SerialHandler)".format(bin_x))
    addr = map_ch_to_addr(ch_x)
    channel_info_dict = dataset.get_ch_func_chip_dict()["CH_{}".format(ch_x)]
    ch_fun = channel_info_dict['function']
    set_bin_function(ch_fun, bin_x)

    print("step 2: Power on(SerialHandler)")
    time.sleep(1)
    # battery.set_output('on')

    print("step 3: Send CH{} request ON (CanoeSync)".format(ch_x))

    send_req_channel(channel_info_dict, get_derating_req_value(ch_fun)['req'])
    time.sleep(1)  # Wait for lighting on and KV_AMP init

    print("step 4: Read current(SerialHandler)")
    ch_current = read_curr_vol.read_current(ch_x)
    time.sleep(1)

    # Send request off
    send_req_channel(channel_info_dict, 0)
    return ch_current


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


def map_ch_to_addr(ch_x):
    chx_analog_input = dataset.get_bin_info_by_channel(ch_x)['ch_analog_input']
    return int(chx_analog_input.split()[-1])


def check_result_if_match_requirement(expect_result, actual_result, margin):
    if expect_result < 200:
        if abs((expect_result - actual_result) / expect_result) <= margin or abs(expect_result - actual_result) < 25:
            return True
        else:
            return False
    else:
        if abs((expect_result - actual_result) / expect_result) <= margin:
            return True
        else:
            return False


def get_tc_data():
    return yaml_case.get_tc_data()['bin_test_case']


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


def send_req_channel(fun_info_dict: dict, req: int):
    """
    Distinguish between Pixel LB and Pixel HB
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

    if fun_info_dict['function'] in ['Pixel', 'Foreground_LB']:
        if req == 0:
            battery_req = 'off'
        else:
            battery_req = 'on'
        battery_KL31.set_output(battery_req)


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

# set_all_function_no_ntc_derating()
# expect_result = BINTest_expect_result(2, 2)
# actual_result = BINTest_step(2, 2)
# print(expect_result,actual_result)
