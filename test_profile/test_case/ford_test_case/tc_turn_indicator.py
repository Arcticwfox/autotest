"""
Desc: This file is to verify the TI function.

@Author: Li.wang
@Date: 2023.1.12
"""

import os
import pytest
import time
import pytest_check

from test_fixture.test_interface.ford_test_interface import turn_indicator_test_interface as ti_test
from test_fixture.test_interface.ford_test_interface import precondition_test_interface as precondition
from Core import global_variables_for_test_report


@pytest.fixture(scope="module", autouse=True)
def self_test_for_tc_turn_indicator():
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


class TestTurnIndicator:
    @pytest.fixture(scope='module', autouse=False, params=ti_test.get_tc_data('turn_indicator_test_case'))
    def ti_tc_data(self, request):
        return request.param

    def test_turn_indicator(self, ti_tc_data):
        """
        This test case is to verify the TI intensity.
        """
        global_variables_for_test_report.g_testScriptID = ti_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = ti_tc_data['toCoverID']

        ti_request = ti_tc_data['ti_request']
        ti_type = ti_tc_data['ti_type']
        drl_x = ti_tc_data['drl_x']

        ti_expected_int, ti_actual_int = ti_test.turn_indicator_step(ti_request, ti_type, drl_x)

        global_variables_for_test_report.g_actually = str(ti_actual_int)
        global_variables_for_test_report.g_expected = str(ti_expected_int)
        pytest_check.equal(ti_expected_int, ti_actual_int)

    # ti as po function need to change dataset and tc_data when test different configuration

    @pytest.fixture(scope='module', autouse=False, params=ti_test.get_tc_data('ti_with_po1234_test_case'))
    def po_with_ti_tc_data(self, request):
        return request.param

    def test_ti_as_po(self, po_with_ti_tc_data):
        """
        This test case is to verify the TI as po intensity.
        """
        global_variables_for_test_report.g_testScriptID = po_with_ti_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = po_with_ti_tc_data['toCoverID']

        ti_request = po_with_ti_tc_data['ti_request']
        ti_type = po_with_ti_tc_data['ti_type']
        drl_x = po_with_ti_tc_data['drl_x']
        drl_request = po_with_ti_tc_data['drl_request']

        ti_expected_int, ti_actual_int = ti_test.ti_with_po_step(ti_request, ti_type, drl_x, drl_request)

        global_variables_for_test_report.g_actually = str(ti_actual_int)
        global_variables_for_test_report.g_expected = str(ti_expected_int)

        pytest_check.equal(ti_expected_int, ti_actual_int)
        # assert ti_expected_int == ti_actual_int

    @pytest.fixture(scope='module', autouse=False, params=ti_test.get_tc_data('ti_with_animation_test_case'))
    def ti_with_animation_tc_data(self, request):
        return request.param

    def test_ti_with_animation(self, ti_with_animation_tc_data):
        """
        This test case is to verify the TI in animation intensity.
        """
        global_variables_for_test_report.g_testScriptID = ti_with_animation_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = ti_with_animation_tc_data['toCoverID']

        ti_request = ti_with_animation_tc_data['ti_request']
        ti_type = ti_with_animation_tc_data['ti_type']
        drl_x = ti_with_animation_tc_data['drl_x']
        animation_request = ti_with_animation_tc_data['animation_request']

        ti_actual_int, ti_expected_int = ti_test.ti_with_animation_step(ti_request, ti_type, drl_x,
                                                                                            animation_request)

        global_variables_for_test_report.g_actually = str(ti_actual_int)
        global_variables_for_test_report.g_expected = str(ti_expected_int)

        pytest_check.equal(ti_expected_int, ti_actual_int)
        # assert ti_expected_int == ti_actual_int
