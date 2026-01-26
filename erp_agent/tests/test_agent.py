#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent 完整测试套件
测试所有核心组件的功能
"""

import unittest
import sys
import os
from datetime import datetime
from typing import Dict, Any

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))


class TestDateUtils(unittest.TestCase):
    """测试时间处理工具（泛化版本）"""
    
    def test_get_current_datetime(self):
        """测试获取当前时间信息"""
        from erp_agent.utils import get_current_datetime
        info = get_current_datetime()
        
        # 验证返回的字典包含所需字段
        self.assertIn('current_date', info)
        self.assertIn('current_datetime', info)
        self.assertIn('year', info)
        self.assertIn('month', info)
        self.assertIn('day', info)
        self.assertIn('weekday', info)
        self.assertIn('weekday_cn', info)
        
        # 验证日期格式
        self.assertRegex(info['current_date'], r'\d{4}-\d{2}-\d{2}')
        self.assertIsInstance(info['year'], int)
        self.assertIsInstance(info['month'], int)
        self.assertTrue(1 <= info['month'] <= 12)
    
    def test_calculate_date_offset(self):
        """测试计算日期偏移"""
        from erp_agent.utils import calculate_date_offset
        
        # 测试年份偏移
        result = calculate_date_offset('2026-01-25', years=-1)
        self.assertEqual(result, '2025-01-25')
        
        # 测试月份偏移
        result = calculate_date_offset('2026-01-25', months=-3)
        self.assertEqual(result, '2025-10-25')
        
        # 测试天数偏移
        result = calculate_date_offset('2026-01-25', days=10)
        self.assertEqual(result, '2026-02-04')
        
        # 测试组合偏移
        result = calculate_date_offset('2026-01-25', years=1, months=2, days=5)
        self.assertEqual(result, '2027-03-30')
    
    def test_get_date_range_for_period(self):
        """测试获取时期的日期范围"""
        from erp_agent.utils import get_date_range_for_period
        
        # 测试整年
        start, end = get_date_range_for_period(2026)
        self.assertEqual(start, '2026-01-01')
        self.assertEqual(end, '2026-12-31')
        
        # 测试整月
        start, end = get_date_range_for_period(2026, month=3)
        self.assertEqual(start, '2026-03-01')
        self.assertEqual(end, '2026-03-31')
        
        # 测试季度
        start, end = get_date_range_for_period(2026, quarter=2)
        self.assertEqual(start, '2026-04-01')
        self.assertEqual(end, '2026-06-30')
        
        # 测试闰年2月
        start, end = get_date_range_for_period(2024, month=2)
        self.assertEqual(start, '2024-02-01')
        self.assertEqual(end, '2024-02-29')
    
    def test_calculate_days_between(self):
        """测试计算天数差"""
        from erp_agent.utils import calculate_days_between
        
        days = calculate_days_between('2026-01-01', '2026-01-31')
        self.assertEqual(days, 30)
        
        days = calculate_days_between('2026-01-31', '2026-01-01')
        self.assertEqual(days, -30)
        
        days = calculate_days_between('2025-01-01', '2026-01-01')
        self.assertEqual(days, 365)
    
    def test_get_month_start_end(self):
        """测试获取月份起止"""
        from erp_agent.utils import get_month_start_end
        
        start, end = get_month_start_end('2026-01-15')
        self.assertEqual(start, '2026-01-01')
        self.assertEqual(end, '2026-01-31')
        
        # 测试闰年2月
        start, end = get_month_start_end('2024-02-15')
        self.assertEqual(start, '2024-02-01')
        self.assertEqual(end, '2024-02-29')
    
    def test_get_quarter_start_end(self):
        """测试获取季度起止"""
        from erp_agent.utils import get_quarter_start_end
        
        # Q1
        start, end = get_quarter_start_end('2026-01-15')
        self.assertEqual(start, '2026-01-01')
        self.assertEqual(end, '2026-03-31')
        
        # Q3
        start, end = get_quarter_start_end('2026-08-15')
        self.assertEqual(start, '2026-07-01')
        self.assertEqual(end, '2026-09-30')
    
    def test_format_date_for_sql(self):
        """测试格式化日期为SQL格式"""
        from erp_agent.utils import format_date_for_sql
        
        self.assertEqual(format_date_for_sql("2026/1/5"), "2026-01-05")
        self.assertEqual(format_date_for_sql("2026-1-5"), "2026-01-05")
        self.assertEqual(format_date_for_sql("2026.1.5"), "2026-01-05")


class TestDatabaseConfig(unittest.TestCase):
    """测试数据库配置"""
    
    def test_database_config_creation(self):
        """测试数据库配置创建"""
        from erp_agent.config import DatabaseConfig
        
        config = DatabaseConfig(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_pass'
        )
        
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.port, 5432)
        self.assertEqual(config.database, 'test_db')
        self.assertEqual(config.user, 'test_user')
        self.assertEqual(config.password, 'test_pass')
    
    def test_database_config_from_dict(self):
        """测试从字典创建配置"""
        from erp_agent.config import DatabaseConfig
        
        config_dict = {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_pass'
        }
        
        config = DatabaseConfig.from_dict(config_dict)
        self.assertEqual(config.host, 'localhost')
        self.assertEqual(config.database, 'test_db')
    
    def test_database_config_validation(self):
        """测试配置验证"""
        from erp_agent.config import DatabaseConfig
        
        # 有效配置
        config = DatabaseConfig(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_pass'
        )
        self.assertTrue(config.validate())
        
        # 无效端口
        config_invalid = DatabaseConfig(
            host='localhost',
            port=0,
            database='test_db',
            user='test_user',
            password='test_pass'
        )
        self.assertFalse(config_invalid.validate())
    
    def test_get_connection_string(self):
        """测试获取连接字符串"""
        from erp_agent.config import DatabaseConfig
        
        config = DatabaseConfig(
            host='localhost',
            port=5432,
            database='test_db',
            user='test_user',
            password='test_pass'
        )
        
        conn_str = config.get_connection_string()
        self.assertIn('postgresql://', conn_str)
        self.assertIn('localhost', conn_str)
        self.assertIn('test_db', conn_str)


class TestLLMConfig(unittest.TestCase):
    """测试LLM配置"""
    
    def test_llm_config_creation(self):
        """测试LLM配置创建"""
        from erp_agent.config import LLMConfig
        
        config = LLMConfig(
            api_key='test_key_12345',
            model='kimi-k2',
            temperature=0.3
        )
        
        self.assertEqual(config.api_key, 'test_key_12345')
        self.assertEqual(config.model, 'kimi-k2')
        self.assertEqual(config.temperature, 0.3)
    
    def test_llm_config_validation(self):
        """测试LLM配置验证"""
        from erp_agent.config import LLMConfig
        
        # 有效配置
        config = LLMConfig(api_key='test_key')
        self.assertTrue(config.validate())
        
        # 无效温度
        config_invalid = LLMConfig(api_key='test_key', temperature=1.5)
        self.assertFalse(config_invalid.validate())
    
    def test_get_api_headers(self):
        """测试获取API请求头"""
        from erp_agent.config import LLMConfig
        
        config = LLMConfig(api_key='test_key_12345')
        headers = config.get_api_headers()
        
        self.assertIn('Authorization', headers)
        self.assertIn('Bearer test_key_12345', headers['Authorization'])
        self.assertEqual(headers['Content-Type'], 'application/json')


class TestAgentConfig(unittest.TestCase):
    """测试Agent配置"""
    
    def test_agent_config_creation(self):
        """测试Agent配置创建"""
        from erp_agent.config import AgentConfig
        
        config = AgentConfig(
            max_iterations=5,
            log_level='INFO'
        )
        
        self.assertEqual(config.max_iterations, 5)
        self.assertEqual(config.log_level, 'INFO')
        self.assertTrue(config.enable_retry)
    
    def test_agent_config_to_dict(self):
        """测试配置转字典"""
        from erp_agent.config import AgentConfig
        
        config = AgentConfig(max_iterations=10)
        config_dict = config.to_dict()
        
        self.assertEqual(config_dict['max_iterations'], 10)
        self.assertIn('enable_retry', config_dict)


class TestSQLExecutor(unittest.TestCase):
    """测试SQL执行器"""
    
    def test_validate_sql_safe(self):
        """测试安全SQL验证"""
        from erp_agent.core import SQLExecutor
        from erp_agent.config import DatabaseConfig
        
        config = DatabaseConfig(
            host='localhost',
            port=5432,
            database='test',
            user='test',
            password='test'
        )
        executor = SQLExecutor(config)
        
        # 安全的SELECT
        is_valid, error = executor.validate_sql("SELECT * FROM employees;")
        self.assertTrue(is_valid)
        self.assertIsNone(error)
        
        # 带WHERE的SELECT
        is_valid, error = executor.validate_sql(
            "SELECT name FROM employees WHERE department = 'A';"
        )
        self.assertTrue(is_valid)
        
        # WITH子句(CTE)
        is_valid, error = executor.validate_sql(
            "WITH temp AS (SELECT * FROM employees) SELECT * FROM temp;"
        )
        self.assertTrue(is_valid)
    
    def test_validate_sql_dangerous(self):
        """测试危险SQL检测"""
        from erp_agent.core import SQLExecutor
        from erp_agent.config import DatabaseConfig
        
        config = DatabaseConfig(
            host='localhost',
            port=5432,
            database='test',
            user='test',
            password='test'
        )
        executor = SQLExecutor(config)
        
        # DROP语句
        is_valid, error = executor.validate_sql("DROP TABLE employees;")
        self.assertFalse(is_valid)
        self.assertIn('DROP', error)
        
        # DELETE语句
        is_valid, error = executor.validate_sql("DELETE FROM employees;")
        self.assertFalse(is_valid)
        self.assertIn('DELETE', error)
        
        # UPDATE语句
        is_valid, error = executor.validate_sql("UPDATE employees SET salary = 0;")
        self.assertFalse(is_valid)
        self.assertIn('UPDATE', error)
        
        # INSERT语句
        is_valid, error = executor.validate_sql("INSERT INTO employees VALUES (1, 'test');")
        self.assertFalse(is_valid)
        self.assertIn('INSERT', error)
    
    def test_validate_sql_multiple_statements(self):
        """测试多语句SQL"""
        from erp_agent.core import SQLExecutor
        from erp_agent.config import DatabaseConfig
        
        config = DatabaseConfig(
            host='localhost',
            port=5432,
            database='test',
            user='test',
            password='test'
        )
        executor = SQLExecutor(config)
        
        # 多条语句
        is_valid, error = executor.validate_sql(
            "SELECT * FROM employees; SELECT * FROM departments;"
        )
        self.assertFalse(is_valid)
        self.assertIn('多条', error)


class TestPromptBuilder(unittest.TestCase):
    """测试Prompt构建器"""
    
    def test_prompt_builder_initialization(self):
        """测试Prompt构建器初始化"""
        from erp_agent.utils import PromptBuilder
        
        builder = PromptBuilder()
        self.assertIsNotNone(builder)
        self.assertTrue(builder.prompts_dir.exists())
    
    def test_load_schema(self):
        """测试加载Schema"""
        from erp_agent.utils import PromptBuilder
        
        builder = PromptBuilder()
        schema = builder.load_schema()
        
        self.assertIsInstance(schema, str)
        self.assertTrue(len(schema) > 0)
        self.assertIn('employees', schema.lower())
    
    def test_load_examples(self):
        """测试加载示例"""
        from erp_agent.utils import PromptBuilder
        
        builder = PromptBuilder()
        examples = builder.load_examples()
        
        self.assertIsInstance(examples, str)
        self.assertTrue(len(examples) > 0)
    
    def test_load_system_prompt_template(self):
        """测试加载系统Prompt模板"""
        from erp_agent.utils import PromptBuilder
        
        builder = PromptBuilder()
        template = builder.load_system_prompt_template()
        
        self.assertIsInstance(template, str)
        self.assertTrue(len(template) > 0)
    
    def test_extract_placeholders(self):
        """测试提取占位符"""
        from erp_agent.utils import PromptBuilder
        
        builder = PromptBuilder()
        template = "今天是 {current_date}，今年是 {year} 年"
        placeholders = builder.extract_placeholders(template)
        
        self.assertIn('current_date', placeholders)
        self.assertIn('year', placeholders)
        self.assertEqual(len(placeholders), 2)
    
    def test_build_sql_generation_prompt(self):
        """测试构建SQL生成Prompt"""
        from erp_agent.utils import PromptBuilder, get_current_datetime
        
        builder = PromptBuilder()
        date_info = get_current_datetime()
        
        prompt = builder.build_sql_generation_prompt(
            user_question="有多少在职员工？",
            date_info=date_info
        )
        
        self.assertIsInstance(prompt, str)
        self.assertTrue(len(prompt) > 0)
        self.assertIn('有多少在职员工', prompt)
    
    def test_build_prompt_with_context(self):
        """测试带上下文构建Prompt"""
        from erp_agent.utils import PromptBuilder, get_current_datetime
        
        builder = PromptBuilder()
        date_info = get_current_datetime()
        
        context = [
            {
                'thought': '需要查询员工表',
                'sql': 'SELECT COUNT(*) FROM employees;',
                'result': {
                    'success': True,
                    'data': [{'count': 88}],
                    'row_count': 1
                }
            }
        ]
        
        prompt = builder.build_sql_generation_prompt(
            user_question="各部门分别有多少人？",
            date_info=date_info,
            context=context
        )
        
        self.assertIn('历史', prompt)
        self.assertIn('SELECT COUNT(*)', prompt)


class TestLogger(unittest.TestCase):
    """测试日志系统"""
    
    def test_setup_logger(self):
        """测试日志设置"""
        from erp_agent.utils import setup_logger
        
        # 设置日志（使用测试日志文件）
        setup_logger(log_level='DEBUG', log_file='logs/test_agent.log')
    
    def test_get_logger(self):
        """测试获取日志记录器"""
        from erp_agent.utils import get_logger
        
        logger = get_logger(__name__)
        self.assertIsNotNone(logger)
        
        # 测试记录日志
        logger.info("测试信息日志")
        logger.debug("测试调试日志")


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    @classmethod
    def setUpClass(cls):
        """设置测试环境"""
        from dotenv import load_dotenv
        load_dotenv()
        
        # 检查环境变量
        required_vars = ['MOONSHOT_API_KEY', 'DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        
        if missing_vars:
            raise unittest.SkipTest(
                f"缺少必需的环境变量: {', '.join(missing_vars)}"
            )
    
    def test_database_connection(self):
        """测试数据库连接"""
        from erp_agent.config import get_database_config, test_connection
        
        try:
            db_config = get_database_config()
            connected = test_connection(db_config)
            self.assertTrue(connected, "数据库连接失败")
        except Exception as e:
            self.fail(f"数据库连接测试失败: {e}")
    
    def test_sql_executor_real_query(self):
        """测试SQL执行器（真实查询）"""
        from erp_agent.core import SQLExecutor
        from erp_agent.config import get_database_config
        
        try:
            db_config = get_database_config()
            executor = SQLExecutor(db_config)
            
            # 执行简单查询
            result = executor.execute("SELECT 1 as test_value;")
            
            self.assertTrue(result['success'])
            self.assertEqual(result['row_count'], 1)
            self.assertEqual(result['data'][0]['test_value'], 1)
        except Exception as e:
            self.fail(f"SQL执行测试失败: {e}")
    
    def test_agent_simple_query(self):
        """测试Agent简单查询"""
        from erp_agent.core import ERPAgent
        from erp_agent.config import get_llm_config, get_database_config, get_agent_config
        
        try:
            llm_config = get_llm_config()
            db_config = get_database_config()
            agent_config = get_agent_config()
            
            agent = ERPAgent(llm_config, db_config, agent_config)
            
            # 执行简单查询
            result = agent.query("公司有多少在职员工？")
            
            self.assertIsInstance(result, dict)
            self.assertIn('success', result)
            self.assertIn('answer', result)
            self.assertIn('iterations', result)
            
        except Exception as e:
            self.fail(f"Agent查询测试失败: {e}")


class TestQuestions(unittest.TestCase):
    """测试问题集"""
    
    def test_all_questions_exist(self):
        """测试所有10个问题都存在"""
        from erp_agent.tests.test_questions import TEST_QUESTIONS, get_question_by_id
        
        self.assertEqual(len(TEST_QUESTIONS), 10)
        
        for i in range(1, 11):
            question = get_question_by_id(i)
            self.assertIsNotNone(question)
    
    def test_question_structure(self):
        """测试问题结构完整性"""
        from erp_agent.tests.test_questions import TEST_QUESTIONS
        
        required_fields = ['id', 'question']
        
        for q in TEST_QUESTIONS:
            for field in required_fields:
                self.assertIn(field, q, f"问题{q.get('id')}缺少字段: {field}")
            
            # 验证问题内容不为空
            self.assertTrue(len(q['question']) > 0)


def run_unit_tests():
    """运行所有单元测试"""
    print("=" * 70)
    print("运行单元测试套件")
    print("=" * 70)
    
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestDateUtils,
        TestDatabaseConfig,
        TestLLMConfig,
        TestAgentConfig,
        TestSQLExecutor,
        TestPromptBuilder,
        TestLogger,
        TestQuestions,
        TestIntegration,
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印统计信息
    print("\n" + "=" * 70)
    print("测试统计:")
    print(f"  总测试数: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print(f"  跳过: {len(result.skipped)}")
    print("=" * 70)
    
    return result


def run_question_tests():
    """运行10个测试问题"""
    print("\n" + "=" * 70)
    print("运行10个测试问题")
    print("=" * 70)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    try:
        from erp_agent.core import ERPAgent
        from erp_agent.config import get_llm_config, get_database_config, get_agent_config
        from erp_agent.tests.test_questions import TEST_QUESTIONS
        
        # 初始化Agent
        print("\n初始化 ERP Agent...")
        llm_config = get_llm_config()
        db_config = get_database_config()
        agent_config = get_agent_config()
        
        agent = ERPAgent(llm_config, db_config, agent_config)
        print("✓ Agent 初始化成功\n")
        
        # 测试结果统计
        results = {
            'total': len(TEST_QUESTIONS),
            'success': 0,
            'failed': 0,
            'details': []
        }
        
        # 逐个测试问题
        for i, test in enumerate(TEST_QUESTIONS, 1):
            question = test['question']
            print(f"\n{'=' * 70}")
            print(f"问题 {i}/{len(TEST_QUESTIONS)}: {question}")
            print("=" * 70)
            
            try:
                result = agent.query(question)
                
                detail = {
                    'id': i,
                    'question': question,
                    'success': result['success'],
                    'answer': result.get('answer', ''),
                    'iterations': result.get('iterations', 0),
                    'time': result.get('total_time', 0),
                    'error': result.get('error')
                }
                
                if result['success']:
                    print(f"\n✓ 成功")
                    print(f"答案: {result['answer']}")
                    print(f"迭代次数: {result['iterations']}")
                    print(f"耗时: {result['total_time']:.2f}秒")
                    results['success'] += 1
                else:
                    print(f"\n✗ 失败")
                    print(f"错误: {result.get('error', '未知错误')}")
                    results['failed'] += 1
                
                results['details'].append(detail)
                
            except Exception as e:
                print(f"\n✗ 执行异常: {e}")
                import traceback
                traceback.print_exc()
                
                results['failed'] += 1
                results['details'].append({
                    'id': i,
                    'question': question,
                    'success': False,
                    'error': str(e)
                })
        
        # 打印总结
        print("\n" + "=" * 70)
        print("测试问题总结")
        print("=" * 70)
        print(f"总问题数: {results['total']}")
        print(f"成功: {results['success']}")
        print(f"失败: {results['failed']}")
        print(f"成功率: {results['success']/results['total']*100:.1f}%")
        
        # 详细结果
        print("\n详细结果:")
        for detail in results['details']:
            status = "✓" if detail['success'] else "✗"
            print(f"{status} 问题{detail['id']}: {detail['question']}")
            if detail['success']:
                print(f"   迭代: {detail.get('iterations', 0)}次, 耗时: {detail.get('time', 0):.2f}秒")
            else:
                print(f"   错误: {detail.get('error', '未知错误')}")
        
        print("\n" + "=" * 70)
        
        return results
        
    except Exception as e:
        print(f"\n❌ 测试问题执行失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print("\n")
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║            ERP Agent 完整测试套件                            ║")
    print("╚══════════════════════════════════════════════════════════════╝")
    print("\n")
    
    # 选择测试模式
    print("请选择测试模式:")
    print("  1. 运行单元测试（快速，不需要API）")
    print("  2. 运行10个测试问题（需要API和数据库）")
    print("  3. 运行所有测试")
    print("  0. 退出")
    
    choice = input("\n请输入选项 (0-3): ").strip()
    
    if choice == '1':
        # 运行单元测试
        run_unit_tests()
    
    elif choice == '2':
        # 运行测试问题
        run_question_tests()
    
    elif choice == '3':
        # 运行所有测试
        print("\n第一部分: 单元测试")
        unit_result = run_unit_tests()
        
        if unit_result.wasSuccessful():
            print("\n✓ 单元测试全部通过，继续运行问题测试...\n")
            run_question_tests()
        else:
            print("\n⚠️  单元测试未全部通过，但仍将继续运行问题测试...\n")
            input("按 Enter 继续...")
            run_question_tests()
    
    elif choice == '0':
        print("\n退出测试")
    
    else:
        print("\n无效的选项")


if __name__ == '__main__':
    # 如果直接运行，提供交互式选择
    if len(sys.argv) > 1:
        # 支持命令行参数
        if sys.argv[1] == 'unit':
            run_unit_tests()
        elif sys.argv[1] == 'questions':
            run_question_tests()
        elif sys.argv[1] == 'all':
            run_unit_tests()
            run_question_tests()
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("用法: python test_agent.py [unit|questions|all]")
    else:
        # 交互式模式
        main()
