#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os

# 设置环境变量，确保 Oracle 中文正确显示
# 必须在导入 cx_Oracle 之前设置
os.environ['NLS_LANG'] = 'SIMPLIFIED CHINESE_CHINA.UTF8'

# 添加项目根目录到 Python 路径，以便可以导入项目模块
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

import cx_Oracle

conn = cx_Oracle.connect("ETL_EXT_KYC/9c16452a063353e1@192.168.133.3:1521/ORCL")

cur = conn.cursor()

cur.execute("SELECT CODE, NAME FROM PS_ETL_CW_BUDSTR WHERE SUBSTR(bcode,1,8)='AA420201' and LENGTH(trim(bcode))>8")

# 确保输出使用 UTF-8 编码
if sys.stdout.encoding != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')

results = cur.fetchall()
for row in results:
    print(row)

cur.close()

conn.close()