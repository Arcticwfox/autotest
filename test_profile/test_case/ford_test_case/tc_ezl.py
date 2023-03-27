"""
Desc: This file is to verify the EZL function.

@Author: Li.wang
@Date: 2023..16
"""

import os
import pytest
import time
import pytest_check

from test_fixture.test_interface.ford_test_interface import ezl_interface as ezl_test
from test_fixture.test_interface.ford_test_interface import precondition_test_interface as precondition
from Core.project.ford import security_access
from Core import global_variables_for_test_report


@pytest.fixture(scope="module", autouse=True)
def self_test_for_tc_turn_indicator():
    try:
        precondition.check_canoe_connection()
        # precondition.check_battery_connection()
        precondition.check_ecu_communication()
    except BaseException as err:
        precondition.logger.error("self test error! \n{}".format(err))
        os._exit(0)
    finally:
        precondition.logger.info("Self test ended")
        security_access.ford_security_access_03(precondition.can_msg, precondition.canoe_app)
        precondition.prepare_for_test()
        time.sleep(3)


class TestEZL:
    @pytest.fixture(scope='module', autouse=False, params=ezl_test.get_tc_data('ezl_request_test_case'))
    def ezl_tc_data(self, request):
        return request.param

    def test_ezl_request(self, ezl_tc_data):
        """
        This test case is to verify the EZL funtion.
        """

        global_variables_for_test_report.g_testScriptID = ezl_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = ezl_tc_data['toCoverID']

        ezl_request = ezl_tc_data['ezl_request']
        did_para = ezl_tc_data['did_para']

        ezl_expected_int, ezl_actual_int = ezl_test.ezl_request_test_step(ezl_request, did_para)

        global_variables_for_test_report.g_actually = str(ezl_actual_int)
        global_variables_for_test_report.g_expected = str(ezl_expected_int)
        # print('ezl_actual_int = ', ezl_actual_int)
        # print('ezl_expected_int = ', ezl_expected_int)
        pytest_check.equal(ezl_actual_int, ezl_expected_int)
        # assert ezl_actual_int == ezl_expected_int

    @pytest.fixture(scope='module', autouse=False, params=ezl_test.get_tc_data('ezl_channel_cfg_test_case'))
    def ezl_tc_data(self, request):
        return request.param

    def test_ezl_channel_cfg(self, ezl_tc_data):
        """
        This test case is to verify the EZL funtion.
        """

        global_variables_for_test_report.g_testScriptID = ezl_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = ezl_tc_data['toCoverID']

        ezl_request = ezl_tc_data['ezl_request']
        did_para = ezl_tc_data['did_para']

        ezl_expected_int, ezl_actual_int = ezl_test.ezl_request_test_step(ezl_request, did_para)

        global_variables_for_test_report.g_actually = str(ezl_actual_int)
        global_variables_for_test_report.g_expected = str(ezl_expected_int)
        # print('ezl_actual_int = ', ezl_actual_int)
        # print('ezl_expected_int = ', ezl_expected_int)
        pytest_check.equal(ezl_actual_int, ezl_expected_int)
        # assert ezl_actual_int == ezl_expected_int

    @pytest.fixture(scope='module', autouse=False, params=ezl_test.get_tc_data('ezl_po_interrupt_ezl_test_case'))
    def ezl_tc_data(self, request):
        return request.param

    def test_po_interrupt_ezl(self, ezl_tc_data):
        """
        This test case is to verify the po interrupt EZL funtion.
        """

        global_variables_for_test_report.g_testScriptID = ezl_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = ezl_tc_data['toCoverID']

        ezl_request = ezl_tc_data['ezl_request']
        did_para = ezl_tc_data['did_para']
        drl_x = ezl_tc_data['drl_x']

        ezl_expected_int, ezl_actual_int = ezl_test.po_interrupt_ezl_step(ezl_request, did_para, drl_x)

        global_variables_for_test_report.g_actually = str(ezl_actual_int)
        global_variables_for_test_report.g_expected = str(ezl_expected_int)
        # print('ezl_actual_int = ', ezl_actual_int)
        # print('ezl_expected_int = ', ezl_expected_int)
        pytest_check.equal(ezl_actual_int, ezl_expected_int)
        # assert ezl_actual_int == ezl_expected_int

    @pytest.fixture(scope='module', autouse=False, params=ezl_test.get_tc_data('ezl_iocontrol_test_case'))
    def ezl_tc_data(self, request):
        return request.param

    def test_iocontrol_ezl(self, ezl_tc_data):
        """
        This test case is to verify the po interrupt EZL funtion.
        """

        global_variables_for_test_report.g_testScriptID = ezl_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = ezl_tc_data['toCoverID']

        ezl_request = ezl_tc_data['ezl_request']
        fun = ezl_tc_data['fun']
        iocontrol_request = ezl_tc_data['iocontrol_request']

        ezl_expected_int, ezl_actual_int = ezl_test.iocontrol_ezl_step(ezl_request, fun, iocontrol_request)

        global_variables_for_test_report.g_actually = str(ezl_actual_int)
        global_variables_for_test_report.g_expected = str(ezl_expected_int)
        # print('ezl_actual_int = ', ezl_actual_int)
        # print('ezl_expected_int = ', ezl_expected_int)
        pytest_check.equal(ezl_actual_int, ezl_expected_int)
        # assert ezl_actual_int == ezl_expected_int


