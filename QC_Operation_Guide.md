# CTS FEMB QC 测试系统操作指南

## 目录
1. [系统概述](#系统概述)
2. [测试前准备](#测试前准备)
3. [控制模式说明](#控制模式说明)
4. [完整测试流程](#完整测试流程)
5. [故障排除](#故障排除)

---

## 系统概述

### 系统组成
- **测试主机**: 运行QC测试软件
- **电源供应**: Rigol DP800 可编程电源（USB控制 或 手动控制）
- **CTS低温系统**: 液氮冷却系统控制盒（USB控制 或 手动控制）
- **WIB测试板**: 冷电子测试板
- **网络存储**: 测试数据自动备份

### 配置文件
所有配置参数在 `init_setup.csv` 中设置：
```csv
Test_Site,BNL
Tech_site_email,lke@bnl.gov
QC_data_root_folder,/mnt/data
Rigol_PS_ID,USB0::0x1AB1::0x0E11::DP8C184550857::INSTR
PS_Control_Mode,USB                    # USB=自动控制, MANUAL=手动控制
CTS_LN2_Fill_Wait,1800                 # LN₂充填等待时间（秒）
CTS_Warmup_Wait,3600                   # 暖化等待时间（秒）
Network_Upload_Path,/data/rtss/femb    # 网盘上传路径
```

---

## 测试前准备

### 1. 硬件连接检查
- [ ] 电源供应连接到测试主机USB端口
- [ ] CTS控制盒连接到测试主机USB端口（通常为 `/dev/ttyACM*`）
- [ ] WIB测试板安装到CTS测试台
- [ ] 网络连接正常，可访问网盘路径

### 2. 软件启动
```bash
cd /home/dune/Workspace/BNL_CE_WIB_SW_QC
python3 CTS_FEMB_QC_top.py
```

### 3. 初始信息输入
1. 输入操作员姓名
2. 确认电子邮件地址
3. 检查预检清单（3个弹窗）

---

## 控制模式说明

系统支持两种控制模式，根据硬件连接状态自动切换：

### 电源供应控制模式

#### 🤖 USB自动模式
**触发条件**:
- `init_setup.csv` 中 `PS_Control_Mode=USB`
- 电源供应USB连接成功

**自动操作**:
- ✅ 自动设置电压和电流
- ✅ 自动开启/关闭输出
- ✅ 自动测量电压和电流
- ✅ 自动验证断电状态

**用户操作**: 无需手动操作

---

#### 👤 手动控制模式
**触发条件**:
- `init_setup.csv` 中 `PS_Control_Mode=MANUAL`
- 或 USB连接失败

**提示示例**:
```
======================================================================
[MANUAL POWER CONTROL] Please configure power supply:
  Channel: CH1
  Voltage: 12.0 V
  Current Limit: 3.0 A
  Action: Turn OUTPUT ON
======================================================================
Press ENTER after you have completed this configuration >>
```

**用户操作**:
1. 在电源供应面板上手动设置参数
2. 手动开启/关闭输出
3. 手动读取并输入测量值
4. 按ENTER确认完成

---

### CTS低温系统控制模式

#### 🤖 自动控制模式
**触发条件**: CTS控制盒USB连接成功（通常为 `/dev/ttyACM1`）

**自动操作**:
- ✅ 自动读取杜瓦瓶液位
- ✅ 自动执行冷气预冷（5分钟）
- ✅ 自动执行LN₂充填并监控液位
- ✅ 自动检测液位达到Level 3或4
- ✅ 自动执行暖气吹扫（20分钟或60分钟）
- ✅ 自动返回IDLE状态

**用户操作**:
- 液位不足时需要手动加注LN₂
- 确认加注完成后按Y继续

---

#### 👤 手动控制模式
**触发条件**: CTS控制盒USB连接失败或不存在

**提示示例**:
```
======================================================================
  MANUAL CTS CONTROL INSTRUCTIONS
======================================================================
Step 1: Cold Gas Pre-cooling (~5 minutes)
  1. Set CTS to STATE 3 (Cold Gas)
  2. Wait approximately 5 minutes
Press ENTER when cold gas pre-cooling is complete >>
```

**用户操作**:
1. 在CTS控制盒上手动设置状态
   - STATE 1: IDLE（待机）
   - STATE 2: Warm Gas（暖气）
   - STATE 3: Cold Gas（冷气）
   - STATE 4: LN₂ Immersion（液氮浸入）
2. 等待指定时间（系统会显示倒计时）
3. 按ENTER确认完成

---

## 完整测试流程

### Phase 0: 系统初始化

#### 🤖 自动: CTS系统初始化
```
==================================================================
  CTS CRYOGENIC SYSTEM INITIALIZATION
==================================================================
Configuration:
  LN₂ Fill Wait Time: 30 minutes
  Warm-up Wait Time: 60 minutes

✓ CTS cryogenic box connected via USB - automatic control enabled
==================================================================
```

**结果**:
- ✅ 自动检测：系统显示"USB - automatic control enabled"
- ⚠️  手动模式：系统显示"manual control mode"

---

#### 🤖 自动: 杜瓦瓶液位检查
**早班（1:00-11:00）**: 要求液位 ≥ 1700
**晚班（12:00-0:00）**: 要求液位 ≥ 1200

**自动模式流程**:
```
Current Shift: Morning
Required Dewar Level: >= 1700
ℹ Checking dewar level via CTS...
Current Dewar Level: 1850
✓ Dewar level (1850) is sufficient for Morning shift
```

**液位不足时**:
1. 🖥️ **自动**: 系统检测液位 < 阈值
2. 🖥️ **自动**: 弹出加注指导图片
3. 👤 **手动**: 加注50L杜瓦瓶到液氮
4. 👤 **手动**: 输入 'Y' 确认加注完成
5. 🖥️ **自动**: 重新检测液位
6. 🖥️ **自动**: 如果仍不足，重复加注流程
7. 🖥️ **自动**: 液位足够后，自动暖气吹扫20分钟

---

### Phase 1: FEMB安装与设置

#### 👤 手动: 组装数据采集
**Bottom Slot (底部槽位)**:
1. 👤 输入是否安装FEMB（Y/EMPTY）
2. 👤 扫描/输入 HWDB QR码（泡沫盒上）
3. 👤 扫描/输入 CE盒序列号
4. 👤 输入CE盒盖后4位数字
5. 🖥️ **自动验证**: 盖子数字必须匹配CE盒后4位
6. 👤 扫描FEMB QR码

**Top Slot (顶部槽位)**: 重复上述步骤

**示例**:
```
Scan HWDB QR code on foam box
>> A12345

Scan/Enter CE box serial number
>> ZZZ9876

Enter last 4 digits on CE box cover
>> 9876
✓ Cover matches CE box

Scan FEMB QR code
>> FEMB001
✓ FEMB registered
```

---

### Phase 2: 配置与文档

#### 👤 手动: 拍照记录
1. 🖥️ **自动**: 弹出拍照提示窗口
2. 👤 **手动**: 使用相机拍摄CE盒照片
3. 👤 **手动**: 选择照片文件上传
4. 🖥️ **自动**: 照片保存到测试记录

#### 🖥️自动: 生成配置文件
- ✅ 创建 `femb_info_implement.csv`
- ✅ 保存所有FEMB ID和槽位信息
- ✅ 保存组装追溯数据

---

### Phase 3: 暖态QC测试

#### 🤖 自动: 电源控制 (USB模式)
```
▶ [1/4] Powering ON WIB
✓ CH1: 12.0V, 3.0A - OUTPUT ON
✓ CH2: 12.0V, 3.0A - OUTPUT ON
ℹ Initializing ethernet link (35 seconds)...
```

#### 👤 手动: 电源控制 (手动模式)
```
======================================================================
[MANUAL POWER CONTROL] Please configure power supply:
  Channel: CH1
  Voltage: 12.0 V
  Current Limit: 3.0 A
  Action: Turn OUTPUT ON
======================================================================
Press ENTER after configuration >> [等待用户输入]
```

#### 🖥️ 自动: 测试执行
1. ✅ WIB连接测试
2. ✅ WIB初始化
3. ✅ FEMB Warm Checkout（最多3次重试）
4. ✅ FEMB Warm QC测试

#### 🖥️ 自动: 结果分析
```
==================================================================
  WARM QC TEST - TEST RESULTS
==================================================================

📊 Test Summary:
   Total Fault Files: 0
   Total Pass Files:  24

🔍 FEMB Status by Slot:
   ✓ Bottom Slot0: FEMB FEMB001 - PASS
      Files: 0 faults, 12 passes
   ✓ Top Slot1: FEMB FEMB002 - PASS
      Files: 0 faults, 12 passes

==================================================================
  ✓✓✓ OVERALL RESULT: PASS ✓✓✓
==================================================================
```

**失败处理**:
```
✗✗✗ OVERALL RESULT: FAIL ✗✗✗

⚠️  Test failed. What would you like to do?
  'r' - Retry the test
  'c' - Continue anyway (not recommended)
  'e' - Exit program
>>
```

---

### Phase 4: 冷态QC测试

#### 🤖 自动: CTS冷却流程 (自动模式)
```
🌡️  Initiating CTS cool down procedure...
ℹ Automatic CTS control enabled

▶ [1/3] Cold gas pre-cooling (~5 min)
✓ Cold gas pre-cooling completed

▶ [2/3] LN₂ immersion with level monitoring (~30 min)
Time pasted = 60s, Chamber Level = 1, Dewar level = 1850
Time pasted = 120s, Chamber Level = 2, Dewar level = 1820
Time pasted = 1200s, Chamber Level = 3, Dewar level = 1650
✓ LN₂ immersion complete - Level 3 reached

▶ [3/3] Checking CTS status
✓ Chamber Level: 3, Dewar Level: 1650
```

#### 👤 手动: CTS冷却流程 (手动模式)
```
======================================================================
  MANUAL CTS CONTROL INSTRUCTIONS
======================================================================
Step 1: Cold Gas Pre-cooling (~5 minutes)
  1. Set CTS to STATE 3 (Cold Gas)
  2. Wait approximately 5 minutes
Press ENTER when complete >> [等待用户输入]

Step 2: LN₂ Immersion (~30 minutes)
  1. Set CTS to STATE 4 (LN₂ Immersion)
  2. Wait for LN₂ to reach LEVEL 3 or 4
  3. Monitor level sensors every few minutes

⏰ Wait for LN2 Refill (~30 min)!
[倒计时 30:00 ... 00:00]
✅ Timer complete!

Please ensure:
   • LN2 level has reached LEVEL 3 or 4
   • Heat LED is OFF

Type "confirm" once CTS is fully cooled down
>> confirm
✓ CTS cool down confirmed
```

#### 🖥️ 自动: 冷态测试执行
1. ✅ 液位监控检查（测试前）
2. ✅ FEMB Cold Checkout（最多3次重试）
3. ✅ FEMB Cold QC测试（~30分钟）
4. ✅ 液位监控检查（测试后）
5. ✅ 结果分析（同Phase 3格式）

---

#### 🤖 自动: CTS暖化流程 (自动模式)
```
==================================================================
  CTS WARM-UP PROCEDURE
==================================================================
ℹ Automatic CTS warm-up control enabled

▶ CTS warm gas purge (~60 min)
✓ CTS warm-up completed successfully
✓ CTS set to IDLE state
==================================================================
```

#### 👤 手动: CTS暖化流程 (手动模式)
```
======================================================================
  MANUAL CTS WARM-UP INSTRUCTIONS
======================================================================
Step 1: Set CTS to Warm Gas mode
  1. Set CTS to STATE 2 (Warm Gas)
  2. Wait approximately 60 minutes

⏰ Wait for warm up (~60 min)!
[倒计时 60:00 ... 00:00]
✅ Timer complete!

Step 2: Return CTS to IDLE state
  1. Set CTS to STATE 1 (IDLE)
Press ENTER when CTS is in IDLE state >> [等待用户输入]
✓ CTS warm-up complete
==================================================================
```

---

### Phase 5: 最终检查

与Phase 3流程相同：
- 🤖 电源控制（自动/手动）
- 🖥️ Final Checkout测试（最多3次重试）
- 🖥️ 结果分析

---

### Phase 6: 拆卸与标签

#### 👤 手动: 拆卸验证
**对每个槽位**:

1. **扫描CE盒验证**
   ```
   Please scan CE box QR code to verify
   >> ZZZ9876
   ✓ CE box verified: ZZZ9876
   ```

2. **安装盖子验证**
   ```
   Please install cover (9876) to CE box (ZZZ9876)
   After cover is installed, type in cover last 4 digits
   >> 9876
   ✓ Cover verified and installed correctly
   ```

3. **泡沫盒包装验证**
   ```
   Please package CE box in Foam box (A12345)
   Scan QR code on the foam box
   >> A12345
   ✓ Foam box verified - correct packaging
   ```

4. **QC结果标签**
   ```
   ✓ PASSED - Put on Green 'PASS' sticker near HWDB QR
   ```
   或
   ```
   ✗ FAILED - Put on Red 'NG' sticker near HWDB QR
   ```

5. **存放确认**
   ```
   Please store foam box in designated location
   Press ENTER when complete >> [等待用户输入]
   ```

---

#### 🖥️ 自动: FEMB标签打印指南
```
==================================================================
  FEMB LABELING GUIDE
==================================================================
Please label each FEMB board according to test results:

✓ Bottom Slot0: FEMB FEMB001
   → Apply GREEN label

✓ Top Slot1: FEMB FEMB002
   → Apply GREEN label
==================================================================
Have you labeled all FEMB boards correctly?
Press ENTER to confirm >> [等待用户输入]
```

---

#### 🖥️ 自动: 数据上传到网盘
```
==================================================================
  UPLOADING TEST DATA TO NETWORK DRIVE
==================================================================
Source: /mnt/data
Destination: /data/rtss/femb

ℹ Copying FEMB_QC data...
✓ Copied FEMB_QC (156 files)
✓ Copied femb_info.csv
✓ Copied femb_info_implement.csv

==================================================================
  UPLOAD COMPLETE
==================================================================
  ✓ Files uploaded: 158
  ✓ Total size: 245.67 MB
  ✓ Location: /data/rtss/femb
==================================================================

✓ All test data uploaded successfully
```

**如果上传失败**:
```
⚠️ Upload failed or incomplete - please upload manually
  Manual upload: Copy data from /mnt/data/FEMB_QC to /data/rtss/femb
```

---

## 故障排除

### 电源供应问题

#### 问题: 无法连接到电源供应
**症状**:
```
❌ Connection failed: No such resource
⚠️ Rigol device not found via USB
```

**解决方案**:
1. 检查USB连接
2. 运行 `lsusb` 查看设备（应显示 `1ab1:0e11 Rigol Technologies`）
3. 如果检测不到：
   - 重启电源供应
   - 重新插拔USB线
   - 更换USB端口
4. 如果仍无法连接：
   - 修改 `init_setup.csv`: `PS_Control_Mode,MANUAL`
   - 重启测试程序
   - 系统将切换到手动控制模式

---

### CTS控制盒问题

#### 问题: 无法找到CTS控制盒
**症状**:
```
No available serial port exists
Can't build communication with CTS
```

**解决方案**:
1. 检查USB连接
2. 运行 `ls /dev/ttyACM*` 查看串口设备
3. 按照屏幕提示操作：
   ```
   step 1: Power off cold control box
   step 2: Unplug USB cable from cold control box
   step 3: Wait 5 seconds
   step 4: Turn cold control box back on
   step 5: Replug USB cable to cold control box
   fixed? (y/n):
   ```
4. 如果仍无法连接，选择 'n' 进入手动控制模式

---

### 液位检查失败

#### 问题: 加注后液位仍不足
**症状**:
```
✗ Dewar level (1150) is still below threshold (1700)
⚠️  Refill was insufficient. Please refill again.
```

**解决方案**:
1. 检查杜瓦瓶是否确实加满
2. 检查液氮是否正在蒸发（保温是否良好）
3. 继续加注直到液位达标
4. 系统会自动循环检查直到通过

---

### 测试失败处理

#### Warm/Cold Checkout 失败
**自动重试**: 系统会自动重试最多3次

**3次后仍失败**: 继续进行QC测试，但会发送邮件通知

#### QC测试失败
**选项**:
- `'r'` - 重试测试（耗时~30分钟）
- `'c'` - 继续到下一阶段（不推荐）
- `'e'` - 退出测试，进入暖化和拆卸流程

---

### 网盘上传失败

#### 问题: 无法访问网络路径
**症状**:
```
✗ Failed to create network directory: Permission denied
```

**解决方案**:
1. 检查网络连接: `ping [网盘服务器]`
2. 检查挂载: `mount | grep /data`
3. 检查权限: `ls -ld /data/rtss/femb`
4. 手动上传:
   ```bash
   cp -r /mnt/data/FEMB_QC /data/rtss/femb/
   cp femb_info*.csv /data/rtss/femb/
   ```

---

## 测试时间估算

### 完整测试周期（自动模式）
| 阶段 | 预计时间 | 说明 |
|------|---------|------|
| Phase 0: 初始化 | 5-10分钟 | 含液位检查，若需加注+40分钟 |
| Phase 1: 安装设置 | 15-20分钟 | 手动组装和扫描 |
| Phase 2: 配置文档 | 5分钟 | 拍照和配置 |
| Phase 3: 暖态QC | 30-40分钟 | 含重试 |
| Phase 4: 冷态QC | 90-120分钟 | 含冷却、测试、暖化 |
| Phase 5: 最终检查 | 30-35分钟 | |
| Phase 6: 拆卸标签 | 15-20分钟 | 手动操作 |
| **总计** | **3-4小时** | 不含额外的LN₂加注 |

### 时间节约（自动vs手动）
| 操作 | 自动模式 | 手动模式 | 节约时间 |
|------|---------|---------|---------|
| 电源控制 | 自动 | ~2分钟/次 × 10次 | ~20分钟 |
| CTS控制 | 自动 | ~3分钟/次 × 5次 | ~15分钟 |
| 液位监控 | 自动 | 需手动检查 | ~10分钟 |
| **总节约** | | | **~45分钟/测试** |

---

## 附录

### A. CTS状态代码
| 状态码 | 名称 | 功能 |
|-------|------|------|
| STATE 1 | IDLE | 待机状态 |
| STATE 2 | Warm Gas | 暖气吹扫（暖化） |
| STATE 3 | Cold Gas | 冷气预冷 |
| STATE 4 | LN₂ Immersion | 液氮浸入模式 |

### B. 液位传感器等级
| Level | ADC范围 | 状态 |
|-------|---------|------|
| 0 | < 10000 | 短路/异常 |
| 1 | 10000-16000 | 室温 |
| 2 | 16000-18400 | 冷气中 |
| 3 | 18400-25000 | 液氮浸入 |
| 4+ | > 25000 | 开路/溢出 |

### C. 杜瓦液位阈值
| 班次 | 时间段 | 最低液位 |
|------|--------|---------|
| 早班 | 1:00-11:00 | 1700 |
| 晚班 | 12:00-0:00 | 1200 |

### D. 常用命令
```bash
# 查看USB设备
lsusb

# 查看串口设备
ls /dev/ttyACM*

# 检查网络挂载
mount | grep /data

# 查看测试数据
ls -lh /mnt/data/FEMB_QC/

# 手动复制到网盘
cp -r /mnt/data/FEMB_QC /data/rtss/femb/
```

---

**文档版本**: v1.0
**更新日期**: 2026-01-14
**维护**: BNL QC Team
