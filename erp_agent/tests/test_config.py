#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置模块测试
测试数据库配置和 LLM 配置的各项功能
"""

import os
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))


def test_database_config_from_dict():
    """测试从字典创建数据库配置"""
    from erp_agent.config import DatabaseConfig
    
    print("\n" + "="*70)
    print("测试 1: 从字典创建数据库配置")
    print("="*70)
    
    config = DatabaseConfig.from_dict({
        'host': 'localhost',
        'port': 5432,
        'database': 'test_db',
        'user': 'test_user',
        'password': 'test_password'
    })
    
    assert config.host == 'localhost'
    assert config.port == 5432
    assert config.database == 'test_db'
    assert config.user == 'test_user'
    assert config.password == 'test_password'
    assert config.timeout == 30
    assert config.max_rows == 1000
    
    print("✓ 配置创建成功")
    print(f"  主机: {config.host}")
    print(f"  端口: {config.port}")
    print(f"  数据库: {config.database}")
    print(f"  用户: {config.user}")
    print(f"  超时: {config.timeout}秒")
    print(f"  最大行数: {config.max_rows}")
    
    # 测试 to_dict（不包含密码）
    config_dict = config.to_dict()
    assert 'password' not in config_dict
    print("✓ to_dict() 正确隐藏了密码")
    
    # 测试 repr（隐藏密码）
    repr_str = repr(config)
    assert 'password=\'***\'' in repr_str
    print("✓ __repr__() 正确隐藏了密码")
    
    return True


def test_database_config_validation():
    """测试数据库配置验证"""
    from erp_agent.config import DatabaseConfig
    
    print("\n" + "="*70)
    print("测试 2: 数据库配置验证")
    print("="*70)
    
    # 有效配置
    valid_config = DatabaseConfig(
        host='localhost',
        port=5432,
        database='test_db',
        user='test_user',
        password='test_password'
    )
    assert valid_config.validate()
    print("✓ 有效配置验证通过")
    
    # 无效端口
    invalid_port = DatabaseConfig(
        host='localhost',
        port=-1,
        database='test_db',
        user='test_user',
        password='test_password'
    )
    assert not invalid_port.validate()
    print("✓ 无效端口被正确检测")
    
    # 空密码
    empty_password = DatabaseConfig(
        host='localhost',
        port=5432,
        database='test_db',
        user='test_user',
        password=''
    )
    assert not empty_password.validate()
    print("✓ 空密码被正确检测")
    
    return True


def test_database_config_connection_string():
    """测试数据库连接字符串生成"""
    from erp_agent.config import DatabaseConfig
    
    print("\n" + "="*70)
    print("测试 3: 数据库连接字符串")
    print("="*70)
    
    config = DatabaseConfig(
        host='localhost',
        port=5432,
        database='erp_agent_db',
        user='erp_user',
        password='password123'
    )
    
    conn_str = config.get_connection_string()
    expected = 'postgresql://erp_user:password123@localhost:5432/erp_agent_db'
    
    assert conn_str == expected
    print(f"✓ 连接字符串生成正确")
    print(f"  {conn_str}")
    
    # 测试 psycopg2 参数
    params = config.get_psycopg2_params()
    assert params['host'] == 'localhost'
    assert params['port'] == 5432
    assert params['database'] == 'erp_agent_db'
    assert params['user'] == 'erp_user'
    assert params['password'] == 'password123'
    assert params['connect_timeout'] == 30
    print("✓ psycopg2 参数生成正确")
    
    return True


def test_llm_config_from_dict():
    """测试从字典创建 LLM 配置"""
    from erp_agent.config import LLMConfig
    
    print("\n" + "="*70)
    print("测试 4: 从字典创建 LLM 配置")
    print("="*70)
    
    config = LLMConfig.from_dict({
        'api_key': 'sk-test-key-12345',
        'model': 'kimi-k2',
        'temperature': 0.2
    })
    
    assert config.api_key == 'sk-test-key-12345'
    assert config.model == 'kimi-k2'
    assert config.temperature == 0.2
    assert config.base_url == 'https://api.moonshot.cn/v1'
    
    print("✓ 配置创建成功")
    print(f"  模型: {config.model}")
    print(f"  温度: {config.temperature}")
    print(f"  基础 URL: {config.base_url}")
    
    # 测试 repr（隐藏 API 密钥）
    repr_str = repr(config)
    assert 'sk-test-' in repr_str
    assert '...' in repr_str
    print("✓ __repr__() 正确隐藏了 API 密钥")
    
    return True


def test_llm_config_api_methods():
    """测试 LLM 配置 API 方法"""
    from erp_agent.config import LLMConfig
    
    print("\n" + "="*70)
    print("测试 5: LLM 配置 API 方法")
    print("="*70)
    
    config = LLMConfig(
        api_key='sk-test-key-12345',
        model='kimi-k2',
        base_url='https://api.moonshot.cn/v1'
    )
    
    # 测试请求头
    headers = config.get_api_headers()
    assert 'Authorization' in headers
    assert headers['Authorization'] == 'Bearer sk-test-key-12345'
    assert headers['Content-Type'] == 'application/json'
    print("✓ API 请求头生成正确")
    
    # 测试 API URL
    url = config.get_chat_completion_url()
    assert url == 'https://api.moonshot.cn/v1/chat/completions'
    print(f"✓ API URL 生成正确: {url}")
    
    # 测试 SQL 生成参数
    sql_params = config.get_sql_generation_params()
    assert sql_params['model'] == 'kimi-k2'
    assert sql_params['temperature'] == 0.1  # 更低的温度
    assert sql_params['max_tokens'] == 2048
    print("✓ SQL 生成参数正确（温度=0.1）")
    
    # 测试答案生成参数
    answer_params = config.get_answer_generation_params()
    assert answer_params['model'] == 'kimi-k2'
    assert answer_params['temperature'] == 0.5  # 稍高的温度
    assert answer_params['max_tokens'] == 1024
    print("✓ 答案生成参数正确（温度=0.5）")
    
    return True


def test_llm_config_validation():
    """测试 LLM 配置验证"""
    from erp_agent.config import LLMConfig
    
    print("\n" + "="*70)
    print("测试 6: LLM 配置验证")
    print("="*70)
    
    # 有效配置
    valid_config = LLMConfig(
        api_key='sk-test-key',
        model='kimi-k2'
    )
    assert valid_config.validate()
    print("✓ 有效配置验证通过")
    
    # 空 API 密钥
    empty_key = LLMConfig(
        api_key='',
        model='kimi-k2'
    )
    assert not empty_key.validate()
    print("✓ 空 API 密钥被正确检测")
    
    # 无效温度
    invalid_temp = LLMConfig(
        api_key='sk-test-key',
        model='kimi-k2',
        temperature=1.5
    )
    assert not invalid_temp.validate()
    print("✓ 无效温度被正确检测")
    
    return True


def test_agent_config():
    """测试 Agent 配置"""
    from erp_agent.config import AgentConfig
    
    print("\n" + "="*70)
    print("测试 7: Agent 配置")
    print("="*70)
    
    # 默认配置
    config = AgentConfig()
    assert config.max_iterations == 5
    assert config.enable_retry == True
    assert config.enable_multi_query == True
    assert config.log_level == 'INFO'
    print("✓ 默认配置正确")
    
    # 从字典创建
    custom_config = AgentConfig.from_dict({
        'max_iterations': 10,
        'log_level': 'DEBUG'
    })
    assert custom_config.max_iterations == 10
    assert custom_config.log_level == 'DEBUG'
    print("✓ 自定义配置创建成功")
    
    # 转换为字典
    config_dict = custom_config.to_dict()
    assert config_dict['max_iterations'] == 10
    assert config_dict['log_level'] == 'DEBUG'
    print("✓ 配置转换为字典成功")
    
    return True


def test_convenience_functions():
    """测试便捷函数"""
    from erp_agent.config import (
        get_database_config,
        get_llm_config,
        get_agent_config
    )
    
    print("\n" + "="*70)
    print("测试 8: 便捷函数")
    print("="*70)
    
    # 测试从字典创建数据库配置
    db_config = get_database_config({
        'host': 'localhost',
        'port': 5432,
        'database': 'test_db',
        'user': 'test_user',
        'password': 'test_password'
    })
    assert db_config.host == 'localhost'
    print("✓ get_database_config() 工作正常")
    
    # 测试从字典创建 LLM 配置
    llm_config = get_llm_config({
        'api_key': 'sk-test-key',
        'model': 'kimi-k2'
    })
    assert llm_config.api_key == 'sk-test-key'
    print("✓ get_llm_config() 工作正常")
    
    # 测试从字典创建 Agent 配置
    agent_config = get_agent_config({
        'max_iterations': 8
    })
    assert agent_config.max_iterations == 8
    print("✓ get_agent_config() 工作正常")
    
    return True


def test_config_from_env():
    """测试从环境变量加载配置（如果环境变量存在）"""
    print("\n" + "="*70)
    print("测试 9: 从环境变量加载配置")
    print("="*70)
    
    # 加载 .env 文件
    try:
        from dotenv import load_dotenv
        env_path = project_root / 'erp_agent' / '.env'
        
        if env_path.exists():
            load_dotenv(env_path)
            print(f"✓ 已加载 .env 文件: {env_path}")
            
            # 尝试从环境变量创建配置
            try:
                from erp_agent.config import DatabaseConfig, LLMConfig, AgentConfig
                
                # 数据库配置
                try:
                    db_config = DatabaseConfig.from_env()
                    print(f"✓ 数据库配置加载成功")
                    print(f"  主机: {db_config.host}")
                    print(f"  数据库: {db_config.database}")
                except ValueError as e:
                    print(f"⚠ 数据库配置不完整: {e}")
                
                # LLM 配置
                try:
                    llm_config = LLMConfig.from_env()
                    print(f"✓ LLM 配置加载成功")
                    print(f"  模型: {llm_config.model}")
                except ValueError as e:
                    print(f"⚠ LLM 配置不完整: {e}")
                
                # Agent 配置
                agent_config = AgentConfig.from_env()
                print(f"✓ Agent 配置加载成功")
                print(f"  最大迭代: {agent_config.max_iterations}")
                
            except Exception as e:
                print(f"⚠ 从环境变量加载配置失败: {e}")
        else:
            print(f"⚠ .env 文件不存在: {env_path}")
            print("  提示: 从 .env.example 复制并配置")
            
    except ImportError:
        print("⚠ 未安装 python-dotenv")
        print("  运行: pip install python-dotenv")
    
    return True


def run_all_tests():
    """运行所有测试"""
    print("\n" + "="*70)
    print("ERP Agent - Config 模块测试套件")
    print("="*70)
    
    tests = [
        test_database_config_from_dict,
        test_database_config_validation,
        test_database_config_connection_string,
        test_llm_config_from_dict,
        test_llm_config_api_methods,
        test_llm_config_validation,
        test_agent_config,
        test_convenience_functions,
        test_config_from_env,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            failed += 1
            print(f"\n✗ 测试失败: {test.__name__}")
            print(f"  错误: {e}")
        except Exception as e:
            failed += 1
            print(f"\n✗ 测试出错: {test.__name__}")
            print(f"  异常: {e}")
    
    print("\n" + "="*70)
    print("测试总结")
    print("="*70)
    print(f"通过: {passed}/{len(tests)}")
    print(f"失败: {failed}/{len(tests)}")
    
    if failed == 0:
        print("\n🎉 所有测试通过！")
    else:
        print(f"\n⚠ {failed} 个测试失败")
    
    print("="*70)


if __name__ == '__main__':
    run_all_tests()
