"""
This sample demonstrates how to connect CANoe via COM API using python script.

@Author: Siwei.Lu
@Date: 2022.11.26

Limitations:
 - choose a specific CANoe project before running this script.
"""

import time
from win32com.client import *
import sys

from Core.log_handler import LogHandler

logger = LogHandler.get_log_handler(__name__, "info")


class CanoeSync(object):
    def __init__(self):
        app = DispatchEx('CANoe.Application')
        app.Configuration.Modified = False
        self.App = app
        self.__bus = "CAN"
        self.__cdd_name = None  # eg: "Lighting_Driver_Control_Module_C"
        self.__network_name = "CAN"
        # Networks("CAN节点的名字: 在simulation setup里查看")， Devices（"CDD的名字：在诊断窗口查看"）

    def start_measurement(self):
        retry = 0
        retry_counter = 5
        # try to establish measurement within 20s timeout
        while not self.App.Measurement.Running and (retry < retry_counter):
            self.App.Measurement.Start()
            time.sleep(1)
            retry += 1
        if retry == retry_counter:
            raise RuntimeWarning("CANoe start measurement failed, Please Check Connection!")

    def stop_measurement(self):
        if self.App.Measurement.Running:
            self.App.Measurement.Stop()
        else:
            pass

    def get_signal(self, msg_name, signal_name):
        """
        Get signal value.
        @param msg_name: Message name.
        @param signal_name: Signal name.
        @return: Signal value
        """
        Signal = self.App.GetBus(self.__bus).GetSignal(1, msg_name, signal_name)  # channel_num, message name, signal name
        return Signal.value

    def set_signal(self, msg_name, signal_name, set_value):
        """
        Before using this function, please configure IL.
        """
        Signal = self.App.GetBus(self.__bus).GetSignal(1, msg_name, signal_name)
        Signal.value = set_value

    def set_doublesignal(self, msgName, signalName1, setValue1, signalName2, setValue2):
        """
        Set the values of both signals at the same time.
        Before using this function, please configure IL!!!
        """
        Signal1 = self.App.GetBus(self.__bus).GetSignal(1, msgName, signalName1)
        Signal1.value = setValue1
        Signal2 = self.App.GetBus(self.__bus).GetSignal(1, msgName, signalName2)
        Signal2.value = setValue2

    def set_EnvVar(self, EnvVar, setValue: int):
        """
        Set the environment value to the given value.
        @param EnvVar: environment value name
        @param setValue: given value
        """
        value = self.App.Environment.GetVariable(EnvVar)
        value.value = setValue

    def get_EnvVar(self, EnvVar):
        """
        get the environment value to the given value.
        @param EnvVar: environment value name
        """
        value = self.App.Environment.GetVariable(EnvVar)
        return int(value)

    def get_SysVar(self, ns_name, sysvar_name):
        """
        get the system value to the given value.
        @param ns_name: Name space
        @param sysvar_name: system value name
        """
        systemCAN = self.App.System.Namespaces
        sys_namespace = systemCAN(ns_name)
        sys_value = sys_namespace.Variables(sysvar_name)
        return sys_value.Value

    def set_SysVar(self, ns_name, sysvar_name, var):
        """
        set the system value to the given value.
        @param ns_name: Name space
        @param sysvar_name: system value name
        @param var: given value
        """
        systemCAN = self.App.System.Namespaces
        sys_namespace = systemCAN(ns_name)
        sys_value = sys_namespace.Variables(sysvar_name)
        sys_value.Value = var

    @property
    def bus(self):
        return self.__bus

    @bus.setter
    def bus(self, bus_type):
        self.__bus = bus_type

    @property
    def cdd_name(self):
        return self.__cdd_name

    @cdd_name.setter
    def cdd_name(self, set_cdd_name: str):
        self.__cdd_name = set_cdd_name
        self._set_diag_device()

    @property
    def network_name(self):
        return self.__network_name

    @network_name.setter
    def network_name(self, set_network_name: str):
        self.__network_name = set_network_name

    def _set_diag_device(self):
        if (self.__cdd_name is None) or (self.__network_name is None):
            raise Exception("Please set cdd name and network name!")
        else:
            try:
                self.DiagDev = self.App.Networks(self.__network_name).Devices(self.__cdd_name).Diagnostic
            except BaseException as err:
                print("Please set the correct cdd name and network name!\n{}".format(err))
                logger.error("Please set the correct cdd name and network name!\n{}".format(err))

    def send_diag_req(self, req_name: str, para: list or str = None, para_value: list or int = None):
        """
        Send diagrequest base on given request name.
        @param req_name: Defined in CDD file. eg: "Method_2_Data_Type_1_Write"
        @param para: Parameter of DID, eg: ["PWM1_Function_Assign_cfg", "PWM2_Function_Assign_cfg"]
        @param para_value: value of Parameter, eg:  [5,5]
        @return: DID response
        """
        try:
            req = self.DiagDev.CreateRequest(req_name)
        except BaseException as err:
            print("No CDD_Name or Network_Name set! \n", err)
            logger.error("No CDD_Name or Network_Name set! \n{}".format(err))
            sys.exit()
            # raise Exception("No CDD_Name or Network_Name set! \n", err)

        if para is not None:
            if (type(para) is str) and (type(para_value) is int):
                req.SetParameter(para, para_value)
            elif (type(para) is list) and (type(para_value) is list):
                for i in range(len(para_value)):
                    req.SetParameter(para[i], para_value[i])
            else:
                raise Exception("Inconsistent types of {} and {}!".format(para, para_value))

        req.Send()
        while req.Pending:
            time.sleep(0.2)

        count = req.Responses.count
        if count == 0:
            print("{}: No Response received!".format(req_name))
        else:
            resp = req.Responses(count)
            if req.Responses(1).Positive:  # 判断是否为肯定响应
                stream = resp.Stream.tolist()
                return stream
            else:
                raise Exception("DID {} get a negative response".format(req_name))
