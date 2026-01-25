#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent 主入口
提供命令行交互界面
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))


def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    ERP Agent v0.1.0                          ║
    ║          基于 Kimi-K2 的智能数据查询助手                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def print_help():
    """打印帮助信息"""
    help_text = """
    使用说明:
    
    1. 直接输入您的问题，Agent 将自动生成 SQL 并返回答案
    2. 支持的查询类型：
       - 简单统计: "有多少在职员工？"
       - 部门分析: "每个部门有多少人？"
       - 时间查询: "今年新入职了多少人？"
       - 排名查询: "工资最高的前10名员工是谁？"
       - 复杂分析: "有没有拖欠工资的情况？"
    
    3. 特殊命令:
       - help: 显示帮助信息
       - test: 运行10个测试问题
       - exit/quit: 退出程序
    
    示例问题:
       > 有多少在职员工？
       > 去年A部门的平均工资是多少？
       > 工资最高的前10名员工是谁？
    """
    print(help_text)


def load_env():
    """加载环境变量"""
    try:
        from dotenv import load_dotenv
        env_path = project_root / '.env'
        if env_path.exists():
            load_dotenv(env_path)
            return True
        else:
            print("⚠️  未找到 .env 文件，请从 .env.example 复制并配置")
            return False
    except ImportError:
        print("⚠️  未安装 python-dotenv，请运行: pip install python-dotenv")
        return False


def check_environment():
    """检查环境配置"""
    print("正在检查环境配置...")
    
    # 检查必需的环境变量
    required_vars = [
        'KIMI_API_KEY',
        'DB_HOST',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("请在 .env 文件中配置这些变量")
        return False
    
    print("✓ 环境变量配置完整")
    return True


def test_database_connection():
    """测试数据库连接"""
    print("正在测试数据库连接...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✓ 数据库连接成功（共 {count} 名员工）")
        return True
        
    except ImportError:
        print("❌ 未安装 psycopg2，请运行: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def run_test_questions():
    """运行10个测试问题"""
    print("\n" + "="*70)
    print("运行测试问题集...")
    print("="*70)
    
    try:
        from tests.test_questions import TEST_QUESTIONS, print_all_questions
        print_all_questions()
        
        # TODO: 实现 Agent 后，实际运行这些问题
        print("\n注意: Agent 模块尚未实现，无法执行实际查询")
        print("请先完成 core/agent.py 的开发")
        
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")


def interactive_mode():
    """交互模式"""
    print("\n进入交互模式（输入 'help' 查看帮助，输入 'exit' 退出）\n")
    
    # TODO: 实现 Agent 后取消注释
    # from core.agent import ERPAgent
    # 
    # config = {
    #     'kimi_api_key': os.getenv('KIMI_API_KEY'),
    #     'db_config': {
    #         'host': os.getenv('DB_HOST'),
    #         'port': int(os.getenv('DB_PORT', 5432)),
    #         'database': os.getenv('DB_NAME'),
    #         'user': os.getenv('DB_USER'),
    #         'password': os.getenv('DB_PASSWORD')
    #     }
    # }
    # 
    # agent = ERPAgent(config)
    
    while True:
        try:
            question = input("\n> 请输入您的问题: ").strip()
            
            if not question:
                continue
            
            # 处理特殊命令
            if question.lower() in ['exit', 'quit', 'q']:
                print("\n感谢使用 ERP Agent，再见！")
                break
            
            elif question.lower() == 'help':
                print_help()
                continue
            
            elif question.lower() == 'test':
                run_test_questions()
                continue
            
            # TODO: 实现 Agent 后取消注释
            # print("\n正在处理您的问题...")
            # result = agent.query(question)
            # 
            # if result['success']:
            #     print(f"\n答案: {result['answer']}")
            #     print(f"查询迭代次数: {result['iterations']}")
            # else:
            #     print(f"\n❌ 查询失败: {result.get('error', '未知错误')}")
            
            print("\n注意: Agent 模块尚未实现")
            print("请先完成以下模块的开发:")
            print("  - core/agent.py")
            print("  - core/sql_generator.py")
            print("  - core/sql_executor.py")
            print("  - core/result_analyzer.py")
            print("  - utils/date_utils.py")
            
        except KeyboardInterrupt:
            print("\n\n中断操作，正在退出...")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")


def main():
    """主函数"""
    print_banner()
    
    # 加载环境变量
    if not load_env():
        print("\n请先配置 .env 文件后再运行")
        return
    
    # 检查环境
    if not check_environment():
        return
    
    # 测试数据库连接
    if not test_database_connection():
        return
    
    print("\n✓ 所有检查通过，准备就绪！\n")
    
    # 显示帮助
    print_help()
    
    # 进入交互模式
    interactive_mode()


if __name__ == '__main__':
    main()
