#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent 主入口
提供命令行交互界面
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径（erp_agent 文件夹的父目录）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置当前工作目录为项目根目录
os.chdir(str(project_root))


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
       - help   : 显示帮助信息
       - test   : 运行10个测试问题
       - stream : 切换流式/标准输出模式
       - exit   : 退出程序（也可使用 quit 或 q）
    
    4. Agent 特性:
       - 多轮 ReAct 推理：自动分析、查询、迭代
       - 智能错误修正：SQL 错误自动重试
       - 流式输出：实时查看推理过程
       - 时间智能：自动处理"今年"、"去年"等表达
    
    示例问题:
       > 有多少在职员工？
       > 去年A部门的平均工资是多少？
       > 工资最高的前10名员工是谁？
       > 从去年到今年涨薪幅度最大的10位员工是谁？
    """
    print(help_text)


def load_env():
    """加载环境变量"""
    try:
        from dotenv import load_dotenv
        
        # 尝试多个可能的.env文件位置
        env_paths = [
            project_root / '.env',  # 项目根目录
            Path(__file__).parent / '.env',  # erp_agent目录
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                print(f"✓ 已加载环境配置: {env_path}")
                return True
        
        # 如果没找到.env文件，检查是否有env.example
        env_example = Path(__file__).parent / 'env.example'
        if env_example.exists():
            print("⚠️  未找到 .env 文件")
            print(f"   请将 {env_example} 复制为 .env 并配置相关参数")
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
        'MOONSHOT_API_KEY',  # 更新为正确的环境变量名
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


def run_test_questions(agent):
    """运行10个测试问题"""
    print("\n" + "="*70)
    print("运行测试问题集...")
    print("="*70)
    
    try:
        from erp_agent.tests.test_questions import TEST_QUESTIONS
        
        for i, test in enumerate(TEST_QUESTIONS, 1):
            question = test['question']
            print(f"\n问题 {i}/{len(TEST_QUESTIONS)}: {question}")
            print("-" * 70)
            
            try:
                result = agent.query(question)
                
                if result['success']:
                    print(f"✓ 答案: {result['answer']}")
                    print(f"  迭代次数: {result['iterations']}, 耗时: {result['total_time']:.2f}秒")
                else:
                    print(f"✗ 查询失败: {result.get('error', '未知错误')}")
                    
            except Exception as e:
                print(f"✗ 执行出错: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*70)
        print("测试完成！")
        print("="*70)
        
    except ImportError as e:
        print(f"❌ 无法导入测试问题模块: {e}")
        print("   请确保 erp_agent/tests/test_questions.py 文件存在")
    except Exception as e:
        print(f"❌ 运行测试失败: {e}")
        import traceback
        traceback.print_exc()


def interactive_mode(agent, enable_stream=False):
    """交互模式"""
    mode_text = "流式模式" if enable_stream else "标准模式"
    print(f"\n进入交互模式 - {mode_text}（输入 'help' 查看帮助，输入 'exit' 退出）\n")
    
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
                run_test_questions(agent)
                continue
            
            elif question.lower() == 'stream':
                enable_stream = not enable_stream
                mode_text = "流式模式" if enable_stream else "标准模式"
                print(f"\n已切换到 {mode_text}")
                continue
            
            # 执行查询
            print("\n正在处理您的问题...")
            
            if enable_stream:
                # 流式输出
                print()
                for chunk in agent.query_stream(question):
                    chunk_type = chunk['type']
                    
                    if chunk_type == 'iteration_start':
                        print(f"\n[第 {chunk['iteration']} 轮]")
                    
                    elif chunk_type == 'thought':
                        print(f"💭 思考: {chunk['thought']}")
                    
                    elif chunk_type == 'action':
                        action_emoji = "⚙️" if chunk['action'] == 'execute_sql' else "💬"
                        print(f"{action_emoji} 动作: {chunk['action']}")
                    
                    elif chunk_type == 'sql_executing':
                        sql_preview = chunk['sql'][:100] + "..." if len(chunk['sql']) > 100 else chunk['sql']
                        print(f"📊 执行 SQL: {sql_preview}")
                    
                    elif chunk_type == 'sql_result':
                        result_data = chunk['result']
                        if result_data['success']:
                            print(f"✓ 查询成功，返回 {result_data['row_count']} 行")
                        else:
                            print(f"✗ 查询失败: {result_data['error']}")
                    
                    elif chunk_type == 'answer':
                        print(f"\n💬 答案: {chunk['answer']}")
                    
                    elif chunk_type == 'final':
                        print(f"\n{'='*60}")
                        if chunk['success']:
                            print(f"✓ 查询完成")
                            print(f"   最终答案: {chunk['answer']}")
                        else:
                            print(f"✗ 查询失败: {chunk.get('error', '未知错误')}")
                        print(f"   迭代次数: {chunk['iterations']}, 总耗时: {chunk['total_time']:.2f}秒")
                        print(f"{'='*60}")
                    
                    elif chunk_type == 'error':
                        print(f"✗ 错误: {chunk['error']}")
            else:
                # 标准输出
                result = agent.query(question)
                
                print(f"\n{'='*60}")
                if result['success']:
                    print(f"✓ 答案: {result['answer']}")
                    print(f"   迭代次数: {result['iterations']}, 总耗时: {result['total_time']:.2f}秒")
                else:
                    print(f"✗ 查询失败: {result.get('error', '未知错误')}")
                print(f"{'='*60}")
            
        except KeyboardInterrupt:
            print("\n\n中断操作，正在退出...")
            break
        except Exception as e:
            print(f"\n❌ 发生错误: {e}")
            import traceback
            traceback.print_exc()


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
    
    # 初始化 Agent
    print("正在初始化 ERP Agent...")
    try:
        from erp_agent.core import ERPAgent
        from erp_agent.config import get_llm_config, get_database_config, get_agent_config
        
        llm_config = get_llm_config()
        db_config = get_database_config()
        agent_config = get_agent_config()
        
        agent = ERPAgent(llm_config, db_config, agent_config)
        print("✓ ERP Agent 初始化成功\n")
        
    except Exception as e:
        print(f"❌ 初始化 Agent 失败: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 显示帮助
    print_help()
    
    # 进入交互模式
    interactive_mode(agent, enable_stream=False)


if __name__ == '__main__':
    main()
