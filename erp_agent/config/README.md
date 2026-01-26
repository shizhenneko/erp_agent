# Config 模块文档

## 📋 概述

Config 模块提供了 ERP Agent 系统的配置管理功能，包括数据库配置、LLM API 配置和 Agent 全局配置。

## 🏗 模块结构

```
config/
├── __init__.py           # 模块入口，导出所有公共接口
├── database.py           # 数据库配置
├── llm.py               # LLM 和 Agent 配置
└── README.md            # 本文档
```

## 📦 核心类和接口

### 1. DatabaseConfig - 数据库配置类

#### 类定义

```python
@dataclass
class DatabaseConfig:
    """数据库配置类"""
    host: str
    port: int
    database: str
    user: str
    password: str
    timeout: int = 30
    max_rows: int = 1000
```

#### 主要方法

| 方法 | 说明 | 返回类型 |
|------|------|----------|
| `from_env()` | 从环境变量创建配置 | `DatabaseConfig` |
| `from_dict(config_dict)` | 从字典创建配置 | `DatabaseConfig` |
| `to_dict()` | 转换为字典（不含密码） | `Dict` |
| `get_connection_string()` | 获取连接字符串 | `str` |
| `get_psycopg2_params()` | 获取 psycopg2 参数 | `Dict` |
| `validate()` | 验证配置有效性 | `bool` |

#### 使用示例

```python
from erp_agent.config import DatabaseConfig

# 方式1: 从环境变量加载
config = DatabaseConfig.from_env()

# 方式2: 从字典加载
config = DatabaseConfig.from_dict({
    'host': 'localhost',
    'port': 5432,
    'database': 'erp_agent_db',
    'user': 'erp_user',
    'password': 'password123'
})

# 获取连接参数
import psycopg2
conn = psycopg2.connect(**config.get_psycopg2_params())

# 获取连接字符串
conn_str = config.get_connection_string()
print(conn_str)  # postgresql://user:password@localhost:5432/erp_agent_db
```

#### 环境变量

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `DB_HOST` | 数据库主机地址 | ✓ | - |
| `DB_PORT` | 数据库端口 | ✗ | 5432 |
| `DB_NAME` | 数据库名称 | ✓ | - |
| `DB_USER` | 数据库用户名 | ✓ | - |
| `DB_PASSWORD` | 数据库密码 | ✓ | - |
| `SQL_TIMEOUT` | SQL 超时时间（秒） | ✗ | 30 |
| `MAX_RESULT_ROWS` | 最大返回行数 | ✗ | 1000 |

---

### 2. LLMConfig - LLM API 配置类

#### 类定义

```python
@dataclass
class LLMConfig:
    """LLM 配置类"""
    api_key: str
    base_url: str = "https://api.moonshot.cn/v1"
    model: str = "kimi-k2"
    temperature: float = 0.3
    max_tokens: int = 4096
    timeout: int = 60
    max_retries: int = 3
    retry_delay: int = 2
    
    # SQL 生成专用配置
    sql_temperature: float = 0.1
    sql_max_tokens: int = 2048
    
    # 答案生成专用配置
    answer_temperature: float = 0.5
    answer_max_tokens: int = 1024
```

#### 主要方法

| 方法 | 说明 | 返回类型 |
|------|------|----------|
| `from_env()` | 从环境变量创建配置 | `LLMConfig` |
| `from_dict(config_dict)` | 从字典创建配置 | `LLMConfig` |
| `to_dict()` | 转换为字典（不含 API 密钥） | `Dict` |
| `get_api_headers()` | 获取 API 请求头 | `Dict[str, str]` |
| `get_chat_completion_url()` | 获取 API 端点 URL | `str` |
| `get_sql_generation_params()` | 获取 SQL 生成参数 | `Dict` |
| `get_answer_generation_params()` | 获取答案生成参数 | `Dict` |
| `validate()` | 验证配置有效性 | `bool` |

#### 使用示例

```python
from erp_agent.config import LLMConfig
import requests

# 方式1: 从环境变量加载
config = LLMConfig.from_env()

# 方式2: 从字典加载
config = LLMConfig.from_dict({
    'api_key': 'sk-xxxxx',
    'model': 'kimi-k2-pro',
    'temperature': 0.2
})

# 调用 API
url = config.get_chat_completion_url()
headers = config.get_api_headers()

# SQL 生成时使用
sql_params = config.get_sql_generation_params()
data = {
    **sql_params,
    'messages': [{'role': 'user', 'content': 'Generate SQL...'}]
}
response = requests.post(url, headers=headers, json=data)

# 答案生成时使用
answer_params = config.get_answer_generation_params()
data = {
    **answer_params,
    'messages': [{'role': 'user', 'content': 'Explain results...'}]
}
response = requests.post(url, headers=headers, json=data)
```

#### 环境变量

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `KIMI_API_KEY` | Kimi API 密钥 | ✓ | - |
| `KIMI_BASE_URL` | API 基础 URL | ✗ | https://api.moonshot.cn/v1 |
| `KIMI_MODEL` | 模型名称 | ✗ | kimi-k2 |
| `KIMI_TEMPERATURE` | 生成温度 | ✗ | 0.3 |
| `KIMI_MAX_TOKENS` | 最大 token 数 | ✗ | 4096 |
| `KIMI_TIMEOUT` | 请求超时（秒） | ✗ | 60 |
| `KIMI_MAX_RETRIES` | 最大重试次数 | ✗ | 3 |

#### 温度参数说明

- **sql_temperature = 0.1**: SQL 生成时使用极低温度，确保生成的 SQL 准确且确定
- **temperature = 0.3**: 默认温度，平衡准确性和多样性
- **answer_temperature = 0.5**: 答案生成时使用稍高温度，使回答更自然流畅

---

### 3. AgentConfig - Agent 全局配置类

#### 类定义

```python
@dataclass
class AgentConfig:
    """Agent 全局配置类"""
    max_iterations: int = 5
    enable_retry: bool = True
    enable_multi_query: bool = True
    log_level: str = "INFO"
    log_file: str = "logs/agent.log"
```

#### 主要方法

| 方法 | 说明 | 返回类型 |
|------|------|----------|
| `from_env()` | 从环境变量创建配置 | `AgentConfig` |
| `from_dict(config_dict)` | 从字典创建配置 | `AgentConfig` |
| `to_dict()` | 转换为字典 | `Dict` |

#### 使用示例

```python
from erp_agent.config import AgentConfig

# 从环境变量加载
config = AgentConfig.from_env()

# 从字典加载
config = AgentConfig.from_dict({
    'max_iterations': 10,
    'log_level': 'DEBUG'
})

# 在 Agent 中使用
class ERPAgent:
    def __init__(self, agent_config: AgentConfig):
        self.max_iterations = agent_config.max_iterations
        self.enable_retry = agent_config.enable_retry
```

#### 环境变量

| 变量名 | 说明 | 必需 | 默认值 |
|--------|------|------|--------|
| `MAX_ITERATIONS` | 最大循环迭代次数 | ✗ | 5 |
| `LOG_LEVEL` | 日志级别 | ✗ | INFO |
| `LOG_FILE` | 日志文件路径 | ✗ | logs/agent.log |

---

## 🚀 便捷函数

### 1. get_database_config()

快速获取数据库配置。

```python
from erp_agent.config import get_database_config

# 从环境变量加载
config = get_database_config()

# 从字典加载
config = get_database_config({
    'host': 'localhost',
    'database': 'erp_agent_db',
    'user': 'erp_user',
    'password': 'password123'
})
```

**参数:**
- `config_dict` (Optional[Dict]): 配置字典，如果为 None 则从环境变量加载

**返回:**
- `DatabaseConfig`: 数据库配置对象

**异常:**
- `ValueError`: 当配置无效或缺少必需变量时

---

### 2. get_llm_config()

快速获取 LLM 配置。

```python
from erp_agent.config import get_llm_config

# 从环境变量加载
config = get_llm_config()

# 从字典加载
config = get_llm_config({
    'api_key': 'sk-xxxxx',
    'model': 'kimi-k2'
})
```

**参数:**
- `config_dict` (Optional[Dict]): 配置字典，如果为 None 则从环境变量加载

**返回:**
- `LLMConfig`: LLM 配置对象

**异常:**
- `ValueError`: 当配置无效或缺少 API 密钥时

---

### 3. get_agent_config()

快速获取 Agent 配置。

```python
from erp_agent.config import get_agent_config

# 从环境变量加载
config = get_agent_config()

# 从字典加载
config = get_agent_config({'max_iterations': 10})
```

**参数:**
- `config_dict` (Optional[Dict]): 配置字典，如果为 None 则从环境变量加载

**返回:**
- `AgentConfig`: Agent 配置对象

---

### 4. test_connection()

测试数据库连接。

```python
from erp_agent.config import test_connection, get_database_config

# 测试默认配置
if test_connection():
    print("数据库连接成功")

# 测试指定配置
config = get_database_config({'host': 'localhost', ...})
if test_connection(config):
    print("数据库连接成功")
```

**参数:**
- `config` (Optional[DatabaseConfig]): 数据库配置，如果为 None 则从环境变量加载

**返回:**
- `bool`: 连接是否成功

---

### 5. test_api_connection()

测试 Kimi API 连接。

```python
from erp_agent.config import test_api_connection, get_llm_config

# 测试默认配置
if test_api_connection():
    print("API 连接成功")

# 测试指定配置
config = get_llm_config({'api_key': 'sk-xxxxx', ...})
if test_api_connection(config):
    print("API 连接成功")
```

**参数:**
- `config` (Optional[LLMConfig]): LLM 配置，如果为 None 则从环境变量加载

**返回:**
- `bool`: API 连接是否成功

---

## 📝 完整使用示例

### 示例 1: 基础使用

```python
from erp_agent.config import (
    get_database_config,
    get_llm_config,
    get_agent_config
)

# 加载所有配置
db_config = get_database_config()
llm_config = get_llm_config()
agent_config = get_agent_config()

# 使用配置
print(f"数据库: {db_config.database}")
print(f"LLM 模型: {llm_config.model}")
print(f"最大迭代次数: {agent_config.max_iterations}")
```

### 示例 2: 在 Agent 中使用

```python
from erp_agent.config import (
    get_database_config,
    get_llm_config,
    get_agent_config
)
import psycopg2
import requests

class ERPAgent:
    def __init__(self):
        # 加载配置
        self.db_config = get_database_config()
        self.llm_config = get_llm_config()
        self.agent_config = get_agent_config()
        
        # 初始化数据库连接
        self.db_conn = psycopg2.connect(
            **self.db_config.get_psycopg2_params()
        )
        
    def query_llm(self, messages):
        """调用 LLM API"""
        url = self.llm_config.get_chat_completion_url()
        headers = self.llm_config.get_api_headers()
        
        data = {
            **self.llm_config.get_sql_generation_params(),
            'messages': messages
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def execute_sql(self, sql):
        """执行 SQL"""
        cursor = self.db_conn.cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        cursor.close()
        return result
```

### 示例 3: 测试配置

```python
from erp_agent.config import (
    test_connection,
    test_api_connection
)

def check_all_configs():
    """检查所有配置"""
    print("检查配置...")
    
    # 测试数据库
    if test_connection():
        print("✓ 数据库连接正常")
    else:
        print("✗ 数据库连接失败")
        return False
    
    # 测试 API
    if test_api_connection():
        print("✓ API 连接正常")
    else:
        print("✗ API 连接失败")
        return False
    
    print("所有配置检查通过")
    return True

if __name__ == '__main__':
    check_all_configs()
```

### 示例 4: 使用字典配置（用于测试）

```python
from erp_agent.config import (
    get_database_config,
    get_llm_config
)

# 测试环境配置
test_db_config = get_database_config({
    'host': 'localhost',
    'port': 5432,
    'database': 'test_db',
    'user': 'test_user',
    'password': 'test_password'
})

test_llm_config = get_llm_config({
    'api_key': 'test-api-key',
    'model': 'kimi-k2',
    'temperature': 0.1
})

# 在测试中使用
def test_agent():
    agent = ERPAgent(
        db_config=test_db_config,
        llm_config=test_llm_config
    )
    # 运行测试...
```

---

## 🔒 安全最佳实践

### 1. 保护敏感信息

```python
# ✓ 正确：使用环境变量
config = get_database_config()  # 从 .env 加载

# ✗ 错误：硬编码密码
config = DatabaseConfig(
    host='localhost',
    password='my_password'  # 不要这样做！
)
```

### 2. 日志记录时隐藏敏感信息

```python
config = get_database_config()

# ✓ 正确：使用 to_dict()（自动隐藏密码）
print(config.to_dict())  # 不包含密码

# ✓ 正确：使用 repr（自动隐藏敏感信息）
print(config)  # 显示为 password='***'

# ✗ 错误：直接打印完整配置
print(config.password)  # 不要在日志中这样做
```

### 3. 验证配置

```python
config = get_database_config()

# 验证配置
if not config.validate():
    raise ValueError("配置无效")
```

---

## 🧪 测试

### 运行配置测试

```python
# test_config.py
from erp_agent.config import (
    DatabaseConfig,
    LLMConfig,
    test_connection,
    test_api_connection
)

def test_database_config():
    """测试数据库配置"""
    config = DatabaseConfig.from_dict({
        'host': 'localhost',
        'port': 5432,
        'database': 'test_db',
        'user': 'test_user',
        'password': 'test_password'
    })
    
    assert config.validate()
    assert config.host == 'localhost'
    assert config.port == 5432

def test_llm_config():
    """测试 LLM 配置"""
    config = LLMConfig.from_dict({
        'api_key': 'test-key',
        'model': 'kimi-k2'
    })
    
    assert config.validate()
    assert config.model == 'kimi-k2'
    assert 'Bearer test-key' in config.get_api_headers()['Authorization']

def test_connections():
    """测试实际连接"""
    # 需要真实的环境变量
    assert test_connection()
    assert test_api_connection()
```

---

## 📚 API 参考总结

### 导出的类

| 类名 | 说明 |
|------|------|
| `DatabaseConfig` | 数据库配置类 |
| `LLMConfig` | LLM API 配置类 |
| `AgentConfig` | Agent 全局配置类 |

### 导出的函数

| 函数名 | 说明 |
|--------|------|
| `get_database_config(config_dict=None)` | 获取数据库配置 |
| `get_llm_config(config_dict=None)` | 获取 LLM 配置 |
| `get_agent_config(config_dict=None)` | 获取 Agent 配置 |
| `test_connection(config=None)` | 测试数据库连接 |
| `test_api_connection(config=None)` | 测试 API 连接 |

### 所有方法快速索引

#### DatabaseConfig 方法
- `from_env()` - 从环境变量创建
- `from_dict(dict)` - 从字典创建
- `to_dict()` - 转为字典
- `get_connection_string()` - 获取连接字符串
- `get_psycopg2_params()` - 获取 psycopg2 参数
- `validate()` - 验证配置

#### LLMConfig 方法
- `from_env()` - 从环境变量创建
- `from_dict(dict)` - 从字典创建
- `to_dict()` - 转为字典
- `get_api_headers()` - 获取请求头
- `get_chat_completion_url()` - 获取 API URL
- `get_sql_generation_params()` - 获取 SQL 生成参数
- `get_answer_generation_params()` - 获取答案生成参数
- `validate()` - 验证配置

#### AgentConfig 方法
- `from_env()` - 从环境变量创建
- `from_dict(dict)` - 从字典创建
- `to_dict()` - 转为字典

---

## 💡 常见问题

### Q: 如何切换不同的环境配置？

A: 使用不同的 `.env` 文件：

```bash
# 开发环境
cp .env.development .env

# 生产环境
cp .env.production .env
```

### Q: 如何在测试中使用 mock 配置？

A: 使用字典创建配置：

```python
test_config = get_database_config({
    'host': 'mock-db',
    'database': 'test',
    'user': 'test',
    'password': 'test'
})
```

### Q: 配置验证失败怎么办？

A: 检查配置的 `validate()` 方法返回值，确保所有必需字段都已设置且值合理。

---

**版本**: 0.1.0  
**最后更新**: 2026-01-25
