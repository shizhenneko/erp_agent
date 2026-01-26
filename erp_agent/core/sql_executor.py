#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 执行模块

负责安全地执行 SQL 查询并返回结果。
包含 SQL 安全验证、执行超时控制、结果格式化等功能。
"""

import time
import psycopg2
import psycopg2.extras
from typing import Dict, List, Any, Optional, Tuple
from contextlib import contextmanager

from erp_agent.config.database import DatabaseConfig
from erp_agent.utils.logger import get_logger, log_sql_execution


class SQLExecutor:
    """
    SQL 执行器
    
    功能:
        1. 安全验证 SQL 语句（仅允许 SELECT）
        2. 执行 SQL 查询
        3. 格式化查询结果
        4. 处理执行错误
        5. 记录执行日志
    
    属性:
        db_config (DatabaseConfig): 数据库配置
        max_rows (int): 最大返回行数
        timeout (int): 查询超时时间（秒）
        
    使用示例:
        >>> executor = SQLExecutor(db_config)
        >>> result = executor.execute("SELECT COUNT(*) FROM employees;")
        >>> print(result['success'])
        True
        >>> print(result['data'])
        [{'count': 100}]
    """
    
    def __init__(self, db_config: DatabaseConfig):
        """
        初始化 SQL 执行器
        
        参数:
            db_config: 数据库配置对象
        """
        self.db_config = db_config
        self.max_rows = db_config.max_rows
        self.timeout = db_config.timeout
        self.logger = get_logger(__name__)
        
        # SQL 安全黑名单（禁止的关键字）
        self.forbidden_keywords = [
            'DROP', 'DELETE', 'UPDATE', 'INSERT', 'TRUNCATE',
            'ALTER', 'CREATE', 'REPLACE', 'GRANT', 'REVOKE'
        ]
    
    def execute(self, sql: str) -> Dict[str, Any]:
        """
        执行 SQL 查询
        
        参数:
            sql: SQL 查询语句
            
        返回:
            Dict: 包含执行结果的字典
                {
                    'success': bool,          # 是否成功
                    'data': List[Dict],       # 查询结果（字典列表）
                    'columns': List[str],     # 列名列表
                    'row_count': int,         # 返回行数
                    'execution_time': float,  # 执行时间（秒）
                    'error': Optional[str],   # 错误信息
                    'sql': str                # 执行的SQL
                }
        """
        start_time = time.time()
        
        result = {
            'success': False,
            'data': [],
            'columns': [],
            'row_count': 0,
            'execution_time': 0.0,
            'error': None,
            'sql': sql.strip()
        }
        
        try:
            # 1. 验证 SQL 安全性
            is_valid, error_msg = self.validate_sql(sql)
            if not is_valid:
                result['error'] = f"SQL验证失败: {error_msg}"
                execution_time = time.time() - start_time
                result['execution_time'] = execution_time
                log_sql_execution(sql, False, execution_time, error=result['error'])
                return result
            
            # 2. 执行 SQL 查询
            with self._get_connection() as conn:
                with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                    # 设置查询超时
                    cursor.execute(f"SET statement_timeout = {self.timeout * 1000};")
                    
                    # 执行查询
                    cursor.execute(sql)
                    
                    # 获取结果
                    rows = cursor.fetchall()
                    
                    # 限制返回行数
                    if len(rows) > self.max_rows:
                        self.logger.warning(
                            f"查询结果超过最大行数限制 ({len(rows)} > {self.max_rows})，"
                            f"仅返回前 {self.max_rows} 行"
                        )
                        rows = rows[:self.max_rows]
                    
                    # 转换为普通字典列表
                    result['data'] = [dict(row) for row in rows]
                    result['columns'] = list(rows[0].keys()) if rows else []
                    result['row_count'] = len(rows)
                    result['success'] = True
            
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            
            # 记录成功日志
            log_sql_execution(sql, True, execution_time, row_count=result['row_count'])
            
            return result
            
        except psycopg2.Error as e:
            # 数据库错误
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            result['error'] = self._format_db_error(e)
            
            self.logger.error(f"SQL执行失败: {result['error']}")
            log_sql_execution(sql, False, execution_time, error=result['error'])
            
            return result
            
        except Exception as e:
            # 其他错误
            execution_time = time.time() - start_time
            result['execution_time'] = execution_time
            result['error'] = f"执行错误: {str(e)}"
            
            self.logger.error(f"SQL执行失败: {result['error']}")
            log_sql_execution(sql, False, execution_time, error=result['error'])
            
            return result
    
    def validate_sql(self, sql: str) -> Tuple[bool, Optional[str]]:
        """
        验证 SQL 的安全性
        
        检查项:
            1. SQL 不能为空
            2. 必须是 SELECT 语句
            3. 不包含危险关键字（DROP, DELETE, UPDATE 等）
            4. 基本语法检查
        
        参数:
            sql: SQL 查询语句
            
        返回:
            Tuple[bool, Optional[str]]: (是否有效, 错误消息)
        """
        sql_normalized = sql.strip().upper()
        
        # 1. 检查是否为空
        if not sql_normalized:
            return False, "SQL 语句不能为空"
        
        # 2. 移除注释
        # 移除单行注释 --
        lines = []
        for line in sql_normalized.split('\n'):
            if '--' in line:
                line = line[:line.index('--')]
            lines.append(line)
        sql_no_comments = ' '.join(lines)
        
        # 移除多行注释 /* */
        while '/*' in sql_no_comments and '*/' in sql_no_comments:
            start = sql_no_comments.index('/*')
            end = sql_no_comments.index('*/') + 2
            sql_no_comments = sql_no_comments[:start] + ' ' + sql_no_comments[end:]
        
        # 3. 检查是否以 SELECT 或 WITH 开头（允许 CTE）
        first_keyword = sql_no_comments.split()[0] if sql_no_comments.split() else ""
        if first_keyword not in ['SELECT', 'WITH']:
            return False, f"只允许 SELECT 查询（或使用 CTE 的 WITH 语句），当前开头: {first_keyword}"
        
        # 4. 检查是否包含危险关键字
        for keyword in self.forbidden_keywords:
            # 使用单词边界检查，避免误判（如 "UPDATE" 不应出现在 SELECT 语句中）
            if f' {keyword} ' in f' {sql_no_comments} ' or \
               f' {keyword};' in f' {sql_no_comments};':
                return False, f"检测到禁止的关键字: {keyword}"
        
        # 5. 检查是否有分号后还有其他语句（防止多语句注入）
        statements = [s.strip() for s in sql_normalized.split(';') if s.strip()]
        if len(statements) > 1:
            return False, "不允许执行多条 SQL 语句"
        
        return True, None
    
    @contextmanager
    def _get_connection(self):
        """
        获取数据库连接（上下文管理器）
        
        使用 with 语句自动管理连接的打开和关闭
        """
        conn = None
        try:
            conn = psycopg2.connect(**self.db_config.get_psycopg2_params())
            yield conn
        finally:
            if conn:
                conn.close()
    
    def _format_db_error(self, error: psycopg2.Error) -> str:
        """
        格式化数据库错误信息
        
        参数:
            error: psycopg2 错误对象
            
        返回:
            str: 格式化的错误信息
        """
        error_msg = str(error).strip()
        
        # 提取关键错误信息
        if 'syntax error' in error_msg.lower():
            return f"SQL语法错误: {error_msg}"
        elif 'does not exist' in error_msg.lower():
            return f"表或字段不存在: {error_msg}"
        elif 'permission denied' in error_msg.lower():
            return f"权限不足: {error_msg}"
        elif 'timeout' in error_msg.lower() or 'canceling statement' in error_msg.lower():
            return f"查询超时（超过{self.timeout}秒）: {error_msg}"
        else:
            return f"数据库错误: {error_msg}"
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        返回:
            bool: 连接是否成功
        """
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1;")
                    result = cursor.fetchone()
                    return result[0] == 1
        except Exception as e:
            self.logger.error(f"数据库连接测试失败: {e}")
            return False
    
    def get_table_info(self) -> Dict[str, Any]:
        """
        获取数据库表信息（用于调试）
        
        返回:
            Dict: 包含表名和行数的字典
        """
        sql = """
        SELECT 
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
        FROM pg_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY tablename;
        """
        
        result = self.execute(sql)
        return result


# 导出的公共接口
__all__ = ['SQLExecutor']


if __name__ == '__main__':
    # 测试代码
    print("=== 测试 SQLExecutor ===\n")
    
    try:
        from erp_agent.config import get_database_config
        
        # 加载配置
        db_config = get_database_config()
        print(f"数据库配置: {db_config}\n")
        
        # 创建执行器
        executor = SQLExecutor(db_config)
        
        # 测试 1: 连接测试
        print("测试 1: 数据库连接")
        if executor.test_connection():
            print("✓ 数据库连接成功\n")
        else:
            print("✗ 数据库连接失败\n")
            exit(1)
        
        # 测试 2: SQL 验证
        print("测试 2: SQL 安全验证")
        
        valid_sql = "SELECT COUNT(*) FROM employees;"
        is_valid, error = executor.validate_sql(valid_sql)
        print(f"  有效SQL: {valid_sql}")
        print(f"  验证结果: {'✓ 通过' if is_valid else f'✗ 失败 - {error}'}\n")
        
        invalid_sql = "DROP TABLE employees;"
        is_valid, error = executor.validate_sql(invalid_sql)
        print(f"  无效SQL: {invalid_sql}")
        print(f"  验证结果: {'✓ 通过' if is_valid else f'✗ 失败 - {error}'}\n")
        
        # 测试 3: 执行简单查询
        print("测试 3: 执行简单查询")
        sql = "SELECT COUNT(*) as employee_count FROM employees WHERE leave_date IS NULL;"
        result = executor.execute(sql)
        
        if result['success']:
            print(f"✓ 查询成功")
            print(f"  执行时间: {result['execution_time']:.3f}秒")
            print(f"  返回行数: {result['row_count']}")
            print(f"  结果: {result['data']}\n")
        else:
            print(f"✗ 查询失败: {result['error']}\n")
        
        # 测试 4: 执行复杂查询
        print("测试 4: 执行复杂查询（分组统计）")
        sql = """
        SELECT 
            department_name,
            COUNT(*) as employee_count
        FROM employees
        WHERE leave_date IS NULL
        GROUP BY department_name
        ORDER BY employee_count DESC;
        """
        result = executor.execute(sql)
        
        if result['success']:
            print(f"✓ 查询成功")
            print(f"  执行时间: {result['execution_time']:.3f}秒")
            print(f"  返回行数: {result['row_count']}")
            print(f"  列名: {result['columns']}")
            print(f"  结果预览（前3行）:")
            for row in result['data'][:3]:
                print(f"    {row}")
            print()
        else:
            print(f"✗ 查询失败: {result['error']}\n")
        
        # 测试 5: 执行错误的 SQL
        print("测试 5: 执行错误的 SQL")
        sql = "SELECT * FROM non_existent_table;"
        result = executor.execute(sql)
        
        if not result['success']:
            print(f"✓ 正确捕获错误")
            print(f"  错误信息: {result['error']}\n")
        else:
            print(f"✗ 应该失败但成功了\n")
        
        # 测试 6: 获取表信息
        print("测试 6: 获取数据库表信息")
        result = executor.get_table_info()
        
        if result['success']:
            print(f"✓ 获取表信息成功")
            print(f"  表数量: {result['row_count']}")
            if result['data']:
                print(f"  表列表:")
                for table in result['data']:
                    print(f"    - {table['schemaname']}.{table['tablename']} ({table['size']})")
            print()
        else:
            print(f"✗ 获取表信息失败: {result['error']}\n")
        
        print("=" * 60)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
