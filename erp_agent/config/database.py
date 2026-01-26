#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库配置模块
提供数据库连接配置和连接池管理
"""

import os
from typing import Dict, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class DatabaseConfig:
    """
    数据库配置类
    
    属性:
        host: 数据库主机地址
        port: 数据库端口
        database: 数据库名称
        user: 数据库用户名
        password: 数据库密码
        timeout: 连接超时时间（秒）
        max_rows: 最大返回行数
        
    示例:
        >>> config = DatabaseConfig.from_env()
        >>> print(config.host)
        'localhost'
    """
    host: str
    port: int
    database: str
    user: str
    password: str
    timeout: int = 30
    max_rows: int = 1000
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """
        从环境变量创建数据库配置
        
        需要的环境变量:
            - DB_HOST: 数据库主机地址
            - DB_PORT: 数据库端口（默认: 5432）
            - DB_NAME: 数据库名称
            - DB_USER: 数据库用户名
            - DB_PASSWORD: 数据库密码
            - SQL_TIMEOUT: SQL 执行超时时间（默认: 30秒）
            - MAX_RESULT_ROWS: 最大返回行数（默认: 1000）
            
        返回:
            DatabaseConfig: 数据库配置对象
            
        异常:
            ValueError: 当必需的环境变量缺失时抛出
            
        示例:
            >>> config = DatabaseConfig.from_env()
        """

        host = os.getenv('DB_HOST')
        database = os.getenv('DB_NAME')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        
        # 检查必需的环境变量
        missing_vars = []
        if not host:
            missing_vars.append('DB_HOST')
        if not database:
            missing_vars.append('DB_NAME')
        if not user:
            missing_vars.append('DB_USER')
        if not password:
            missing_vars.append('DB_PASSWORD')
            
        if missing_vars:
            raise ValueError(
                f"缺少必需的数据库环境变量: {', '.join(missing_vars)}"
            )
        
        port = int(os.getenv('DB_PORT', '5432'))
        timeout = int(os.getenv('SQL_TIMEOUT', '30'))
        max_rows = int(os.getenv('MAX_RESULT_ROWS', '1000'))
        
        return cls(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password,
            timeout=timeout,
            max_rows=max_rows
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'DatabaseConfig':
        """
        从字典创建数据库配置
        
        参数:
            config_dict: 包含配置信息的字典
            
        返回:
            DatabaseConfig: 数据库配置对象
            
        示例:
            >>> config = DatabaseConfig.from_dict({
            ...     'host': 'localhost',
            ...     'port': 5432,
            ...     'database': 'erp_agent_db',
            ...     'user': 'erp_user',
            ...     'password': 'password123'
            ... })
        """
        return cls(
            host=config_dict['host'],
            port=config_dict.get('port', 5432),
            database=config_dict['database'],
            user=config_dict['user'],
            password=config_dict['password'],
            timeout=config_dict.get('timeout', 30),
            max_rows=config_dict.get('max_rows', 1000)
        )
    
    def to_dict(self) -> Dict:
        """
        将配置转换为字典
        
        返回:
            Dict: 配置字典（不包含密码，用于日志记录）
            
        示例:
            >>> config = DatabaseConfig.from_env()
            >>> config_dict = config.to_dict()
        """
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'timeout': self.timeout,
            'max_rows': self.max_rows,
            # 注意: 密码不包含在字典中，以保护安全
        }
    
    def get_connection_string(self) -> str:
        """
        获取数据库连接字符串
        
        返回:
            str: PostgreSQL 连接字符串
            
        示例:
            >>> config = DatabaseConfig.from_env()
            >>> conn_str = config.get_connection_string()
            >>> print(conn_str)
            'postgresql://user:password@localhost:5432/erp_agent_db'
        """
        return (
            f"postgresql://{self.user}:{self.password}"
            f"@{self.host}:{self.port}/{self.database}"
        )
    
    def get_psycopg2_params(self) -> Dict:
        """
        获取 psycopg2 连接参数
        
        返回:
            Dict: psycopg2.connect() 可用的参数字典
            
        示例:
            >>> import psycopg2
            >>> config = DatabaseConfig.from_env()
            >>> conn = psycopg2.connect(**config.get_psycopg2_params())
        """
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'user': self.user,
            'password': self.password,
            'connect_timeout': self.timeout
        }
    
    def validate(self) -> bool:
        """
        验证配置的有效性
        
        返回:
            bool: 配置是否有效
            
        示例:
            >>> config = DatabaseConfig.from_env()
            >>> if config.validate():
            ...     print("配置有效")
        """
        if not self.host or not self.database or not self.user or not self.password:
            return False
        
        if self.port <= 0 or self.port > 65535:
            return False
        
        if self.timeout <= 0:
            return False
        
        if self.max_rows <= 0:
            return False
        
        return True
    
    def __repr__(self) -> str:
        """返回配置的字符串表示（隐藏密码）"""
        return (
            f"DatabaseConfig(host='{self.host}', port={self.port}, "
            f"database='{self.database}', user='{self.user}', "
            f"password='***', timeout={self.timeout}, max_rows={self.max_rows})"
        )


def get_database_config(
    config_dict: Optional[Dict] = None
) -> DatabaseConfig:
    """
    获取数据库配置（便捷函数）
    
    参数:
        config_dict: 可选的配置字典。如果提供，使用字典创建配置；
                     否则从环境变量加载
    
    返回:
        DatabaseConfig: 数据库配置对象
        
    异常:
        ValueError: 当配置无效时抛出
        
    示例:
        >>> # 从环境变量加载
        >>> config = get_database_config()
        >>> 
        >>> # 从字典加载
        >>> config = get_database_config({
        ...     'host': 'localhost',
        ...     'database': 'erp_agent_db',
        ...     'user': 'erp_user',
        ...     'password': 'password123'
        ... })
    """
    if config_dict:
        config = DatabaseConfig.from_dict(config_dict)
    else:
        config = DatabaseConfig.from_env()
    
    if not config.validate():
        raise ValueError("数据库配置无效")
    
    return config


def test_connection(config: Optional[DatabaseConfig] = None) -> bool:
    """
    测试数据库连接
    
    参数:
        config: 可选的数据库配置。如果不提供，从环境变量加载
        
    返回:
        bool: 连接是否成功
        
    示例:
        >>> if test_connection():
        ...     print("数据库连接成功")
        ... else:
        ...     print("数据库连接失败")
    """
    try:
        import psycopg2
        
        if config is None:
            config = get_database_config()
        
        conn = psycopg2.connect(**config.get_psycopg2_params())
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False


# 导出的公共接口
__all__ = [
    'DatabaseConfig',
    'get_database_config',
    'test_connection'
]
