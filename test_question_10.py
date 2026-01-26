#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试第10题
"""

import sys
import os
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

load_dotenv()

from erp_agent.core import ERPAgent
from erp_agent.config import get_llm_config, get_database_config, get_agent_config

# 初始化Agent
print("初始化 ERP Agent...")
llm_config = get_llm_config()
db_config = get_database_config()
agent_config = get_agent_config()

agent = ERPAgent(llm_config, db_config, agent_config)
print("✓ Agent 初始化成功\n")

# 测试第10题
question = "有没有出现过拖欠员工工资的情况？如果有，是哪些员工？"

print(f"{'=' * 70}")
print(f"测试问题: {question}")
print("=" * 70)

result = agent.query(question)

print(f"\n{'=' * 70}")
if result['success']:
    print("✓ 成功")
    print(f"答案: {result.get('answer', '')}")
    print(f"迭代次数: {result.get('iterations', 0)}")
    print(f"耗时: {result.get('total_time', 0):.2f}秒")
else:
    print("✗ 失败")
    print(f"错误: {result.get('error', '未知错误')}")
print("=" * 70)
