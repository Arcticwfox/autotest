"""
This file is used to provide the interface of fault injection for the use of test cases.
The dataset path is defined in test_configuration/config.yaml.

@Author: Li.Wang
@Date: 2022.12.01
"""
from Core.project.ford.parameter_def import *
from test_fixture.test_interface.ford_test_interface.precondition_test_interface import canoe_app


def check_dtc(dtc):
    """
    @author:Li.Wang
    读取DTC并与造错的DTC进行比较
    空列表与未发现造错DTC返回值相同
    """
    dtc_list = canoe_app.send_diag_req(DiagRequest.read_dtc.value, "Status_mask", 9)  # 读DTC
    # print('dtc_list = ', dtc_list)
    if len(dtc_list) <= 3:  # 如果没有任何DTC，就返回[1]，方便后续判断结果
        return [1]
    else:
        dtc1 = dtc_list[3:]
        # print("dtc1 ", dtc1)
        for i in range(len(dtc1) // 4):  # 如果没有发现造错的DIC，返回长度为1的列表，如果发现了造错的DTC，返回该DTC
            dtc2 = dtc1[4 * i:4 * (i + 1)]
            # print("dtc2 ", dtc2)
            if dtc2[3] == 0x2f:
                dtc3 = dtc2[0:3]
                # print("dtc3", dtc3)
                if dtc == dtc3:
                    return dtc3
                else:
                    continue
        return [1]


def check_e2e_dtc(dtc):
    """
    @author:Li.Wang
    @attention: 仅适用与e2e功能测试使用！！！！！！！！
    """
    dtc_list = canoe_app.send_diag_req(DiagRequest.read_dtc.value, "Status_mask", 9)  # 读DTC
    # print('dtc_list = ', dtc_list)
    if len(dtc_list) <= 3:  # 如果没有任何DTC，就返回[1]，方便后续判断结果
        return [1]
    else:
        dtc1 = dtc_list[3:]
        # print("dtc1 ", dtc1)
        for i in range(len(dtc1) // 4):  # 如果没有发现造错的DIC，返回长度为1的列表，如果发现了造错的DTC，返回该DTC
            dtc2 = dtc1[4 * i:4 * (i + 1)]
            # print("dtc2 ", dtc2)
            if dtc2[3] == 0x2E:  # 检测搭配历史DTC存在
                dtc3 = dtc2[0:3]
                # print("dtc3", dtc3)
                if dtc == dtc3:
                    return dtc3
                else:
                    continue
        return [1]
