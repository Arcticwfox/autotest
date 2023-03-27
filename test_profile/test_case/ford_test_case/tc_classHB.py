"""
Desc: This file is to verify the class HB
Note: LB Power = 13V, LB CAN signal = NotLow(0x01)

@Author: Siwei.Lu
@Date: 2022.11.27
"""

import time

from Core.project.ford.calc_process import *

Dataset = CalHandler("D:/001_Ford/00_Dataset/Dataset_12B/AB/A070/FaultInject_LDM12B_AB_DatasetVB009.xlsm")
# Dataset = Dataset(global_variables_for_test_report.g_dataset_path)

# 默认ECU为左节点
Dataset.side = "Left ECU"


#  *******************************  Test Function  *******************************
def ClassHBTest(ClassLvl, HBReq):
    ch_int = []
    pre_test()
    # step 1: Send CAN request : DBL/ClassLvl/HB
    app.set_EnvVar(ENV_name.LB_ClassLvl_Left.value, ClassLvl)
    app.set_EnvVar(ENV_name.LB_ClassLvl_Right.value, ClassLvl)
    app.set_EnvVar(ENV_name.HB_Req.value, HBReq)
    time.sleep(0.5)
    # Step 2: Calculate the actual intensity
    Dataset.get_dbl_move_ang()
    DBL_result = Dataset.get_pixel_ch_int_dict()
    for value in DBL_result.values():
        for i in range(12):
            ch_int.append(value[i + 1])

    return DBL_result.keys(), ch_int
