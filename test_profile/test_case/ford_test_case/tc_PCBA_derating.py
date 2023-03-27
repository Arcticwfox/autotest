"""
Desc: This file is to verify the PCBA derating function.

@Author: Yujie.shi
@Date: 2023.03.07
"""

import os
import pytest
import pytest_check

from test_fixture.test_interface.ford_test_interface import PCBA_derating_interface as pcba_test
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


class Test_start_stop_derating:
    @pytest.fixture(scope='module', autouse=False, params=pcba_test.get_tc_data('pcba_derating_test_case'))
    def pcba_derating_tc_data(self, request):
        return request.param

    def test_PCBA_derating(self, pcba_derating_tc_data):
        """
        This test case is to verify the PCBA derating.
        """
        global_variables_for_test_report.g_testScriptID = pcba_derating_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = pcba_derating_tc_data['toCoverID']

        test_function = pcba_derating_tc_data['function']
        PCBA_tem = pcba_derating_tc_data['PCBA_tem']
        margin = 0.08

        current_bef_derating, actual_result, function_cal = pcba_test.PCBA_derating_test_step(test_function, PCBA_tem)
        expect_result = pcba_test.cal_expect_result(function_cal, current_bef_derating)

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.is_true(pcba_test.check_result_if_match_requirement(expect_result, actual_result, margin))
