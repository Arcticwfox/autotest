"""
FordDatasetHandler extended from data_set.DatasetHandler.

This file is only used to read out data from Ford dataset.

@Author: Siwei.Lu
@Date: 2022.11.30
"""

from Core.dataset_handler.data_set import DatasetHandler
from Core.project.ford.parameter_def import UsedSheet
from Core import parse_config


# todo:12/12B dataset
class FordDatasetHandler(DatasetHandler):
    def __init__(self):
        self.__yaml_path = '/test_fixture/test_configuration/ford_test_configuration/ford_config.yaml'
        self.__config = parse_config.ConfigHandler(self.__yaml_path)
        self.__path = self.__config.get_dataset_info()['path']
        super(FordDatasetHandler, self).__init__(self.__path, UsedSheet)

        self._get_dataset_para()

    def _get_dataset_para(self):
        self.__bin_info = self.__config.get_dataset_info()['bin']
        self.__drl_sheet_info = self.__config.get_dataset_info()['drl_ti_aux_bending']

        self.__e2e_cfg = self.__config.get_dataset_info()['e2e_cfg']
        self.__ntc_info = self.__config.get_dataset_info()['ntc']

        self.__variant = self.get_row_column_array(UsedSheet.basic.value, [16, 16, 3, 3])

        if self.__variant == 'LDM12FNV3':
            # GFHB
            self.__GFHB_para = self.get_row_column_array(UsedSheet.ghfb.value, [2, 11, 2, 2])  # GFHB function列的参数
            self.__HLT_AnDistLutBrkPnts = self.get_row_column_array(UsedSheet.ghfb.value, [2, 12, 4, 5])
            self.__HLT_AnLuBrkPnts = self.get_row_column_array(UsedSheet.ghfb.value, [2, 8, 7, 14])

        # ch_output
        self.__ch_function = self.get_row_column_array(UsedSheet.ch_output.value, [2, 14, 1, 3])
        self.__ch_x01_x12 = self.get_row_column_array(UsedSheet.ch_output.value, [2, 14, 12, 23], 1)

        # Pixel
        self.__pixel_system = self.get_row_column_array(UsedSheet.pixel.value, [10, 105, 4, 5])
        self.__pixel_site_value = self.get_row_column_array(UsedSheet.pixel.value, [10, 105, 8, 11])
        self.__sec01_site_value = self.get_row_column_array(UsedSheet.pixel.value, [10, 41, 8, 11])
        self.__sec23_site_value = self.get_row_column_array(UsedSheet.pixel.value, [42, 73, 8, 11])
        self.__sec45_site_value = self.get_row_column_array(UsedSheet.pixel.value, [74, 105, 8, 11])
        self.__matrix_add_swi = self.get_row_column_array(UsedSheet.pixel.value, [10, 105, 4, 5])
        self.__sec01_matrix_add_swi = self.get_row_column_array(UsedSheet.pixel.value, [10, 41, 4, 5])
        self.__sec23_matrix_add_swi = self.get_row_column_array(UsedSheet.pixel.value, [42, 73, 4, 5])
        self.__sec45_matrix_add_swi = self.get_row_column_array(UsedSheet.pixel.value, [74, 105, 4, 5])

        # drl_ti_fog_aux__sbl
        self.__fog_cfg = self.get_row_column_array(UsedSheet.drl_ti.value, [18, 18, 11, 11])

        # DBL
        self.__DBL_shiftAway = self.get_row_column_array(UsedSheet.dbl.value, [2, 2, 2, 2])
        self.__DBL_leading_fac = self.get_row_column_array(UsedSheet.dbl.value, [5, 5, 2, 2])
        self.__DBL_follow_fac = self.get_row_column_array(UsedSheet.dbl.value, [6, 6, 2, 2])
        self.__DBL_speed = self.get_row_column_array(UsedSheet.dbl.value, [3, 52, 101, 101])
        self.__DBL_base_row = self.get_row_column_array(UsedSheet.dbl.value, [19, 19, 2, 2])
        self.__DBL_row1_enable = self.get_row_column_array(UsedSheet.dbl.value, [16, 16, 2, 2])
        self.__DBL_row2_enable = self.get_row_column_array(UsedSheet.dbl.value, [17, 17, 2, 2])
        self.__DBL_row3_enable = self.get_row_column_array(UsedSheet.dbl.value, [18, 18, 2, 2])

        # NTC_R
        self.__NTC_Tem = self.get_row_column_array(UsedSheet.ntc_ad.value, [2, 112, 1, 1])
        self.__NTC_R = self.get_row_column_array(UsedSheet.ntc_ad.value, [2, 112, 2, 2])
        self.__NTC_R_AD = self.get_row_column_array(UsedSheet.ntc_ad.value, [2, 112, 3, 3])

    def get_bin_info_by_channel(self, ch_x: int):
        """
        Get BIN information(bin range, current, analog input) base on given channel.
        @param ch_x: given channel
        @return: dict
        """
        chx = "ch{ch}".format(ch=ch_x)
        chx_bin_range = self.__bin_info['bin_range'][chx]
        chx_bin_current = self.__bin_info['bin_current'][chx]
        chx_bin_adc = self.__bin_info['bin_analog_input'][chx]

        """self.__ch_bin is middle point of BIN range"""
        ch_bin = self.get_row_column_array(UsedSheet.bin_ntc.value, chx_bin_range)
        ch_current = self.get_row_column_array(UsedSheet.bin_ntc.value, chx_bin_current)
        ch_analog_input = self.get_row_column_array(UsedSheet.bin_ntc.value, chx_bin_adc)

        tmp_dict = {"ch_bin": ch_bin,
                    "ch_current": ch_current,
                    "ch_analog_input": ch_analog_input}

        return tmp_dict

    def get_ch_func_chip_dict(self):
        ch_chip_dict = {}
        for index, item in enumerate(self.__ch_function[0]):
            ch_chip_dict.update({item: {"function": self.__ch_function[1][index].replace(" ", "_"),
                                        "matrix_chip": self.__ch_function[2][index],
                                        "x01~x12": self.__ch_x01_x12[index]}
                                 })

        # print("ch: ", ch_chip_dict["CH_{}".format(8)]['function'])
        # ch_fun = ch_chip_dict["CH_{}".format(8)]['function']
        return ch_chip_dict

    def get_drl_int_in_dataset(self, drl_x: int, drl_request: int, ti_request: int):
        """
        @param ti_request: 0: Null, 1:off, 2:on, 3:SEQ
        @param drl_x: 1,2,3,4
        @param drl_request: 0:off, 1:po, 2:drl, other:invalid value
        @return:
        """
        drl_info = self.__drl_sheet_info['drl/po']['drl{}_intensity'.format(drl_x)]
        po_info = self.__drl_sheet_info['drl/po']['po{}_intensity'.format(drl_x)]

        po_behavior_ti_active_info = self.__drl_sheet_info['drl/po']['po_behavior_ti_active']
        po_as_ti_info = self.__drl_sheet_info['drl/po']['po{}_as_ti_int'.format(drl_x)]

        if drl_request == 0:
            drl_po_int = 0
        elif drl_request == 1:
            drl_po_int = self.get_row_column_array(UsedSheet.drl_ti.value, po_info)
        elif drl_request == 2:
            drl_po_int = self.get_row_column_array(UsedSheet.drl_ti.value, drl_info)
        else:
            drl_po_int = self.get_row_column_array(UsedSheet.drl_ti.value, po_info)

        po_behavior_ti_active = self.get_row_column_array(UsedSheet.drl_ti.value, po_behavior_ti_active_info)

        if ((ti_request in [1, 2, 3]) and (po_behavior_ti_active == 'Use TI active intensity when TI is Actv')) or \
                ((ti_request in [2, 3]) and (po_behavior_ti_active == 'Use TI active intensity when TI is Actv and '
                                                                      'not in the off cycle')):
            drl_po_int = self.get_row_column_array(UsedSheet.drl_ti.value, po_as_ti_info)

        return drl_po_int

    def get_aux_int_in_dataset(self, aux_x: int, drl_request: int):
        """
        @param aux_x: 1,2,3,4
        @param drl_request: 0:off, 1:po, 2:drl, other:invalid value
        @return:
        """
        aux_drl_info = self.__drl_sheet_info['aux']['aux{}_drl_int'.format(aux_x)]
        aux_po_info = self.__drl_sheet_info['aux']['aux{}_po_int'.format(aux_x)]

        if drl_request == 0:
            aux_int = 0
        elif drl_request == 1:
            aux_int = self.get_row_column_array(UsedSheet.drl_ti.value, aux_po_info)
        elif drl_request == 2:
            aux_int = self.get_row_column_array(UsedSheet.drl_ti.value, aux_drl_info)
        else:
            aux_int = self.get_row_column_array(UsedSheet.drl_ti.value, aux_po_info)

        return aux_int

    def get_ti_int_in_request(self, ti_request: int, function: str, drl_request: int):
        """
        @param drl_request: 0:off, 1:po, 2:DRL, 3:invalid vlue
        @param function:TI type
        @param ti_request: 0:null, 1:off, 2:on, 3:SEQ
        @return:
        """

        sseq_ti = ['Static_TI', 'Sequential_TI_Section_10', 'Sequential_TI_Section_11', 'Sequential_TI_Section_13']
        chseq_ti = ['Channel_Sequential_TI_1', 'Channel_Sequential_TI_2', 'Channel_Sequential_TI_3']

        chseqti_animation = self.__drl_sheet_info['ti']['chseq_ti_animation']
        chseq_ti1_time = self.__drl_sheet_info['ti']['chseq1_time']
        chseq_ti2_time = self.__drl_sheet_info['ti']['chseq2_time']
        chseq_ti3_time = self.__drl_sheet_info['ti']['chseq3_time']
        ti_deact_brght = self.__drl_sheet_info['ti']['ti_deactv_brght']
        turn_deactv_cfg = self.__drl_sheet_info['ti']['turn_deactv_pos_cfg']

        chseqti_animation_info = self.get_row_column_array(UsedSheet.drl_ti.value, chseqti_animation)
        chseqti1_time = self.get_row_column_array(UsedSheet.drl_ti.value, chseq_ti1_time)
        chseqti2_time = self.get_row_column_array(UsedSheet.drl_ti.value, chseq_ti2_time)
        chseqti3_time = self.get_row_column_array(UsedSheet.drl_ti.value, chseq_ti3_time)
        turn_deactv_pos_cfg = self.get_row_column_array(UsedSheet.drl_ti.value, turn_deactv_cfg)
        # print(turn_deactv_pos_cfg, ', DRL_request= ', drl_request)

        wait = 0
        ti_time = 0
        if ti_request == 0:
            ti_int = 0
        elif ti_request == 1:
            ti_int = 0
        elif ti_request == 2:
            ti_int = 100
        elif ti_request == 3:
            ti_int = 100

        if (turn_deactv_pos_cfg == 'TI as Position Light deactivated') or (drl_request in [0, 2]):
            if function in sseq_ti:
                pass
            elif (function in chseq_ti) and (chseqti_animation_info == 'Activation'):
                wait = 1
                ti_time = max(chseqti1_time, chseqti2_time, chseqti3_time)
            elif (function in chseq_ti) and (chseqti_animation_info == 'Deactivation'):
                wait = 1
                ti_time = max(chseqti1_time, chseqti2_time, chseqti3_time)
                if ti_request == 3:
                    ti_int = 0
            else:
                ti_int = 0
                # print("Not configure", function, "chseqti_animation_info = ", chseqti_animation_info,
                #       ", turn_deactv_pos_cfg = ", turn_deactv_pos_cfg)

        elif drl_request in [3, 1]:
            if ti_request == 0:
                ti_int = self.get_row_column_array(UsedSheet.drl_ti.value, ti_deact_brght)
            elif ti_request == 1:
                ti_int = self.get_row_column_array(UsedSheet.drl_ti.value, ti_deact_brght)

            if function in sseq_ti:
                pass
            elif (function in chseq_ti) and (chseqti_animation_info == 'Activation'):
                wait = 1
                ti_time = max(chseqti1_time, chseqti2_time, chseqti3_time)
            elif (function in chseq_ti) and (chseqti_animation_info == 'Deactivation'):
                wait = 1
                ti_time = max(chseqti1_time, chseqti2_time, chseqti3_time)
                if ti_request == 3:
                    ti_int = 0
            else:
                ti_int = 0
                print("Not configure", function, ", turn_deactv_pos_cfg = ", turn_deactv_pos_cfg)

        return ti_int, ti_time, wait

    def get_ntc_info(self, ch_x: int):
        """
        get channel NTC TD NTC source and NTC BD
        @Author: YuJie.Shi
        @param ch_x:
        @return: dict
        """
        chx = "CH{ch}".format(ch=ch_x)
        chx_TD = self.__ntc_info['TD'][chx]
        chx_NTC_source = self.__ntc_info['NTC_source'][chx]
        chx_BD = self.__ntc_info["BD"][chx]

        ch_TD = self.get_row_column_array(UsedSheet.bin_ntc.value, chx_TD)
        ch_NTC_source = self.get_row_column_array(UsedSheet.bin_ntc.value, chx_NTC_source)
        ch_BD = self.get_row_column_array(UsedSheet.bin_ntc.value, chx_BD)

        tmp_dict = {"ch_TD": ch_TD,
                    "ch_NTC_source": ch_NTC_source,
                    "ch_BD": ch_BD}

        return tmp_dict

    def get_ezl_int_in_dataset(self, ezl_config: list, ezl_request: int, drl_request: int, drl_x: int):
        """
        @param ezl_config: ezl_channel_int(auto calculater)
        @param ezl_request: 0:null, 1:off, 2:on, 3:not used
        @param drl_request: 0:null, 1:off, 2:on, 3:seq
        @param drl_x: 1:drl 1, 2:drl 2, 3:drl 3, 4:drl 4
        @author:Li.Wang
        @return:
        """

        ezl_int = {}
        ch_info = self.get_ch_func_chip_dict()
        ezl_m2 = ezl_config[4: 16]
        drl = ['DRL1', 'DRL2', 'DRL3', 'DRL4']
        aux = ['Auxiliary_Signature_Light_1', 'Auxiliary_Signature_Light_2', 'Auxiliary_Signature_Light_3',
               'Auxiliary_Signature_Light_4']
        bending_shb = ['Segment_Bending', 'Static_Bending', 'Static_HB']
        ti = ['Sequential_TI_Section_10', 'Sequential_TI_Section_11', 'Sequential_TI_Section_13',
              'Channel_Sequential_TI_1', 'Channel_Sequential_TI_2', 'Channel_Sequential_TI_3',
              'Static_TI']

        if drl_request in [0, 2]:
            if ezl_request == 2:
                if ezl_config[3] == 1:
                    print('EZL function configure enable.')
                    for index_ezl, item_ezl in enumerate(ezl_m2):
                        if ezl_m2[index_ezl] == 1:
                            print('CH{} EZL function configure enable'.format((index_ezl) + 1))
                            for index, item in enumerate(ch_info.keys()):
                                for key, value in ch_info.items():
                                    if key == 'CH_{}'.format((index_ezl) + 1):
                                        if value['function'] in bending_shb:
                                            # print(value['function'])
                                            ezl_int[key] = 100
                                        elif value['function'] in drl:
                                            drl_info = self.__drl_sheet_info['drl/po']['drl{}_intensity'.format(
                                                value['function'][3])]
                                            ezl_int[key] = self.get_row_column_array(UsedSheet.drl_ti.value,
                                                                                     drl_info)
                                        elif value['function'] in aux:
                                            aux_info = self.__drl_sheet_info['aux']['aux{}_drl_int'.format(
                                                value['function'][26])]
                                            ezl_int[key] = self.get_row_column_array(UsedSheet.drl_ti.value,
                                                                                     aux_info)
                                        elif value['function'] in ti:
                                            ezl_int[key] = 0

                        elif ezl_m2[index_ezl] == 0:
                            print('CH{} EZL function configure disable'.format((index_ezl) + 1))
                            # print("m2 = ", index_ezl, item_ezl)
                            for index, item in enumerate(ch_info.keys()):
                                for key, value in ch_info.items():
                                    if key == 'CH_{}'.format((index_ezl) + 1):
                                        ezl_int[key] = 0
                elif ezl_config[3] == 0:
                    print('EZL funtion configure disable')
                    for key, value in ch_info.items():
                        ezl_int[key] = 0
            else:
                if ezl_config[3] == 1:
                    print("EZL configure enable")
                elif ezl_config[3] == 0:
                    print("EZL configure disable")
                elif ezl_request in [0, 1, 3]:
                    print("EZL function request off.")
                for key, value in ch_info.items():
                    ezl_int[key] = 0
        elif drl_request in [1, 3]:
            print('ECU exit EZL mode')
            for key, value in ch_info.items():
                if value['function'] == 'DRL{}'.format(drl_x):
                    po_info = self.__drl_sheet_info['drl/po']['po{}_intensity'.format(value['function'][3])]
                    ezl_int[key] = self.get_row_column_array(UsedSheet.drl_ti.value, po_info)
                if value['function'] == 'Auxiliary_Signature_Light_{}'.format(drl_x):
                    po_info = self.__drl_sheet_info['aux']['aux{}_po_int'.format(value['function'][26])]
                    ezl_int[key] = self.get_row_column_array(UsedSheet.drl_ti.value, po_info)
        # print('ezl_int = ', ezl_int)
        return ezl_int

    def get_ezl_iocontrol_int_in_dataset(self, fun: str, iocontrol_request: int):
        """
        @param fun:function systerm
        @param iocontrol_request: 1: on,2: off
        @author:Li.Wang
        @return:
        """

        ezl_int = {}
        ch_info = self.get_ch_func_chip_dict()

        drl = ['DRL1', 'DRL2', 'DRL3', 'DRL4']
        aux = ['Auxiliary_Signature_Light_1', 'Auxiliary_Signature_Light_2', 'Auxiliary_Signature_Light_3',
               'Auxiliary_Signature_Light_4']
        bending = ['Segment_Bending', 'Static_Bending']
        ti = ['Sequential_TI_Section_10', 'Sequential_TI_Section_11', 'Sequential_TI_Section_13',
              'Channel_Sequential_TI_1', 'Channel_Sequential_TI_2', 'Channel_Sequential_TI_3',
              'Static_TI']

        if iocontrol_request == 1:
            if fun == 'drl':
                for key, value in ch_info.items():
                    if value['function'] in drl:
                        # add sidemarker
                        drl_info = self.__drl_sheet_info['drl/po']['drl{}_intensity'.format(value['function'][3])]
                        ezl_int[key] = self.get_row_column_array(UsedSheet.drl_ti.value, drl_info)
                    else:
                        ezl_int[key] = 0
            elif fun == 'ti':
                for key, value in ch_info.items():
                    if value['function'] in ti:
                        ezl_int[key] = 100
                    else:
                        ezl_int[key] = 0
            elif fun == 'aux':
                for key, value in ch_info.items():
                    if value['function'] in aux:
                        aux_info = self.__drl_sheet_info['aux']['aux{}_drl_int'.format(value['function'][26])]
                        ezl_int[key] = self.get_row_column_array(UsedSheet.drl_ti.value, aux_info)
                    else:
                        ezl_int[key] = 0
            elif fun == 'bending':
                for key, value in ch_info.items():
                    if value['function'] in bending:
                        ezl_int[key] = 100
                    else:
                        ezl_int[key] = 0
            else:
                for key, value in ch_info.items():
                    ezl_int[key] = 0
        elif iocontrol_request == 2:
            for key, value in ch_info.items():
                ezl_int[key] = 0
        # print('ezl_int = ', ezl_int)
        return ezl_int

    def get_e2e_config(self):
        """
        @author: Li.Wang
        """
        e2e_config = self.get_row_column_array(UsedSheet.basic.value, self.__e2e_cfg)
        return e2e_config

    def get_e2e_int(self, dtc_expect: list, wait_time: int):
        """
        @author: Li.Wang
        """
        ch_info = self.get_ch_func_chip_dict()
        funtion = ['Sequential_TI_Section_10', 'Sequential_TI_Section_11', 'Sequential_TI_Section_13',
                   'Channel_Sequential_TI_1', 'Channel_Sequential_TI_2', 'Channel_Sequential_TI_3',
                   'Static_TI']
        e2e_int = {}
        if dtc_expect != [] and dtc_expect != [1] and wait_time >= 3:
            for key, value in ch_info.items():
                if value['function'] in funtion:
                    e2e_int[key] = 0
        else:
            for key, value in ch_info.items():
                if value['function'] in funtion:
                    e2e_int[key] = 100
        # print(dtc_expect)
        # print(e2e_int)
        return e2e_int

    def get_ntc_R_AD(self, tem: int):
        """
        Get the resistance value and AD corresponding to the temperature
        @Author: YuJie.Shi
        @param tem:
        @return: ntc_R, ntc_R_AD
        """
        tem_list = self.__NTC_Tem
        ntc_R, ntc_R_AD = 0, 0
        for temperature in tem_list:
            if tem == temperature:
                ntc_R = self.__NTC_R[tem_list.index(tem)]
                ntc_R_AD = self.__NTC_R_AD[tem_list.index(tem)]
        if tem <= tem_list[0]:
            ntc_R = self.__NTC_R[0]
            ntc_R_AD = self.__NTC_R_AD[0]
        elif tem >= tem_list[-1]:
            ntc_R = self.__NTC_R[-1]
            ntc_R_AD = self.__NTC_R_AD[-1]
        ntc_R = round(ntc_R / 1000, 3)

        return ntc_R, ntc_R_AD

    def get_ntc_tem(self, AD: int):
        """
        input AD value get tem
        @Author: YuJie.Shi
        @param AD:
        @return: tem
        """
        ad_list = self.__NTC_R_AD
        tem_list = self.__NTC_Tem
        for i in range(111):
            if ad_list[i+1] < AD < ad_list[i]:
                return tem_list[i+1]
            elif AD > ad_list[0]:
                return tem_list[0]
            elif AD < ad_list[110]:
                return tem_list[110]
            elif AD == ad_list[i]:
                return tem_list[i]

    def get_TI_matrix_info(self, ch_x: int):
        """
        if configure TI maxtrix,get min_ad max_ad and bin current
        @Author: YuJie.Shi
        :param ch_x:
        :return: dict
        """
        min_ad = self.get_row_column_array(UsedSheet.bin_ntc.value, [11 * ch_x - 7, 11 * ch_x - 1, 7, 7])
        max_ad = self.get_row_column_array(UsedSheet.bin_ntc.value, [11 * ch_x - 7, 11 * ch_x - 1, 8, 8])
        bin_current = self.get_row_column_array(UsedSheet.bin_ntc.value, [11 * ch_x - 7, 11 * ch_x - 1, 10, 10])
        ch_info_dict = {
            'min_ad': min_ad,
            'max_ad': max_ad,
            'bin_current': bin_current
        }
        return ch_info_dict

    def get_NXP_matrix_info(self, ch_x: int):
        """
        if configure TI maxtrix,get min_ad max_ad and bin current
        @Author: YuJie.Shi
        :param ch_x:
        :return: dict
        """
        min_ad = self.get_row_column_array(UsedSheet.bin_ntc.value, [11 * ch_x - 8, 11 * ch_x - 1, 7, 7])
        max_ad = self.get_row_column_array(UsedSheet.bin_ntc.value, [11 * ch_x - 8, 11 * ch_x - 1, 8, 8])
        bin_current = self.get_row_column_array(UsedSheet.bin_ntc.value, [11 * ch_x - 8, 11 * ch_x - 1, 10, 10])
        ch_info_dict = {
            'min_ad': min_ad,
            'max_ad': max_ad,
            'bin_current': bin_current
        }
        return ch_info_dict


    @property
    def HLT_AnLuBrkPnts(self):
        return self.__HLT_AnLuBrkPnts

    @property
    def ch_x01_12(self):
        return self.__ch_x01_x12

    @property
    def ch_function(self):
        return self.__ch_function

    @property
    def fog_cfg(self):
        return self.__fog_cfg

    @property
    def pixel_site_value(self):
        return self.__pixel_site_value

    @property
    def sec01_site_value(self):
        return self.__sec01_site_value

    @property
    def sec23_site_value(self):
        return self.__sec23_site_value

    @property
    def sec45_site_value(self):
        return self.__sec45_site_value

    @property
    def matrix_add_swi(self):
        return self.__matrix_add_swi

    @property
    def sec01_matrix_add_swi(self):
        return self.__sec01_matrix_add_swi

    @property
    def sec23_matrix_add_swi(self):
        return self.__sec23_matrix_add_swi

    @property
    def sec45_matrix_add_swi(self):
        return self.__sec45_matrix_add_swi

    @property
    def GFHB_para(self):
        return self.__GFHB_para

    @property
    def HLT_AnDistLutBrkPnts(self):
        return self.__HLT_AnDistLutBrkPnts

    @property
    def DBL_shiftAway(self):
        return self.__DBL_shiftAway

    @property
    def DBL_leading_fac(self):
        return self.__DBL_leading_fac

    @property
    def DBL_follow_fac(self):
        return self.__DBL_follow_fac

    @property
    def DBL_base_row(self):
        return self.__DBL_base_row

    @property
    def DBL_row1_enable(self):
        return self.__DBL_row1_enable

    @property
    def DBL_row2_enable(self):
        return self.__DBL_row2_enable

    @property
    def DBL_row3_enable(self):
        return self.__DBL_row3_enable

    @property
    def DBL_speed(self):
        return self.__DBL_speed
