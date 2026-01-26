#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent 验证测试运行器

运行10个测试问题，并使用标准答案进行验证
"""

import sys
import os
import time
from pathlib import Path
from typing import Dict, Any

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


def print_banner():
    """打印横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║              ERP Agent 验证测试运行器                          ║
    ║         测试10个问题并使用标准答案进行验证                      ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def check_environment() -> bool:
    """检查环境配置"""
    print("正在检查环境配置...")
    
    required_vars = [
        'MOONSHOT_API_KEY',
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
        return False
    
    print("✓ 环境变量配置完整")
    return True


def test_database_connection() -> bool:
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
        
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def run_test_with_validation(
    agent,
    question_id: int,
    question_text: str,
    validation_func
) -> Dict[str, Any]:
    """
    运行单个测试问题并验证结果
    
    Args:
        agent: ERPAgent 实例
        question_id: 问题ID
        question_text: 问题文本
        validation_func: 验证函数
        
    Returns:
        测试结果字典
    """
    print(f"\n{'='*70}")
    print(f"问题 {question_id}: {question_text}")
    print('-' * 70)
    
    start_time = time.time()
    
    try:
        # 执行查询
        result = agent.query(question_text)
        elapsed_time = time.time() - start_time
        
        test_result = {
            'question_id': question_id,
            'question': question_text,
            'success': result['success'],
            'answer': result.get('answer', ''),
            'iterations': result.get('iterations', 0),
            'time': elapsed_time,
            'error': result.get('error'),
            'validated': False,
            'validation_message': '',
            'validation_details': {}
        }
        
        if result['success']:
            print(f"✓ 查询成功")
            print(f"  答案: {result['answer'][:200]}..." if len(result['answer']) > 200 else f"  答案: {result['answer']}")
            print(f"  迭代次数: {result['iterations']}, 耗时: {elapsed_time:.2f}秒")
            
            # 验证结果
            if validation_func:
                # 提取最后一次成功的SQL结果
                sql_result = None
                for ctx in reversed(result.get('context', [])):
                    if 'result' in ctx and ctx['result'].get('success'):
                        sql_result = ctx['result']
                        break
                
                if sql_result:
                    validated, message, details = validation_func(question_id, sql_result)
                    test_result['validated'] = validated
                    test_result['validation_message'] = message
                    test_result['validation_details'] = details
                    
                    if validated:
                        print(f"  ✓ 验证通过: {message}")
                    else:
                        print(f"  ✗ 验证失败: {message}")
                        if details:
                            print(f"    详情: {details}")
                else:
                    print(f"  ⚠️  无法提取SQL结果进行验证")
        else:
            print(f"✗ 查询失败: {result.get('error', '未知错误')}")
        
        return test_result
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"✗ 测试出错: {e}")
        import traceback
        traceback.print_exc()
        
        return {
            'question_id': question_id,
            'question': question_text,
            'success': False,
            'error': str(e),
            'time': elapsed_time,
            'validated': False
        }


def print_summary(results: list):
    """打印测试总结"""
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    
    total = len(results)
    successful = sum(1 for r in results if r['success'])
    validated = sum(1 for r in results if r.get('validated', False))
    
    print(f"\n总问题数: {total}")
    print(f"查询成功: {successful} ({successful/total*100:.1f}%)")
    print(f"验证通过: {validated} ({validated/total*100:.1f}%)")
    
    # 按类别统计
    print(f"\n详细结果:")
    for i, result in enumerate(results, 1):
        status = "✓" if result['success'] else "✗"
        validation = ""
        if result['success']:
            if result.get('validated'):
                validation = " [验证通过]"
            elif result.get('validation_message'):
                validation = f" [验证失败: {result.get('validation_message', '')}]"
        
        print(f"  {status} 问题 {result['question_id']}: "
              f"{result['question'][:40]}... "
              f"({result['time']:.2f}s){validation}")
    
    # 失败的问题
    failed = [r for r in results if not r['success']]
    if failed:
        print(f"\n失败的问题 ({len(failed)}):")
        for result in failed:
            print(f"  - 问题 {result['question_id']}: {result.get('error', '未知错误')}")
    
    # 验证失败的问题
    validation_failed = [r for r in results if r['success'] and not r.get('validated', False) and r.get('validation_message')]
    if validation_failed:
        print(f"\n验证失败的问题 ({len(validation_failed)}):")
        for result in validation_failed:
            print(f"  - 问题 {result['question_id']}: {result.get('validation_message', '')}")


def main():
    """主函数"""
    print_banner()
    
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
        from erp_agent.tests.test_questions import TEST_QUESTIONS, validate_result
        
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
    
    # 运行所有测试
    print("="*70)
    print("开始运行测试")
    print("="*70)
    
    results = []
    
    for test_q in TEST_QUESTIONS:
        result = run_test_with_validation(
            agent=agent,
            question_id=test_q['id'],
            question_text=test_q['question'],
            validation_func=validate_result
        )
        results.append(result)
        
        # 短暂暂停以避免API限流
        time.sleep(1)
    
    # 打印总结
    print_summary(results)
    
    print("\n" + "="*70)
    print("测试完成！")
    print("="*70)


if __name__ == '__main__':
    main()
