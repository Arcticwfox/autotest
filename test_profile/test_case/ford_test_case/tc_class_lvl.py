"""
Desc: This file is to verify the class level
Note: LB Power = 13V, LB CAN signal = NotLow(0x01)

@Author: Siwei.Lu
@Date: 2022.11.27
"""
import os

import pytest

from Core import global_variables_for_test_report
from Core.project.ford import parameter_def
from test_fixture.test_interface.ford_test_interface import classlvl_test_interface as class_lvl_test
from test_fixture.test_interface.ford_test_interface import precondition_test_interface as precondition


@pytest.fixture(scope="module", autouse=True)
def self_test_for_tc_dbl():
    try:
        precondition.check_canoe_connection()
        precondition.check_battery_connection()
        precondition.check_ecu_communication()
    except BaseException as err:
        precondition.logger.error("Self test error! \n{}".format(err))
        os._exit(0)
    finally:
        precondition.logger.info("Self test ended")
        precondition.prepare_for_test()


class TestClassLvl:
    @pytest.fixture(scope='module', autouse=False, params=class_lvl_test.get_tc_data('class_lvl_test_case'))
    def class_tc_data(self, request):
        return request.param

    def test_class(self, class_tc_data):
        """
        This test case is to verify the pixel/FLB intensity in different class level.
        """
        global_variables_for_test_report.g_testScriptID = class_tc_data['testCaseID']
        global_variables_for_test_report.g_data_measurement = 0
        global_variables_for_test_report.g_testcaseID = class_tc_data['toCoverID']

        class_lvl_req = class_tc_data['class_lvl_req']
        hb_request = class_tc_data['hb_request']

        ch_pixel, pixel_int = class_lvl_test.ClassTest(class_lvl_req, hb_request)
        pixel_did_result = class_lvl_test.read_matrix_ch_did(ch_pixel)

        ch_flb, flb_int = class_lvl_test.FLBIntensityTest(class_lvl_req, hb_request)
        flb_did_result = class_lvl_test.read_static_ch_did(ch_flb)

        global_variables_for_test_report.g_actually = str(pixel_did_result) + str(flb_did_result)
        global_variables_for_test_report.g_expected = str(pixel_int) + str(flb_int)

        assert (pixel_did_result == pixel_int) and (flb_did_result == flb_int)


@pytest.mark.skip
class TestClassChange:
    @pytest.fixture(scope='module', autouse=False, params=class_lvl_test.get_tc_data('class_change_test_case'))
    def class_change_tc_data(self, request):
        return request.param

    def test_class_change(self, class_change_tc_data):
        """
        This test case is to verify the pixel/FLB intensity when class level change.
        """
        global_variables_for_test_report.g_testCaseID = class_change_tc_data['testCaseID']
        global_variables_for_test_report.g_data_measurement = 0
        global_variables_for_test_report.g_toCover = class_change_tc_data['toCoverID']

        class_lvl1 = class_change_tc_data['class_lvl_current_req']
        class_lvl2 = class_change_tc_data['class_lvl_target_req']

        ch_x, pixel_int = class_lvl_test.ClassChangeTest(parameter_def.ClassLvl_Def['Class{}'.format(class_lvl1)].value,
                                                         parameter_def.ClassLvl_Def['Class{}'.format(class_lvl2)].value,
                                                         0)
        pixel_did_result = class_lvl_test.read_matrix_ch_did(ch_x)

        global_variables_for_test_report.g_actually = str(pixel_did_result)
        global_variables_for_test_report.g_expected = str(pixel_int)

        assert pixel_did_result == pixel_int


@pytest.mark.skip
class TestTrafficChange:
    def test_traffic_change_class(self):
        """
        This test case is to verify the traffic style change.
        """
        global_variables_for_test_report.g_testCaseID = "systss-8034"
        global_variables_for_test_report.g_data_measurement = 0
        global_variables_for_test_report.g_toCover = "systs-8034"

        ch_x, dbl_result = class_lvl_test.TrafficChangeTest(Traffic_Def.LeftHand.value, Traffic_Def.RightHand.value,
                                                            ClassLvl_Def.ClassC.value, 0)
        did_result = class_lvl_test.read_matrix_ch_did(ch_x)

        assert did_result == dbl_result
