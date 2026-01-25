#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent 单元测试
测试各个模块的功能
"""

import unittest
from datetime import date, datetime
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class TestDateUtils(unittest.TestCase):
    """测试时间处理工具"""
    
    def test_get_current_date_info(self):
        """测试获取当前日期信息"""
        # TODO: 实现 date_utils 后取消注释
        # from utils.date_utils import get_current_date_info
        # info = get_current_date_info()
        # self.assertIn('current_date', info)
        # self.assertIn('current_year', info)
        # self.assertIn('last_year', info)
        pass
    
    def test_calculate_date_range(self):
        """测试计算日期范围"""
        # TODO: 实现 date_utils 后取消注释
        # from utils.date_utils import calculate_date_range
        # start, end = calculate_date_range("去年3月到今年5月")
        # self.assertIsInstance(start, str)
        # self.assertIsInstance(end, str)
        pass


class TestSQLExecutor(unittest.TestCase):
    """测试SQL执行器"""
    
    def test_validate_sql_safe(self):
        """测试安全SQL验证"""
        # TODO: 实现 sql_executor 后取消注释
        # from core.sql_executor import SQLExecutor
        # executor = SQLExecutor({})
        # is_valid, error = executor.validate_sql("SELECT * FROM employees")
        # self.assertTrue(is_valid)
        pass
    
    def test_validate_sql_dangerous(self):
        """测试危险SQL检测"""
        # TODO: 实现 sql_executor 后取消注释
        # from core.sql_executor import SQLExecutor
        # executor = SQLExecutor({})
        # is_valid, error = executor.validate_sql("DROP TABLE employees")
        # self.assertFalse(is_valid)
        pass


class TestSQLGenerator(unittest.TestCase):
    """测试SQL生成器"""
    
    def test_generate_simple_query(self):
        """测试生成简单查询"""
        # TODO: 实现 sql_generator 后取消注释
        # from core.sql_generator import SQLGenerator
        # generator = SQLGenerator(api_key="test_key")
        # result = generator.generate_sql(
        #     user_question="有多少在职员工？",
        #     date_info={'current_year': 2026}
        # )
        # self.assertIn('sql', result)
        pass


class TestResultAnalyzer(unittest.TestCase):
    """测试结果分析器"""
    
    def test_analyze_successful_result(self):
        """测试分析成功的查询结果"""
        # TODO: 实现 result_analyzer 后取消注释
        # from core.result_analyzer import ResultAnalyzer
        # analyzer = ResultAnalyzer()
        # result = {
        #     'success': True,
        #     'data': [{'count': 88}],
        #     'row_count': 1
        # }
        # analysis = analyzer.analyze(
        #     user_question="有多少在职员工？",
        #     sql="SELECT COUNT(*) FROM employees WHERE leave_date IS NULL",
        #     result=result,
        #     iteration=1
        # )
        # self.assertTrue(analysis['is_complete'])
        pass
    
    def test_analyze_error_result(self):
        """测试分析错误的查询结果"""
        # TODO: 实现 result_analyzer 后取消注释
        # from core.result_analyzer import ResultAnalyzer
        # analyzer = ResultAnalyzer()
        # result = {
        #     'success': False,
        #     'error': 'syntax error'
        # }
        # analysis = analyzer.analyze(
        #     user_question="有多少在职员工？",
        #     sql="SELECT COUNT(*) FRM employees",
        #     result=result,
        #     iteration=1
        # )
        # self.assertTrue(analysis['needs_retry'])
        pass


class TestERPAgent(unittest.TestCase):
    """测试Agent主控制器"""
    
    def test_query_simple_question(self):
        """测试简单问题查询"""
        # TODO: 实现 agent 后取消注释
        # from core.agent import ERPAgent
        # agent = ERPAgent(config={})
        # result = agent.query("有多少在职员工？")
        # self.assertIn('answer', result)
        # self.assertTrue(result['success'])
        pass


class TestTestQuestions(unittest.TestCase):
    """测试问题集"""
    
    def test_all_questions_exist(self):
        """测试所有10个问题都存在"""
        from test_questions import TEST_QUESTIONS, get_question_by_id
        
        self.assertEqual(len(TEST_QUESTIONS), 10)
        
        for i in range(1, 11):
            question = get_question_by_id(i)
            self.assertIsNotNone(question)
            self.assertEqual(question['id'], i)
    
    def test_question_structure(self):
        """测试问题结构完整性"""
        from test_questions import TEST_QUESTIONS
        
        required_fields = ['id', 'question', 'category', 'description', 
                          'expected_type', 'validation', 'complexity', 'keywords']
        
        for q in TEST_QUESTIONS:
            for field in required_fields:
                self.assertIn(field, q, f"问题{q.get('id')}缺少字段: {field}")
    
    def test_validation_numeric(self):
        """测试数值类型验证"""
        from test_questions import validate_result
        
        # 测试问题2: 在职员工数量（期望80-95）
        result_valid = validate_result(2, 88)
        self.assertTrue(result_valid['valid'])
        
        result_invalid = validate_result(2, 100)
        self.assertFalse(result_invalid['valid'])
    
    def test_validation_table(self):
        """测试表格类型验证"""
        from test_questions import validate_result
        
        # 测试问题3: 各部门在职员工（期望5行）
        result_valid = validate_result(3, [
            {'department_name': 'A部门', 'count': 22},
            {'department_name': 'B部门', 'count': 20},
            {'department_name': 'C部门', 'count': 18},
            {'department_name': 'D部门', 'count': 16},
            {'department_name': 'E部门', 'count': 12},
        ])
        self.assertTrue(result_valid['valid'])
        
        result_invalid = validate_result(3, [
            {'department_name': 'A部门', 'count': 22},
        ])
        self.assertFalse(result_invalid['valid'])


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDateUtils))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSQLExecutor))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSQLGenerator))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestResultAnalyzer))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestERPAgent))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestTestQuestions))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 打印统计信息
    print("\n" + "="*70)
    print("测试统计:")
    print(f"  总测试数: {result.testsRun}")
    print(f"  成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"  失败: {len(result.failures)}")
    print(f"  错误: {len(result.errors)}")
    print("="*70)
    
    return result


if __name__ == '__main__':
    run_tests()
