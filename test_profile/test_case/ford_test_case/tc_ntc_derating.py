"""
Desc: This file is to verify the NTC derating function.

@Author: Yujie.shi
@Date: 2023.02.21
"""
import os
import pytest
import pytest_check

from test_fixture.test_interface.ford_test_interface import ntc_derating_test_interface as ntc_test
from test_fixture.test_interface.ford_test_interface import precondition_test_interface as precondition
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

"""
Test analog/ TI matrix chip/ NXP matrix chip NTC derating
When test analog NTC derating:
        the max bin_set channel is 8, so the analog channel should configure in [1,2,3,4,5,6,7,8] in dataset
        
When test TI/NXP matrix chip NTC derating:
        BIN_SET channel 7 to set bin level, all function BIN source should configure the same matrix chip !
        BIN_SET channel 8 to set NTC level, all function NTC source should configure the same matrix chip !

        The BIN level of test function will be set BIN5!
        So the BIN5 current should configure > 500mA!
        
TD 1 mean: the BD derating < BD1
TD 2 mean: the BD derating is between BD1 and BD2
.......
TD 6 mean: the BD derating is between BD5 and BD MAX
TD 7 mean: the BD derating > BD MAX

"""


class Test_analog_ntc_derating:
    @pytest.fixture(scope='module', autouse=False, params=ntc_test.get_tc_data('analog_ntc_derating_test_case'))
    def analog_ntc_derating_tc_data(self, request):
        return request.param

    def test_analog_ntc_derating(self, analog_ntc_derating_tc_data):
        """
        This test case is to verify the ntc derating.
        """
        global_variables_for_test_report.g_testScriptID = analog_ntc_derating_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = analog_ntc_derating_tc_data['toCoverID']

        test_function = analog_ntc_derating_tc_data['function']
        test_TD_value = analog_ntc_derating_tc_data['TD_value']
        margin = 0.08

        current_bef_derating, actual_result, derating_value, function_cal = \
            ntc_test.ntc_test_step(test_function, test_TD_value)
        expect_result = ntc_test.expect_current(current_bef_derating, derating_value, function_cal)

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.is_true(ntc_test.check_result_if_match_requirement(expect_result, actual_result, margin))


class Test_TI_matrix_chip_ntc_derating:
    @pytest.fixture(scope='module', autouse=False, params=ntc_test.get_tc_data('TI_ntc_derating_test_case'))
    def TI_ntc_derating_tc_data(self, request):
        return request.param

    def test_TI_matrix_ntc_derating(self, TI_ntc_derating_tc_data):
        """
        This test case is to verify the TI matrix ntc derating.
        """
        global_variables_for_test_report.g_testScriptID = TI_ntc_derating_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = TI_ntc_derating_tc_data['toCoverID']

        test_function = TI_ntc_derating_tc_data['function']
        test_TD_value = TI_ntc_derating_tc_data['TD_value']
        margin = 0.08

        current_bef_derating, actual_result, ch_list, function_cal = \
            ntc_test.TI_matrix_chip_NTC_test_step(test_function, test_TD_value)
        expect_result = ntc_test.matrix_expect_current(ch_list, current_bef_derating, function_cal)

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.is_true(ntc_test.check_result_if_match_requirement(expect_result, actual_result, margin))


class Test_NXP_matrix_chip_ntc_derating:
    @pytest.fixture(scope='module', autouse=False, params=ntc_test.get_tc_data('NXP_ntc_derating_test_case'))
    def NXP_ntc_derating_tc_data(self, request):
        return request.param

    def test_NXP_matrix_ntc_derating(self, NXP_ntc_derating_tc_data):
        """
        This test case is to verify the NXP matrix ntc derating.
        """
        global_variables_for_test_report.g_testScriptID = NXP_ntc_derating_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = NXP_ntc_derating_tc_data['toCoverID']

        test_function = NXP_ntc_derating_tc_data['function']
        test_TD_value = NXP_ntc_derating_tc_data['TD_value']
        margin = 0.08

        current_bef_derating, actual_result, ch_list, function_cal = \
            ntc_test.NXP_matrix_chip_NTC_test_step(test_function, test_TD_value)
        expect_result = ntc_test.matrix_expect_current(ch_list, current_bef_derating, function_cal)

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.is_true(ntc_test.check_result_if_match_requirement(expect_result, actual_result, margin))
