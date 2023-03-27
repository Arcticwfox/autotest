"""
Desc: This file is to verify the DRL/PO function.

@Author: Siwei.Lu
@Date: 2022.12.12
"""

import os
import pytest

from test_fixture.test_interface.ford_test_interface import drl_test_interface as drl_test
from test_fixture.test_interface.ford_test_interface import precondition_test_interface as precondition
from Core import global_variables_for_test_report


@pytest.fixture(scope="module", autouse=True)
def self_test_for_tc_drl():
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


class TestDrlPo:
    @pytest.fixture(scope='module', autouse=False, params=drl_test.get_tc_data('drl_po_test_case'))
    def drl_po_tc_data(self, request):
        return request.param

    def test_drl_po(self, drl_po_tc_data):
        """
        This test case is to verify the DRL/PO intensity.
        """
        global_variables_for_test_report.g_testScriptID = drl_po_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = drl_po_tc_data['toCoverID']

        drl_request = drl_po_tc_data['drl/po_request']
        drl_x = drl_po_tc_data['drl/po_x']

        drl_ch_info_dict, drl_expected_int = drl_test.drl_test_step(drl_request, drl_x)
        drl_actual_int = drl_test.send_did_to_read_ch_intensity(drl_ch_info_dict)

        global_variables_for_test_report.g_actually = str(drl_actual_int)
        global_variables_for_test_report.g_expected = str(drl_expected_int)

        assert drl_expected_int == drl_actual_int

    @pytest.fixture(scope='module', autouse=False, params=drl_test.get_tc_data('po_with_ti_test_case'))
    def po_with_ti_tc_data(self, request):
        return request.param

    def test_po_with_ti(self, po_with_ti_tc_data):
        """
        This test case is to verify the PO with TI intensity.
        """
        global_variables_for_test_report.g_testScriptID = po_with_ti_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = po_with_ti_tc_data['toCoverID']

        ti_request = po_with_ti_tc_data['ti_request']
        drl_x = po_with_ti_tc_data['drl/po_x']

        drl_ch_info_dict, drl_expected_int = drl_test.po_with_ti_test_step(drl_x, ti_request)
        drl_actual_int = drl_test.send_did_to_read_ch_intensity(drl_ch_info_dict)

        global_variables_for_test_report.g_actually = str(drl_actual_int)
        global_variables_for_test_report.g_expected = str(drl_expected_int)

        assert drl_expected_int == drl_actual_int


class TestAux:
    @pytest.fixture(scope='module', autouse=False, params=drl_test.get_tc_data('aux_test_case'))
    def aux_tc_data(self, request):
        return request.param

    def test_drl_po(self, aux_tc_data):
        """
        This test case is to verify the AUX intensity.
        """
        global_variables_for_test_report.g_testScriptID = aux_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = aux_tc_data['toCoverID']

        drl_request = aux_tc_data['drl_request']
        aux_x = aux_tc_data['aux_x']

        aux_ch_info_dict, aux_expected_int = drl_test.aux_test_step(drl_request, aux_x)
        aux_actual_int = drl_test.send_did_to_read_ch_intensity(aux_ch_info_dict)

        global_variables_for_test_report.g_actually = str(aux_actual_int)
        global_variables_for_test_report.g_expected = str(aux_expected_int)

        assert aux_expected_int == aux_actual_int
