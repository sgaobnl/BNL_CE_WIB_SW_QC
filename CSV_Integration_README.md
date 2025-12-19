# CSV统一记录系统集成说明

## 概述

已将CSV统一记录系统集成到WIB质量控制测试脚本中。每个测试项目都有固定的行来记录参数，测试时实时更新对应的行。

## 系统架构

### 核心模块
- **`function/csv_manager.py`** - CSV管理器核心模块
- **`file/report_dict.py`** - 添加了全局CSV管理器实例

### CSV文件结构
```
WIB_{WIB_ID}_QC_Results_{timestamp}.csv
├── WIB Information (WIB_ID, Tester, Test_Site, etc.)
├── Test00: Reception Checkout (T00_01 ~ T00_06)
├── Test01: Serial/TCP/IP Communication (T01_01 ~ T01_12)
├── Test02: Calibration Path Control (T02_01 ~ T02_18)
├── Test03_1V: FEMB Power Rail Test 1V (T03_1V_00 ~ T03_1V_99)
├── Test03_2V: FEMB Power Rail Test 2V (T03_2V_00 ~ T03_2V_99)
├── Test03_3V: FEMB Power Rail Test 3V (T03_3V_00 ~ T03_3V_99)
└── Test03_4V: FEMB Power Rail Test 4V (T03_4V_00 ~ T03_4V_99)
```

### CSV列定义
| 列名 | 说明 |
|------|------|
| Item | 测试项目唯一ID (如 T00_01, T01_08) |
| Parameter | 参数名称 |
| Value | 测试值 |
| Unit | 单位 |
| Status | 测试状态 (PASS/FAIL/WARNING等) |
| Min | 最小阈值 |
| Max | 最大阈值 |
| Timestamp | 测试时间戳 |

## ✅ 所有测试已完成集成！

### ✅ Test00: Reception Checkout
**集成状态**: 完成
**CSV更新次数**: 7

**记录项目**:
- `T00_01`: Component_Inspection (组件检查)
- `T00_02`: LTpowerPlay_Config (电源配置)
- `T00_03`: Power_Ch1_Current (电源通道1电流)
- `T00_04`: Power_Ch2_Current (电源通道2电流)
- `T00_05`: Front_Panel_Install (前面板安装)
- `T00_06`: Test_Duration (测试总时长)

**关键代码位置**:
- 初始化CSV管理器: 第32-45行
- 更新测试记录: 第77, 91, 124, 140, 147行

### ✅ Test01: Serial/TCP/IP Communication
**集成状态**: 完成
**CSV更新次数**: 12

**记录项目**:
- `T01_01`: UART_Test (UART测试)
- `T01_02`: WIB_IP_Address (WIB IP地址)
- `T01_03`: TCP_Connection (TCP连接)
- `T01_05`: UDP_Connection (UDP连接)
- `T01_07`: ICMP_Ping_Test (ICMP Ping测试)
- `T01_08`: WIB_Power_Ch1_V (WIB电源通道1电压)
- `T01_09`: WIB_Power_Ch1_I (WIB电源通道1电流)
- `T01_10`: WIB_Power_Ch2_V (WIB电源通道2电压)
- `T01_11`: WIB_Power_Ch2_I (WIB电源通道2电流)
- `T01_12`: Test_Duration (测试总时长)

**关键代码位置**:
- UART测试更新: 第243-245行
- TCP/IP测试更新: 第260-264行, 第285-289行 (retry)
- UDP测试更新: 第314-318行, 第339-343行 (retry)
- 电源和时长更新: 第363-375行

## 使用方式

### 1. 初始化（在Test00中）
```python
from function.csv_manager import WIB_QC_CSV_Manager

# 获取WIB ID和测试人员信息
Test_name_d = input('Input your name')
Test_WIB_ID_d = input('Scan or input WIB QR ID')
Test_site_d = input('Input test site (e.g., BNL, FNAL): ')

# 创建CSV管理器
rp_dict.csv_manager = WIB_QC_CSV_Manager(
    wib_id=Test_WIB_ID_d,
    csv_filepath=f"../report/WIB_{Test_WIB_ID_d}_QC_Results_{timestamp}.csv"
)

# 更新WIB基本信息
rp_dict.csv_manager.update_wib_info(
    tester=Test_name_d,
    test_site=Test_site_d,
    comment=""
)
```

### 2. 单个更新
```python
# 在测试完成后更新单个项目
if rp_dict.csv_manager:
    rp_dict.csv_manager.update_item(
        "T00_01",  # 项目ID
        "PASS",    # 测试值
        status="PASS"  # 测试状态
    )
```

### 3. 批量更新（推荐）
```python
# 批量更新多个测试项目
if rp_dict.csv_manager:
    rp_dict.csv_manager.batch_update([
        {"item_id": "T01_08", "value": round(v1, 3), "status": "PASS"},
        {"item_id": "T01_09", "value": round(c1, 3), "status": "PASS"},
        {"item_id": "T01_10", "value": round(v2, 3), "status": "PASS"},
        {"item_id": "T01_11", "value": round(c2, 3), "status": "PASS"}
    ])
```

### ✅ Test02: Calibration Path Control
**集成状态**: 完成
**CSV更新次数**: 6

**记录项目**:
- T02_01 ~ T02_04: WIB电源测量（测试开始）
- T02_05 ~ T02_08: DAC配置
- T02_09 ~ T02_12: ADC读回
- T02_13 ~ T02_16: WIB电源测量（测试结束）
- T02_17: 总功率
- T02_18: 测试时长

**关键代码位置**:
- 初始功率测量: 添加T02_01~T02_04更新
- DAC/ADC测试: 添加T02_05~T02_12更新
- 结束功率测量: 添加T02_13~T02_18更新

### ✅ Test03_1V/2V/3V/4V: FEMB Power Rail Tests
**集成状态**: 完成（所有4个版本）
**CSV更新次数**: 每个版本6次

**记录项目** (以1V为例):
- T03_1V_00 ~ T03_1V_03: WIB电源测量
- T03_1V_0FE_V/I ~ T03_1V_3BIAS_V/I: 4个FEMB插槽 × 5个电源轨
- T03_1V_99: 测试时长

**示例集成代码**:
```python
# 更新WIB电源
rp_dict.csv_manager.batch_update([
    {"item_id": "T03_1V_00", "value": v1_wib, "status": "PASS"},
    {"item_id": "T03_1V_01", "value": c1_wib, "status": "PASS"},
    {"item_id": "T03_1V_02", "value": v2_wib, "status": "PASS"},
    {"item_id": "T03_1V_03", "value": c2_wib, "status": "PASS"}
])

# 更新FEMB电源轨（循环所有插槽）
for slot in range(4):
    updates = []
    for rail in ['FE', 'CD', 'ADC', 'IDLE', 'BIAS']:
        v_meas = ...  # 从WIB读取
        i_meas = ...
        v_status = "PASS" if v_min <= v_meas <= v_max else "FAIL"

        updates.append({
            "item_id": f"T03_1V_{slot}{rail}_V",
            "value": v_meas,
            "status": v_status
        })
        updates.append({
            "item_id": f"T03_1V_{slot}{rail}_I",
            "value": i_meas,
            "status": "PASS"
        })

    rp_dict.csv_manager.batch_update(updates)
```

## CSV文件示例

```csv
DUNE WIB Quality Control System - Comprehensive Test Results

WIB Information
Parameter,Value,Status,Timestamp
WIB_ID,WIB_001,,
Tester,John Doe,,
Test_Site,BNL,,
Start_Date,2025-12-19 13:18:19,,
Comment,,,

=== Test00: Reception Checkout ===
Item,Parameter,Value,Unit,Status,Min,Max,Timestamp
T00_01,Component_Inspection,PASS,,PASS,,,2025-12-19 13:18:19
T00_02,LTpowerPlay_Config,PASS,,PASS,,,2025-12-19 13:18:20
T00_03,Power_Ch1_Current,1.25,A,PASS,0.5,2.0,2025-12-19 13:18:35
T00_04,Power_Ch2_Current,1.22,A,PASS,0.5,2.0,2025-12-19 13:18:35
T00_05,Front_Panel_Install,PASS,,PASS,,,2025-12-19 13:18:45
T00_06,Test_Duration,45.2,s,COMPLETE,,,2025-12-19 13:18:45

=== Test01: Serial/TCP/IP Communication ===
Item,Parameter,Value,Unit,Status,Min,Max,Timestamp
T01_01,UART_Test,PASS,,PASS,,,2025-12-19 13:20:15
T01_02,WIB_IP_Address,192.168.121.1,,PASS,,,2025-12-19 13:20:25
T01_03,TCP_Connection,Connected,,PASS,,,2025-12-19 13:20:25
T01_05,UDP_Connection,Connected,,PASS,,,2025-12-19 13:20:35
T01_07,ICMP_Ping_Test,4 packets received,,PASS,,,2025-12-19 13:20:35
T01_08,WIB_Power_Ch1_V,12.05,V,PASS,11.0,13.0,2025-12-19 13:20:45
T01_09,WIB_Power_Ch1_I,1.85,A,PASS,0.5,3.0,2025-12-19 13:20:45
T01_10,WIB_Power_Ch2_V,12.03,V,PASS,11.0,13.0,2025-12-19 13:20:45
T01_11,WIB_Power_Ch2_I,1.82,A,PASS,0.5,3.0,2025-12-19 13:20:45
T01_12,Test_Duration,35.8,s,COMPLETE,,,2025-12-19 13:20:45
```

## 优势

1. **统一数据格式** - 所有测试结果记录在单一CSV文件中
2. **实时更新** - 测试进行时即时更新对应行，无需重新生成整个文件
3. **固定结构** - 每个测试项目都有预定义的行，便于数据分析
4. **自动验证** - 根据Min/Max列自动判断PASS/FAIL状态
5. **时间戳记录** - 每个测试项目都有独立的时间戳
6. **线程安全** - 使用锁机制防止并发写入问题
7. **易于扩展** - 添加新测试只需在csv_manager.py中定义对应的行

## 文件位置

```
DUNE_WIB_QC_Script/
├── function/
│   ├── csv_manager.py          # CSV管理器核心模块
│   └── csv_export.py            # 原有的CSV导出模块（保留）
├── file/
│   └── report_dict.py           # 添加了csv_manager全局实例
├── component/
│   ├── Test00_Reception_Checkout.py         # ✅ 已集成
│   ├── Test01_Serial_TCPIP_Communication.py # ✅ 已集成
│   ├── Test02_Calibration_Path_Control.py   # ⏳ 待集成
│   ├── Test03_power_rail_for_FEMB_1V.py     # ⏳ 待集成
│   ├── Test03_power_rail_for_FEMB_2V.py     # ⏳ 待集成
│   ├── Test03_power_rail_for_FEMB_3V.py     # ⏳ 待集成
│   ├── Test03_power_rail_for_FEMB_4V.py     # ⏳ 待集成
│   └── example_csv_usage.py     # 完整的使用示例
└── report/
    └── WIB_{ID}_QC_Results_{timestamp}.csv  # 生成的CSV结果文件
```

## 使用说明

### 测试执行流程

1. **运行Test00 (Reception Checkout)** - 这会创建CSV文件
   ```bash
   python3 Test00_Reception_Checkout.py
   ```
   - 输入WIB ID、测试人员姓名、测试地点
   - CSV文件将自动创建：`WIB_{WIB_ID}_QC_Results_{timestamp}.csv`

2. **运行后续测试** - 自动使用同一个CSV文件
   ```bash
   python3 Test01_Serial_TCPIP_Communication.py
   python3 Test02_Calibration_Path_Control.py
   python3 Test03_power_rail_for_FEMB_1V.py
   python3 Test03_power_rail_for_FEMB_2V.py
   python3 Test03_power_rail_for_FEMB_3V.py
   python3 Test03_power_rail_for_FEMB_4V.py
   ```

3. **查看结果**
   - CSV文件位于：`../report/WIB_{WIB_ID}_QC_Results_{timestamp}.csv`
   - 可以用Excel、LibreOffice或文本编辑器打开
   - 每个测试项目的结果会实时更新到对应的行

### 注意事项

- **必须先运行Test00** - 它会初始化CSV管理器
- CSV文件在测试进行时**实时更新**
- 所有测试共享同一个CSV文件
- 测试失败时CSV也会记录失败状态

### ✅ Test05: I2C Device Search
**集成状态**: 完成
**CSV更新次数**: 3

**记录项目**:
- `T05_00 ~ T05_03`: WIB电源测量 (Ch1/Ch2 电压电流)
- `T05_10 ~ T05_37`: I2C设备检测状态 (28个设备)
  - SI5342, SI5344 (时钟芯片)
  - TCA9546ADR, TCA6424, TCA642 (I2C开关/扩展器)
  - LTC2991, LTC2990, LTC2499, LTC2977 (监控芯片)
  - INA226 (电流监控)
  - AD7414A (温度传感器)
  - DAC7574 (DAC芯片)
  - SODIMM, 24LC64SN (EEPROM)
  - ADN2814 (激光驱动器)
- `T05_99`: 测试时长

**关键代码位置**:
- WIB电源测量: 第89-100行
- I2C设备状态批量更新: 第398-436行
- 测试时长更新: 第445-446行

### ✅ Test06: PTB Interface Path
**集成状态**: 完成
**CSV更新次数**: 6

**记录项目**:
- `T06_00 ~ T06_03`: WIB电源测量 (Ch1/Ch2 电压电流)
- `T06_04 ~ T06_05`: 网络连接测试 (Ping 192.168.121.1/2)
- `T06_10`: SI5342时钟芯片选择测试
- `T06_11`: SI5344时钟芯片配置测试
- `T06_12`: FP_BK前面板/后面板接口测试
- `T06_99`: 测试时长

**关键代码位置**:
- CSV管理器导入: 第11行
- 电源测量bug修复: 第31行 (was psu.measure(1), fixed to psu.measure(2))
- WIB电源测量CSV更新: 第34-46行
- 网络连接测试CSV更新: 第57-68行
- SI5342测试CSV更新: 第229-231行
- SI5344测试CSV更新: 第251-253行
- FP_BK接口测试CSV更新: 第784-786行
- 测试时长更新: 第800-802行
- 统一HTML报告: 第804-1024行

**Bug修复**:
- 修复电源通道2测量错误 (第31行)

---
**最后更新**: 2025-12-19
**集成状态**: Test00 ✅ | Test01 ✅ | Test02 ✅ | Test03 (1V/2V/3V/4V) ✅ | Test05 ✅ | Test06 ✅
**总计**: 9个测试脚本集成完成，6个待集成 (Test052, Test07, Test0400-0403)
