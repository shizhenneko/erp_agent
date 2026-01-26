"""
核心模块

包含 ERP Agent 的核心组件：
1. ERPAgent - Agent 主控制器（ReAct 范式）
2. SQLGenerator - SQL 生成器（调用 Kimi API）
3. SQLExecutor - SQL 执行器（执行查询）
4. ResultAnalyzer - 结果分析器（分析查询结果）
5. AgentState - Agent 状态数据类

快速开始:
    >>> from erp_agent.core import ERPAgent
    >>> from erp_agent.config import get_llm_config, get_database_config
    >>> 
    >>> llm_config = get_llm_config()
    >>> db_config = get_database_config()
    >>> 
    >>> agent = ERPAgent(llm_config, db_config)
    >>> result = agent.query("公司有多少在职员工？")
    >>> print(result['answer'])
"""

from .agent import ERPAgent, AgentState
from .sql_generator import SQLGenerator
from .sql_executor import SQLExecutor
from .result_analyzer import ResultAnalyzer

__all__ = [
    'ERPAgent',
    'AgentState',
    'SQLGenerator',
    'SQLExecutor',
    'ResultAnalyzer',
]

__version__ = '0.1.0'
