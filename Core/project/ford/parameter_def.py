"""
This file defines the constant values.
Please update this file if the DBC or Dataset is updated.

@Author: Siwei.Lu
@Date: 2022.11.27

注意：更换项目时需要使用对应的UsedSheet
"""
from enum import Enum

# From Dataset


class UsedSheet(Enum):
    # 12B/12C
    dbl = "DBL"
    ghfb = "GFHB"
    pixel = "Pixel-System"
    ch_output = "CH-Output"
    bin_ntc = "Binning-NTC-Derating"
    ntc_ad = "NTC-AD"
    drl_ti = "DRL-TI-Fog-Aux-SBL"
    motor = "Leveling-Motor"
    animation = "Animation"
    development = "Development Data"
    basic = "Basic-Parameter"


# class UsedSheet(Enum):
# #   12A
#     dbl = "DBL"
#     ghfb = "GFHB"
#     pixel = "Pixel-System"
#     ch_output = "CH-Output"
#     bin_ntc = "Binning-NTC"
#     ntc_ad = "NTC-AD"
#     drl_ti = "DRL-TI-Fog-Aux"
#     motor = "Leveling-Motor"
#     animation = "Welcome-Animation"
#     basic = "Basic-Parameter"
#     beam_variant = "Beam_Variant"


# From DBC
class ENV_name(Enum):
    LB_Left_Req = "HeadLampLoFlOn_B_Stat_1"
    LB_Right_Req = "HeadLampLoFrOn_B_Stat_1"

    LB_ClassLvl_Left = "LowBeamLightClassL_D_Rq_4"
    LB_ClassLvl_Right = "LowBeamLightClassR_D_Rq_4"

    # HB_Req = "HeadLghtHi_D_Rq"  # 12B
    HB_Req = "HBHL_Beam_D_Rq_3"  # 12C
    TI_Req_Left = "TurnLghtLeft_D_Rq_2"
    TI_Req_Right = "TurnLghtRight_D_Rq_2"
    Bending1_Req_Left = "Slght1BrghtLeft_Pc_Rq_8"
    Bending1_Req_Right = "Slght1BrghtRight_Pc_Rq_8"
    DRL1_Req_Left = "DrlPos1_Actv_Lf_Rq_2"
    DRL1_Req_Right = "DrlPos1_Actv_Rf_Rq_2"
    DRL2_Req_Left = "DrlPos2_Actv_Lf_Rq_2"
    DRL2_Req_Right = "DrlPos2_Actv_Rf_Rq_2"
    DRL3_Req_Left = "DrlPos3_Actv_Lf_Rq_2"
    DRL3_Req_Right = "DrlPos3_Actv_Rf_Rq_2"
    DRL4_Req_Left = "DrlPos4_Actv_Lf_Rq_2"
    DRL4_Req_Right = "DrlPos4_Actv_Rf_Rq_2"


class FunMapToENV(Enum):
    Pixel = [ENV_name.LB_Left_Req.value, ENV_name.LB_Right_Req.value]
    Foreground_LB = [ENV_name.LB_Left_Req.value, ENV_name.LB_Right_Req.value, 0]
    Segment_Bending = [ENV_name.Bending1_Req_Left.value, ENV_name.Bending1_Req_Right.value]
    Static_Bending = [ENV_name.Bending1_Req_Left.value, ENV_name.Bending1_Req_Right.value, 0]
    Static_HB = [ENV_name.HB_Req.value, ENV_name.HB_Req.value]
    Matrix_HB_Section_4 = [ENV_name.HB_Req.value, ENV_name.HB_Req.value, 4]
    Sequential_TI_Section_10 = [ENV_name.TI_Req_Left.value, ENV_name.TI_Req_Right.value, 10]
    Sequential_TI_Section_11 = [ENV_name.TI_Req_Left.value, ENV_name.TI_Req_Right.value, 11]
    Sequential_TI_Section_13 = [ENV_name.TI_Req_Left.value, ENV_name.TI_Req_Right.value, 13]
    Channel_Sequential_TI_1 = [ENV_name.TI_Req_Left.value, ENV_name.TI_Req_Right.value, 1]
    Channel_Sequential_TI_2 = [ENV_name.TI_Req_Left.value, ENV_name.TI_Req_Right.value, 2]
    Channel_Sequential_TI_3 = [ENV_name.TI_Req_Left.value, ENV_name.TI_Req_Right.value, 3]
    Static_TI = [ENV_name.TI_Req_Left.value, ENV_name.TI_Req_Right.value]
    DRL1 = [ENV_name.DRL1_Req_Left.value, ENV_name.DRL1_Req_Right.value]
    DRL2 = [ENV_name.DRL2_Req_Left.value, ENV_name.DRL2_Req_Right.value]
    DRL3 = [ENV_name.DRL3_Req_Left.value, ENV_name.DRL3_Req_Right.value]
    DRL4 = [ENV_name.DRL4_Req_Left.value, ENV_name.DRL4_Req_Right.value]
    Auxiliary_Signature_Light_1 = [ENV_name.DRL1_Req_Left.value, ENV_name.DRL1_Req_Right.value, 1]
    Auxiliary_Signature_Light_2 = [ENV_name.DRL2_Req_Left.value, ENV_name.DRL2_Req_Right.value, 2]
    Auxiliary_Signature_Light_3 = [ENV_name.DRL3_Req_Left.value, ENV_name.DRL3_Req_Right.value, 3]
    Auxiliary_Signature_Light_4 = [ENV_name.DRL4_Req_Left.value, ENV_name.DRL4_Req_Right.value, 4]


class DiagRequest(Enum):
    session_02 = [0x02, 0x10, 0x02]
    session_03 = [0x02, 0x10, 0x03]
    req_2703 = [0x02, 0x27, 0x03]

    FC = [0x30]

    DE00 = [0x10, 0x2F, 0xDE, 0x00]

    FD11 = [0x03, 0x22, 0xFD, 0x11]
    FD12 = [0x03, 0x22, 0xFD, 0x12]
    FD13 = [0x03, 0x22, 0xFD, 0x13]
    FD14 = [0x03, 0x22, 0xFD, 0x14]
    FD15 = [0x03, 0x22, 0xFD, 0x15]
    FD16 = [0x03, 0x22, 0xFD, 0x16]
    FD17 = [0x03, 0x22, 0xFD, 0x17]
    FD18 = [0x03, 0x22, 0xFD, 0x18]
    FD19 = [0x03, 0x22, 0xFD, 0x19]
    FD20 = [0x03, 0x22, 0xFD, 0x20]
    FD21 = [0x03, 0x22, 0xFD, 0x21]
    FD22 = [0x03, 0x22, 0xFD, 0x22]

    FD11_DID = "LED_Intensity_CH1_Read"
    FD12_DID = "LED_Intensity_CH2_Read"
    FD13_DID = "LED_Intensity_CH3_Read"
    FD14_DID = "LED_Intensity_CH4_Read"
    FD15_DID = "LED_Intensity_CH5_Read"
    FD16_DID = "LED_Intensity_CH6_Read"
    FD17_DID = "LED_Intensity_CH7_Read"
    FD18_DID = "LED_Intensity_CH8_Read"
    FD19_DID = "LED_Intensity_CH9_Read"
    FD20_DID = "LED_Intensity_CH10_Read"
    FD21_DID = "LED_Intensity_CH11_Read"
    FD22_DID = "LED_Intensity_CH12_Read"

    FD50_DID = "InternalState_CH1_Read"
    FD51_DID = "InternalState_CH2_Read"
    FD52_DID = "InternalState_CH3_Read"
    FD53_DID = "InternalState_CH4_Read"
    FD54_DID = "InternalState_CH5_Read"
    FD55_DID = "InternalState_CH6_Read"
    FD56_DID = "InternalState_CH7_Read"
    FD57_DID = "InternalState_CH8_Read"
    FD58_DID = "InternalState_CH9_Read"
    FD59_DID = "InternalState_CH10_Read"
    FD60_DID = "InternalState_CH11_Read"
    FD61_DID = "InternalState_CH12_Read"
    FD62_DID = "InternalState_CH13_Read"

    FD08_DID = "High_Side_Status_Read"

    DE00_read_DID = "Method_2_Data_Type_1_Read"
    DE01_read_DID = "Method_2_Data_Type_2_Read"
    DE02_read_DID = "Method_2_Data_Type_3_Read"
    DE03_read_DID = "Method_2_Data_Type_4_Read"
    DE04_read_DID = "Method_2_Data_Type_5_Read"

    DE00_write_DID = "Method_2_Data_Type_1_Write"
    DE01_write_DID = "Method_2_Data_Type_2_Write"
    DE02_write_DID = "Method_2_Data_Type_3_Write"
    DE03_write_DID = "Method_2_Data_Type_4_Write"
    DE04_write_DID = "Method_2_Data_Type_5_Write"

    Left_Headlamp_Power_Supply_Read = "Left_Headlamp_Power_Supply_Read"
    Right_Headlamp_Power_Supply_Read = "Right_Headlamp_Power_Supply_Read"

    FD33_DID = "Read_Channel_Current_Read"

    read_dtc_1906 = "DTCs_Read_DTC_Count_by_Status"
    read_dtc = "DTCs_Read_DTCs_by_Status"
    clear_dtc = "DTCs_Clear_All"


# User defined
class ecu_side(Enum):
    right = "Right ECU"
    left = "Left ECU"


# From Dataset
class SpotKinkStrategy(Enum):
    NotTurnOff = "No Turn Off"
    TurnOff = "Turn Off"
    PartialTurnOff = "Partial Turn Off"


# Form Dataset
class DBLMoveBaseRow(Enum):
    row1 = "Row1_Sec4/5"
    row2 = "Row2_Sec2/3"
    row3 = "Row3_Sec0/1"


# Form Dataset
class DBLShiftAway(Enum):
    RemainOn = "LEDs Remain On"
    Deactivated = "LEDs Deactivated"


# Form Dataset
class DBLMoveDire(Enum):
    MoveToRight = "Move to Right"
    MoveToLeft = "Move to Left"
    NoMove = "No Move: "


# Form Dataset
class Function(Enum):
    DBL = "DBL"
    Spot = "Spot"


# Form Dataset
class EnableStatus(Enum):
    Enable = "Enable"
    Disable = "Disable"


CHxDIDx_map = {
    "CH_1": [DiagRequest.FD11_DID.value, DiagRequest.FD50_DID.value],
    "CH_2": [DiagRequest.FD12_DID.value, DiagRequest.FD51_DID.value],
    "CH_3": [DiagRequest.FD13_DID.value, DiagRequest.FD52_DID.value],
    "CH_4": [DiagRequest.FD14_DID.value, DiagRequest.FD53_DID.value],
    "CH_5": [DiagRequest.FD15_DID.value, DiagRequest.FD54_DID.value],
    "CH_6": [DiagRequest.FD16_DID.value, DiagRequest.FD55_DID.value],
    "CH_7": [DiagRequest.FD17_DID.value, DiagRequest.FD56_DID.value],
    "CH_8": [DiagRequest.FD18_DID.value, DiagRequest.FD57_DID.value],
    "CH_9": [DiagRequest.FD19_DID.value, DiagRequest.FD58_DID.value],
    "CH_10": [DiagRequest.FD20_DID.value, DiagRequest.FD59_DID.value],
    "CH_11": [DiagRequest.FD21_DID.value, DiagRequest.FD60_DID.value],
    "CH_12": [DiagRequest.FD22_DID.value, DiagRequest.FD61_DID.value],
    "CH_6 LS": [DiagRequest.FD62_DID.value, DiagRequest.FD62_DID.value],
}


class ClassLvl_Def(Enum):
    ClassC = 0
    ClassV1 = 1
    ClassE = 9
    ClassE1 = 10
    ClassE2 = 11
    ClassE3 = 12
    ClassW = 13


class derating_req(Enum):
    LB = {"Start": 0, "Stop": 5, "req": 1, "PCBA": [0, 0, 20], "type_num": 3}
    Pixel = {"Start": 20, "Stop": 25, "req": 1, "PCBA": [10, 20, 50],  "type_num": 1}
    HB = {"Start": 20, "Stop": 25, "req": 1, "PCBA": [20, 50, 100], "type_num": 1}
    TI = {"Start": 0, "Stop": 5, "req": 2, "PCBA": [0, 0, 20], "type_num": 5}
    DRL = {"Start": 20, "Stop": 40, "req": 2, "PCBA": [0, 20, 50], "type_num": 4}
    Aux = {"Start": 20, "Stop": 40, "req": 2, "PCBA": [50, 50, 100], "type_num": 6}
    Bending = {"Start": 20, "Stop": 40, "req": 100, "PCBA": [50, 50, 100], "type_num": 2}
    SML = {"Start": 0, "Stop": 0, "req": 1}


class NXP_BIN_Level_vol(Enum):
    BIN0 = 0.08
    BIN1 = 0.15
    BIN2 = 0.2
    BIN3 = 0.3
    BIN4 = 0.4
    BIN5 = 0.48
    BIN6 = 0.68
    BIN7 = 0.8


total_power = {
    "start_vol": 9, "start_power": 150, "stop_vol": 6, "stop_power": 60
}


class Right_DTC(Enum):
    e2e_82 = [0xC5, 0x42, 0x82]
    e2e_83 = [0xC5, 0x42, 0x83]
    lb_lost = [0x9D, 0x01, 0x87]
    ti_lost = [0x92, 0x3B, 0x87]
    hcm_can_lost = [0xc2, 0x41, 0x00]
    hb_lost = [0x9D, 0x03, 0x87]
    drl_lost = [0x92, 0x4a, 0x87]
    sm_lost = [0x94, 0x9f, 0x87]
    aux_lost = [0x94, 0xa3, 0x87]
    bending_lost = [0x95, 0x68, 0x87]
    motor_lost = [0x9a, 0x58, 0x87]
