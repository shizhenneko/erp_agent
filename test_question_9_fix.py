#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试：验证问题9的时间推理是否修复

预期：应该使用2025和2026年，而不是2024和2025年
"""

import re
from erp_agent.main import get_agent
from erp_agent.utils.date_utils import get_current_datetime


def test_question_9():
    """测试问题9的时间推理"""
    
    # 获取当前年份
    date_info = get_current_datetime()
    current_year = date_info['year']
    expected_years = [current_year - 1, current_year]  # 应该是 [2025, 2026]
    forbidden_years = [2024]  # 不应该使用2024
    
    print("=" * 80)
    print("测试问题9：从去年到今年涨薪幅度最大的10位员工")
    print("=" * 80)
    print(f"当前年份: {current_year}")
    print(f"预期使用年份: {expected_years} (去年={current_year-1}, 今年={current_year})")
    print(f"不应该使用: {forbidden_years}")
    print("=" * 80)
    
    # 执行查询
    question = "从去年到今年涨薪幅度最大的10位员工是谁？"
    print(f"\n问题: {question}\n")
    
    agent = get_agent()
    result = agent.query(question)
    
    # 分析结果
    print("\n" + "=" * 80)
    print("分析结果")
    print("=" * 80)
    
    # 1. 提取第一轮的thought
    if result['context'] and len(result['context']) > 0:
        first_iteration = result['context'][0]
        thought = first_iteration.get('thought', '')
        sql = first_iteration.get('sql', '')
        
        print(f"\n【第1轮 Thought】\n{thought}\n")
        
        # 2. 检查thought中提到的年份
        thought_years = re.findall(r'\b(20\d{2})\b', thought)
        print(f"Thought中提到的年份: {thought_years}")
        
        # 3. 检查SQL中使用的年份
        sql_years = re.findall(r'\b(20\d{2})\b', sql)
        sql_years_int = sorted(set(int(y) for y in sql_years))
        print(f"SQL中使用的年份: {sql_years_int}")
        
        if sql:
            print(f"\n【生成的SQL（前300字符）】\n{sql[:300]}...\n")
        
        # 4. 验证
        print("\n" + "=" * 80)
        print("验证结果")
        print("=" * 80)
        
        checks = {
            "使用了正确的年份": all(y in sql_years_int for y in expected_years),
            "避免了错误的年份": not any(y in sql_years_int for y in forbidden_years),
            "Thought中有明确的时间推理": any(str(current_year) in thought for _ in [1]),
        }
        
        all_passed = all(checks.values())
        
        for check_name, passed in checks.items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} - {check_name}")
        
        print("\n" + "=" * 80)
        if all_passed:
            print("🎉 测试通过！时间推理已修复。")
        else:
            print("❌ 测试失败！还需要进一步调整。")
        print("=" * 80)
        
        # 5. 打印完整答案
        print(f"\n【最终答案】\n{result.get('answer', '无答案')}\n")
        
        return all_passed
    else:
        print("❌ 没有执行上下文，查询可能失败")
        return False


def main():
    """主函数"""
    try:
        success = test_question_9()
        exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        exit(1)


if __name__ == '__main__':
    main()
