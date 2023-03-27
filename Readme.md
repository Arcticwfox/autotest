### 1. Note:

+ 运行前请确定CANoe工程是否打开
+ 请修改 config.yaml 文件里的参数配置
+ 新增的testcase路径：test_case/tc_xxx.py
+ 运行util.code_gen.gen_dbc_name_def.py自动生成msg_sig_env_def.py
+ 编写项目对应的dataset处理文件：dataset_handler.xxx_dataset_handler.py, 参考ford_dataset_handler.py
+ 所有的路径都设置为 绝对路径
+ 请确保所有三方库已安装, 生成requirements.txt: pipreqs ./ --encoding=utf-8, 安装requirements.txt：pip install -r requirements.txt
+ 生成目录树: tree /f >tree.txt

### 2. Update:

1. 更新Core.instrument_control里相关文件：捕获异常,记录至log文件.
2. 新增self_test方法：运行case前将执行self_test检测测试环境，如果不满足测试条件，testcase将不会运行，错误会记录在log文件中.
   不同testcase的self_test不同，按需修改/增加.
3. 更新log记录路径, 新增清除log缓存.
4. battery_xxx_control.py：新增设置电源默认状态方法
5. 新增precondition_test_interface.py
6. 新增QUICKSTART.md, INSTALL.md文件
7. 修改Core.util.code_gen.gen_dbc_name_def.py, 生成继电器DBC里定义的MessageSignal枚举类
8. 修改Core/instrument_control/battery_ngi.py
9. 新增Core/project, parameter_def.py等文件移至project文件夹.
10. 新增Ford L3安全访问

### 3. 目录结构描述

```
D:.
│  conftest.py                   // pytest自动调用该文件，用于编写本地插件
│  INSTALL.md
│  QUICKSTART.md                //快速入门
│  Readme.md                       // help
│  requirements.txt                //依赖包及版本信息
│  Run.py                              // 程序入口
│  test_information.txt          //测试信息
│  
│              
├─Core   // 具体操作逻辑
│  │  global_variables_for_test_report.py
│  │  log_handler.py
│  │  parse_config.py
│  │  parse_yaml_case.py
│  │  read_test_info.py
│  │  test.py
│  │  
│  ├─can_related    // 和CAN相关的文件
│  │  │  canoe_connect.py
│  │  │  can_control.py
│  │  └  parse_canoe_tools.py  
│  │  
│  │          
│  ├─dataset_handler     //处理dataset
│  │  │  data_set.py
│  │  │  e001_dataset_handler.py
│  │  │  ford_dataset_handler.py
│  │  │  H93_dataset_handler.py
│  │  │  ldm206x_dataset_handler.py  
│  │  └
│  │          
│  ├─instrument_control      // 通过串口控制设备
│  │  │  battery_chroma_control.py
│  │  │  battery_gmc_control.py
│  │  │  battery_itech_control.py
│  │  │  battery_korad_control.py
│  │  │  battery_ngi.py
│  │  │  bin_set_module_control.py
│  │  │  read_curr_vol_module_control.py
│  │  │  serial_control.py 
│  │  └
│  │          
│  ├─project     //项目相关内容
│  │  ├─e001
│  │  │      parameter_def.py
│  │  │      
│  │  ├─ford
│  │  │      calc_process.py
│  │  │      cdd_qualifier_def.py
│  │  │      dbl_calc.py
│  │  │      EncryptedUserData.key
│  │  │      FordUnlockKBD.dll
│  │  │      KeyDownX64.dll
│  │  │      msg_sig_env_def.py
│  │  │      parameter_def.py
│  │  │      security_access.py
│  │  │      spot_calc.py
│  │  │      
│  │  ├─H93
│  │  │      parameter_def.py
│  │  │      
│  │  └─ldm206x
│  │          parameter_def.py
│  │          
│  └─util
│      └─code_gen   //枚举类的生成工具
│              demo_msg_sig_env_def.py
│              gen_cdd_name_def.py
│              gen_dbc_name_def.py
│              gen_sys_name_def.py
│              
├─test_fixture
│  ├─test_configuration
│  │  │  CAN_control _Relay_20221128.dbc
│  │  │  config.yaml
│  │  │  FaultInject_LDM12B_AB_DatasetVB009.xlsm
│  │  │  pytest.ini
│  │  │  report.css
│  │  │  
│  │  └─ldm206x
│  │              
│  └─test_interface     // 给test_case提供测试接口，按功能/项目增加
│      ├─e001_test_interface
│      │      faultinjection.py
│      │      pcba_derating.py
│      │      precondition_test_interface.py
│      │      
│      ├─ford_test_interface
│      │  │  bending_test_interface.py
│      │  │  bin_test_interface.py
│      │  │  classlvl_test_interface.py
│      │  │  dbl_test_interface.py
│      │  │  drl_test_interface.py
│      │  │  power_derating_test_interface.py
│      │  │  precondition_test_interface.py
│      │  │  sml_test_interface.py
│      │  │  turn_indicator_test_interface.py
│      │  │  
│      │  └
│      │          
│      └─ldm206_test_interface
│              BC.py
│              faultinjection.py
│              KL30_derate.py
│              pcba_derate.py
│              precondition_test_interface.py
│              temperature_derate.py
│              Voltage_manager.py
│              
├─test_profile
│  ├─test_case
│  │  ├─e001_test_case
│  │  │      tc_faultInjection.py
│  │  │      tc_faultInjection.yaml
│  │  │      
│  │  ├─ford_test_case
│  │  │  │  tc_bending.py
│  │  │  │  tc_bending.yaml
│  │  │  │  tc_bin.py
│  │  │  │  tc_bin.yaml
│  │  │  │  tc_classHB.py
│  │  │  │  tc_class_lvl.py
│  │  │  │  tc_class_lvl.yaml
│  │  │  │  tc_dbl.py
│  │  │  │  tc_dbl.yaml
│  │  │  │  tc_drl_po.py
│  │  │  │  tc_drl_po.yaml
│  │  │  │  tc_power_derating.py
│  │  │  │  tc_power_derating.yaml
│  │  │  │  tc_sml.py
│  │  │  │  tc_sml.yaml
│  │  │  │  tc_turn_indicator.py
│  │  │  │  tc_turn_indicator.yaml
│  │  │  │  
│  │  │  └
│  │  │          
│  │  └─ldm206_test_case
│  │      │  tc_BC.py
│  │      │  tc_BC.yaml
│  │      │  tc_faultInjection.py
│  │      │  tc_faultInjection.yaml
│  │      │  tc_KL30_derate.py
│  │      │  tc_KL30_derate.yaml
│  │      │  tc_pcba.py
│  │      │  tc_pcba.yaml
│  │      │  tc_temperature_derate.py
│  │      │  tc_temperature_derate.yaml
│  │      │  tc_voltage_manager.py
│  │      │  tc_voltage_manager.yaml
│  │      │  
│  │      └
│  │                      
│  └─test_sets
├─test_result
│  ├─assets
│  │      style.css
│  │      
│  ├─test_log   // 测试log文件
│  │      log.txt
│  │      
│  └─test_report   // 测试报告
│          LDM_12B_Ford_BIN_Test_2023-01-03-17-26-45.html
        

```

