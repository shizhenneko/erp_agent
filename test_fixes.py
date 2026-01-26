#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试修复后的 Agent 对于问题9和问题10的SQL生成能力
"""

import sys
from erp_agent.config import get_llm_config, get_database_config, get_agent_config
from erp_agent.core.agent import ERPAgent


def test_question_9():
    """测试问题9: 从去年到今年涨薪幅度最大的10位员工是谁？"""
    print("="*70)
    print("测试问题9: 从去年到今年涨薪幅度最大的10位员工是谁？")
    print("="*70)
    
    # 初始化
    llm_config = get_llm_config()
    db_config = get_database_config()
    agent_config = get_agent_config()
    agent = ERPAgent(llm_config, db_config, agent_config)
    
    # 执行查询
    result = agent.query("从去年到今年涨薪幅度最大的10位员工是谁？")
    
    # 打印结果
    print(f"\n成功: {result['success']}")
    print(f"迭代次数: {result['iterations']}")
    print(f"答案:\n{result['answer']}")
    
    # 打印生成的SQL
    print("\n生成的SQL:")
    for i, ctx in enumerate(result['context'], 1):
        if 'sql' in ctx:
            print(f"\n第{i}轮SQL:")
            print(ctx['sql'])
            if 'result' in ctx and ctx['result']['success']:
                print(f"返回行数: {ctx['result']['row_count']}")
    
    print("\n" + "="*70)
    return result


def test_question_10():
    """测试问题10: 有没有出现过拖欠员工工资的情况？"""
    print("\n" + "="*70)
    print("测试问题10: 有没有出现过拖欠员工工资的情况？如果有，是哪些员工？")
    print("="*70)
    
    # 初始化
    llm_config = get_llm_config()
    db_config = get_database_config()
    agent_config = get_agent_config()
    agent = ERPAgent(llm_config, db_config, agent_config)
    
    # 执行查询
    result = agent.query("有没有出现过拖欠员工工资的情况？如果有，是哪些员工？")
    
    # 打印结果
    print(f"\n成功: {result['success']}")
    print(f"迭代次数: {result['iterations']}")
    print(f"答案:\n{result['answer']}")
    
    # 打印生成的SQL
    print("\n生成的SQL:")
    for i, ctx in enumerate(result['context'], 1):
        if 'sql' in ctx:
            print(f"\n第{i}轮SQL:")
            print(ctx['sql'])
            if 'result' in ctx and ctx['result']['success']:
                print(f"返回行数: {ctx['result']['row_count']}")
    
    print("\n" + "="*70)
    return result


def main():
    """运行测试"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════════════╗")
    print("║          测试修复后的 SQL 生成能力                               ║")
    print("╚═══════════════════════════════════════════════════════════════════╝")
    print("\n")
    
    try:
        # 测试问题9
        result9 = test_question_9()
        
        # 测试问题10
        result10 = test_question_10()
        
        # 总结
        print("\n" + "="*70)
        print("测试总结")
        print("="*70)
        print(f"问题9 成功: {result9['success']}, 迭代: {result9['iterations']}")
        print(f"问题10 成功: {result10['success']}, 迭代: {result10['iterations']}")
        
        # 验证要点
        print("\n验证要点:")
        print("1. 问题9应该使用年度平均工资对比（2025年平均 vs 2026年平均）")
        print("   而不是单月对比（2025-12 vs 2026-01）")
        print("2. 问题10应该使用generate_series生成所有应发月份，然后LEFT JOIN")
        print("   而不是只检查最后一次发薪日期")
        print("3. 问题10应该返回所有拖欠记录（可能超过10条），不应使用LIMIT")
        
    except Exception as e:
        print(f"\n测试失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
