# ERP Agent - 智能数据查询助手

基于 Kimi-K2 大语言模型的 ERP 数据库智能查询系统，可以将用户的自然语言问题转换为精确的 SQL 查询并返回友好的答案。

## 📋 项目概述

本项目实现了一个基于 **ReAct (Reasoning + Acting)** 范式的智能 Agent，能够：

- ✅ 理解用户用自然语言表达的数据查询需求
- ✅ 自动生成准确的 PostgreSQL SQL 查询语句
- ✅ 执行查询并分析结果
- ✅ 将查询结果转换为自然语言答案
- ✅ 支持复杂的时间表达式（如"今年"、"去年"、"最近三个月"）
- ✅ 自动错误修正和多轮查询
- ✅ 支持流式输出，实时展示推理过程

**项目状态**: ✅ Core 模块开发完成，可以开始测试使用！

## 🏗 系统架构

```
用户接口层 (CLI/Web)
    ↓
Agent 核心层
    ├── Agent Controller (主控制器)
    ├── SQL Generator (SQL生成模块)
    ├── SQL Executor (SQL执行模块)
    └── Result Analyzer (结果分析模块)
    ↓
工具层
    ├── Date Utils (时间处理)
    ├── Kimi-K2 API (LLM调用)
    └── PostgreSQL (数据库)
```

## 📦 项目结构

```
erp_agent/
├── config/                 # 配置模块
│   ├── __init__.py
│   ├── database.py        # 数据库配置
│   └── llm.py             # Kimi API 配置
├── core/                  # 核心模块
│   ├── __init__.py
│   ├── agent.py           # Agent 主控制器
│   ├── sql_generator.py   # SQL 生成模块
│   ├── sql_executor.py    # SQL 执行模块
│   └── result_analyzer.py # 结果分析模块
├── utils/                 # 工具模块
│   ├── __init__.py
│   ├── date_utils.py      # 时间处理工具
│   ├── prompt_builder.py  # Prompt 构建工具
│   └── logger.py          # 日志工具
├── prompts/               # Prompt 模板
│   ├── schema.txt         # 数据库 Schema 说明
│   ├── examples.txt       # Few-shot 示例
│   └── system_prompt.txt  # 系统 Prompt
├── tests/                 # 测试模块
│   ├── __init__.py
│   ├── test_questions.py  # 10个测试问题
│   └── test_agent.py      # 单元测试
├── main.py                # 主入口
├── .env.example           # 环境变量示例
└── README.md              # 项目说明
```

## 🚀 快速开始

### 1. 环境准备

**系统要求**:
- Python 3.9+
- PostgreSQL 14+

**安装依赖**:

```bash
pip install -r requirements.txt
```

### 2. 数据库设置

按照 `../database/setup_database.ps1` 脚本初始化数据库：

```bash
# 在 PowerShell 中运行
cd ../database
.\setup_database.ps1
```

或手动执行：

```bash
# 1. 初始化数据库结构
psql -U postgres -f init_database.sql

# 2. 连接到数据库
psql -U postgres -d erp_agent_db

# 3. 生成测试数据
python generate_test_data.py
```

### 3. 配置环境变量

复制 `.env.example` 为 `.env` 并填写配置：

```bash
cp .env.example .env
```

编辑 `.env` 文件，填写必需的配置：

```bash
# Kimi API 配置（从 https://platform.moonshot.cn/ 获取）
MOONSHOT_API_KEY=your_api_key_here
MOONSHOT_BASE_URL=https://api.moonshot.cn/v1
MOONSHOT_MODEL=kimi-k2

# 数据库连接信息
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_agent_db
DB_USER=erp_agent_user
DB_PASSWORD=your_password

# Agent 配置（可选）
MAX_ITERATIONS=5
LOG_LEVEL=INFO
LOG_FILE=logs/agent.log
```

### 4. 运行测试

```bash
# 查看10个测试问题
python tests/test_questions.py

# 运行单元测试
python tests/test_agent.py
```

### 5. 运行 Agent

```bash
python main.py
```

## 🎯 功能特性

### 支持的查询类型

1. **简单统计查询**
   - "有多少在职员工？"
   - "公司有多少个部门？"

2. **部门分析查询**
   - "每个部门有多少人？"
   - "A部门的平均工资是多少？"

3. **时间范围查询**
   - "今年新入职了多少人？"
   - "从去年到今年涨薪幅度最大的员工是谁？"

4. **排名查询**
   - "工资最高的前10名员工是谁？"
   - "职级最高的员工有哪些？"

5. **复杂分析查询**
   - "有没有出现过拖欠工资的情况？"
   - "平均每个员工在公司在职多久？"

### 核心能力

- ✅ **ReAct 范式**: 完整实现思考-行动-观察循环
- ✅ **智能时间解析**: 自动理解"今年"、"去年"等相对时间表达
- ✅ **Few-shot 学习**: 通过示例提高 SQL 生成准确率
- ✅ **错误自动修正**: 发现错误后自动重试并修正
- ✅ **多轮迭代**: 复杂问题自动拆解为多个查询步骤
- ✅ **流式输出**: 实时查看 Agent 的推理和执行过程
- ✅ **安全检查**: 仅允许 SELECT 查询，防止数据修改
- ✅ **完整日志**: 详细记录所有执行过程

## 📊 10个测试问题

1. 平均每个员工在公司在职多久？
2. 公司目前有多少在职员工？
3. 每个部门分别有多少在职员工？
4. 每个部门今年和去年各新入职了多少人？
5. 在职员工中职级最高的5位员工是谁？
6. 工资最高的前10名在职员工是谁？
7. 去年A部门的平均工资是多少？
8. 从前年3月到去年5月，A部门的平均工资是多少？
9. 从去年到今年涨薪幅度最大的10位员工是谁？
10. 有没有出现过拖欠员工工资的情况？

## 🔧 开发指南

### 开发流程

1. **Phase 1**: 基础框架（数据库连接、时间工具、API调用）
2. **Phase 2**: SQL 生成模块（Prompt 工程、Few-shot 示例）
3. **Phase 3**: 循环和分析模块（结果分析、错误重试）
4. **Phase 4**: 复杂查询和优化（多步查询、性能优化）
5. **Phase 5**: 完善和交付（日志、文档、演示）

### 技术栈

- **编程语言**: Python 3.9+
- **LLM**: Kimi-K2 (Moonshot AI)
- **数据库**: PostgreSQL 14+
- **核心库**:
  - `psycopg2` - PostgreSQL 连接
  - `requests` - HTTP API 调用
  - `python-dotenv` - 环境变量管理
  - `pydantic` - 数据验证
  - `loguru` - 日志记录

## 🔐 安全考虑

1. **SQL 注入防护**: 白名单检查，仅允许 SELECT 语句
2. **权限最小化**: 数据库用户仅有 SELECT 权限
3. **查询超时**: 30秒超时限制
4. **结果限制**: 最多返回1000行数据
5. **API Key 保护**: 使用环境变量，不硬编码

## 📝 API 调用示例

### Python API

```python
from erp_agent.core import ERPAgent
from erp_agent.config import get_llm_config, get_database_config

# 初始化 Agent（使用环境变量配置）
llm_config = get_llm_config()
db_config = get_database_config()
agent = ERPAgent(llm_config, db_config)

# 标准查询
result = agent.query("有多少在职员工？")
print(result['answer'])
print(f"迭代次数: {result['iterations']}")

# 流式查询（实时查看推理过程）
for chunk in agent.query_stream("每个部门分别有多少在职员工？"):
    if chunk['type'] == 'thought':
        print(f"💭 思考: {chunk['thought']}")
    elif chunk['type'] == 'sql_executing':
        print(f"📊 执行 SQL: {chunk['sql']}")
    elif chunk['type'] == 'answer':
        print(f"💬 答案: {chunk['answer']}")
```

### CLI 使用

```bash
# 运行交互式界面
python -m erp_agent.main

# 或
cd erp_agent
python main.py

# 交互命令
> 有多少在职员工？          # 直接提问
> help                       # 查看帮助
> test                       # 运行 10 个测试问题
> stream                     # 切换流式/标准输出模式
> exit                       # 退出

# 示例输出（标准模式）
> 有多少在职员工？
正在处理您的问题...

============================================================
✓ 答案: 公司目前有 88 名在职员工。
   迭代次数: 2, 总耗时: 3.45秒
============================================================

# 示例输出（流式模式）
> stream
已切换到 流式模式

> 每个部门分别有多少在职员工？
正在处理您的问题...

[第 1 轮]
💭 思考: 这是一个按部门分组统计在职员工数量的查询...
⚙️ 动作: execute_sql
📊 执行 SQL: SELECT department_name, COUNT(*) as count...
✓ 查询成功，返回 5 行

[第 2 轮]
💭 思考: 查询结果已获取，可以生成最终答案
💬 动作: answer

💬 答案: 各部门的在职员工数量如下：A部门 18人，B部门 17人...

============================================================
✓ 查询完成
   最终答案: 各部门的在职员工数量如下...
   迭代次数: 2, 总耗时: 4.23秒
============================================================
```

## 🐛 故障排除

### 常见问题

**Q: 连接数据库失败**
- 检查 PostgreSQL 是否运行
- 检查 `.env` 中的数据库配置
- 确认防火墙允许 5432 端口

**Q: Kimi API 调用失败**
- 检查 API Key 是否正确
- 检查网络连接
- 查看 API 调用配额

**Q: SQL 生成不准确**
- 检查 prompts/schema.txt 是否完整
- 增加相关的 Few-shot 示例
- 检查时间上下文是否正确传递

## 📚 参考文档

- [Core 模块文档](core/README.md) - 详细的 Core 模块使用说明
- [Core 模块示例](core/example.py) - 可运行的示例代码
- [配置模块文档](config/README.md) - 配置管理说明
- [API 接口文档](config/API_INTERFACE.md) - 完整的 API 接口文档
- [开发总结](../CORE_MODULE_COMPLETE.md) - Core 模块开发完成总结
- [Agent 开发指南](../agent_development.md) - 完整的开发指南
- [Kimi API 文档](https://platform.moonshot.cn/docs) - Moonshot AI API
- [PostgreSQL 文档](https://www.postgresql.org/docs/) - 数据库文档

## 📄 许可证

本项目仅用于学习和研究目的。

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

## 🎉 完成状态

### ✅ 已完成的模块

- [x] **Config 模块**: 数据库和 LLM 配置管理
- [x] **Utils 模块**: 时间处理、日志、Prompt 构建
- [x] **Prompts 模块**: 系统 Prompt、Few-shot 示例、Schema
- [x] **Core 模块**: Agent 主控制器、SQL 生成器、SQL 执行器
- [x] **主程序**: 交互式 CLI 界面
- [x] **文档**: 完整的使用文档和示例

### 🚀 可以开始使用！

Core 模块已完成开发，系统已就绪，可以：
1. 运行 10 个测试问题验证功能
2. 通过 CLI 交互式查询
3. 通过 Python API 集成到其他系统
4. 查看流式输出观察 Agent 推理过程

---

**开发状态**: ✅ Core 模块开发完成  
**版本**: v0.1.0  
**最后更新**: 2026-01-25
