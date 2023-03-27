"""
Desc: This file is to verify the DBL move
Note: LB Power = 13V, LB CAN signal = NotLow(0x01)
      Pixel system is configured

@Author: Siwei.Lu
@Date: 2022.12.7
"""
import os
import pytest

from test_fixture.test_interface.ford_test_interface import dbl_test_interface as dbl_test
from test_fixture.test_interface.ford_test_interface import precondition_test_interface as precondition
from Core import global_variables_for_test_report


@pytest.fixture(scope="module", autouse=True)
def self_test_for_tc_dbl():
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


class TestDBL:
    @pytest.fixture(scope='module', autouse=False, params=dbl_test.get_tc_data())
    def tc_data(self, request):
        return request.param

    def test_dbl_LB_class(self, tc_data):
        global_variables_for_test_report.g_testCaseID = tc_data['testCaseID']
        global_variables_for_test_report.g_data_measurement = 0
        global_variables_for_test_report.g_toCover = tc_data['toCoverID']

        dbl_move_ang = tc_data['dbl_move_ang']
        class_lvl_req = tc_data['class_lvl_req']
        hb_request = tc_data['hb_request']

        ch_x, dbl_result = dbl_test.DBLTest(dbl_move_ang, class_lvl_req, hb_request)
        did_result = dbl_test.read_ch_did(ch_x)

        global_variables_for_test_report.g_actually = str(did_result)
        global_variables_for_test_report.g_expected = str(dbl_result)

        assert did_result == dbl_result

    @pytest.mark.skip
    def test_dbl_LB_class0_r4(self):
        ch_x, dbl_result = dbl_test.DBLTest(-4, 0, 0)
        did_result = dbl_test.read_ch_did(ch_x)

        assert did_result == dbl_result


