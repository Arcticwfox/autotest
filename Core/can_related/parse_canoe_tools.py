"""
This file is used to parse DBC/CDD files and provides some methods.

@Author: Siwei.Lu
@Date: 2022.11.30
@Update: Yanjiao.Li
@Date: 2023.02.06
"""

import os
from xml.etree import ElementTree as Et

import cantools
import odxtools

from Core import parse_config

SysNamespacesInfo = []
SysVariablesInfo = []
Namespace_Var = []
namespace_tag = "namespace"
variable_tag = "variable"
name_tag = "name"

Services = []
SubFunctions = []
SubDatas = []
service_tag = ["DIAGCLASS", "DCLTMPL"]
sub_function_tag = "SHORTCUTQUAL"
sub_data_tag = "DATAOBJ"
data_iter = "QUAL"


class CANoeToolHandler:
    def __init__(self, project_name: str):
        """处理DBC/CDD文件 : Absolute Path"""
        self.__project_config_path = "/test_fixture/test_configuration/{}_test_configuration/{}_config.yaml". \
            format(project_name, project_name)
        self.__config = parse_config.ConfigHandler(self.__project_config_path)
        self.__dbc_msg_path = self.__config.get_config_by_name('canoe_tools')['dbc_msg_path']
        self.__dbc_env_path = self.__config.get_config_by_name('canoe_tools')['dbc_env_path']
        self.__dbc_relay_path = self.__config.get_config_by_name('canoe_tools')['dbc_relay_path']

        if self.__dbc_relay_path:
            self.__can_relay_data = self._parse_can_data(self.__dbc_relay_path)
            self.__relay_message_signals_info_dict = self._get_all_signals(self.__can_relay_data)
            self.__relay_message_signals_name_dict = self._map_message_to_signals(
                self.__relay_message_signals_info_dict)

    @staticmethod
    def _parse_can_data(path):
        return cantools.db.load_file(path)

    @staticmethod
    def _get_all_signals(data):
        message_signals_info_dict = {}
        for item in data.messages:
            message_signals_info_dict.update({item.name: item.signals})

        return message_signals_info_dict

    @staticmethod
    def _get_env_name_map(can_env_data):
        env_name_dict = {}
        for key, value in can_env_data.dbc.environment_variables.items():
            env_name_dict.update({value.name: value.name})

        return env_name_dict

    @staticmethod
    def _map_message_to_signals(info_dict: dict):
        message_signals_name_dict = {}

        for message_name, signals in info_dict.items():
            signals_list = []
            for signal_info in signals:
                signals_list.append(signal_info.name)
            message_signals_name_dict.update({message_name: signals_list})

        return message_signals_name_dict

    def _read_data_according_to_dbc_type(self, data_type, file_path):
        """
        @param data_type: "Message" or "Environment"
        @param file_path:
        @return: dict
        """

        info_dict = {}

        if type(file_path) == list:
            for path in file_path:
                if path:
                    if data_type == "Message":
                        info_dict.update(self._get_all_signals(self._parse_can_data(path)))
                    elif data_type == "Environment":
                        info_dict.update(self._get_env_name_map(self._parse_can_data(path)))
                    else:
                        raise Exception("DBC type error: {} ".format(data_type))

        elif type(file_path) == str:
            if data_type == "Message":
                info_dict = self._get_all_signals(self._parse_can_data(file_path))
            elif data_type == "Environment":
                info_dict = self._get_env_name_map(self._parse_can_data(file_path))
            else:
                raise Exception("DBC type error: {} ".format(data_type))

        return info_dict

    def write_msg_sig_to_enum_class(self, project_name: str):
        generate_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
                        + r'\project\{}\msg_sig_env_def.py'.format(project_name)

        with open(generate_path, 'w') as file:
            file.write('from enum import Enum\r\n')

            if self.__dbc_msg_path:
                message_signals_info_dict = self._read_data_according_to_dbc_type("Message", self.__dbc_msg_path)
                message_signals_name_dict = self._map_message_to_signals(message_signals_info_dict)

                messages = message_signals_name_dict.keys()
                signals = self._get_signal_list(message_signals_name_dict)

                self._write_class_info_to_file(file, "Message", messages)
                self._write_class_info_to_file(file, "Signal", signals)

            if self.__dbc_relay_path:
                relay_signal = self._get_signal_list(self.__relay_message_signals_name_dict)

                self._write_class_info_to_file(file, "RelayMessage", self.__relay_message_signals_name_dict.keys())
                self._write_class_info_to_file(file, "RelaySignal", relay_signal)

            if self.__dbc_env_path:
                env_names = self._read_data_according_to_dbc_type("Environment", self.__dbc_env_path)
                self._write_class_info_to_file(file, "EnvName", env_names)

    @staticmethod
    def _write_class_info_to_file(file, class_name, para_list):
        file.write('\r\n')
        file.write('class {}(Enum):\r\n'.format(class_name))

        for para in para_list:
            file.write("    " + para + ' = "' + para + '"\r')

    def _get_signal_list(self, name_dict: dict):
        tmp_list = []
        for item in list(name_dict.values()):
            tmp_list.extend(item)
        return list(set(tmp_list))


# 用于解析系统变量（.xml或.vsysvar文件）的类和函数
class SysHandler:
    def __init__(self, project_name: str):
        """处理系统变量.xml或.vsysvar文件 : 获取其Absolute Path"""
        self.__project_config_path = "/test_fixture/test_configuration/{}_test_configuration/{}_config.yaml". \
            format(project_name, project_name)
        self.__config = parse_config.ConfigHandler(self.__project_config_path)
        self.__sys_path = self.__config.get_config_by_name('canoe_tools')['sys_path']
        self._get_xml()

    def _get_xml(self):
        # ET去打开.xml文件或.vsysvar文件
        tree = Et.parse(self.__sys_path)
        # 获取根标签
        root = tree.getroot()
        # print(root[0])  # <Element 'systemvariables' at 0x02193B68>
        # 获取systemvariables根标签的子标签
        for arpackage in root[0].iter(namespace_tag):
            if arpackage.attrib[name_tag]:
                namespace = arpackage.attrib[name_tag]
                SysNamespacesInfo.append(namespace)

        for i in range(len(SysNamespacesInfo)):
            for arpackage in root[0][i].iter(variable_tag):
                variable = arpackage.attrib[name_tag]
                SysVariablesInfo.append(variable)
                namespace_var = SysNamespacesInfo[i] + '::' + variable
                Namespace_Var.append(namespace_var)
        return SysNamespacesInfo, SysVariablesInfo, Namespace_Var

    @staticmethod
    def write_sys_namespace_variable_to_enum_class(project_name: str):
        generate_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
                        + r'\project\{}\sys_namespace_variable_def.py'.format(project_name)

        with open(generate_path, 'w') as file:
            file.write('from enum import Enum\r\n\n')

            file.write('class Namespace(Enum):\r\n')
            for namespace_name in SysNamespacesInfo:
                file.write("    " + namespace_name + ' = "' + namespace_name + '"\r')
            file.write('\r\n')

            file.write('class Variables(Enum):\r\n')
            for var in SysVariablesInfo:
                file.write("    " + var + ' = "' + var + '"\r')
            file.write('\r\n')

            file.write('class Namespace_Variables(Enum):\r\n')
            for namespace_var in Namespace_Var:
                file.write("    " + ' "' + namespace_var + '"\r')


# 用于解析CDD（.cdd文件）的类和函数
class CddHandler:
    def __init__(self, project_name: str):
        """处理.cdd文件 : 获取其Absolute Path"""
        self.__project_config_path = "/test_fixture/test_configuration/{}_test_configuration/{}_config.yaml". \
            format(project_name, project_name)
        self.__config = parse_config.ConfigHandler(self.__project_config_path)
        self.__cdd_path = self.__config.get_config_by_name('canoe_tools')['cdd_path']

        for cdd_path in self.__cdd_path:
            self._get_cdd(cdd_path)

    # 解析cdd(.cdd格式),遍历所有P_Port
    @staticmethod
    def _get_cdd(self, path):
        tree = Et.parse(path)
        root = tree.getroot()

        for arpackage in root.iter():
            # print(arpackage.tag) # 遍历所有包节点
            if arpackage.tag in service_tag:
                for k in arpackage.iter(data_iter):
                    service = k.text
                    if service not in Services:
                        Services.append(service)
                    break

            if arpackage.tag == sub_function_tag:
                sub_function = arpackage.text
                # print(sub_function)
                if sub_function not in SubFunctions:
                    SubFunctions.append(sub_function)

            if arpackage.tag == sub_data_tag:
                for i in arpackage.iter(data_iter):
                    sub_data = i.text
                    if sub_data not in SubDatas:  # 去除重复项
                        SubDatas.append(sub_data)

        return Services, SubFunctions, SubDatas

    @staticmethod
    def write_cdd_qualifier_to_enum_class(project_name: str):

        generate_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
                        + r'\project\{}\cdd_qualifier_def.py'.format(project_name)

        with open(generate_path, 'w') as file:
            file.write('from enum import Enum\r\n\n')

            file.write('class Service(Enum):\r\n')
            for service in Services:
                file.write("    " + service + ' = "' + service + '"\r')
            file.write('\r\n')

            file.write('class SubFunctions(Enum):\r\n')
            for sub_function in SubFunctions:
                file.write("    " + sub_function + ' = "' + sub_function + '"\r')
            file.write('\r\n')

            file.write('class SubParameter(Enum):\r\n')
            for sub_data in SubDatas:
                file.write("    " + sub_data + ' = "' + sub_data + '"\r')


class PDXHandler:
    def __init__(self, project_name: str):
        """处理PDX文件 : Absolute Path"""
        self.__project_config_path = "/test_fixture/test_configuration/{}_test_configuration/{}_config.yaml". \
            format(project_name, project_name)
        self.__config = parse_config.ConfigHandler(self.__project_config_path)
        self.__pdx_path = self.__config.get_config_by_name('canoe_tools')['pdx_path']

        self.__services = []
        self.__requests = []
        self.__structures = []

        if self.__pdx_path:
            self.__pdx_db = self._parse_pdx_data(self.__pdx_path)
            self._get_service_request_in_pdx_data()

    @staticmethod
    def _parse_pdx_data(path):
        return odxtools.load_pdx_file(path)

    def _get_service_request_in_pdx_data(self):
        for container in self.__pdx_db.diag_layer_containers:
            for item in container.base_variants:
                for ser in item.services:
                    self.__services.append(ser.short_name)

                for req in item.requests:
                    self.__requests.append(req.short_name)

                for structure in item.local_diag_data_dictionary_spec.structures:
                    self.__structures.append(structure.short_name)

    def write_pdx_data_to_enum_class(self, project_name: str):
        generate_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) \
                        + r'\project\{}\pdx_qualifier_def.py'.format(project_name)

        with open(generate_path, 'w') as file:
            file.write('from enum import Enum\r\n\n')

            file.write('class Service(Enum):\r\n')
            for service in self.__services:
                file.write("    " + service + ' = "' + service + '"\r')
            file.write('\r\n')

            file.write('class Requests(Enum):\r\n')
            for request in self.__requests:
                file.write("    " + request + ' = "' + request + '"\r')
            file.write('\r\n')

            file.write('class Structures(Enum):\r\n')
            for structure in self.__structures:
                file.write("    " + structure + ' = "' + structure + '"\r')
