"""
Desc: This file is to verify the Bending function.

@Author: Yujie.shi
@Date: 2023.01.10
"""
import os
import pytest
import pytest_check

from test_fixture.test_interface.ford_test_interface import bending_test_interface as bending_test
from test_fixture.test_interface.ford_test_interface import precondition_test_interface as precondition
from Core import global_variables_for_test_report


@pytest.fixture(scope="module", autouse=True)
def self_test_for_tc_bending():
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


class TestBending:
    @pytest.fixture(scope='module', autouse=False, params=bending_test.get_tc_data('Static_Bending_test_case'))
    def static_bending_tc_data(self, request):
        return request.param

    def test_static_bending(self, static_bending_tc_data):
        """
        This test case is to verify the static Bending intensity.
        """
        global_variables_for_test_report.g_testScriptID = static_bending_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = static_bending_tc_data['toCoverID']

        bending_intensity = static_bending_tc_data['intensity']

        bending_ch_info_dict, bending_expected_int = bending_test.static_Bending_test_step(bending_intensity)
        bending_actual_int = bending_test.send_did_to_read_ch_intensity(bending_ch_info_dict)

        global_variables_for_test_report.g_actually = str(bending_actual_int)
        global_variables_for_test_report.g_expected = str(bending_expected_int)

        pytest_check.equal(bending_actual_int, bending_expected_int)

    @pytest.fixture(scope='module', autouse=False, params=bending_test.get_tc_data('Segment_Bending_test_case'))
    def segment_bending_tc_data(self, request):
        return request.param

    def test_segment_bending(self, segment_bending_tc_data):
        """
        This test case is to verify the segment Bending intensity.
        """
        global_variables_for_test_report.g_testScriptID = segment_bending_tc_data['testCaseID']
        global_variables_for_test_report.g_testcaseID = segment_bending_tc_data['toCoverID']

        bending_addr = segment_bending_tc_data['addr']
        bending_intensity = segment_bending_tc_data['intensity']

        bending_ch_info_dict, bending_expected_int_physical = bending_test.segment_Bending_test_step(bending_addr,
                                                                                                     bending_intensity)
        bending_expected_int_logical = bending_test.bending_expected_intensity_logical()
        bending_actual_intensity = bending_test.send_did_to_read_ch_intensity(bending_ch_info_dict)

        global_variables_for_test_report.g_actually = str(bending_actual_intensity)
        global_variables_for_test_report.g_expected = str(bending_expected_int_logical)

        pytest_check.equal(bending_actual_intensity, bending_expected_int_logical)
