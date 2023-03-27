"""
Desc: This file is to verify the sml function.

@Author: Yujie.shi
@Date: 2023.01.12
"""

import os
import time

import pytest
import pytest_check

from test_fixture.test_interface.ford_test_interface import sml_test_interface as sml_test
from test_fixture.test_interface.ford_test_interface import precondition_test_interface as precondition
from Core import global_variables_for_test_report
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import can_msg, canoe_app
from Core.project.ford import security_access,msg_sig_env_def


@pytest.fixture(scope="module", autouse=True)
def self_test_for_tc_sml():
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
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SwitchOnOff.value, 0x00)
        time.sleep(1)
        security_access.ford_security_access_03(can_msg, canoe_app, True)
        canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SwitchOnOff.value, 0x01)


class Testsml:
    @pytest.fixture(scope='module', autouse=False, params=sml_test.get_tc_data('sml_test_case'))
    def sml_tc_data(self, request):
        return request.param

    def test_sml(self, sml_tc_data):
        """
        This test case is to verify the sml function.
        """
        global_variables_for_test_report.g_testScriptID = sml_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = sml_tc_data['toCoverID']

        sml_current = sml_tc_data['current']
        sml_num = sml_tc_data['num']
        sml_vol = sml_tc_data['vol']
        sml_hs2_status = sml_tc_data['hs2_status']
        sml_req = sml_tc_data['sml_req']

        margin = 0.08

        actual_result, sm_hss2_status, sm_hss2_current = sml_test.sml_test_step(sml_current, sml_num, sml_vol,
                                                                                sml_hs2_status, sml_req)
        expect_result = sml_test.sml_expect()

        global_variables_for_test_report.g_actually = str(actual_result)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.is_true(sml_test.check_result_if_match_requirement(expect_result, actual_result, margin))

    @pytest.fixture(scope='module', autouse=False, params=sml_test.get_tc_data('sml_hss2_test_case'))
    def sml_hss2_tc_data(self, request):
        return request.param

    def test_sml_hss2(self, sml_hss2_tc_data):
        """
        This test case is to verify the sml hss2 function.
        """
        global_variables_for_test_report.g_testScriptID = sml_hss2_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = sml_hss2_tc_data['toCoverID']

        sml_current = sml_hss2_tc_data['current']
        sml_num = sml_hss2_tc_data['num']
        sml_vol = sml_hss2_tc_data['vol']
        sml_hs2_status = sml_hss2_tc_data['hs2_status']
        sml_req = sml_hss2_tc_data['sml_req']

        hss2_current, actual_sml_hss2_status, sm_hss2_current = sml_test.sml_test_step(sml_current, sml_num, sml_vol,
                                                                                 sml_hs2_status, sml_req)
        expect_result = sml_test.sml_hss2_expect()

        global_variables_for_test_report.g_actually = str(actual_sml_hss2_status)
        global_variables_for_test_report.g_expected = str(expect_result)

        pytest_check.equal(actual_sml_hss2_status, expect_result)
