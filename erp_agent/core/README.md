# ERP Agent Core 模块

## 概述

Core 模块是 ERP Agent 的核心实现，包含基于 ReAct (Reasoning + Acting) 范式的智能查询系统。

## 架构设计

### 模块组成

```
core/
├── agent.py           # Agent 主控制器（ReAct 循环）
├── sql_generator.py   # SQL 生成器（调用 Kimi API）
├── sql_executor.py    # SQL 执行器（执行查询）
└── __init__.py        # 模块导出
```

### 核心类

#### 1. ERPAgent - 主控制器

负责协调整个查询流程，实现 ReAct 范式的多轮迭代。

**主要方法**：
- `query(user_question)` - 执行查询（标准模式）
- `query_stream(user_question)` - 执行查询（流式模式）

**执行流程**：
```
用户问题 
  ↓
[循环开始] ← ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ┐
  ↓                                  │
1. Thought（思考）                    │
   分析当前情况，决定策略             │
  ↓                                  │
2. Action（行动）                     │
   - execute_sql: 执行 SQL 查询      │
   - answer: 给出最终答案            │
  ↓                                  │
3. Observation（观察）                │
   查看执行结果                       │
  ↓                                  │
判断是否完成？                        │
  - 是 → 返回答案                     │
  - 否 → 继续下一轮 ─ ─ ─ ─ ─ ─ ─ ─ ┘
```

#### 2. SQLGenerator - SQL 生成器

调用 Kimi API，将自然语言转换为 SQL 查询。

**特性**：
- 支持 ReAct 格式的 JSON 响应解析
- 自动注入时间上下文
- 错误反馈和重试
- 流式输出支持

**输出格式**：
```json
{
  "thought": "这是一个简单的统计问题...",
  "action": "execute_sql",
  "sql": "SELECT COUNT(*) FROM employees WHERE leave_date IS NULL;",
  "is_final": false
}
```

#### 3. SQLExecutor - SQL 执行器

安全地执行 SQL 查询并返回结果。

**安全特性**：
- SQL 安全验证（仅允许 SELECT）
- 查询超时控制
- 结果行数限制
- 完整的错误处理

## 使用示例

### 基础使用

```python
from erp_agent.core import ERPAgent
from erp_agent.config import get_llm_config, get_database_config

# 初始化配置
llm_config = get_llm_config()
db_config = get_database_config()

# 创建 Agent
agent = ERPAgent(llm_config, db_config)

# 执行查询
result = agent.query("公司有多少在职员工？")

print(f"答案: {result['answer']}")
print(f"迭代次数: {result['iterations']}")
print(f"总耗时: {result['total_time']:.2f}秒")
```

### 流式输出

```python
# 流式查询，实时获取执行过程
for chunk in agent.query_stream("每个部门分别有多少在职员工？"):
    chunk_type = chunk['type']
    
    if chunk_type == 'thought':
        print(f"💭 思考: {chunk['thought']}")
    
    elif chunk_type == 'sql_executing':
        print(f"📊 执行 SQL: {chunk['sql']}")
    
    elif chunk_type == 'sql_result':
        result = chunk['result']
        if result['success']:
            print(f"✓ 查询成功，{result['row_count']} 行")
    
    elif chunk_type == 'answer':
        print(f"💬 答案: {chunk['answer']}")
    
    elif chunk_type == 'final':
        print(f"完成！迭代 {chunk['iterations']} 次")
```

### 查看执行上下文

```python
result = agent.query("去年A部门的平均工资是多少？")

# 查看每一轮的执行详情
for i, ctx in enumerate(result['context'], 1):
    print(f"\n第 {i} 轮:")
    print(f"  思考: {ctx['thought']}")
    print(f"  动作: {ctx['action']}")
    
    if 'sql' in ctx:
        print(f"  SQL: {ctx['sql']}")
        print(f"  结果: {ctx['result']['row_count']} 行")
```

## ReAct 范式详解

### 什么是 ReAct？

ReAct (Reasoning + Acting) 是一种结合推理和行动的 AI Agent 范式：

1. **Reasoning（推理）**：思考当前情况，制定策略
2. **Acting（行动）**：执行具体操作（查询数据库）
3. **Observation（观察）**：查看操作结果
4. **Iteration（迭代）**：根据观察结果继续推理

### 为什么使用 ReAct？

- **鲁棒性**：SQL 错误时可以自动修正重试
- **复杂查询**：将复杂问题分解为多个简单查询
- **透明性**：每一步的思考过程都是可见的
- **灵活性**：可以根据中间结果调整查询策略

### ReAct 示例流程

**问题**: "从去年到今年涨薪幅度最大的10位员工是谁？"

**第 1 轮**:
```
Thought: 这个问题需要比较两个时期的工资。我先查询每个员工去年和今年的平均工资。
Action: execute_sql
SQL: 
  WITH salary_2025 AS (
    SELECT employee_id, AVG(salary_amount) as avg_2025
    FROM salaries
    WHERE EXTRACT(YEAR FROM payment_date) = 2025
    GROUP BY employee_id
  ),
  salary_2026 AS (
    SELECT employee_id, AVG(salary_amount) as avg_2026
    FROM salaries
    WHERE EXTRACT(YEAR FROM payment_date) = 2026
    GROUP BY employee_id
  )
  SELECT 
    e.employee_name,
    s25.avg_2025,
    s26.avg_2026,
    (s26.avg_2026 - s25.avg_2025) / s25.avg_2025 * 100 as increase_pct
  FROM employees e
  JOIN salary_2025 s25 ON e.employee_id = s25.employee_id
  JOIN salary_2026 s26 ON e.employee_id = s26.employee_id
  ORDER BY increase_pct DESC
  LIMIT 10;
```

**第 2 轮**:
```
Thought: 查询成功，我已经获得了涨薪幅度最大的10位员工。可以给出最终答案了。
Action: answer
Answer: 从去年到今年涨薪幅度最大的10位员工是：...
```

## 配置说明

### LLM 配置

```python
from erp_agent.config import LLMConfig

config = LLMConfig(
    api_key="your-api-key",
    model="kimi-k2",
    temperature=0.1,           # SQL 生成使用低温度
    max_tokens=2048,
    timeout=60
)
```

### 数据库配置

```python
from erp_agent.config import DatabaseConfig

config = DatabaseConfig(
    host="localhost",
    port=5432,
    database="erp_agent_db",
    user="erp_user",
    password="password",
    timeout=30,                # SQL 执行超时
    max_rows=1000              # 最大返回行数
)
```

### Agent 配置

```python
from erp_agent.config import AgentConfig

config = AgentConfig(
    max_iterations=5,          # 最大迭代次数
    enable_retry=True,         # 启用错误重试
    enable_multi_query=True,   # 启用多步查询
    log_level="INFO"
)
```

## 日志记录

Agent 会自动记录详细的执行日志：

```
2026-01-25 10:30:15 | INFO     | agent:query:123 | 开始处理问题: 公司有多少在职员工？
2026-01-25 10:30:15 | INFO     | agent:query:128 | ===== 第 1 轮迭代 =====
2026-01-25 10:30:16 | INFO     | sql_executor:execute:78 | SQL执行成功 | 耗时: 0.051s | 行数: 1 | SQL: SELECT COUNT(*) FROM ...
2026-01-25 10:30:17 | INFO     | agent:query:189 | 最终答案: 公司目前有 88 名在职员工。
2026-01-25 10:30:17 | INFO     | agent:query:256 | 查询完成 - 成功: True, 迭代: 2次, 耗时: 2.15秒
```

日志文件默认保存在 `logs/agent.log`。

## 错误处理

### SQL 执行错误

当 SQL 执行失败时，Agent 会自动：
1. 将错误信息传递给 LLM
2. LLM 分析错误原因
3. 生成修正后的 SQL
4. 重新执行

示例：
```
第 1 轮: SELECT * FROM employee;  # 表名错误
  错误: relation "employee" does not exist

第 2 轮: SELECT * FROM employees;  # 修正后的表名
  成功!
```

### 达到最大迭代次数

如果达到最大迭代次数仍未完成：
1. 检查是否有成功的查询结果
2. 如果有，基于这些结果生成答案
3. 如果没有，返回错误信息

### API 调用失败

SQLGenerator 内置重试机制：
- 默认重试 3 次
- 重试间隔 2 秒
- 超时时间 60 秒

## 性能优化

### 提示

1. **SQL 优化**：LLM 生成的 SQL 应该高效
2. **结果限制**：设置合理的 max_rows
3. **超时控制**：避免长时间查询
4. **日志级别**：生产环境使用 INFO 或 WARNING

### 监控指标

```python
result = agent.query(question)

# 查看性能指标
print(f"迭代次数: {result['iterations']}")
print(f"总耗时: {result['total_time']:.2f}秒")

for ctx in result['context']:
    if 'result' in ctx:
        exec_time = ctx['result']['execution_time']
        print(f"SQL执行时间: {exec_time:.3f}秒")
```

## 扩展开发

### 自定义 Prompt

```python
from erp_agent.utils.prompt_builder import PromptBuilder

# 使用自定义 prompts 目录
prompt_builder = PromptBuilder(prompts_dir="/path/to/custom/prompts")

# 创建 Agent
agent = ERPAgent(llm_config, db_config, prompt_builder=prompt_builder)
```

### 添加结果分析器

未来可以添加 `result_analyzer.py` 来：
- 验证结果合理性
- 检测异常数据
- 提供数据洞察

```python
class ResultAnalyzer:
    def analyze(self, result):
        # 分析结果
        # 返回洞察
        pass
```

## 测试

运行 core 模块测试：

```bash
# 测试 SQL 执行器
python -m erp_agent.core.sql_executor

# 测试 SQL 生成器（需要配置 API）
python -m erp_agent.core.sql_generator

# 测试完整 Agent（需要配置 API 和数据库）
python -m erp_agent.core.agent
```

## 常见问题

### Q: Agent 一直循环无法停止？

A: 检查：
1. `max_iterations` 设置是否合理
2. LLM 是否正确输出 `is_final: true`
3. Prompt 中的指令是否清晰

### Q: SQL 生成不准确？

A: 改进方法：
1. 优化 `prompts/system_prompt.txt`
2. 添加更多 `prompts/examples.txt`
3. 调整 LLM 的 `temperature` 参数

### Q: 如何查看详细的推理过程？

A: 使用流式输出：
```python
for chunk in agent.query_stream(question):
    print(chunk)
```

## 更新日志

### v0.1.0 (2026-01-25)

- ✅ 实现 ERPAgent 主控制器
- ✅ 实现 SQLGenerator（支持 ReAct 范式）
- ✅ 实现 SQLExecutor（安全执行）
- ✅ 支持流式输出
- ✅ 完整的错误处理和重试
- ✅ 详细的日志记录

## 相关文档

- [配置模块文档](../config/README.md)
- [工具模块文档](../utils/README.md)
- [开发指南](../../agent_development.md)
- [API 接口文档](../config/API_INTERFACE.md)
