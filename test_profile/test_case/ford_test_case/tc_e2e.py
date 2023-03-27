"""
Desc: This file is to verify the E2E function.

@Author: Li.wang
@Date: 2023.2.21
"""

import os
import pytest
import time
import pytest_check

from test_fixture.test_interface.ford_test_interface import e2e_interface as e2e_test
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
        # security_access.ford_security_access_03(precondition.can_msg, precondition.canoe_app)
        precondition.prepare_for_test()
        time.sleep(3)


class TestE2E:
    # @pytest.fixture(scope='module', autouse=False, params=e2e_test.get_tc_data('e2e_test_case'))
    # def e2e_tc_data(self, request):
    #     return request.param
    #
    # def test_e2e_config(self, e2e_tc_data):
    #     """
    #     This test case is to verify the E2E funtion.
    #     """
    #
    #     global_variables_for_test_report.g_testScriptID = e2e_tc_data['testCaseID']
    #     global_variables_for_test_report.g_testcaseID = e2e_tc_data['toCoverID']
    #     e2e_error = e2e_tc_data['e2e_error']
    #     e2e_type = e2e_tc_data['e2e_type']
    #
    #     dtc_test, dtc_expect = e2e_test.e2e_test_step(e2e_error, e2e_type)
    #     # print(dtc_test)
    #     # print(dtc_expect)
    #     global_variables_for_test_report.g_actually = str(dtc_test)
    #     global_variables_for_test_report.g_expected = str(dtc_expect)
    #     # print('ezl_actual_int = ', ezl_actual_int)
    #     # print('ezl_expected_int = ', ezl_expected_int)
    #     pytest_check.equal(dtc_test, dtc_expect)

    @pytest.fixture(scope='module', autouse=False, params=e2e_test.get_tc_data('e2e_light_test_case'))
    def e2e_tc_data(self, request):
        return request.param

    def test_e2e_light_config(self, e2e_tc_data):
        """
        This test case is to verify the E2E funtion.
        """

        global_variables_for_test_report.g_testScriptID = e2e_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = e2e_tc_data['toCoverID']
        e2e_error = e2e_tc_data['e2e_error']
        e2e_type = e2e_tc_data['e2e_type']

        dtc_test, dtc_expect, ezl_actual_int, ezl_expect_int = e2e_test.e2e_light_test_step(e2e_error, e2e_type)
        # print(dtc_test)
        # print(dtc_expect)
        global_variables_for_test_report.g_actually = str(ezl_actual_int)
        global_variables_for_test_report.g_expected = str(ezl_expect_int)
        # print('ezl_actual_int = ', ezl_actual_int)
        # print('ezl_expected_int = ', ezl_expected_int)
        pytest_check.equal(dtc_test, dtc_expect)
        pytest_check.equal(ezl_actual_int, ezl_expect_int)
