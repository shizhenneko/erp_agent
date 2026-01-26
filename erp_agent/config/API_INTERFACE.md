# Config 模块接口文档

## 📋 概述

Config 模块提供了 ERP Agent 的所有配置管理功能，包括数据库配置、LLM API 配置和 Agent 全局配置。

---

## 🔌 公共接口（Public API）

### 导入方式

```python
from erp_agent.config import (
    # 配置类
    DatabaseConfig,
    LLMConfig,
    AgentConfig,
    
    # 便捷函数
    get_database_config,
    get_llm_config,
    get_agent_config,
    
    # 测试函数
    test_connection,
    test_api_connection
)
```

---

## 📦 核心类

### 1. DatabaseConfig

**数据库配置类**

#### 属性

| 属性 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `host` | `str` | 数据库主机地址 | 必需 |
| `port` | `int` | 数据库端口 | `5432` |
| `database` | `str` | 数据库名称 | 必需 |
| `user` | `str` | 数据库用户名 | 必需 |
| `password` | `str` | 数据库密码 | 必需 |
| `timeout` | `int` | 连接超时时间（秒） | `30` |
| `max_rows` | `int` | 最大返回行数 | `1000` |

#### 类方法

```python
@classmethod
def from_env() -> DatabaseConfig
```
从环境变量创建配置。

**环境变量：**
- `DB_HOST` (必需)
- `DB_PORT` (可选，默认 5432)
- `DB_NAME` (必需)
- `DB_USER` (必需)
- `DB_PASSWORD` (必需)
- `SQL_TIMEOUT` (可选，默认 30)
- `MAX_RESULT_ROWS` (可选，默认 1000)

**异常：** `ValueError` - 缺少必需的环境变量

---

```python
@classmethod
def from_dict(config_dict: Dict) -> DatabaseConfig
```
从字典创建配置。

**参数：**
- `config_dict`: 包含配置信息的字典

**返回：** `DatabaseConfig`

---

#### 实例方法

```python
def to_dict() -> Dict
```
将配置转换为字典（不包含密码）。

**返回：** 配置字典

---

```python
def get_connection_string() -> str
```
获取 PostgreSQL 连接字符串。

**返回：** 格式为 `postgresql://user:password@host:port/database`

---

```python
def get_psycopg2_params() -> Dict
```
获取 psycopg2.connect() 可用的参数字典。

**返回：** 参数字典

**使用示例：**
```python
import psycopg2
config = DatabaseConfig.from_env()
conn = psycopg2.connect(**config.get_psycopg2_params())
```

---

```python
def validate() -> bool
```
验证配置的有效性。

**返回：** `True` 如果配置有效，否则 `False`

---

### 2. LLMConfig

**LLM API 配置类**

#### 属性

| 属性 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `api_key` | `str` | Kimi API 密钥 | 必需 |
| `base_url` | `str` | API 基础 URL | `https://api.moonshot.cn/v1` |
| `model` | `str` | 模型名称 | `kimi-k2` |
| `temperature` | `float` | 生成温度（0-1） | `0.3` |
| `max_tokens` | `int` | 最大生成 token 数 | `4096` |
| `timeout` | `int` | 请求超时时间（秒） | `60` |
| `max_retries` | `int` | 最大重试次数 | `3` |
| `retry_delay` | `int` | 重试延迟（秒） | `2` |
| `sql_temperature` | `float` | SQL 生成温度 | `0.1` |
| `sql_max_tokens` | `int` | SQL 生成最大 token | `2048` |
| `answer_temperature` | `float` | 答案生成温度 | `0.5` |
| `answer_max_tokens` | `int` | 答案生成最大 token | `1024` |

#### 类方法

```python
@classmethod
def from_env() -> LLMConfig
```
从环境变量创建配置。

**环境变量：**
- `KIMI_API_KEY` (必需)
- `KIMI_BASE_URL` (可选)
- `KIMI_MODEL` (可选)
- `KIMI_TEMPERATURE` (可选)
- `KIMI_MAX_TOKENS` (可选)
- `KIMI_TIMEOUT` (可选)
- `KIMI_MAX_RETRIES` (可选)

**异常：** `ValueError` - 缺少 API 密钥

---

```python
@classmethod
def from_dict(config_dict: Dict) -> LLMConfig
```
从字典创建配置。

**参数：**
- `config_dict`: 包含配置信息的字典

**返回：** `LLMConfig`

---

#### 实例方法

```python
def to_dict() -> Dict
```
将配置转换为字典（不包含 API 密钥）。

**返回：** 配置字典

---

```python
def get_api_headers() -> Dict[str, str]
```
获取 API 请求头。

**返回：** HTTP 请求头字典

**示例：**
```python
{
    'Authorization': 'Bearer sk-xxxxx',
    'Content-Type': 'application/json'
}
```

---

```python
def get_chat_completion_url() -> str
```
获取聊天补全 API 端点 URL。

**返回：** 完整的 API URL

**示例：** `https://api.moonshot.cn/v1/chat/completions`

---

```python
def get_sql_generation_params() -> Dict
```
获取 SQL 生成时的参数（使用低温度 0.1）。

**返回：** 参数字典

**示例：**
```python
{
    'model': 'kimi-k2',
    'temperature': 0.1,
    'max_tokens': 2048
}
```

---

```python
def get_answer_generation_params() -> Dict
```
获取答案生成时的参数（使用中等温度 0.5）。

**返回：** 参数字典

**示例：**
```python
{
    'model': 'kimi-k2',
    'temperature': 0.5,
    'max_tokens': 1024
}
```

---

```python
def validate() -> bool
```
验证配置的有效性。

**返回：** `True` 如果配置有效，否则 `False`

---

### 3. AgentConfig

**Agent 全局配置类**

#### 属性

| 属性 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `max_iterations` | `int` | 最大循环迭代次数 | `5` |
| `enable_retry` | `bool` | 是否启用错误重试 | `True` |
| `enable_multi_query` | `bool` | 是否启用多步查询 | `True` |
| `log_level` | `str` | 日志级别 | `INFO` |
| `log_file` | `str` | 日志文件路径 | `logs/agent.log` |

#### 类方法

```python
@classmethod
def from_env() -> AgentConfig
```
从环境变量创建配置。

**环境变量：**
- `MAX_ITERATIONS` (可选，默认 5)
- `LOG_LEVEL` (可选，默认 INFO)
- `LOG_FILE` (可选，默认 logs/agent.log)

---

```python
@classmethod
def from_dict(config_dict: Dict) -> AgentConfig
```
从字典创建配置。

---

```python
def to_dict() -> Dict
```
将配置转换为字典。

---

## 🔧 便捷函数

### get_database_config()

```python
def get_database_config(config_dict: Optional[Dict] = None) -> DatabaseConfig
```

快速获取数据库配置。

**参数：**
- `config_dict` (可选): 配置字典。如果为 `None`，从环境变量加载。

**返回：** `DatabaseConfig`

**异常：** `ValueError` - 配置无效

**使用示例：**
```python
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

---

### get_llm_config()

```python
def get_llm_config(config_dict: Optional[Dict] = None) -> LLMConfig
```

快速获取 LLM 配置。

**参数：**
- `config_dict` (可选): 配置字典。如果为 `None`，从环境变量加载。

**返回：** `LLMConfig`

**异常：** `ValueError` - 配置无效

**使用示例：**
```python
# 从环境变量加载
config = get_llm_config()

# 从字典加载
config = get_llm_config({
    'api_key': 'sk-xxxxx',
    'model': 'kimi-k2'
})
```

---

### get_agent_config()

```python
def get_agent_config(config_dict: Optional[Dict] = None) -> AgentConfig
```

快速获取 Agent 配置。

**参数：**
- `config_dict` (可选): 配置字典。如果为 `None`，从环境变量加载。

**返回：** `AgentConfig`

**使用示例：**
```python
# 从环境变量加载
config = get_agent_config()

# 从字典加载
config = get_agent_config({'max_iterations': 10})
```

---

### test_connection()

```python
def test_connection(config: Optional[DatabaseConfig] = None) -> bool
```

测试数据库连接。

**参数：**
- `config` (可选): 数据库配置。如果为 `None`，从环境变量加载。

**返回：** `True` 如果连接成功，否则 `False`

**使用示例：**
```python
if test_connection():
    print("数据库连接成功")
else:
    print("数据库连接失败")
```

---

### test_api_connection()

```python
def test_api_connection(config: Optional[LLMConfig] = None) -> bool
```

测试 Kimi API 连接。

**参数：**
- `config` (可选): LLM 配置。如果为 `None`，从环境变量加载。

**返回：** `True` 如果 API 连接成功，否则 `False`

**使用示例：**
```python
if test_api_connection():
    print("API 连接成功")
else:
    print("API 连接失败")
```

---

## 💡 完整使用示例

### 示例 1: 基础使用

```python
from erp_agent.config import (
    get_database_config,
    get_llm_config,
    get_agent_config
)

# 从环境变量加载所有配置
db_config = get_database_config()
llm_config = get_llm_config()
agent_config = get_agent_config()

print(f"数据库: {db_config.database}")
print(f"LLM 模型: {llm_config.model}")
print(f"最大迭代: {agent_config.max_iterations}")
```

---

### 示例 2: 在 Agent 类中使用

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
    
    def call_llm_for_sql(self, messages):
        """调用 LLM 生成 SQL"""
        url = self.llm_config.get_chat_completion_url()
        headers = self.llm_config.get_api_headers()
        
        # 使用 SQL 生成参数（低温度）
        data = {
            **self.llm_config.get_sql_generation_params(),
            'messages': messages
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
    
    def call_llm_for_answer(self, messages):
        """调用 LLM 生成答案"""
        url = self.llm_config.get_chat_completion_url()
        headers = self.llm_config.get_api_headers()
        
        # 使用答案生成参数（稍高温度）
        data = {
            **self.llm_config.get_answer_generation_params(),
            'messages': messages
        }
        
        response = requests.post(url, headers=headers, json=data)
        return response.json()
```

---

### 示例 3: 测试配置

```python
from erp_agent.config import test_connection, test_api_connection

def check_all_configs():
    """检查所有配置"""
    print("检查配置...")
    
    # 测试数据库连接
    if test_connection():
        print("✓ 数据库连接正常")
    else:
        print("✗ 数据库连接失败")
        return False
    
    # 测试 API 连接
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

---

### 示例 4: 使用字典配置（用于测试）

```python
from erp_agent.config import get_database_config, get_llm_config

# 创建测试配置
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
def test_my_agent():
    agent = MyAgent(
        db_config=test_db_config,
        llm_config=test_llm_config
    )
    # 运行测试...
```

---

## 🔒 安全注意事项

### 1. 敏感信息保护

- ✅ **正确：** 使用环境变量存储密码和 API 密钥
- ❌ **错误：** 在代码中硬编码敏感信息

### 2. 日志记录

- `to_dict()` 方法自动隐藏密码和 API 密钥
- `__repr__()` 方法自动脱敏显示

### 3. 配置验证

始终使用 `validate()` 方法验证配置：

```python
config = get_database_config()
if not config.validate():
    raise ValueError("配置无效")
```

---

## 📊 温度参数说明

| 场景 | 温度 | 说明 |
|------|------|------|
| SQL 生成 | 0.1 | 极低温度，确保生成准确的 SQL |
| 默认 | 0.3 | 平衡准确性和多样性 |
| 答案生成 | 0.5 | 稍高温度，使回答更自然流畅 |

---

## 📚 导出接口列表

```python
__all__ = [
    # 配置类
    'DatabaseConfig',
    'LLMConfig',
    'AgentConfig',
    
    # 便捷函数
    'get_database_config',
    'get_llm_config',
    'get_agent_config',
    
    # 测试函数
    'test_connection',
    'test_api_connection',
]
```

---

## 📝 版本信息

- **版本号：** 0.1.0
- **最后更新：** 2026-01-25
- **Python 版本要求：** 3.9+

---

## 🔗 相关文档

- [Config 模块完整文档](./README.md)
- [数据库配置详细说明](./database.py)
- [LLM 配置详细说明](./llm.py)
- [配置测试](../tests/test_config.py)
