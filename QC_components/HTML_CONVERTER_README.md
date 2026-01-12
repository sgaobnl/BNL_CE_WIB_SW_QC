# Markdown to HTML Converter for FEMB QC Reports

## 功能说明

该工具可以将 Markdown 格式的 FEMB QC 测试报告自动转换为专业科研风格的 HTML 报告。

## 主要特性

- ✅ 自动转换 Markdown 到 HTML
- ✅ 专业科研风格的 CSS 样式
- ✅ 响应式设计，支持打印
- ✅ 保留所有原始 Markdown 内容和格式
- ✅ 支持单文件和批量转换

## 使用方法

### 1. 转换单个文件

```bash
python3 QC_components/md_to_html_converter.py report_FEMB_123_t1_P_S0.md
```

### 2. 批量转换目录中的所有报告

```bash
# 转换当前目录的所有 report_FEMB_*.md 文件
cd D:/data/temp  # 进入报告目录
python3 /path/to/md_to_html_converter.py .
```

### 3. 转换指定目录

```bash
python3 QC_components/md_to_html_converter.py /path/to/reports/directory
```

### 4. 直接运行（转换当前目录）

```bash
cd /path/to/reports
python3 /path/to/md_to_html_converter.py
```

## 输出文件

- 输入文件：`report_FEMB_123_t1_P_S0.md`
- 输出文件：`report_FEMB_123_t1_P_S0.html`（自动生成在同一目录）

## 集成到测试流程

可以在测试完成后自动转换报告：

```python
# 在 All_Report.py 的最后添加
from QC_components.md_to_html_converter import convert_md_to_html

# 生成 markdown 报告后
fpmd = ... # markdown 文件路径
# 自动转换为 HTML
convert_md_to_html(fpmd)
```

## 样式特点

- 🎨 专业科研风格设计
- 📊 优化的表格显示
- 🖼️ 自动适应的图片大小
- 🔗 清晰的链接样式
- ✓/✗ 醒目的通过/失败标记
- 🖨️ 打印友好的布局

## 注意事项

- 原始的 `.md` 文件不会被删除或修改
- HTML 文件会覆盖同名的旧文件
- 支持所有标准 Markdown 语法
- 内嵌 HTML 标签会被保留

## 系统要求

- Python 3.x
- 无需额外依赖库（仅使用标准库）
