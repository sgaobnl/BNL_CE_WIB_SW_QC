# from wib_cfgs import WIB_CFGS
# import time
# import sys
# import numpy as np
# import pickle
# import copy
# import os
# import time, datetime, random, statistics
# import fpdf as fpdf
# import fitz
#
#
#
#
# import fitz  # PyMuPDF
#
# def merge_pdfs(input_paths, output_path):
#     # 创建 PdfWriter 对象来写入合并后的PDF
#     pdf_writer = fitz.open()
#
#     try:
#         # 遍历输入的PDF文件路径
#         for path in input_paths:
#             # 打开每个PDF文件
#             pdf_document = fitz.open(path)
#
#             # 遍历每一页，将其添加到 PdfWriter 对象中
#             for page_num in range(pdf_document.page_count):
#                 page = pdf_document[page_num]
#                 pdf_writer.insert_pdf(pdf_document, from_page=page_num, to_page=page_num, start_at=pdf_writer.page_count)
#
#         # 保存合并后的PDF到输出文件
#         pdf_writer.save(output_path)
#
#         print(f'Success Merge Report to {output_path}')
#
#     except Exception as e:
#         print(f'发生错误: {str(e)}')
#
#     finally:
#         # 关闭所有打开的PDF文件
#         pdf_writer.close()
#
# # 指定输入PDF文件的路径列表
#
#
# def Gather_Report(datadir):
#     print(datadir)
#     item1   = datadir+'/' + 'PWR_Meas/report.pdf'
#     item3   = datadir+'/' + 'Leakage_Current/report.pdf'
#     item4   = datadir+'/' + 'CHK/report.pdf'
#     item5   = datadir+'/' + 'RMS/report.pdf'
#
#     item6_1 = datadir+'/' + 'CALI1/report_200mVBL_4_7mVfC_2_0us.pdf'
#     item6_2 = datadir+'/' + 'CALI1/report_200mVBL_7_8mVfC_2_0us.pdf'
#     item6_3 = datadir+'/' + 'CALI1/report_200mVBL_14_0mVfC_2_0us.pdf'
#     item6_4 = datadir+'/' + 'CALI1/report_200mVBL_25_0mVfC_2_0us.pdf'
#     item7   = datadir+'/' + 'CALI2/report_900mVBL_14_0mVfC_2_0us.pdf'
#     item8   = datadir+'/' + 'CALI3/report_200mVBL_14_0mVfC_2_0us_sgp1.pdf'
#     item9   = datadir+'/' + 'CALI4/report_900mVBL_14_0mVfC_2_0us_sgp1.pdf'
#
#     input_pdf_paths = [item1, item6_1, item6_2, item6_3, item6_4, item7, item8, item9, item3, item4, item5]
#
#     # 指定输出PDF文件的路径
#     output_pdf_path = datadir + '/temp_report.pdf'
#
#     # 调用函数以合并PDF文件
#     merge_pdfs(input_pdf_paths, output_pdf_path)
#
#
#     print(314159)