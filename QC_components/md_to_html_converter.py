#!/usr/bin/env python3
"""
Markdown to HTML Converter for FEMB QC Reports
将 Markdown 格式的测试报告转换为专业科研风格的 HTML 报告
"""

import os
import sys
import glob
import re


def get_html_template(title, content):
    """生成完整的 HTML 文档，包含专业科研风格的 CSS"""
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        /* 专业科研风格样式 */
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Segoe UI', 'Arial', sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }}

        .container {{
            background-color: white;
            padding: 40px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-radius: 4px;
        }}

        h1 {{
            color: #1a1a1a;
            border-bottom: 3px solid #2c3e50;
            padding-bottom: 15px;
            margin-bottom: 30px;
            font-size: 2.2em;
            font-weight: 600;
        }}

        h2 {{
            color: #2c3e50;
            margin-top: 40px;
            margin-bottom: 20px;
            font-size: 1.8em;
            font-weight: 600;
            border-bottom: 2px solid #ecf0f1;
            padding-bottom: 10px;
        }}

        h3 {{
            color: #34495e;
            margin-top: 30px;
            margin-bottom: 15px;
            font-size: 1.4em;
            font-weight: 600;
        }}

        hr {{
            border: none;
            border-top: 1px solid #ddd;
            margin: 30px 0;
        }}

        /* 表格样式 */
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background-color: white;
            box-shadow: 0 1px 3px rgba(0,0,0,0.05);
            font-size: 0.95em;
        }}

        table thead {{
            background-color: #34495e;
            color: white;
        }}

        table th {{
            padding: 12px 15px;
            text-align: left;
            font-weight: 600;
            border: 1px solid #2c3e50;
        }}

        table td {{
            padding: 10px 15px;
            border: 1px solid #ddd;
        }}

        table tbody tr:nth-child(even) {{
            background-color: #f8f9fa;
        }}

        table tbody tr:hover {{
            background-color: #e8f4f8;
        }}

        /* 状态标签 */
        .status-pass {{
            color: #27ae60;
            font-weight: bold;
        }}

        .status-fail {{
            color: #e74c3c;
            font-weight: bold;
        }}

        .status-warning {{
            color: #f39c12;
            font-weight: bold;
        }}

        /* 图片样式 */
        img {{
            max-width: 100%;
            height: auto;
            margin: 15px 0;
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 5px;
            background-color: white;
        }}

        /* 链接样式 */
        a {{
            color: #3498db;
            text-decoration: none;
            transition: color 0.2s;
        }}

        a:hover {{
            color: #2980b9;
            text-decoration: underline;
        }}

        /* 段落 */
        p {{
            margin: 10px 0;
        }}

        /* 列表 */
        ul, ol {{
            margin: 10px 0 10px 30px;
        }}

        li {{
            margin: 5px 0;
        }}

        /* 代码块 */
        code {{
            background-color: #f4f4f4;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
        }}

        pre {{
            background-color: #f4f4f4;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            margin: 15px 0;
        }}

        pre code {{
            padding: 0;
        }}

        /* 打印样式 */
        @media print {{
            body {{
                background-color: white;
                padding: 0;
            }}

            .container {{
                box-shadow: none;
                padding: 20px;
            }}

            @page {{
                margin: 2cm;
            }}
        }}

        /* 颜色文本 */
        span[style*="color: green"] {{
            color: #27ae60 !important;
            font-weight: bold;
        }}

        span[style*="color: red"] {{
            color: #e74c3c !important;
            font-weight: bold;
        }}
    </style>
</head>
<body>
<div class="container">
{content}
</div>
</body>
</html>
'''


def markdown_to_html(md_content):
    """
    简单的 Markdown 到 HTML 转换
    处理常见的 Markdown 语法
    """
    html = md_content

    # 转换标题 (必须先处理长的，再处理短的)
    html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
    html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
    html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

    # 转换水平线
    html = re.sub(r'^---+$', r'<hr>', html, flags=re.MULTILINE)
    html = re.sub(r'^___ +$', r'<hr>', html, flags=re.MULTILINE)

    # 转换图片 ![alt](src)
    html = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)', r'<img src="\2" alt="\1">', html)

    # 转换链接 [text](url)
    html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)

    # 转换粗体 **text** 或 __text__
    html = re.sub(r'\*\*([^\*]+)\*\*', r'<strong>\1</strong>', html)
    html = re.sub(r'__([^_]+)__', r'<strong>\1</strong>', html)

    # 转换斜体 *text* 或 _text_
    html = re.sub(r'\*([^\*]+)\*', r'<em>\1</em>', html)
    html = re.sub(r'_([^_]+)_', r'<em>\1</em>', html)

    # 转换代码 `code`
    html = re.sub(r'`([^`]+)`', r'<code>\1</code>', html)

    # 转换段落 (连续的非空行)
    lines = html.split('\n')
    in_paragraph = False
    result_lines = []

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 跳过已经是 HTML 标签的行
        if stripped.startswith('<h') or stripped.startswith('<hr') or \
           stripped.startswith('<img') or stripped.startswith('<table') or \
           stripped.startswith('</table') or stripped.startswith('<div'):
            if in_paragraph:
                result_lines.append('</p>')
                in_paragraph = False
            result_lines.append(line)
        elif stripped == '':
            if in_paragraph:
                result_lines.append('</p>')
                in_paragraph = False
            result_lines.append(line)
        else:
            if not in_paragraph and not stripped.startswith('|'):  # 不包裹表格
                result_lines.append('<p>')
                in_paragraph = True
            result_lines.append(line)

    if in_paragraph:
        result_lines.append('</p>')

    html = '\n'.join(result_lines)

    return html


def convert_md_to_html(md_file, output_file=None):
    """
    转换单个 Markdown 文件为 HTML

    Args:
        md_file: Markdown 文件路径
        output_file: 输出 HTML 文件路径 (如果为 None，则自动生成)

    Returns:
        输出文件路径
    """
    # 读取 Markdown 文件
    with open(md_file, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # 提取标题 (第一个 # 标题)
    title_match = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
    title = title_match.group(1) if title_match else "FEMB QC Test Report"

    # 转换 Markdown 到 HTML
    html_content = markdown_to_html(md_content)

    # 生成完整的 HTML 文档
    full_html = get_html_template(title, html_content)

    # 确定输出文件名
    if output_file is None:
        output_file = os.path.splitext(md_file)[0] + '.html'

    # 写入 HTML 文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_html)

    print(f"✓ 已转换: {md_file} → {output_file}")
    return output_file


def batch_convert(directory='.', pattern='report_FEMB_*.md'):
    """
    批量转换目录中的 Markdown 文件

    Args:
        directory: 要搜索的目录
        pattern: 文件匹配模式

    Returns:
        转换的文件数量
    """
    search_pattern = os.path.join(directory, pattern)
    md_files = glob.glob(search_pattern)

    if not md_files:
        print(f"未找到匹配的文件: {search_pattern}")
        return 0

    print(f"找到 {len(md_files)} 个 Markdown 文件")
    print("=" * 60)

    converted_count = 0
    for md_file in md_files:
        try:
            convert_md_to_html(md_file)
            converted_count += 1
        except Exception as e:
            print(f"✗ 转换失败: {md_file}")
            print(f"  错误: {e}")

    print("=" * 60)
    print(f"转换完成: {converted_count}/{len(md_files)} 个文件")

    return converted_count


def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 如果提供了参数，转换指定文件或目录
        arg = sys.argv[1]
        if os.path.isfile(arg):
            convert_md_to_html(arg)
        elif os.path.isdir(arg):
            batch_convert(arg)
        else:
            print(f"错误: 文件或目录不存在: {arg}")
            sys.exit(1)
    else:
        # 否则转换当前目录的所有报告文件
        batch_convert('.')


if __name__ == '__main__':
    main()
