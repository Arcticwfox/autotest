# 快速开始

## 使用简介

### 1. 测试环境相关

#### 1.1 相关依赖

在终端运行如下命令即可安装运行该项目所需要的相关依赖包：

```sh
pip install -r requirements.txt
```

#### 1.2 环境配置

- 操作系统: Windows
- Python版本: Python3.6+ (建议使用 3.10，不要安装多个python版本)
- CANoe版本: 11.0

#### 1.3 硬件设备

- 可编程电源
- 电流/电压检测模块
- Vector硬件
- 24路-电流-电压输出模块 + 电压跟随器
- 故障注入模块

### 2. 修改配置文件

**配置文件路径为：test_fixture/test_configuration/config.yaml**

- 修改所使用设备(电源，电流电压检测模块，BIN设置模块，Vector硬件)的参数：COM,波特率,默认电压电流等.
- 修改Dataset, CANoe_tools相关路径（绝对路径）.
- Dataset下的内容根据项目case需要新增/修改.
- 其他配置文件，如：dataset，可以放到test_fixture/test_configuration路径下.
- 不要修改test_fixture/test_configuration路径下的pytest.ini, report.css.
- 以上没有用到的设备/Dataset/CANoe_tools等, 可以不用修改相关配置.

### 3. 自动生成msg_sig_env_def.py/cdd_qualifier_def.py/sys_namespace_variable_def.py, 修改parameter_def.py

**如果需要用到DBC里定义的message，signal，env等变量，可以使用该工具自动生成msg_sig_env_def.py
不需要可跳过该步骤.**
**如果需要用到CDD里定义的service，sub_function，data_qualifier等变量，可以使用该工具自动生成cdd_qualifier_def.py
不需要可跳过该步骤.**
**如果需要用到系统变量里定义的namespace，variables等变量，可以使用该工具自动生成sys_namespace_variable_def.py
不需要可跳过该步骤.**

- 使用该工具前，请先在config.yaml文件里配置CANoe_tools相关路径, 创建项目文件夹Core/project/xxx(项目名)
- 运行Core.util.code_gen.gen_dbc_name_def.py(如下)即可自动生成Core.project.xxx.msg_sig_env_def.py
- 运行Core.util.code_gen.gen_cdd_name_def.py(如下)即可自动生成Core.project.xxx.cdd_qualifier_def.py
- 运行Core.util.code_gen.gen_sys_name_def.py(如下)即可自动生成Core.project.xxx.sys_namespace_variable_def.py

```sh
Core/util/code_gen/gen_dbc_name_def.py
```

```sh
Core/util/code_gen/gen_cdd_name_def.py
```

```sh
Core/util/code_gen/gen_sys_name_def.py
```

- 按项目需求修改project/xxx(项目名)/parameter_def.py(枚举类文件)

### 4. 编写dataset处理文件

**如果没有dataset或者不需要读取dataset数据，可跳过该步骤.**

根据项目新建Core/dataset_handler/xxx_dataset_handler.py,
参考Core/dataset_handler/ford_dataset_handler.py.

### 5. 编写testcase

**编写testcase主要分为以下3个步骤**

#### 5.1 新建 precondition_test_interface

根据项目新建test_fixture/test_interface/xxx(项目名)_test_interface/precondition_test_interface.py,
参考ford_test_interface/precondition_test_interface.py.

precondition_test_interface.py主要用于实现测试的前提条件以及提供self-test方法.

前提条件按项目需求新增.

目前ford_test_interface/precondition_test_interface.py里已实现的self-test包括：

- check_ecu_communication: 检查ECU通信
- check_read_current_voltage_module_status: 检查电流/电压检测模块
- check_canoe_connection: 检查CANoe通信
- check_bin_set_module: 检查24路-电流-电压输出模块
- check_battery_connection: 检查电源状态
  上述方法按需修改/增加。

#### 5.2 新建 xxx_test_interface

根据功能建立test_fixture/test_interface/xxx(项目名)_test_interface/xxx(功能名)_test_interface.py，
参考ford_test_interface/drl_test_interface.py.

test_interface.py文件主要通过调用Core文件夹的内容，按testcase文档里的步骤实现功能，然后给testcase提供测试接口.

#### 5.3 新建 xxx_test_testcase

根据功能建立test_profile/test_case/xxx(项目名)_test_case/tc_xxx(功能名).py，参考ford_test_case
/tc_drl_po.py.

tc_xxx.py文件通过读取tc_xxx.yaml文件里的数据，实现testcase.

#### 5.4 新建 xxx_yaml文件

根据功能建立test_profile/test_case/xxx(项目名)_test_case/tc_xxx(功能名).yaml，参考ford_test_case
/tc_drl_po.yaml.

tc_xxx.yaml用于编写测试案例，实现测试数据和脚本分离.

### 6. 运行程序入口 Run.py

修改test_information.txt，点击运行Run.py

### 7. 查看log和报告
**log文件路径：test_result/test_log/log.txt, 报告路径：test_result/test_report**

当testcase运行结束后，会自动生成报告.
如果testcase运行失败，可在log文件中查看报错原因.

# Note

- 运行前, 请先打开对应的CANoe工程.
- 不要修改Core文件夹下的其他文件，如果有需要，请联系Author进行修改.
  Email:
  siwei.lu@keboda.com
  yanjiao.li@keboda.com

