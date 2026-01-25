# ERP Agent - 智能数据查询助手

基于 Kimi-K2 大语言模型的 ERP 数据库智能查询系统，可以将用户的自然语言问题转换为精确的 SQL 查询并返回友好的答案。

## 📋 项目概述

本项目实现了一个智能 Agent，能够：

- 理解用户用自然语言表达的数据查询需求
- 自动生成准确的 PostgreSQL SQL 查询语句
- 执行查询并分析结果
- 将查询结果转换为自然语言答案
- 支持复杂的时间表达式（如"今年"、"去年"、"最近三个月"）
- 自动错误修正和多轮查询

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

编辑 `.env` 文件，填写：
- Kimi API Key（从 https://platform.moonshot.cn/ 获取）
- 数据库连接信息

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

- ✅ **智能时间解析**: 自动理解"今年"、"去年"等相对时间表达
- ✅ **Few-shot 学习**: 通过示例提高 SQL 生成准确率
- ✅ **错误自动修正**: 发现错误后自动重试并修正
- ✅ **多轮查询**: 复杂问题自动拆解为多个查询步骤
- ✅ **安全检查**: 仅允许 SELECT 查询，防止数据修改
- ✅ **结果验证**: 自动检查查询结果的合理性

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
from core.agent import ERPAgent

# 初始化 Agent
config = {
    'kimi_api_key': 'your_api_key',
    'db_config': {
        'host': 'localhost',
        'database': 'erp_agent_db',
        'user': 'erp_agent_user',
        'password': 'erp_agent_2026'
    }
}

agent = ERPAgent(config)

# 查询
result = agent.query("有多少在职员工？")
print(result['answer'])
```

### CLI 使用

```bash
python main.py

> 请输入您的问题: 有多少在职员工？
正在分析问题...
正在生成 SQL...
正在执行查询...

答案: 公司目前有 88 名在职员工。
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

- [Kimi API 文档](https://platform.moonshot.cn/docs)
- [PostgreSQL 文档](https://www.postgresql.org/docs/)
- [Agent 开发指南](../agent_development.md)
- [数据库设置说明](../database/README.md)

## 📄 许可证

本项目仅用于学习和研究目的。

## 👥 贡献

欢迎提交 Issue 和 Pull Request！

---

**开发状态**: 准备就绪 ✅  
**最后更新**: 2026-01-25
