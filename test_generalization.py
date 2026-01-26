#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
泛化能力测试脚本

测试模型是否能够：
1. 正确理解相对时间（而非复制示例中的具体年份）
2. 使用实际Schema（而非示例中的虚构表名）
3. 在新场景中应用学到的技术
"""

import re
from datetime import datetime
from erp_agent.main import get_agent
from erp_agent.utils.date_utils import get_current_datetime


class GeneralizationTester:
    """泛化能力测试器"""
    
    def __init__(self):
        self.agent = get_agent()
        self.date_info = get_current_datetime()
        self.current_year = self.date_info['year']
        self.results = []
        
    def test_time_reasoning(self):
        """测试时间推理能力"""
        print("\n" + "=" * 80)
        print("测试1: 时间推理能力")
        print("=" * 80)
        
        test_cases = [
            {
                "name": "相对年份 - 去年到今年",
                "question": "从去年到今年涨薪幅度最大的10位员工是谁？",
                "expected_years": [self.current_year - 1, self.current_year],
                "forbidden_years": [2024] if self.current_year > 2025 else [],
                "description": "应该使用{year-1}和{year}，而不是示例中的固定年份"
            },
            {
                "name": "相对年份 - 前年",
                "question": "前年的平均工资是多少？",
                "expected_years": [self.current_year - 2],
                "forbidden_years": [],
                "description": "应该使用{year-2}"
            }
        ]
        
        for case in test_cases:
            print(f"\n测试用例: {case['name']}")
            print(f"问题: {case['question']}")
            print(f"预期使用年份: {case['expected_years']}")
            
            # 执行查询
            result = self.agent.query(case['question'])
            
            # 提取SQL中的年份
            sql_years = self._extract_years_from_context(result['context'])
            
            # 验证
            passed = self._validate_years(
                sql_years, 
                case['expected_years'], 
                case['forbidden_years']
            )
            
            self._record_result(case['name'], passed, {
                'expected': case['expected_years'],
                'actual': sql_years,
                'description': case['description']
            })
            
    def test_schema_usage(self):
        """测试是否正确使用实际Schema"""
        print("\n" + "=" * 80)
        print("测试2: Schema使用准确性")
        print("=" * 80)
        
        # 实际Schema中的表名
        real_tables = ['employees', 'departments', 'salaries']
        # 示例中使用的虚构表名
        fake_tables = ['orders', 'customers', 'readers', 'loans', 'books']
        
        test_cases = [
            {
                "name": "部门统计查询",
                "question": "每个部门的平均工资是多少？",
                "should_use": ['employees', 'departments', 'salaries'],
                "should_not_use": fake_tables
            }
        ]
        
        for case in test_cases:
            print(f"\n测试用例: {case['name']}")
            print(f"问题: {case['question']}")
            
            result = self.agent.query(case['question'])
            
            # 提取使用的表名
            tables_used = self._extract_tables_from_context(result['context'])
            
            # 验证
            passed = self._validate_tables(
                tables_used,
                case['should_use'],
                case['should_not_use']
            )
            
            self._record_result(case['name'], passed, {
                'tables_used': tables_used,
                'should_use': case['should_use'],
                'forbidden': case['should_not_use']
            })
    
    def test_technique_transfer(self):
        """测试技术迁移能力（在新场景中应用学到的技术）"""
        print("\n" + "=" * 80)
        print("测试3: 技术迁移能力")
        print("=" * 80)
        
        test_cases = [
            {
                "name": "跨期对比新场景",
                "question": "比较去年和今年各部门的平均在职时长",
                "required_techniques": ["CTE", "JOIN", "AVG"],
                "description": "应该能将示例8教的CTE跨期对比技术应用到新场景"
            },
            {
                "name": "数据完整性检测新场景",
                "question": "检查是否有部门从未发放过奖金",
                "required_techniques": ["LEFT JOIN", "IS NULL"],
                "description": "应该能应用示例9教的完整性检测方法"
            }
        ]
        
        for case in test_cases:
            print(f"\n测试用例: {case['name']}")
            print(f"问题: {case['question']}")
            print(f"需要的技术: {case['required_techniques']}")
            
            result = self.agent.query(case['question'])
            
            # 检查SQL中是否使用了预期技术
            techniques_used = self._extract_techniques_from_context(result['context'])
            
            # 验证
            passed = all(
                tech.lower() in ' '.join(techniques_used).lower() 
                for tech in case['required_techniques']
            )
            
            self._record_result(case['name'], passed, {
                'required': case['required_techniques'],
                'found': techniques_used,
                'description': case['description']
            })
    
    def test_thought_quality(self):
        """测试思维链质量"""
        print("\n" + "=" * 80)
        print("测试4: 思维链完整性")
        print("=" * 80)
        
        question = "从去年到今年涨薪幅度最大的10位员工是谁？"
        print(f"\n问题: {question}")
        
        result = self.agent.query(question)
        
        # 检查第一轮的thought
        if result['context']:
            first_thought = result['context'][0].get('thought', '')
            
            print(f"\n第一轮Thought:\n{first_thought}\n")
            
            # 验证thought是否包含关键推理步骤
            checks = {
                "时间明确性": self._check_time_explicit(first_thought),
                "Schema引用": self._check_schema_reference(first_thought),
                "技术说明": self._check_technique_explanation(first_thought)
            }
            
            print("思维链质量评估:")
            for check_name, passed in checks.items():
                status = "✅ PASS" if passed else "❌ FAIL"
                print(f"  {check_name}: {status}")
            
            overall_passed = sum(checks.values()) >= 2  # 至少通过2/3
            
            self._record_result("思维链质量", overall_passed, checks)
    
    def _extract_years_from_context(self, context):
        """从SQL上下文中提取年份"""
        years = set()
        for item in context:
            if 'sql' in item:
                # 查找形如 2024, 2025 的年份
                found_years = re.findall(r'\b(20\d{2})\b', item['sql'])
                years.update(int(y) for y in found_years)
        return sorted(years)
    
    def _extract_tables_from_context(self, context):
        """从SQL上下文中提取表名"""
        tables = set()
        for item in context:
            if 'sql' in item:
                sql = item['sql'].lower()
                # 简单的表名提取（FROM 和 JOIN 后面的词）
                patterns = [
                    r'from\s+(\w+)',
                    r'join\s+(\w+)'
                ]
                for pattern in patterns:
                    found = re.findall(pattern, sql)
                    tables.update(found)
        return sorted(tables)
    
    def _extract_techniques_from_context(self, context):
        """从SQL上下文中提取使用的技术"""
        techniques = []
        for item in context:
            if 'sql' in item:
                sql = item['sql'].upper()
                # 检测各种SQL技术
                if 'WITH' in sql:
                    techniques.append('CTE')
                if 'JOIN' in sql:
                    techniques.append('JOIN')
                if 'LEFT JOIN' in sql:
                    techniques.append('LEFT JOIN')
                if 'AVG(' in sql:
                    techniques.append('AVG')
                if 'GROUP BY' in sql:
                    techniques.append('GROUP BY')
                if 'IS NULL' in sql:
                    techniques.append('IS NULL')
        return techniques
    
    def _validate_years(self, actual_years, expected_years, forbidden_years):
        """验证年份是否正确"""
        # 检查是否使用了预期年份
        has_expected = all(year in actual_years for year in expected_years)
        # 检查是否避免了禁用年份
        no_forbidden = not any(year in actual_years for year in forbidden_years)
        return has_expected and no_forbidden
    
    def _validate_tables(self, tables_used, should_use, should_not_use):
        """验证表名使用是否正确"""
        # 至少使用了一个正确的表
        has_correct = any(table in tables_used for table in should_use)
        # 没有使用虚构表
        no_fake = not any(table in tables_used for table in should_not_use)
        return has_correct and no_fake
    
    def _check_time_explicit(self, thought):
        """检查thought是否明确说明了时间计算"""
        keywords = [
            str(self.current_year),
            str(self.current_year - 1),
            "当前年份",
            "去年",
            "今年"
        ]
        return any(kw in thought for kw in keywords)
    
    def _check_schema_reference(self, thought):
        """检查thought是否引用了Schema"""
        keywords = ["表", "字段", "employees", "salaries", "departments"]
        return any(kw in thought.lower() for kw in keywords)
    
    def _check_technique_explanation(self, thought):
        """检查thought是否解释了技术选择"""
        keywords = ["CTE", "JOIN", "GROUP BY", "使用", "计算", "统计"]
        return any(kw in thought for kw in keywords)
    
    def _record_result(self, test_name, passed, details):
        """记录测试结果"""
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"\n{status} - {test_name}")
        print(f"详情: {details}")
        
        self.results.append({
            'test': test_name,
            'passed': passed,
            'details': details
        })
    
    def run_all_tests(self):
        """运行所有测试"""
        print("\n" + "=" * 80)
        print("ERP Agent 泛化能力测试套件")
        print(f"当前时间: {self.date_info['current_date']}")
        print(f"当前年份: {self.current_year}")
        print("=" * 80)
        
        try:
            self.test_time_reasoning()
            self.test_schema_usage()
            # self.test_technique_transfer()  # 可选：更高级的测试
            self.test_thought_quality()
            
            self.print_summary()
            
        except Exception as e:
            print(f"\n❌ 测试过程中出错: {e}")
            import traceback
            traceback.print_exc()
    
    def print_summary(self):
        """打印测试摘要"""
        print("\n" + "=" * 80)
        print("测试摘要")
        print("=" * 80)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r['passed'])
        
        print(f"\n总计: {total} 个测试")
        print(f"通过: {passed} 个")
        print(f"失败: {total - passed} 个")
        print(f"通过率: {passed/total*100:.1f}%")
        
        if passed == total:
            print("\n🎉 所有测试通过！泛化能力良好。")
        elif passed >= total * 0.7:
            print("\n⚠️ 大部分测试通过，但仍有改进空间。")
        else:
            print("\n❌ 泛化能力不足，需要进一步改进prompt设计。")
        
        print("\n失败的测试:")
        for r in self.results:
            if not r['passed']:
                print(f"  - {r['test']}")
                print(f"    {r['details']}")


def main():
    """主函数"""
    tester = GeneralizationTester()
    tester.run_all_tests()


if __name__ == '__main__':
    main()
