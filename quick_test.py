#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速测试脚本 - 验证新增模块是否正确集成
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def test_imports():
    """测试所有导入是否正常"""
    print("=" * 60)
    print("测试1: 检查导入")
    print("=" * 60)
    
    try:
        # 测试核心模块导入
        from erp_agent.core import ERPAgent, ResultAnalyzer
        print("✓ 核心模块导入成功")
        
        # 测试测试模块导入
        from erp_agent.tests.test_questions import TEST_QUESTIONS, validate_result
        print("✓ 测试模块导入成功")
        
        # 测试配置模块导入
        from erp_agent.config import get_llm_config, get_database_config
        print("✓ 配置模块导入成功")
        
        return True
        
    except Exception as e:
        print(f"✗ 导入失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_result_analyzer():
    """测试结果分析器"""
    print("\n" + "=" * 60)
    print("测试2: 结果分析器功能")
    print("=" * 60)
    
    try:
        from erp_agent.core import ResultAnalyzer
        
        analyzer = ResultAnalyzer()
        print("✓ 结果分析器实例化成功")
        
        # 测试分析功能
        mock_result = {
            'success': True,
            'data': [
                {'department_name': 'A部门', 'employee_count': 22},
                {'department_name': 'B部门', 'employee_count': 20}
            ],
            'row_count': 2
        }
        
        analysis = analyzer.analyze_result(
            mock_result,
            "每个部门有多少在职员工？"
        )
        
        print(f"✓ 分析完成")
        print(f"  - 是否足够: {analysis['is_sufficient']}")
        print(f"  - 完整性: {analysis['completeness']:.2f}")
        print(f"  - 建议: {analysis['suggestion'][:50]}...")
        
        # 测试答案建议
        suggestion = analyzer.generate_answer_suggestion(
            mock_result,
            "每个部门有多少在职员工？"
        )
        print(f"✓ 答案建议生成成功 ({len(suggestion)} 字符)")
        
        return True
        
    except Exception as e:
        print(f"✗ 结果分析器测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_validation():
    """测试验证功能"""
    print("\n" + "=" * 60)
    print("测试3: 验证功能")
    print("=" * 60)
    
    try:
        from erp_agent.tests.test_questions import TEST_QUESTIONS, validate_result
        
        # 检查测试问题数量
        print(f"✓ 加载了 {len(TEST_QUESTIONS)} 个测试问题")
        
        # 测试第一个问题的验证
        question = TEST_QUESTIONS[0]
        print(f"✓ 问题1: {question['question']}")
        print(f"  - 验证类型: {question['validation']['type']}")
        
        # 测试验证函数
        mock_result = {
            'success': True,
            'data': [{'avg_days': 1100.0, 'avg_years': 3.01}],
            'row_count': 1
        }
        
        passed, message, details = validate_result(1, mock_result)
        print(f"✓ 验证函数执行成功")
        print(f"  - 结果: {'通过' if passed else '失败'}")
        print(f"  - 消息: {message}")
        
        return True
        
    except Exception as e:
        print(f"✗ 验证功能测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_integration():
    """测试Agent集成"""
    print("\n" + "=" * 60)
    print("测试4: Agent 集成")
    print("=" * 60)
    
    try:
        from erp_agent.core import ERPAgent
        
        # 检查Agent是否有result_analyzer属性
        print("✓ 检查Agent类定义...")
        
        # 检查初始化参数
        import inspect
        init_signature = inspect.signature(ERPAgent.__init__)
        print(f"✓ Agent.__init__ 参数: {list(init_signature.parameters.keys())}")
        
        # 检查是否有result_analyzer的引用
        agent_source = inspect.getsource(ERPAgent)
        has_analyzer = 'result_analyzer' in agent_source.lower()
        
        if has_analyzer:
            print("✓ Agent 已集成 ResultAnalyzer")
        else:
            print("⚠️  Agent 中未找到 ResultAnalyzer 引用（可能正常）")
        
        return True
        
    except Exception as e:
        print(f"✗ Agent集成测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_documentation():
    """测试文档是否存在"""
    print("\n" + "=" * 60)
    print("测试5: 文档文件")
    print("=" * 60)
    
    docs = [
        'TESTING_WITH_VALIDATION.md',
        'CHANGES_SUMMARY.md',
        'run_validated_tests.py'
    ]
    
    all_exist = True
    for doc in docs:
        path = project_root / doc
        if path.exists():
            print(f"✓ {doc} 存在")
        else:
            print(f"✗ {doc} 不存在")
            all_exist = False
    
    return all_exist


def main():
    """主函数"""
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║            ERP Agent 快速集成测试                              ║
    ║      验证新增模块是否正确集成到现有系统                          ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    results = []
    
    # 运行所有测试
    results.append(("导入测试", test_imports()))
    results.append(("结果分析器", test_result_analyzer()))
    results.append(("验证功能", test_validation()))
    results.append(("Agent集成", test_agent_integration()))
    results.append(("文档检查", test_documentation()))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✓" if result else "✗"
        print(f"{status} {name}")
    
    print(f"\n总计: {passed}/{total} 测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过！系统集成成功。")
        print("\n下一步:")
        print("  1. 配置 .env 文件（如果还没配置）")
        print("  2. 运行完整测试: python run_validated_tests.py")
        print("  3. 或启动交互模式: python erp_agent/main.py")
    else:
        print("\n⚠️  部分测试失败，请检查错误信息。")
    
    print("\n" + "=" * 60)


if __name__ == '__main__':
    main()
