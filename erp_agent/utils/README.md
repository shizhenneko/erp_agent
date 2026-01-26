# Utils 模块

ERP Agent 工具模块，提供时间处理、Prompt 构建和日志记录功能。

## 📁 模块结构

```
utils/
├── __init__.py           # 模块导出
├── date_utils.py         # 时间处理工具
├── prompt_builder.py     # Prompt 构建工具
├── logger.py            # 日志工具
├── DESIGN.md            # 详细设计文档
└── README.md            # 本文件
```

## 🚀 快速开始

### 安装依赖

```bash
pip install loguru
```

### 导入模块

```python
from erp_agent.utils import (
    # 时间工具
    get_current_date_info,
    calculate_date_range,
    
    # Prompt 构建
    PromptBuilder,
    
    # 日志工具
    setup_logger,
    get_logger
)
```

## 📚 功能模块

### 1. 时间处理工具 (date_utils.py)

提供准确的时间信息和时间表达式解析功能。

#### 主要函数

**get_current_date_info()**
- 获取当前日期、年份、季度等完整时间信息
- 返回字典包含：current_date, current_year, last_year 等

```python
date_info = get_current_date_info()
print(date_info['current_date'])  # 2026-01-25
print(date_info['current_year'])  # 2026
```

**calculate_date_range(time_expression, date_info=None)**
- 解析自然语言时间表达式为日期范围
- 支持："今年"、"去年3月"、"去年3月到今年5月"等

```python
start, end = calculate_date_range("去年3月到今年5月")
print(f"{start} 到 {end}")  # 2025-03-01 到 2026-05-31
```

**其他工具函数**
- `format_date_for_sql(date_str)` - 格式化日期为 SQL 标准格式
- `get_month_range(year, month)` - 获取月份日期范围
- `get_quarter_range(year, quarter)` - 获取季度日期范围
- `get_year_range(year)` - 获取年份日期范围

#### 测试

```bash
cd erp_agent/utils
python date_utils.py
```

### 2. Prompt 构建工具 (prompt_builder.py)

负责构建完整的 Prompt，支持动态参数注入和历史上下文管理。

#### 主要类

**PromptBuilder**

```python
from erp_agent.utils import PromptBuilder, get_current_date_info

# 初始化
builder = PromptBuilder()

# 获取时间信息
date_info = get_current_date_info()

# 构建 SQL 生成 Prompt
prompt = builder.build_sql_generation_prompt(
    user_question="今年新入职了多少人?",
    date_info=date_info,
    context=None,  # 可选：历史上下文
    error_feedback=None  # 可选：错误反馈
)

# 构建答案生成 Prompt
answer_prompt = builder.build_answer_generation_prompt(
    user_question="今年新入职了多少人?",
    sql_history=[
        {
            'sql': 'SELECT COUNT(*) FROM employees...',
            'result': {'success': True, 'data': [{'count': 15}]}
        }
    ]
)
```

#### 主要方法

- `load_schema()` - 加载数据库 Schema 说明
- `load_examples()` - 加载 Few-shot 示例
- `build_sql_generation_prompt()` - 构建 SQL 生成 Prompt
- `build_answer_generation_prompt()` - 构建答案生成 Prompt
- `format_date_context()` - 格式化时间上下文

#### 辅助函数

- `create_user_message(content)` - 创建用户消息对象
- `create_system_message(content)` - 创建系统消息对象
- `create_messages_for_api(system_prompt, user_question, history)` - 创建 API 消息列表

#### 测试

```bash
cd erp_agent/utils
python prompt_builder.py
```

### 3. 日志工具 (logger.py)

提供统一的日志记录接口，支持控制台和文件双输出。

#### 配置日志

```python
from erp_agent.utils import setup_logger

# 配置日志系统
setup_logger(
    log_level="INFO",           # 日志级别
    log_file="logs/agent.log",  # 日志文件路径
    rotation="10 MB",           # 日志轮转大小
    retention="7 days"          # 日志保留时间
)
```

#### 使用日志

```python
from erp_agent.utils import get_logger

# 获取日志记录器
logger = get_logger(__name__)

# 记录不同级别的日志
logger.debug("调试信息")
logger.info("普通信息")
logger.warning("警告信息")
logger.error("错误信息")
```

#### 专用日志函数

```python
from erp_agent.utils import (
    log_sql_execution,
    log_api_call,
    log_agent_iteration,
    log_error_with_context,
    log_performance
)

# 记录 SQL 执行
log_sql_execution(
    sql="SELECT * FROM employees",
    success=True,
    execution_time=0.05,
    row_count=10
)

# 记录 API 调用
log_api_call(
    api_name="kimi-k2",
    success=True,
    response_time=1.2,
    request_data={"prompt": "..."},
    response_data={"result": "..."}
)

# 记录 Agent 迭代
log_agent_iteration(
    iteration=1,
    user_question="有多少在职员工?",
    sql="SELECT COUNT(*) FROM employees WHERE leave_date IS NULL",
    result_summary="查询成功,返回1行数据",
    next_action="完成"
)
```

#### 功能特性

- ✅ 彩色控制台输出
- ✅ 自动日志文件轮转
- ✅ 敏感信息脱敏（API key 等）
- ✅ 异步写入提升性能
- ✅ 结构化日志格式

#### 测试

```bash
cd erp_agent/utils
python logger.py
# 查看生成的日志文件
cat logs/agent.log
```

## 📖 完整示例

### 示例 1：完整的 Prompt 构建流程

```python
from erp_agent.utils import (
    PromptBuilder,
    get_current_date_info,
    setup_logger,
    get_logger
)

# 1. 配置日志
setup_logger(log_level="INFO")
logger = get_logger(__name__)

# 2. 初始化 Prompt 构建器
builder = PromptBuilder()

# 3. 获取时间信息
date_info = get_current_date_info()
logger.info(f"当前日期: {date_info['current_date']}")

# 4. 构建 Prompt
prompt = builder.build_sql_generation_prompt(
    user_question="今年新入职了多少人?",
    date_info=date_info
)

logger.info(f"Prompt 长度: {len(prompt)} 字符")
```

### 示例 2：时间表达式解析

```python
from erp_agent.utils import calculate_date_range, get_current_date_info

date_info = get_current_date_info()

# 测试各种时间表达式
expressions = [
    "今年",
    "去年",
    "今年3月",
    "去年12月",
    "去年3月到今年5月",
    "第一季度",
    "去年第二季度"
]

for expr in expressions:
    start, end = calculate_date_range(expr, date_info)
    print(f"{expr}: {start} 到 {end}")
```

### 示例 3：日志系统集成

```python
from erp_agent.utils import (
    setup_logger,
    log_sql_execution,
    log_api_call,
    log_agent_iteration
)

# 配置日志
setup_logger()

# 模拟 Agent 执行流程
log_agent_iteration(
    iteration=1,
    user_question="有多少在职员工?",
    sql="SELECT COUNT(*) FROM employees WHERE leave_date IS NULL",
    result_summary="查询成功,返回1行数据",
    next_action="执行 SQL"
)

log_sql_execution(
    sql="SELECT COUNT(*) FROM employees WHERE leave_date IS NULL",
    success=True,
    execution_time=0.05,
    row_count=1
)

log_agent_iteration(
    iteration=2,
    user_question="有多少在职员工?",
    sql="",
    result_summary="根据查询结果得出答案: 88名在职员工",
    next_action="完成"
)
```

## 🧪 测试状态

| 模块 | 状态 | 测试命令 |
|------|------|----------|
| date_utils.py | ✅ 通过 | `python date_utils.py` |
| prompt_builder.py | ✅ 通过 | `python prompt_builder.py` |
| logger.py | ✅ 通过 | `python logger.py` |

## 📋 依赖要求

```txt
loguru==0.7.2
python-dateutil==2.8.2  # 可选，用于高级日期解析
```

## 🔧 开发说明

### 设计原则

1. **模块化**: 每个工具模块独立可测试
2. **易用性**: 提供简洁的 API 接口
3. **可扩展**: 支持自定义配置和扩展
4. **健壮性**: 完善的错误处理和边界情况处理

### 目录结构

- `DESIGN.md` - 详细的设计文档，包含所有函数签名和实现要点
- `README.md` - 本文件，快速入门指南
- 每个模块文件末尾都包含测试代码（`if __name__ == '__main__'`）

### 下一步开发

Utils 模块已完成，可以开始开发：
- ✅ config 模块（数据库配置、LLM 配置）
- ✅ core 模块（Agent、SQL 生成器、SQL 执行器等）

## 📝 更新日志

### 2026-01-25
- ✅ 创建 utils 模块
- ✅ 实现 date_utils.py（时间处理工具）
- ✅ 实现 logger.py（日志工具）
- ✅ 实现 prompt_builder.py（Prompt 构建工具）
- ✅ 完成所有模块测试
- ✅ 编写完整文档

## 📞 使用帮助

如有问题，请参考：
1. `DESIGN.md` - 详细的设计文档
2. 各模块文件中的测试代码
3. 本文档的完整示例

---

**Utils 模块开发完成！** 🎉
