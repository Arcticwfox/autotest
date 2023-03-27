"""
Desc: This file is to verify the power derating function.

@Author: Yujie.shi
@Date: 2023.01.12
"""

import os
import pytest
import pytest_check

from test_fixture.test_interface.ford_test_interface import power_derating_test_interface as derating_test
from test_fixture.test_interface.ford_test_interface import precondition_test_interface as precondition
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import can_msg, canoe_app
from Core.project.ford import security_access
from Core import global_variables_for_test_report


@pytest.fixture(scope="module", autouse=True)
def self_test_for_tc_derating():
    try:
        precondition.check_canoe_connection()
        precondition.check_battery_connection()
        precondition.check_ecu_communication()
    except BaseException as err:
        precondition.logger.error("self test error! \n{}".format(err))
        os._exit(0)
    finally:
        precondition.logger.info("Self test ended")
        precondition.prepare_for_test()
        derating_test.set_all_function_no_ntc_derating()
        derating_test.set_all_function_bin(5)
        security_access.ford_security_access_03(can_msg, canoe_app, False)


class Test_start_stop_derating:
    @pytest.fixture(scope='module', autouse=False, params=derating_test.get_tc_data('start_stop_derating_test_case'))
    def start_stop_derating_tc_data(self, request):
        return request.param

    def test_start_stop_derating(self, start_stop_derating_tc_data):
        """
        This test case is to verify the start stop derating.
        """
        global_variables_for_test_report.g_testScriptID = start_stop_derating_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = start_stop_derating_tc_data['toCoverID']

        test_function = start_stop_derating_tc_data['function']
        set_vol = start_stop_derating_tc_data['voltage']
        margin = 0.08

        current_bef_derating, actual_result, function_cal = derating_test.set_start_stop_derating(test_function,
                                                                                                  set_vol)
        expect_result = derating_test.start_stop_expect_current(current_bef_derating, test_function)

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.is_true(derating_test.check_result_if_match_requirement(expect_result, actual_result, margin))


class Test_low_voltage_derating:
    @pytest.fixture(scope='module', autouse=False, params=derating_test.get_tc_data('low_voltage_derating_test_case'))
    def low_voltage_derating_tc_data(self, request):
        return request.param

    def test_low_voltage_derating(self, low_voltage_derating_tc_data):
        """
        This test case is to verify the low voltage derating.
        """
        global_variables_for_test_report.g_testScriptID = low_voltage_derating_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = low_voltage_derating_tc_data['toCoverID']

        test_function = low_voltage_derating_tc_data['function']
        set_vol = low_voltage_derating_tc_data['voltage']
        margin = 0.08

        current_bef_derating, actual_result, function_cal = derating_test.set_low_vol_derating(test_function,
                                                                                               set_vol)
        expect_result = derating_test.cal_expect_current_by_DID(current_bef_derating, test_function)

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.is_true(derating_test.check_result_if_match_requirement(expect_result, actual_result, margin))


class Test_low_voltage_animation_derating:
    @pytest.fixture(scope='module', autouse=False, params=derating_test.
                    get_tc_data('low_power_animation_derating_test_case'))
    def low_voltage_animation_derating_tc_data(self, request):
        return request.param

    def test_low_voltage_animation_derating(self, low_voltage_animation_derating_tc_data):
        """
        This test case is to verify the low voltage animation derating.
        """
        global_variables_for_test_report.g_testScriptID = low_voltage_animation_derating_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = low_voltage_animation_derating_tc_data['toCoverID']

        test_function = low_voltage_animation_derating_tc_data['function']
        set_vol = low_voltage_animation_derating_tc_data['voltage']
        margin = 0.08

        current_bef_derating, actual_result, function_cal = derating_test.set_low_vol_animation_derating(
            test_function, set_vol)
        expect_result = derating_test.animation_expect_result(current_bef_derating, test_function)

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.is_true(derating_test.check_result_if_match_requirement(expect_result, actual_result, margin))


class Test_total_power_derating:
    @pytest.fixture(scope='module', autouse=False, params=derating_test.
                    get_tc_data('total_power_derating_test_case'))
    def total_power_derating_tc_data(self, request):
        return request.param

    def test_total_power_derating(self, total_power_derating_tc_data):
        """
        This test case is to verify the total power derating.
        """
        global_variables_for_test_report.g_testScriptID = total_power_derating_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = total_power_derating_tc_data['toCoverID']

        set_bin = total_power_derating_tc_data['bin']
        set_vol = total_power_derating_tc_data['voltage']
        main_power_status = total_power_derating_tc_data['main_power_status']

        actual_result = derating_test.set_total_power_derating(set_bin, set_vol, main_power_status)
        expect_result = derating_test.total_power_expect_result(main_power_status)

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.is_true(derating_test.check_total_power_result(expect_result, actual_result))


class Test_channel_power_derating:
    @pytest.fixture(scope='module', autouse=False, params=derating_test.
                    get_tc_data('channel_power_derating_test_case'))
    def channel_power_derating_tc_data(self, request):
        return request.param

    def test_channel_power_derating(self, channel_power_derating_tc_data):
        """
        This test case is to verify the channel power derating.
        """
        global_variables_for_test_report.g_testScriptID = channel_power_derating_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = channel_power_derating_tc_data['toCoverID']

        channel = channel_power_derating_tc_data['channel']
        expect_result = channel_power_derating_tc_data['expect_max_power']

        actual_result = derating_test.channel_derating_test_step(channel)

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.less_equal(actual_result, expect_result + 1.5)
