"""
This file is used to connect bin_set_module(ModBus) via serial port.

@Author: Siwei.Lu
@Date: 2022.11.27
"""
import sys

from Core import parse_config
from Core.instrument_control import serial_control


class BinSetModuleControl:
    def __init__(self, config: parse_config.ConfigHandler):
        self.__config = config
        self.__modbus_config = self.__config.get_config_by_inst('bin_set_module')
        self.__baud = self.__config.get_baud_rate('bin_set_module')
        self.__com = self.__config.get_com('bin_set_module')

        try:
            self.__serialHandler = serial_control.SerialHandler(self.__com, self.__baud)
        except BaseException as err:
            print("bin_set_module({}) open failed! \n{}".format(self.__com, err))
            serial_control.logger.error("bin_set_module({}) open failed! \n{}".format(self.__com, err))
            sys.exit()

    def set_vol_base_on_resistor(self, addr, resistor):
        """
        :param resistor: KΩ
        """
        bin_req = self.__modbus_config['set_req'].copy()
        bin_req[3] = addr - 1 + 0x20

        self.__serialHandler.send_req(self._get_array_of_modbus(bin_req, resistor))

    def set_vol_base_on_TI_matrix_ad(self, addr, ad):
        """
        the error of ad is 1 - 2
        :param addr:
        :param ad:
        :return:
        """
        bin_req = self.__modbus_config['set_req'].copy()
        bin_req[3] = addr - 1 + 0x20
        vol_1, vol_2 = self._cal_ad_TI_matrix_chip_voltage(ad)
        bin_req.append(vol_1)
        bin_req.append(vol_2)

        self.__serialHandler.send_req(self.__serialHandler.get_array_after_crc16(bin_req))

    def set_vol_base_on_NXP_matrix_ad(self, addr, ad):
        """
        the error of ad is 2 -3 AND when set ad <=5 or ad >= 55, the error is too large
        :param addr:
        :param ad:
        :return:
        """
        bin_req = self.__modbus_config['set_req'].copy()
        bin_req[3] = addr - 1 + 0x20
        vol_1, vol_2 = self._cal_ad_NXP_matrix_chip_voltage(ad)
        bin_req.append(vol_1)
        bin_req.append(vol_2)

        self.__serialHandler.send_req(self.__serialHandler.get_array_after_crc16(bin_req))

    def set_vol_base_on_PCBA_Tem(self, addr, tem):
        """
        the error is +- 1 when set tem<145, 145< tem < 150, the max error is about -4 or -5
        :param addr:
        :param tem: 45 deg - 150 deg
        """
        if tem >= 100:
            tem_value = 1.0262 * tem + 2.0092
        else:
            tem_value = 1.0442 * tem - 1.8841
        resistor = (6e-05 * tem_value ** 4 - 0.0298 * tem_value ** 3 + 5.6844 * tem_value ** 2
                    - 507.34 * tem_value + 18669) / 1000

        self.set_vol_base_on_resistor(addr, resistor)

    @staticmethod
    def _cal_resistor_analog_voltage(resistor):
        """
        Change resistor to voltage.
        :param resistor:  KΩ
        :return:
        """
        re = resistor * 0.979 - 0.0728
        vo = (5 * re + 0.5) / (re + 5.09) * 100  # 将电阻换算成相应的电压值
        vo_1 = vo / 0.95
        vol = round(vo_1, 2)  # 取两位

        vol_1 = int(vol / 0x100)
        vol_2 = int(vol - (int(vol / 0x100) << 8))
        return vol_1, vol_2  # 返回计算结果

    @staticmethod
    def _cal_ad_TI_matrix_chip_voltage(ad):
        """
        cal TI matrix chip ad to voltage
        :param ad:
        :return:
        """
        value = ad * 1.0118 - 4.1389
        if value < 0:
            value = 0
        val = (value / 255) * 5
        vo_1 = val / 0.01
        vol = round(vo_1, 2)  # 取两位

        vol_1 = int(vol / 0x100)
        vol_2 = int(vol - (int(vol / 0x100) << 8))
        return vol_1, vol_2  # 返回计算结果

    @staticmethod
    def _cal_ad_NXP_matrix_chip_voltage(ad):
        """
        cal NXP matrix chip ad to voltage
        :param ad:
        :return:
        """
        value = ad * 1.0693 - 2.5834
        if value < 0:
            value = 0
        vo = value / 63
        vo_1 = vo / 0.0095
        vol = round(vo_1, 2)  # 取两位

        vol_1 = int(vol / 0x100)
        vol_2 = int(vol - (int(vol / 0x100) << 8))
        return vol_1, vol_2  # 返回计算结果

    def _get_array_of_modbus(self, input_req: list, resistor: int):
        """
        Get the request list of bin_set_module based on a given resistor.
        :param input_req:
        :param resistor: KΩ
        :return: The request of bin_set_module.
        """
        vol_1, vol_2 = self._cal_resistor_analog_voltage(resistor)
        input_req.append(vol_1)
        input_req.append(vol_2)

        return self.__serialHandler.get_array_after_crc16(input_req)

    def send_vol_output(self, addr, vo):
        """
        send vol output
        :param addr:
        :param vo:
        :return:
        """
        vol = vo * 100
        bin_req = self.__modbus_config['set_req'].copy()
        bin_req[3] = addr - 1 + 0x20
        vol_1 = int(vol / 0x100)
        vol_2 = int(vol - (int(vol / 0x100) << 8))
        bin_req.append(vol_1)
        bin_req.append(vol_2)

        self.__serialHandler.send_req(self.__serialHandler.get_array_after_crc16(bin_req))
