"""
conftest.py：
1、可以跨.py文件调用，有多个.py文件调用时，可让conftest.py只调用了一次fixture，或调用多次fixture
2、conftest.py与运行的用例要在同一个pakage下，并且有__init__.py文件
3、不需要import导入 conftest.py，pytest用例会自动识别该文件，放到项目的根目录下就可以全局目录调用了，
   如果放到某个package下，那就在该package内有效，可有多个conftest.py
4、conftest.py配置脚本名称是固定的，不能改名称
5、conftest.py文件不能被其他文件导入
6、所有同目录测试文件运行前都会执行conftest.py文件

This file ’conftest.py‘ defines the framework for pytest-html reports.
The name of 'conftest.py' cannot be modified!!!

@Author: Yanjiao.Li
@Date: 2022.12.13
"""

from py.xml import html
import pytest  # pytest是Python的单元测试框架
from Core import global_variables_for_test_report  # global_variables
# from pytest_html import extras  # pytest插件生成一个HTML测试报告


# def test_extra(extra):
#     extra.append(extras.text("some string"))


def pytest_html_report_title(report):
    """ 测试报告的标题!
    建议每次都修改一下测试的标题,与产品对应
    """
    if global_variables_for_test_report.g_report_title:
        report.title = global_variables_for_test_report.g_report_title
    else:
        report.title = "project title is undefined!"


def pytest_html_results_table_header(cells):
    """修改测试报告的模板!
    表文件的头
    """
    cells.insert(0, html.th('Test Script ID'))
    cells.insert(1, html.th('Test Case ID'))
    cells.insert(2, html.th('Description'))  # insert()函数，用于将指定对象插入列表的指定位置
    cells.insert(4, html.th('Expected Result'))
    cells.insert(5, html.th('Actually Result'))
    cells.pop(-1)  # pop()方法，用于删除列表中的最后一个元素
    # cells.pop(-2)  # pop()方法，用于删除列表中的倒数第2个元素


def pytest_html_results_table_row(report, cells):
    """修改测试报告的模板!
    表文件的主体
    """
    cells.insert(0, html.td(report.TestScriptID))
    cells.insert(1, html.td(report.TestcaseID))
    cells.insert(2, html.td(report.description))
    cells.insert(4, html.td(report.ExpectedResult))
    cells.insert(5, html.th(report.ActuallyResult))
    cells.pop(-1)  # pop()方法，用于删除列表中的最后一个元素
    # cells.pop(-2)  # pop()方法，用于删除列表中的倒数第2个元素


def pytest_html_results_summary(prefix):
    # Summary部分在此设置
    prefix.extend([html.p("Department: ", global_variables_for_test_report.g_department)])
    prefix.extend([html.p("Tester: ", global_variables_for_test_report.g_tester)])
    prefix.extend([html.p("Time: ", global_variables_for_test_report.g_time)])


def pytest_configure(config):  # 修改Environment展示信息
    # 添加项目名称、测试版本信息等
    # 条目排布是按首字母顺序！
    config._metadata["TestComputer_IP"] = global_variables_for_test_report.g_computer_ip
    config._metadata["Project"] = global_variables_for_test_report.g_project
    config._metadata["Sample Phase"] = global_variables_for_test_report.g_sample
    config._metadata["ECU Variant"] = global_variables_for_test_report.g_variant
    config._metadata["SW Version"] = global_variables_for_test_report.g_SW
    config._metadata["Tag Version"] = global_variables_for_test_report.g_tag
    config._metadata["HW Version"] = global_variables_for_test_report.g_HW
    config._metadata["Bootloader Version"] = global_variables_for_test_report.g_bootloader
    config._metadata["Dataset Version"] = global_variables_for_test_report.g_dataset
    # config._metadata.pop("JAVA_HOME")
    config._metadata.pop("Packages")
    config._metadata.pop("Platform")
    config._metadata.pop("Plugins")
    config._metadata.pop("Python")


# def pytest_html_results_table_html(report, data):
# """  如果用例执行通过，则不会展示log，会展示自己定义的输出   """
#     if report.passed:
#         del data[:]
#         data.append(html.div('这条用例通过啦~~~'))


@pytest.mark.hookwrapper
def pytest_runtest_makereport(item, call):
    """把函数的描述和输出结果输出到表格中!

    如果有docstring, 则打印到 Description中,
    如果测试到了实际结果,则打印到measurement中.
    """
    outcome = yield
    report = outcome.get_result()
    report.description = str(item.function.__doc__)
    report.title = report.nodeid.encode("unicode_escape").decode("utf-8")  # 再把编码改回来

    if (report.when == 'teardown') | (report.when == 'call'):
        # print(dir(item.function))
        ExpectedResult = global_variables_for_test_report.g_expected
        if ExpectedResult:
            report.ExpectedResult = ExpectedResult
        else:
            report.ExpectedResult = "None"
        ActuallyResult = global_variables_for_test_report.g_actually
        if ActuallyResult:
            report.ActuallyResult = ActuallyResult
        else:
            report.ActuallyResult = "None"
        TestcaseID = global_variables_for_test_report.g_testcaseID
        if TestcaseID:
            report.TestcaseID = TestcaseID
        else:
            report.TestcaseID = "None"
        TestScriptID = global_variables_for_test_report.g_testScriptID
        if TestScriptID:
            report.TestScriptID = TestScriptID
        else:
            report.TestScriptID = "None"

    elif report.when == 'setup':
        report.TestcaseID = "None"
        report.TestScriptID = "None"
        report.ExpectedResult = "None"
        report.ActuallyResult = "None"
