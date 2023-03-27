"""
This file defines specific test cases according to system test case.

@Author: Siwei.Lu
@Date: 2022.11.26
"""
import os
import pytest
import pytest_check

from Core import global_variables_for_test_report
from test_fixture.test_interface.ford_test_interface import precondition_test_interface as precondition, \
    bin_test_interface as bin_test


@pytest.fixture(scope="module", autouse=True)
def self_test_for_tc_bin():
    try:
        precondition.check_battery_connection()
        precondition.check_canoe_connection()
        precondition.check_bin_set_module()
        precondition.check_ecu_communication()
        precondition.check_read_current_voltage_module_status()
    except BaseException as err:
        precondition.logger.error("self test error! \n{}".format(err))
        os._exit(0)
    finally:
        precondition.logger.info("Self test ended")
        precondition.prepare_for_test()
        bin_test.set_all_function_no_ntc_derating()


@pytest.fixture(scope="function", autouse=True)
def precondition_for_each_test_case():
    """
    Precondition: Set CANoe Request. Set input voltage and current. Power off.
    """
    print("Set precondition: Power off")
    bin_test.battery.set_output('off')


#     todo: NTC降额25°


class TestBIN:
    @pytest.fixture(scope='module', autouse=False, params=bin_test.get_tc_data())
    def tc_data(self, request):
        return request.param

    def test_ch_bin(self, tc_data):
        """
        This test case is to verify the bin current.
        """
        global_variables_for_test_report.g_testScriptID = tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = tc_data['toCoverID']

        # 误差：8% ~ 10%
        margin = 0.1
        ch_x = tc_data['ch']
        bin_x = tc_data['bin']

        expect_result = bin_test.BINTest_expect_result(ch_x, bin_x)
        actual_result = bin_test.BINTest_step(ch_x, bin_x)

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        # test_result = bin_test.check_result_if_match_requirement(expect_result, actual_result, margin)
        pytest_check.almost_equal(expect_result, actual_result, margin)
        # assert test_result
