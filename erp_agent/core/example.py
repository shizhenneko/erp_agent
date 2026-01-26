#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent Core 模块使用示例

展示如何使用 core 模块的各个组件：
1. 基础查询
2. 流式查询
3. 查看执行上下文
4. 错误处理
"""

import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def example_basic_query():
    """示例 1: 基础查询"""
    print("=" * 70)
    print("示例 1: 基础查询")
    print("=" * 70)
    
    from erp_agent.core import ERPAgent
    from erp_agent.config import get_llm_config, get_database_config
    
    # 初始化 Agent
    llm_config = get_llm_config()
    db_config = get_database_config()
    agent = ERPAgent(llm_config, db_config)
    
    # 执行查询
    question = "公司有多少在职员工？"
    print(f"\n问题: {question}\n")
    
    result = agent.query(question)
    
    # 显示结果
    print(f"✓ 成功: {result['success']}")
    print(f"✓ 答案: {result['answer']}")
    print(f"✓ 迭代次数: {result['iterations']}")
    print(f"✓ 总耗时: {result['total_time']:.2f}秒")
    
    if result['error']:
        print(f"✗ 错误: {result['error']}")


def example_stream_query():
    """示例 2: 流式查询"""
    print("\n" + "=" * 70)
    print("示例 2: 流式查询（实时查看推理过程）")
    print("=" * 70)
    
    from erp_agent.core import ERPAgent
    from erp_agent.config import get_llm_config, get_database_config
    
    # 初始化 Agent
    llm_config = get_llm_config()
    db_config = get_database_config()
    agent = ERPAgent(llm_config, db_config)
    
    # 流式查询
    question = "每个部门分别有多少在职员工？"
    print(f"\n问题: {question}\n")
    
    for chunk in agent.query_stream(question):
        chunk_type = chunk['type']
        
        if chunk_type == 'start':
            print(f"[开始] 处理问题...")
        
        elif chunk_type == 'iteration_start':
            print(f"\n[第 {chunk['iteration']} 轮迭代]")
        
        elif chunk_type == 'thought':
            print(f"💭 思考: {chunk['thought'][:100]}...")
        
        elif chunk_type == 'action':
            action_emoji = "⚙️" if chunk['action'] == 'execute_sql' else "💬"
            print(f"{action_emoji} 动作: {chunk['action']}")
        
        elif chunk_type == 'sql_executing':
            sql = chunk['sql']
            sql_preview = sql[:150] + "..." if len(sql) > 150 else sql
            sql_preview = sql_preview.replace('\n', ' ')
            print(f"📊 执行 SQL: {sql_preview}")
        
        elif chunk_type == 'sql_result':
            result_data = chunk['result']
            if result_data['success']:
                print(f"✓ 查询成功，返回 {result_data['row_count']} 行")
            else:
                print(f"✗ 查询失败: {result_data['error']}")
        
        elif chunk_type == 'answer':
            print(f"\n💬 最终答案: {chunk['answer']}")
        
        elif chunk_type == 'final':
            print(f"\n[完成]")
            print(f"  成功: {chunk['success']}")
            print(f"  迭代次数: {chunk['iterations']}")
            print(f"  总耗时: {chunk['total_time']:.2f}秒")
        
        elif chunk_type == 'error':
            print(f"✗ 错误: {chunk['error']}")


def example_context_inspection():
    """示例 3: 查看执行上下文"""
    print("\n" + "=" * 70)
    print("示例 3: 查看执行上下文（每一轮的详细信息）")
    print("=" * 70)
    
    from erp_agent.core import ERPAgent
    from erp_agent.config import get_llm_config, get_database_config
    
    # 初始化 Agent
    llm_config = get_llm_config()
    db_config = get_database_config()
    agent = ERPAgent(llm_config, db_config)
    
    # 执行查询
    question = "去年A部门的平均工资是多少？"
    print(f"\n问题: {question}\n")
    
    result = agent.query(question)
    
    # 显示每一轮的详细信息
    print(f"查询{'成功' if result['success'] else '失败'}，共 {result['iterations']} 轮迭代\n")
    
    for i, ctx in enumerate(result['context'], 1):
        print(f"第 {i} 轮:")
        print(f"  思考: {ctx.get('thought', 'N/A')[:80]}...")
        print(f"  动作: {ctx.get('action', 'N/A')}")
        
        if 'sql' in ctx:
            sql = ctx['sql'].replace('\n', ' ').strip()
            print(f"  SQL: {sql[:100]}...")
            
            if 'result' in ctx:
                res = ctx['result']
                if res['success']:
                    print(f"  结果: ✓ 成功，{res['row_count']} 行，{res['execution_time']:.3f}秒")
                else:
                    print(f"  结果: ✗ 失败，{res['error']}")
        
        if 'answer' in ctx:
            print(f"  答案: {ctx['answer'][:100]}...")
        
        print()


def example_complex_query():
    """示例 4: 复杂查询（需要多轮迭代）"""
    print("=" * 70)
    print("示例 4: 复杂查询（可能需要多轮迭代）")
    print("=" * 70)
    
    from erp_agent.core import ERPAgent
    from erp_agent.config import get_llm_config, get_database_config
    
    # 初始化 Agent
    llm_config = get_llm_config()
    db_config = get_database_config()
    agent = ERPAgent(llm_config, db_config)
    
    # 复杂问题
    question = "从去年到今年涨薪幅度最大的10位员工是谁？"
    print(f"\n问题: {question}\n")
    
    result = agent.query(question)
    
    print(f"答案: {result['answer']}")
    print(f"\n分析:")
    print(f"  迭代次数: {result['iterations']} 轮")
    print(f"  总耗时: {result['total_time']:.2f}秒")
    print(f"  成功: {result['success']}")


def example_error_handling():
    """示例 5: 错误处理和重试"""
    print("\n" + "=" * 70)
    print("示例 5: 错误处理（观察 Agent 如何自动修正错误）")
    print("=" * 70)
    
    from erp_agent.core import ERPAgent
    from erp_agent.config import get_llm_config, get_database_config
    
    # 初始化 Agent
    llm_config = get_llm_config()
    db_config = get_database_config()
    agent = ERPAgent(llm_config, db_config)
    
    # 这个问题可能会导致 LLM 生成错误的 SQL
    question = "统计所有部门的员工数量"
    print(f"\n问题: {question}\n")
    
    result = agent.query(question)
    
    # 查看是否有错误重试
    has_error = False
    for ctx in result['context']:
        if 'result' in ctx and not ctx['result'].get('success', False):
            has_error = True
            print(f"检测到错误:")
            print(f"  SQL: {ctx['sql'][:100]}...")
            print(f"  错误: {ctx['result']['error']}")
            print()
    
    if has_error:
        print("Agent 自动修正错误并重试 ✓")
    
    print(f"\n最终结果:")
    print(f"  答案: {result['answer']}")
    print(f"  迭代次数: {result['iterations']}")


def example_component_usage():
    """示例 6: 单独使用各个组件"""
    print("\n" + "=" * 70)
    print("示例 6: 单独使用各个组件")
    print("=" * 70)
    
    from erp_agent.core import SQLExecutor, SQLGenerator
    from erp_agent.config import get_llm_config, get_database_config
    
    # 1. 单独使用 SQLExecutor
    print("\n[SQLExecutor] 直接执行 SQL:")
    db_config = get_database_config()
    executor = SQLExecutor(db_config)
    
    sql = "SELECT COUNT(*) as count FROM employees WHERE leave_date IS NULL;"
    result = executor.execute(sql)
    
    if result['success']:
        print(f"✓ 查询成功: {result['data']}")
    else:
        print(f"✗ 查询失败: {result['error']}")
    
    # 2. 单独使用 SQLGenerator
    print("\n[SQLGenerator] 生成 SQL:")
    llm_config = get_llm_config()
    generator = SQLGenerator(llm_config)
    
    question = "有多少在职员工？"
    gen_result = generator.generate(question)
    
    print(f"思考: {gen_result['thought']}")
    print(f"动作: {gen_result['action']}")
    if gen_result['action'] == 'execute_sql':
        print(f"生成的 SQL: {gen_result['sql']}")


def main():
    """运行所有示例"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║         ERP Agent Core 模块使用示例                          ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("\n")
    
    try:
        # 检查环境
        from dotenv import load_dotenv
        load_dotenv()
        
        # 运行示例
        examples = [
            ("基础查询", example_basic_query),
            ("流式查询", example_stream_query),
            ("查看执行上下文", example_context_inspection),
            ("复杂查询", example_complex_query),
            ("错误处理", example_error_handling),
            ("组件单独使用", example_component_usage),
        ]
        
        print("可用的示例:")
        for i, (name, _) in enumerate(examples, 1):
            print(f"  {i}. {name}")
        print(f"  0. 运行所有示例")
        
        choice = input("\n请选择要运行的示例 (0-6): ").strip()
        
        if choice == '0':
            # 运行所有示例
            for name, func in examples:
                print(f"\n运行示例: {name}")
                func()
                input("\n按 Enter 继续...")
        elif choice.isdigit() and 1 <= int(choice) <= len(examples):
            # 运行选定的示例
            name, func = examples[int(choice) - 1]
            print(f"\n运行示例: {name}")
            func()
        else:
            print("无效的选择")
        
        print("\n" + "=" * 70)
        print("示例运行完成！")
        print("=" * 70)
        
    except KeyboardInterrupt:
        print("\n\n用户中断，退出...")
    except Exception as e:
        print(f"\n运行示例时出错: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
