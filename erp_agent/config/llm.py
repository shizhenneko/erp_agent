#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLM 配置模块
提供 Kimi API 配置和相关设置
"""

import os
from typing import Dict, Optional, List
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()

@dataclass
class LLMConfig:
    """
    LLM 配置类
    
    属性:
        api_key: Kimi API 密钥
        base_url: API 基础 URL
        model: 使用的模型名称
        temperature: 生成温度（0-1）
        max_tokens: 最大生成 token 数
        timeout: API 请求超时时间（秒）
        max_retries: 最大重试次数
        retry_delay: 重试延迟（秒）
        
    示例:
        >>> config = LLMConfig.from_env()
        >>> print(config.model)
        'kimi-k2'
    """
    api_key: str
    base_url: str = "https://api.moonshot.cn/v1"
    model: str = "kimi-k2"
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: int = 120  # 增加到120秒，应对复杂查询
    max_retries: int = 5  # 增加重试次数
    retry_delay: int = 5  # 增加重试间隔到5秒
    
    # SQL 生成专用配置
    sql_temperature: float = 0.1  # SQL 生成时使用更低的温度以提高确定性
    sql_max_tokens: int = 4096
    
    # 答案生成专用配置
    answer_temperature: float = 0.5  # 答案生成时允许更高的温度
    answer_max_tokens: int = 1024
    
    @classmethod
    def from_env(cls) -> 'LLMConfig':
        """
        从环境变量创建 LLM 配置
        
        需要的环境变量:
            - MOONSHOT_API_KEY: Moonshot API 密钥（必需）
            - MOONSHOT_BASE_URL: API 基础 URL（默认: https://api.moonshot.cn/v1）
            - MOONSHOT_MODEL: 模型名称（默认: kimi-k2）
            
        返回:
            LLMConfig: LLM 配置对象
            
        异常:
            ValueError: 当 API 密钥缺失时抛出
            
        示例:
            >>> config = LLMConfig.from_env()
        """
        api_key = os.getenv('MOONSHOT_API_KEY')
        
        if not api_key:
            raise ValueError("缺少必需的环境变量: MOONSHOT_API_KEY")
        
        return cls(
            api_key=api_key,
            base_url=os.getenv('MOONSHOT_BASE_URL', 'https://api.moonshot.cn/v1'),
            model=os.getenv('MOONSHOT_MODEL', 'kimi-k2')
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'LLMConfig':
        """
        从字典创建 LLM 配置
        
        参数:
            config_dict: 包含配置信息的字典
            
        返回:
            LLMConfig: LLM 配置对象
            
        示例:
            >>> config = LLMConfig.from_dict({
            ...     'api_key': 'sk-xxxxx',
            ...     'model': 'kimi-k2-pro',
            ...     'temperature': 0.2
            ... })
        """
        return cls(
            api_key=config_dict['api_key'],
            base_url=config_dict.get('base_url', 'https://api.moonshot.cn/v1'),
            model=config_dict.get('model', 'kimi-k2'),
            temperature=config_dict.get('temperature', 0.3),
            max_tokens=config_dict.get('max_tokens', 4096),
            timeout=config_dict.get('timeout', 60),
            max_retries=config_dict.get('max_retries', 3),
            retry_delay=config_dict.get('retry_delay', 2)
        )
    
    def to_dict(self) -> Dict:
        """
        将配置转换为字典
        
        返回:
            Dict: 配置字典（不包含 API 密钥，用于日志记录）
            
        示例:
            >>> config = LLMConfig.from_env()
            >>> config_dict = config.to_dict()
        """
        return {
            'base_url': self.base_url,
            'model': self.model,
            'temperature': self.temperature,
            'max_tokens': self.max_tokens,
            'timeout': self.timeout,
            'max_retries': self.max_retries,
            'retry_delay': self.retry_delay,
            # 注意: API 密钥不包含在字典中，以保护安全
        }
    
    def get_api_headers(self) -> Dict[str, str]:
        """
        获取 API 请求头
        
        返回:
            Dict: HTTP 请求头字典
            
        示例:
            >>> import requests
            >>> config = LLMConfig.from_env()
            >>> headers = config.get_api_headers()
            >>> response = requests.post(url, headers=headers, json=data)
        """
        return {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_chat_completion_url(self) -> str:
        """
        获取聊天补全 API 端点 URL
        
        返回:
            str: 完整的 API 端点 URL
            
        示例:
            >>> config = LLMConfig.from_env()
            >>> url = config.get_chat_completion_url()
            >>> print(url)
            'https://api.moonshot.cn/v1/chat/completions'
        """
        return f"{self.base_url.rstrip('/')}/chat/completions"
    
    def get_sql_generation_params(self) -> Dict:
        """
        获取 SQL 生成时的参数
        
        返回:
            Dict: SQL 生成专用参数
            
        示例:
            >>> config = LLMConfig.from_env()
            >>> params = config.get_sql_generation_params()
            >>> # 这些参数会使用更低的温度以提高准确性
        """
        return {
            'model': self.model,
            'temperature': self.sql_temperature,
            'max_tokens': self.sql_max_tokens
        }
    
    def get_answer_generation_params(self) -> Dict:
        """
        获取答案生成时的参数
        
        返回:
            Dict: 答案生成专用参数
            
        示例:
            >>> config = LLMConfig.from_env()
            >>> params = config.get_answer_generation_params()
            >>> # 这些参数会使用稍高的温度以提高回答的自然度
        """
        return {
            'model': self.model,
            'temperature': self.answer_temperature,
            'max_tokens': self.answer_max_tokens
        }
    
    def validate(self) -> bool:
        """
        验证配置的有效性
        
        返回:
            bool: 配置是否有效
            
        示例:
            >>> config = LLMConfig.from_env()
            >>> if config.validate():
            ...     print("配置有效")
        """
        if not self.api_key:
            return False
        
        if not self.base_url:
            return False
        
        if not self.model:
            return False
        
        if not (0 <= self.temperature <= 1):
            return False
        
        if self.max_tokens <= 0:
            return False
        
        if self.timeout <= 0:
            return False
        
        if self.max_retries < 0:
            return False
        
        return True
    
    def __repr__(self) -> str:
        """返回配置的字符串表示（隐藏 API 密钥）"""
        api_key_masked = f"{self.api_key[:8]}..." if len(self.api_key) > 8 else "***"
        return (
            f"LLMConfig(api_key='{api_key_masked}', model='{self.model}', "
            f"temperature={self.temperature}, max_tokens={self.max_tokens})"
        )


@dataclass
class AgentConfig:
    """
    Agent 整体配置类
    
    属性:
        max_iterations: 最大循环迭代次数
        enable_retry: 是否启用错误重试
        enable_multi_query: 是否启用多步查询
        log_level: 日志级别
        log_file: 日志文件路径
        
    示例:
        >>> config = AgentConfig.from_env()
        >>> print(config.max_iterations)
        5
    """
    max_iterations: int = 5
    enable_retry: bool = True
    enable_multi_query: bool = True
    log_level: str = "INFO"
    log_file: str = "logs/agent.log"
    
    @classmethod
    def from_env(cls) -> 'AgentConfig':
        """
        从环境变量创建 Agent 配置
        
        需要的环境变量:
            - MAX_ITERATIONS: 最大循环迭代次数（默认: 5）
            - LOG_LEVEL: 日志级别（默认: INFO）
            - LOG_FILE: 日志文件路径（默认: logs/agent.log）
            
        返回:
            AgentConfig: Agent 配置对象
            
        示例:
            >>> config = AgentConfig.from_env()
        """
        return cls(
            max_iterations=int(os.getenv('MAX_ITERATIONS', '5')),
            log_level=os.getenv('LOG_LEVEL', 'INFO'),
            log_file=os.getenv('LOG_FILE', 'logs/agent.log')
        )
    
    @classmethod
    def from_dict(cls, config_dict: Dict) -> 'AgentConfig':
        """
        从字典创建 Agent 配置
        
        参数:
            config_dict: 包含配置信息的字典
            
        返回:
            AgentConfig: Agent 配置对象
            
        示例:
            >>> config = AgentConfig.from_dict({
            ...     'max_iterations': 10,
            ...     'log_level': 'DEBUG'
            ... })
        """
        return cls(
            max_iterations=config_dict.get('max_iterations', 5),
            enable_retry=config_dict.get('enable_retry', True),
            enable_multi_query=config_dict.get('enable_multi_query', True),
            log_level=config_dict.get('log_level', 'INFO'),
            log_file=config_dict.get('log_file', 'logs/agent.log')
        )
    
    def to_dict(self) -> Dict:
        """
        将配置转换为字典
        
        返回:
            Dict: 配置字典
            
        示例:
            >>> config = AgentConfig.from_env()
            >>> config_dict = config.to_dict()
        """
        return {
            'max_iterations': self.max_iterations,
            'enable_retry': self.enable_retry,
            'enable_multi_query': self.enable_multi_query,
            'log_level': self.log_level,
            'log_file': self.log_file
        }


def get_llm_config(config_dict: Optional[Dict] = None) -> LLMConfig:
    """
    获取 LLM 配置（便捷函数）
    
    参数:
        config_dict: 可选的配置字典。如果提供，使用字典创建配置；
                     否则从环境变量加载
    
    返回:
        LLMConfig: LLM 配置对象
        
    异常:
        ValueError: 当配置无效时抛出
        
    示例:
        >>> # 从环境变量加载
        >>> config = get_llm_config()
        >>> 
        >>> # 从字典加载
        >>> config = get_llm_config({
        ...     'api_key': 'sk-xxxxx',
        ...     'model': 'kimi-k2'
        ... })
    """
    if config_dict:
        config = LLMConfig.from_dict(config_dict)
    else:
        config = LLMConfig.from_env()
    
    if not config.validate():
        raise ValueError("LLM 配置无效")
    
    return config


def get_agent_config(config_dict: Optional[Dict] = None) -> AgentConfig:
    """
    获取 Agent 配置（便捷函数）
    
    参数:
        config_dict: 可选的配置字典。如果提供，使用字典创建配置；
                     否则从环境变量加载
    
    返回:
        AgentConfig: Agent 配置对象
        
    示例:
        >>> # 从环境变量加载
        >>> config = get_agent_config()
        >>> 
        >>> # 从字典加载
        >>> config = get_agent_config({'max_iterations': 10})
    """
    if config_dict:
        config = AgentConfig.from_dict(config_dict)
    else:
        config = AgentConfig.from_env()
    
    return config


def test_api_connection(config: Optional[LLMConfig] = None) -> bool:
    """
    测试 Kimi API 连接
    
    参数:
        config: 可选的 LLM 配置。如果不提供，从环境变量加载
        
    返回:
        bool: API 连接是否成功
        
    示例:
        >>> if test_api_connection():
        ...     print("API 连接成功")
        ... else:
        ...     print("API 连接失败")
    """
    try:
        import requests
        
        if config is None:
            config = get_llm_config()
        
        # 发送一个简单的测试请求
        url = config.get_chat_completion_url()
        headers = config.get_api_headers()
        data = {
            'model': config.model,
            'messages': [
                {'role': 'user', 'content': 'test'}
            ],
            'max_tokens': 10
        }
        
        response = requests.post(
            url,
            headers=headers,
            json=data,
            timeout=config.timeout
        )
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"API 连接测试失败: {e}")
        return False


# 导出的公共接口
__all__ = [
    'LLMConfig',
    'AgentConfig',
    'get_llm_config',
    'get_agent_config',
    'test_api_connection'
]
