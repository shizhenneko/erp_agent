#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
快速运行测试脚本

这是一个便捷脚本，用于快速运行 ERP Agent 的测试套件。
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def check_environment():
    """检查环境是否就绪"""
    from dotenv import load_dotenv
    
    # 加载环境变量
    env_file = project_root / '.env'
    if not env_file.exists():
        print("⚠️  未找到 .env 文件")
        print("请从 .env.example 复制并配置环境变量")
        return False
    
    load_dotenv(env_file)
    
    # 检查必需的环境变量
    required_vars = ['MOONSHOT_API_KEY', 'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing = [var for var in required_vars if not os.getenv(var)]
    
    if missing:
        print(f"⚠️  缺少必需的环境变量: {', '.join(missing)}")
        return False
    
    return True


def print_banner():
    """打印横幅"""
    print("\n" + "=" * 70)
    print("               ERP Agent 测试套件")
    print("=" * 70 + "\n")


def show_menu():
    """显示菜单"""
    print("测试选项:")
    print("  1. 运行单元测试（快速，不需要API）")
    print("  2. 运行10个测试问题（需要API和数据库）")
    print("  3. 运行所有测试")
    print("  4. 查看测试说明")
    print("  0. 退出")
    print()


def show_help():
    """显示帮助信息"""
    help_text = """
╔══════════════════════════════════════════════════════════════╗
║                    测试说明                                   ║
╚══════════════════════════════════════════════════════════════╝

1. 单元测试
   - 测试所有核心组件的功能
   - 不需要API密钥和数据库连接
   - 快速执行（约2-5秒）
   - 包含35+个测试方法

2. 10个测试问题
   - 测试完整的业务场景
   - 需要有效的API密钥和数据库连接
   - 较慢执行（约30-50秒）
   - 涵盖简单到复杂的查询

3. 测试覆盖范围
   - Config模块: DatabaseConfig, LLMConfig, AgentConfig
   - Core模块: ERPAgent, SQLExecutor, SQLGenerator
   - Utils模块: date_utils, logger, prompt_builder

4. 详细文档
   - TEST_GUIDE.md - 快速入门指南
   - erp_agent/tests/README.md - 详细测试文档
   - erp_agent/tests/TESTING_SUMMARY.md - 测试总结

5. 运行要求
   - Python 3.8+
   - 已安装所有依赖 (pip install -r requirements.txt)
   - 配置好 .env 文件（问题测试需要）

按 Enter 继续...
"""
    print(help_text)
    input()


def run_unit_tests():
    """运行单元测试"""
    print("\n开始运行单元测试...\n")
    from erp_agent.tests.test_agent import run_unit_tests
    result = run_unit_tests()
    return result.wasSuccessful()


def run_question_tests():
    """运行问题测试"""
    if not check_environment():
        print("\n❌ 环境未就绪，无法运行问题测试")
        print("请先配置 .env 文件")
        return False
    
    print("\n开始运行10个测试问题...\n")
    from erp_agent.tests.test_agent import run_question_tests
    results = run_question_tests()
    return results is not None and results['success'] > 0


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("第一部分: 单元测试")
    print("=" * 70)
    
    unit_success = run_unit_tests()
    
    print("\n" + "=" * 70)
    print("第二部分: 10个测试问题")
    print("=" * 70)
    
    question_success = run_question_tests()
    
    print("\n" + "=" * 70)
    print("测试完成")
    print("=" * 70)
    print(f"单元测试: {'✓ 通过' if unit_success else '✗ 失败'}")
    print(f"问题测试: {'✓ 通过' if question_success else '✗ 失败'}")
    print("=" * 70)


def main():
    """主函数"""
    print_banner()
    
    while True:
        show_menu()
        
        try:
            choice = input("请选择 (0-4): ").strip()
            
            if choice == '0':
                print("\n再见！\n")
                break
            
            elif choice == '1':
                run_unit_tests()
                input("\n按 Enter 继续...")
            
            elif choice == '2':
                run_question_tests()
                input("\n按 Enter 继续...")
            
            elif choice == '3':
                run_all_tests()
                input("\n按 Enter 继续...")
            
            elif choice == '4':
                show_help()
            
            else:
                print("\n❌ 无效的选择，请重试\n")
        
        except KeyboardInterrupt:
            print("\n\n中断退出\n")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}\n")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    # 支持命令行参数
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['unit', 'u', '1']:
            run_unit_tests()
        
        elif arg in ['questions', 'q', '2']:
            run_question_tests()
        
        elif arg in ['all', 'a', '3']:
            run_all_tests()
        
        elif arg in ['help', 'h', '-h', '--help']:
            show_help()
        
        else:
            print(f"未知参数: {arg}")
            print("\n用法:")
            print("  python run_tests.py [unit|questions|all|help]")
            print("\n或者直接运行进入交互模式:")
            print("  python run_tests.py")
    
    else:
        # 交互模式
        main()
