# 测试阈值配置说明

## 概述

`test_thresholds.py` 文件包含了所有质量控制测试的阈值配置。您可以根据实际需求修改这些阈值。

## 配置文件位置

```
/home/dune/Documents/DUNE_WIB_QC_Script/config/test_thresholds.py
```

## 主要配置项

### 1. 功耗轨道阈值

#### 电压容差
```python
VOLTAGE_TOLERANCE = 0.2  # ±0.2V from set value
```
- **说明**：测量电压与设定电压的允许偏差
- **推荐值**：0.2V
- **修改建议**：如果连接电缆较长，可适当增加到 0.3V

#### 电流阈值
```python
CURRENT_THRESHOLDS = {
    "FE": {
        "I_ref": 0.42,      # FE (LArASIC) 参考电流 (A)
        "tolerance": 0.1,   # ±0.1A 容差
        "I_ref_alt": 0.63,  # 备用参考值（不同配置）
        "tolerance_alt": 0.1
    },
    "ADC": {
        "I_ref": 1.6,       # ADC (ColdADC) 参考电流 (A)
        "tolerance": 0.2    # ±0.2A 容差
    },
    "CD": {
        "I_ref": 0.2,       # CD (COLDATA) 参考电流 (A)
        "tolerance": 0.1    # ±0.1A 容差
    },
    "BIAS": {
        "I_ref": 0.05,      # BIAS 参考电流 (A)
        "tolerance": 0.1    # ±0.1A 容差
    }
}
```

**修改示例**：
```python
# 如果您的 FE 电流通常在 0.5A 左右
CURRENT_THRESHOLDS["FE"]["I_ref"] = 0.5
CURRENT_THRESHOLDS["FE"]["tolerance"] = 0.15

# 如果 ADC 电流更稳定，可以收紧容差
CURRENT_THRESHOLDS["ADC"]["tolerance"] = 0.15
```

### 2. 总功耗限制

```python
POWER_LIMITS = {
    "SEOFF": {
        "min": 4.0,         # 最小期望功率 (W)
        "max": 7.0          # 最大期望功率 (W)
    },
    "SEON_SDC": {
        "min": 4.5,
        "max": 7.5
    },
    "DIFF": {
        "min": 4.5,
        "max": 7.5
    }
}
```

**说明**：
- `min`: 如果总功耗低于此值，可能表示连接问题
- `max`: 如果总功耗高于此值，可能表示短路或异常

### 3. ADC 监控电压阈值

```python
ADC_VOLTAGE_THRESHOLDS = {
    "VCMI": {
        "min": 800,         # 最小 VCMI 电压 (mV)
        "max": 1200         # 最大 VCMI 电压 (mV)
    },
    "VCMO": {
        "min": 800,
        "max": 1200
    },
    "VREFP": {
        "min": 1600,
        "max": 2400
    },
    "VREFN": {
        "min": 100,
        "max": 400
    }
}
```

**修改建议**：
根据 ADC 数据手册的规格调整

### 4. 通道响应阈值

```python
CHANNEL_THRESHOLDS = {
    "rms_noise": {
        "max": 5.0          # 最大 RMS 噪声 (ADC bins)
    },
    "pedestal": {
        "min": 2000,        # 最小基线值
        "max": 14000        # 最大基线值
    },
    "response": {
        "min_amplitude": 500  # 最小脉冲幅度
    }
}
```

### 5. 测试时间阈值

```python
TIMING_THRESHOLDS = {
    "total_test_time": {
        "max": 180          # 最大总测试时间 (秒)
    },
    "power_startup": {
        "max": 30
    },
    # ... 其他阶段
}
```

**说明**：如果测试时间超过阈值，会在报告中标注为警告

### 6. Reception Checkout 电流限制

```python
RECEPTION_CURRENT_LIMITS = {
    "channel_1": {
        "min": 0.5,         # 最小电流 (A)
        "max": 2.0          # 最大电流 (A)
    },
    "channel_2": {
        "min": 0.5,
        "max": 2.0
    }
}
```

## 如何修改配置

### 方法 1：直接编辑配置文件

1. 打开配置文件：
   ```bash
   nano /home/dune/Documents/DUNE_WIB_QC_Script/config/test_thresholds.py
   ```

2. 修改相应的值

3. 保存文件（Ctrl+O, Enter, Ctrl+X）

4. 重新运行测试，新的阈值会自动生效

### 方法 2：创建本地配置副本（推荐）

```bash
cd /home/dune/Documents/DUNE_WIB_QC_Script/config
cp test_thresholds.py test_thresholds_custom.py
# 编辑 test_thresholds_custom.py
```

然后在测试脚本中导入自定义配置：
```python
from config.test_thresholds_custom import *
```

## 测试结果文件

### HTML 报告
- 路径：`report/FEMB*_RT_0pF/result.html`
- **错误标红**：不符合阈值的测量值会以红色背景显示
- **错误日志**：底部会列出所有检测到的错误

### CSV 详细数据
- 路径：`report/FEMB*_RT_0pF/FEMB*_Test0401_*.csv`
- 包含所有测量值和阈值信息
- 可用 Excel 或其他工具打开分析

## 故障排查

### 1. 电压超出范围

**可能原因**：
- 电缆阻抗导致压降
- 电源设置不准确

**解决方案**：
- 增加 `VOLTAGE_TOLERANCE`
- 检查电源线连接

### 2. 电流超出范围

**可能原因**：
- 不同批次 FEMB 特性不同
- 配置模式不同

**解决方案**：
- 收集多个 FEMB 的电流数据
- 更新 `I_ref` 为实际平均值
- 适当放宽 `tolerance`

### 3. 测试总是失败

**检查步骤**：
1. 查看 CSV 文件中的实际测量值
2. 与已知良好 FEMB 对比
3. 如果测量值一致但都失败，说明阈值设置过严
4. 参考历史数据调整阈值

## 示例：基于历史数据更新阈值

假设您测试了 10 个已知良好的 FEMB，发现：
- FE 电流范围：0.38A - 0.46A
- ADC 电流范围：1.5A - 1.7A

推荐设置：
```python
CURRENT_THRESHOLDS["FE"]["I_ref"] = 0.42  # 平均值
CURRENT_THRESHOLDS["FE"]["tolerance"] = 0.08  # 覆盖 ±2σ

CURRENT_THRESHOLDS["ADC"]["I_ref"] = 1.6  # 平均值
CURRENT_THRESHOLDS["ADC"]["tolerance"] = 0.15  # 覆盖 ±2σ
```

## 配置验证

修改配置后，可以运行此命令验证：

```python
from config.test_thresholds import *
print(f"Voltage tolerance: ±{VOLTAGE_TOLERANCE}V")
print(f"FE current: {CURRENT_THRESHOLDS['FE']['I_ref']}A ±{CURRENT_THRESHOLDS['FE']['tolerance']}A")
```

## 技术支持

如有问题，请联系：
- gao.hillhill@gmail.com
- lingyun.lke@gmail.com
