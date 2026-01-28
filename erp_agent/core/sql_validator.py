#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 验证器模块

在SQL执行前进行语法检查和常见错误检测，提供智能的错误诊断和修复建议。
这是一个架构层面的优化，而不是依赖提示词注入。
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """SQL验证结果"""
    is_valid: bool
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    suggestion: Optional[str] = None
    fixed_sql: Optional[str] = None


class SQLValidator:
    """
    SQL 验证器
    
    功能：
    1. 检测常见的SQL语法错误
    2. 分析错误类型并提供修复建议
    3. 针对PostgreSQL特定限制进行检查
    4. 提供智能的SQL修复建议
    
    设计理念：
    - 不依赖提示词注入，而是在执行前主动检测
    - 提供结构化的错误分析，而不是简单传递错误信息
    - 基于规则和模式匹配，可扩展
    """
    
    def __init__(self):
        """初始化验证器"""
        # 定义需要检测的错误模式
        self.error_patterns = [
            {
                'name': 'generate_series_in_where',
                'pattern': r'WHERE\s+.*?generate_series\s*\(',
                'error_type': 'syntax_error',
                'message': 'generate_series不能直接在WHERE子句中使用',
                'suggestion': '将generate_series移到CTE（WITH子句）或FROM子句中，然后在WHERE中引用结果'
            },
            {
                'name': 'generate_series_in_having',
                'pattern': r'HAVING\s+.*?generate_series\s*\(',
                'error_type': 'syntax_error',
                'message': 'generate_series不能在HAVING子句中使用',
                'suggestion': '将generate_series移到CTE或FROM子句中'
            },
            # 注意：移除了过于简单的引号检查，因为它会误报
            # 更复杂的引号检查需要完整的SQL解析器
        ]
    
    def validate(self, sql: str) -> ValidationResult:
        """
        验证SQL语句
        
        参数:
            sql: 要验证的SQL语句
            
        返回:
            ValidationResult: 验证结果
        """
        # 预处理：移除注释和多余空白
        sql_clean = self._clean_sql(sql)
        
        # 检查各种错误模式
        for pattern_def in self.error_patterns:
            if self._check_pattern(sql_clean, pattern_def):
                # 尝试自动修复
                fixed_sql = self._try_fix_sql(sql_clean, pattern_def)
                
                return ValidationResult(
                    is_valid=False,
                    error_type=pattern_def['error_type'],
                    error_message=pattern_def['message'],
                    suggestion=pattern_def['suggestion'],
                    fixed_sql=fixed_sql
                )
        
        # 检查基本的SQL结构
        structure_check = self._check_sql_structure(sql_clean)
        if not structure_check[0]:
            return ValidationResult(
                is_valid=False,
                error_type='structure_error',
                error_message=structure_check[1],
                suggestion=structure_check[2]
            )
        
        # 所有检查通过
        return ValidationResult(is_valid=True)
    
    def analyze_execution_error(
        self, 
        sql: str, 
        error_message: str
    ) -> Dict[str, str]:
        """
        分析SQL执行错误，提供智能的错误诊断和修复建议
        
        参数:
            sql: 执行失败的SQL
            error_message: 数据库返回的错误信息
            
        返回:
            Dict: 包含错误分析和修复建议
        """
        error_lower = error_message.lower()
        
        # 分析常见错误类型
        if 'set-returning functions are not allowed in where' in error_lower:
            return {
                'error_type': 'generate_series_misuse',
                'diagnosis': 'generate_series等集合返回函数不能直接在WHERE子句中使用',
                'root_cause': 'PostgreSQL不允许在WHERE、HAVING等子句中直接调用返回集合的函数',
                'fix_strategy': '使用CTE（WITH子句）重构查询',
                'example': '''
正确的写法：
WITH expected AS (
    SELECT entity_id, 
           generate_series(start_date, end_date, '1 month'::interval) AS month
    FROM base_table
)
SELECT * FROM expected WHERE condition;

错误的写法：
SELECT * FROM base_table 
WHERE generate_series(...);  -- 这是错误的！
''',
                'next_step': '重新生成SQL，将generate_series移到CTE中'
            }
        
        elif 'relation' in error_lower and 'does not exist' in error_lower:
            # 提取表名
            match = re.search(r'relation "(\w+)" does not exist', error_message)
            table_name = match.group(1) if match else 'unknown'
            
            return {
                'error_type': 'table_not_found',
                'diagnosis': f'表 "{table_name}" 不存在',
                'root_cause': '可能使用了错误的表名或未正确引用Schema中的表',
                'fix_strategy': '检查Schema文档，使用正确的表名',
                'next_step': f'重新生成SQL，确认表名是否正确（当前使用: {table_name}）'
            }
        
        elif 'column' in error_lower and 'does not exist' in error_lower:
            # 提取列名
            match = re.search(r'column "(\w+)" does not exist', error_message)
            column_name = match.group(1) if match else 'unknown'
            
            return {
                'error_type': 'column_not_found',
                'diagnosis': f'列 "{column_name}" 不存在',
                'root_cause': '可能使用了错误的列名或该列不在当前表中',
                'fix_strategy': '检查Schema文档中的表结构，使用正确的列名',
                'next_step': f'重新生成SQL，确认列名是否正确（当前使用: {column_name}）'
            }
        
        elif 'syntax error' in error_lower:
            return {
                'error_type': 'syntax_error',
                'diagnosis': 'SQL语法错误',
                'root_cause': 'SQL语句不符合PostgreSQL语法规范',
                'fix_strategy': '检查SQL语法，特别注意关键字拼写、括号匹配、逗号位置',
                'next_step': '仔细检查SQL语法，重新生成正确的SQL'
            }
        
        elif 'must appear in the group by' in error_lower:
            return {
                'error_type': 'groupby_error',
                'diagnosis': 'GROUP BY子句缺少必要的列',
                'root_cause': 'SELECT中的非聚合列必须出现在GROUP BY子句中',
                'fix_strategy': '将所有非聚合列添加到GROUP BY，或对这些列使用聚合函数',
                'next_step': '修改SQL，确保所有非聚合列都在GROUP BY中'
            }
        
        else:
            # 通用错误处理
            return {
                'error_type': 'unknown_error',
                'diagnosis': '数据库执行错误',
                'root_cause': error_message,
                'fix_strategy': '根据错误信息分析并修正SQL',
                'next_step': '重新分析问题需求，生成新的SQL'
            }
    
    def _clean_sql(self, sql: str) -> str:
        """清理SQL：移除注释和规范化空白"""
        # 移除单行注释
        sql = re.sub(r'--[^\n]*', '', sql)
        # 移除多行注释
        sql = re.sub(r'/\*.*?\*/', '', sql, flags=re.DOTALL)
        # 规范化空白
        sql = re.sub(r'\s+', ' ', sql)
        return sql.strip()
    
    def _check_pattern(self, sql: str, pattern_def: Dict) -> bool:
        """检查SQL是否匹配错误模式"""
        pattern = pattern_def['pattern']
        return bool(re.search(pattern, sql, re.IGNORECASE | re.DOTALL))
    
    def _check_sql_structure(self, sql: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """检查SQL基本结构（改进版：减少误报）"""
        sql_upper = sql.upper()
        
        # 检查是否有SELECT关键字
        if 'SELECT' not in sql_upper:
            return False, 'SQL必须包含SELECT关键字', '确保SQL是有效的查询语句'
        
        # 检查括号匹配
        if sql.count('(') != sql.count(')'):
            return False, '括号不匹配', '检查SQL中的括号是否正确闭合'
        
        # 【重要修复】放宽FROM子句检查，避免误报
        # 对于复杂SQL（包含CTE、子查询等），简单的位置检查会导致误报
        # 只进行最基本的检查：如果有WHERE但整个SQL中没有FROM，才报错
        if 'WHERE' in sql_upper and 'FROM' not in sql_upper:
            return False, '缺少FROM子句', '添加FROM子句'
        
        # 检查是否以分号结尾（可选，不强制）
        # if not sql.strip().endswith(';'):
        #     pass  # 这不是错误
        
        return True, None, None
    
    def _try_fix_sql(self, sql: str, pattern_def: Dict) -> Optional[str]:
        """
        尝试自动修复SQL（针对某些简单的错误）
        
        注意：这是一个实验性功能，只处理最简单的情况
        """
        if pattern_def['name'] == 'generate_series_in_where':
            # 这个修复比较复杂，不在这里自动修复，留给LLM重新生成
            return None
        
        return None


# 导出
__all__ = ['SQLValidator', 'ValidationResult']


if __name__ == '__main__':
    # 测试代码
    print("=== 测试 SQLValidator ===\n")
    
    validator = SQLValidator()
    
    # 测试1: generate_series在WHERE中
    print("测试1: generate_series在WHERE子句中")
    sql1 = """
    SELECT * FROM employees 
    WHERE generate_series(hire_date, CURRENT_DATE, '1 month') < CURRENT_DATE;
    """
    result1 = validator.validate(sql1)
    print(f"验证结果: {result1.is_valid}")
    if not result1.is_valid:
        print(f"错误类型: {result1.error_type}")
        print(f"错误信息: {result1.error_message}")
        print(f"修复建议: {result1.suggestion}")
    print()
    
    # 测试2: 正确的SQL
    print("测试2: 正确的SQL")
    sql2 = """
    WITH expected AS (
        SELECT employee_id, 
               generate_series(hire_date, CURRENT_DATE, '1 month'::interval) AS month
        FROM employees
    )
    SELECT * FROM expected;
    """
    result2 = validator.validate(sql2)
    print(f"验证结果: {result2.is_valid}")
    print()
    
    # 测试3: 分析执行错误
    print("测试3: 分析执行错误")
    error_msg = "set-returning functions are not allowed in WHERE\nLINE 3: WHERE generate_series(...)"
    analysis = validator.analyze_execution_error(sql1, error_msg)
    print(f"错误类型: {analysis['error_type']}")
    print(f"诊断: {analysis['diagnosis']}")
    print(f"根本原因: {analysis['root_cause']}")
    print(f"修复策略: {analysis['fix_strategy']}")
    print(f"下一步: {analysis['next_step']}")
    
    print("\n=== 测试完成 ===")
