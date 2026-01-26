#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试 LLM 驱动的结果分析器

验证新的 ResultAnalyzer 是否正确使用 LLM 进行分析
"""

import sys
import json
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent))

from erp_agent.config import get_llm_config
from erp_agent.core import ResultAnalyzer


def test_basic_analysis():
    """测试基本的结果分析"""
    print("=" * 70)
    print("测试 1: 基本结果分析")
    print("=" * 70)
    
    try:
        llm_config = get_llm_config()
        analyzer = ResultAnalyzer(llm_config)
        
        # 模拟查询结果
        mock_result = {
            'success': True,
            'data': [
                {'department_name': '销售部', 'employee_count': 22, 'avg_salary': 8500.50},
                {'department_name': '技术部', 'employee_count': 35, 'avg_salary': 12000.00},
                {'department_name': '人力资源部', 'employee_count': 8, 'avg_salary': 7200.00}
            ],
            'row_count': 3
        }
        
        question = "每个部门有多少在职员工，平均工资是多少？"
        
        print(f"\n用户问题: {question}")
        print(f"\n查询结果:")
        print(json.dumps(mock_result['data'], ensure_ascii=False, indent=2))
        
        print("\n正在使用 LLM 分析结果...")
        analysis = analyzer.analyze_result(mock_result, question)
        
        print("\n【分析结果】")
        print(f"✓ 是否充分: {analysis['is_sufficient']}")
        print(f"✓ 完整性评分: {analysis['completeness']:.2f}")
        print(f"✓ 下一步动作: {analysis['next_action']}")
        print(f"✓ 建议: {analysis['suggestion']}")
        
        if analysis.get('key_findings'):
            print(f"\n✓ 关键发现:")
            for finding in analysis['key_findings']:
                print(f"  - {finding}")
        
        if analysis.get('anomalies'):
            print(f"\n⚠ 异常情况:")
            for anomaly in analysis['anomalies']:
                print(f"  - {anomaly}")
        
        print("\n✓ 测试 1 通过！\n")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试 1 失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_answer_generation():
    """测试答案生成"""
    print("=" * 70)
    print("测试 2: LLM 答案生成")
    print("=" * 70)
    
    try:
        llm_config = get_llm_config()
        analyzer = ResultAnalyzer(llm_config)
        
        # 模拟查询结果
        mock_result = {
            'success': True,
            'data': [
                {'employee_name': '张三', 'salary': 15000, 'department': '技术部'},
                {'employee_name': '李四', 'salary': 14500, 'department': '技术部'},
                {'employee_name': '王五', 'salary': 13800, 'department': '技术部'}
            ],
            'row_count': 3
        }
        
        question = "工资最高的3名员工是谁？"
        
        print(f"\n用户问题: {question}")
        print(f"\n查询结果:")
        print(json.dumps(mock_result['data'], ensure_ascii=False, indent=2))
        
        print("\n正在使用 LLM 生成自然语言答案...")
        answer = analyzer.generate_answer_suggestion(mock_result, question)
        
        print("\n【生成的答案】")
        print(answer)
        
        print("\n✓ 测试 2 通过！\n")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试 2 失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_empty_result():
    """测试空结果分析"""
    print("=" * 70)
    print("测试 3: 空结果分析")
    print("=" * 70)
    
    try:
        llm_config = get_llm_config()
        analyzer = ResultAnalyzer(llm_config)
        
        # 空结果
        empty_result = {
            'success': True,
            'data': [],
            'row_count': 0
        }
        
        question = "有没有拖欠工资超过3个月的员工？"
        
        print(f"\n用户问题: {question}")
        print(f"\n查询结果: 0 行（空结果）")
        
        print("\n正在分析空结果...")
        analysis = analyzer.analyze_result(empty_result, question)
        
        print("\n【分析结果】")
        print(f"✓ 是否充分: {analysis['is_sufficient']}")
        print(f"✓ 完整性评分: {analysis['completeness']:.2f}")
        print(f"✓ 建议: {analysis['suggestion']}")
        
        print("\n✓ 测试 3 通过！\n")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试 3 失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_continue_querying():
    """测试是否继续查询的判断"""
    print("=" * 70)
    print("测试 4: 是否继续查询判断")
    print("=" * 70)
    
    try:
        llm_config = get_llm_config()
        analyzer = ResultAnalyzer(llm_config)
        
        # 结果看起来不完整
        partial_result = {
            'success': True,
            'data': [
                {'total': 88}
            ],
            'row_count': 1
        }
        
        question = "公司有多少在职员工？他们的平均工资是多少？"
        
        print(f"\n用户问题: {question}")
        print(f"\n查询结果:")
        print(json.dumps(partial_result['data'], ensure_ascii=False, indent=2))
        
        print("\n正在判断是否需要继续查询...")
        should_continue, reason = analyzer.should_continue_querying(
            partial_result,
            question,
            iteration=1,
            max_iterations=5
        )
        
        print("\n【判断结果】")
        print(f"✓ 是否继续: {should_continue}")
        print(f"✓ 原因: {reason}")
        
        print("\n✓ 测试 4 通过！\n")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试 4 失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_fallback_mode():
    """测试降级模式（无 LLM 配置）"""
    print("=" * 70)
    print("测试 5: 降级模式（无 LLM）")
    print("=" * 70)
    
    try:
        # 不提供 LLM 配置
        analyzer = ResultAnalyzer(None)
        
        mock_result = {
            'success': True,
            'data': [
                {'count': 88}
            ],
            'row_count': 1
        }
        
        question = "公司有多少在职员工？"
        
        print(f"\n用户问题: {question}")
        print(f"\n使用降级模式分析...")
        
        analysis = analyzer.analyze_result(mock_result, question)
        
        print("\n【分析结果】")
        print(f"✓ 是否充分: {analysis['is_sufficient']}")
        print(f"✓ 完整性评分: {analysis['completeness']:.2f}")
        print(f"✓ 建议: {analysis['suggestion']}")
        
        answer = analyzer.generate_answer_suggestion(mock_result, question)
        print(f"\n【生成的答案】")
        print(answer)
        
        print("\n✓ 测试 5 通过！\n")
        return True
        
    except Exception as e:
        print(f"\n✗ 测试 5 失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("LLM 驱动的结果分析器 - 完整测试套件")
    print("=" * 70 + "\n")
    
    tests = [
        ("基本结果分析", test_basic_analysis),
        ("答案生成", test_answer_generation),
        ("空结果分析", test_empty_result),
        ("继续查询判断", test_continue_querying),
        ("降级模式", test_fallback_mode)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ 测试 '{name}' 异常: {e}\n")
            results.append((name, False))
    
    # 汇总结果
    print("\n" + "=" * 70)
    print("测试汇总")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓ 通过" if result else "✗ 失败"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 70)
    print(f"总计: {passed}/{total} 测试通过")
    print("=" * 70 + "\n")
    
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
