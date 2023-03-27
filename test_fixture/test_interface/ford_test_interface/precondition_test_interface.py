import time
import math
from func_timeout import func_set_timeout
from Core.project.ford import parameter_def, msg_sig_env_def, cdd_qualifier_def, security_access
from Core import parse_config
from Core.can_related import canoe_connect, can_control
from Core.dataset_handler import ford_dataset_handler
from Core.instrument_control import battery_chroma_control, read_curr_vol_module_control, bin_set_module_control, \
    battery_korad_control
from Core.project.ford.calc_process import CalHandler
from Core.log_handler import LogHandler

logger = LogHandler.get_log_handler(__name__, "info")

config = parse_config.ConfigHandler()

canoe_app = canoe_connect.CanoeSync()
dataset = ford_dataset_handler.FordDatasetHandler()
bin_set = bin_set_module_control.BinSetModuleControl(config)
battery = battery_chroma_control.BatChromaControl(config)
battery_KL31 = battery_korad_control.BatKoradControl(config)
read_curr_vol = read_curr_vol_module_control.ReadCurrVolModuleControl(config)
calc = CalHandler(dataset, canoe_app, battery)
can_msg = can_control.Msg(config, True)
canoe_app.cdd_name = 'Lighting_Driver_Control_Module_A'


@func_set_timeout(5)
def get_ecu_side():
    while True:
        msg = can_msg.bus.recv(100)
        if msg.arbitration_id == 0x74:
            cdd_name = 'Lighting_Driver_Control_Module_A'
            side = parameter_def.ecu_side.left.value
            can_msg.diag_send_msg_id = 0x6f6
            can_msg.diag_rec_msg_id = 0x6fe
            return side, cdd_name
        elif msg.arbitration_id == 0x75:
            cdd_name = 'Lighting_Driver_Control_Module_B'
            side = parameter_def.ecu_side.right.value
            can_msg.diag_send_msg_id = 0x6f7
            can_msg.diag_rec_msg_id = 0x6ff
            return side, cdd_name
        elif msg.arbitration_id == 0x7C:
            cdd_name = 'Lighting_Driver_Control_Module_C'
            side = parameter_def.ecu_side.left.value
            can_msg.diag_send_msg_id = 0x6d7
            can_msg.diag_rec_msg_id = 0x6df
            return side, cdd_name
        elif msg.arbitration_id == 0x7D:
            cdd_name = 'Lighting_Driver_Control_Module_D'
            side = parameter_def.ecu_side.right.value
            can_msg.diag_send_msg_id = 0x6d6
            can_msg.diag_rec_msg_id = 0x6de
            return side, cdd_name


def check_ecu_communication():
    try:
        side, cdd_name = get_ecu_side()
        canoe_app.cdd_name = cdd_name
        calc.side = side
    except BaseException as err:
        raise Exception('No feedback from the ECU, please check the CAN connection.\n{}'.format(err))


def check_read_current_voltage_module_status():
    for i in range(4):
        time.sleep(1)
        try:
            read_curr_vol.read_current(i + 1)
        except BaseException as err:
            raise Exception("{}: Read_current_voltage_module {} has no response!".format(err, i + 1))


def check_canoe_connection():
    canoe_app.stop_measurement()
    time.sleep(1)
    canoe_app.start_measurement()


def check_battery_connection():
    battery.set_default_status()
    battery.read_output_voltage()


def check_bin_set_module():
    for i in range(3):
        time.sleep(1)
        try:
            bin_set.set_vol_base_on_resistor(i + 1, 0)
        except BaseException as err:
            raise Exception("{}: BIN_set_module {} has no response!".format(err, i + 1))


# todo:更新self test方法

def prepare_for_test():
    """
    Precondition: Set CANoe Request. Set input voltage and current.
    """
    battery.set_default_status()

    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.SwitchOnOff.value, 0x01)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.Ignition_Status_4.value, 0x04)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLampLoFlOn_B_Stat_1.value, 0x01)
    canoe_app.set_EnvVar(msg_sig_env_def.EnvName.HeadLampLoFrOn_B_Stat_1.value, 0x01)
