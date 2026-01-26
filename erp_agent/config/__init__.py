"""
配置模块
包含数据库配置和LLM配置

提供以下功能:
1. 数据库配置管理（DatabaseConfig）
2. LLM API 配置管理（LLMConfig）
3. Agent 全局配置管理（AgentConfig）
4. 便捷的配置加载函数
5. 配置验证和测试功能

快速开始:
    >>> from erp_agent.config import get_database_config, get_llm_config
    >>> 
    >>> # 从环境变量加载配置
    >>> db_config = get_database_config()
    >>> llm_config = get_llm_config()
    >>> 
    >>> # 测试连接
    >>> from erp_agent.config import test_connection, test_api_connection
    >>> if test_connection(db_config) and test_api_connection(llm_config):
    ...     print("所有配置正常")
"""

from .database import (
    DatabaseConfig,
    get_database_config,
    test_connection
)

from .llm import (
    LLMConfig,
    AgentConfig,
    get_llm_config,
    get_agent_config,
    test_api_connection
)

__all__ = [
    # 数据库配置
    'DatabaseConfig',
    'get_database_config',
    'test_connection',
    
    # LLM 配置
    'LLMConfig',
    'AgentConfig',
    'get_llm_config',
    'get_agent_config',
    'test_api_connection',
]

__version__ = '0.1.0'
