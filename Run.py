"""
Run.py is the entry file for the entire program.
Please select the test case file to be executed from test_case/tc_xxx.py.

@Author: Siwei.Lu
@Update: Yanjiao.Li
@Date: 2022.12.01
"""

import pytest
import time
from Core import global_variables_for_test_report, read_test_info


if __name__ == '__main__':
    global_variables_for_test_report.information(tester=read_test_info.get_test_info('tester'),
                                                 report_title=read_test_info.get_test_info('report_title'),
                                                 project=read_test_info.get_test_info('project'),
                                                 sample=read_test_info.get_test_info('sample'),
                                                 variant=read_test_info.get_test_info('variant'),
                                                 bootloader=read_test_info.get_test_info('bootloader'),
                                                 HW=read_test_info.get_test_info('HW'),
                                                 SW=read_test_info.get_test_info('SW'),
                                                 tag=read_test_info.get_test_info('tag'),
                                                 dataset=read_test_info.get_test_info('dataset'))

    time = time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime(time.time()))

    pytest.main(['-v',
                 '--html=./test_result/test_report/{}_{}_{}_{}.html'.format(global_variables_for_test_report.g_project,
                                                                            global_variables_for_test_report.g_variant,
                                                                            global_variables_for_test_report.g_report_title,
                                                                            time),
                 read_test_info.get_test_info('testcase_path'),
                 '--self-contained-html',
                 '--css=test_fixture/test_configuration/report.css'])

#  todo:pytruthtable, REST API, statemachine

