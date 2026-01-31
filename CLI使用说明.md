# ERP Agent Main 模块使用说明

## 概述

`erp_agent/main.py` 是 ERP Agent 的主入口程序，提供命令行交互界面，可以接收自然语言查询，通过 Agent 转化为 SQL 查询并返回结果。

## 修复内容

已对 `main.py` 进行以下修复：

1. **修复了路径设置**：添加了工作目录设置，确保从任何位置运行都能正确加载资源
2. **改进了环境变量加载**：支持多个可能的 .env 文件位置
3. **修复了导入路径**：确保所有模块导入使用正确的包路径
4. **增强了错误处理**：添加详细的 traceback 和错误提示

## 运行方式

### 1. 从命令行运行

在项目根目录下运行：

```bash
# Windows PowerShell
cd C:\Users\86159\Desktop\erp_agent
python erp_agent/main.py

# 或者直接运行
python -m erp_agent.main
```

### 2. 作为 Python 模块运行

```bash
cd C:\Users\86159\Desktop\erp_agent
python -m erp_agent.main
```

## 功能说明

### 1. 自动检查

程序启动时会自动执行以下检查：

- ✓ 加载环境变量（从 .env 文件）
- ✓ 检查必需的环境变量是否配置完整
- ✓ 测试数据库连接
- ✓ 初始化 ERP Agent

### 2. 交互模式

进入交互模式后，可以：

- **输入自然语言问题**：直接输入您的问题，Agent 会自动生成 SQL 并返回答案
- **使用特殊命令**：
  - `help` - 显示帮助信息
  - `test` - 运行10个测试问题
  - `stream` - 切换流式/标准输出模式
  - `exit` / `quit` / `q` - 退出程序

### 3. Agent 运行流程

Agent 的运行过程遵循 ReAct 范式，与 `test_agent.py` 中的测试流程一致：

```
用户输入问题
    ↓
Agent 初始化
    ↓
[迭代循环开始]
    ↓
1. Thought（思考）：分析当前情况，决定下一步策略
    ↓
2. Action（行动）：
   - 执行 SQL 查询 (execute_sql)
   - 或给出最终答案 (answer)
    ↓
3. Observation（观察）：
   - SQL 执行成功 → 使用 ResultAnalyzer 分析结果
     - 信息充分 → 生成最终答案并退出
     - 信息不足 → 继续下一轮迭代
   - SQL 执行失败 → 记录错误，继续下一轮迭代
    ↓
[迭代循环结束或达到最大次数]
    ↓
返回最终结果
```

### 4. 核心组件

Agent 内部使用以下核心组件（与项目架构一致）：

- **SQLGenerator**：根据用户问题生成 SQL 查询
- **SQLExecutor**：安全执行 SQL 查询
- **SQLValidator**：验证 SQL 语法和安全性
- **ResultAnalyzer**：智能分析查询结果，判断是否充分
- **PromptBuilder**：构建系统 Prompt 和上下文

## 示例对话

```
> 请输入您的问题: 有多少在职员工？

正在处理您的问题...

============================================================
✓ 答案: 公司目前有 89 名在职员工。
   迭代次数: 2, 总耗时: 3.45秒
============================================================

> 请输入您的问题: 每个部门有多少人？

正在处理您的问题...

============================================================
✓ 答案: 各部门在职员工人数如下：
   • A部门：22人
   • B部门：20人
   • C部门：18人
   • D部门：16人
   • E部门：13人
   迭代次数: 1, 总耗时: 2.87秒
============================================================
```

## 流式输出模式

输入 `stream` 命令后，可以实时查看 Agent 的推理过程：

```
> stream
已切换到 流式模式

> 请输入您的问题: 工资最高的前10名员工是谁？

正在处理您的问题...

[第 1 轮]
💭 思考: 需要查询 salaries 表获取最新工资数据，按工资降序排列，取前10名
⚙️ 动作: execute_sql
📊 执行 SQL: SELECT e.employee_id, e.name, d.department_name, s.salary...
✓ 查询成功，返回 10 行

💬 答案: 工资最高的前10名员工是：
   1. 张三（A部门）- 85,000元
   2. 李四（B部门）- 82,000元
   ...

============================================================
✓ 查询完成
   最终答案: [详细答案]
   迭代次数: 1, 总耗时: 3.21秒
============================================================
```

## 环境变量配置

确保 `.env` 文件包含以下配置：

```env
# Kimi API 配置
MOONSHOT_API_KEY=your_kimi_api_key_here
MOONSHOT_MODEL=kimi-k2

# 数据库配置
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_agent_db
DB_USER=erp_agent_user
DB_PASSWORD=erp_agent_2026

# Agent 配置
MAX_ITERATIONS=5
SQL_TIMEOUT=30
MAX_RESULT_ROWS=1000

# 日志配置
LOG_LEVEL=INFO
LOG_FILE=logs/agent.log
```

## 支持的查询类型

- **简单统计**："有多少在职员工？"
- **部门分析**："每个部门有多少人？"
- **时间查询**："今年新入职了多少人？"
- **排名查询**："工资最高的前10名员工是谁？"
- **复杂分析**："有没有拖欠工资的情况？"

## 故障排查

### 问题1：找不到 .env 文件

**解决方案**：
```bash
# 复制 env.example 为 .env
cd C:\Users\86159\Desktop\erp_agent\erp_agent
copy env.example .env
# 然后编辑 .env 文件，填写实际配置
```

### 问题2：数据库连接失败

**解决方案**：
1. 检查 PostgreSQL 服务是否启动
2. 验证 .env 中的数据库配置是否正确
3. 确保数据库已经初始化（运行 `database/setup_database.ps1`）

### 问题3：导入模块失败

**解决方案**：
1. 确保从项目根目录运行
2. 检查 Python 路径是否正确：
   ```bash
   python -c "import sys; print(sys.path)"
   ```

### 问题4：API 调用失败

**解决方案**：
1. 检查 MOONSHOT_API_KEY 是否正确
2. 验证网络连接
3. 确认 API 配额是否充足

## 与测试模块的关系

`main.py` 的 Agent 运行流程与 `erp_agent/tests/test_agent.py` 中的测试流程完全一致：

- 两者都使用相同的 `ERPAgent` 类
- 两者都从环境变量加载相同的配置
- 两者都执行相同的查询流程（ReAct 范式）
- `test_agent.py` 中的测试问题可以在 `main.py` 中通过 `test` 命令运行

## 架构符合性

修复后的 `main.py` 完全符合项目的现有架构设计：

1. **分层架构**：
   - 表示层：`main.py` 提供命令行交互界面
   - 业务层：`ERPAgent` 协调各个组件
   - 数据层：`SQLExecutor` 执行数据库查询

2. **模块化设计**：
   - 配置管理：`config/` 模块
   - 核心逻辑：`core/` 模块
   - 工具函数：`utils/` 模块

3. **设计模式**：
   - 使用工厂模式创建配置对象
   - 使用策略模式处理不同类型的查询
   - 使用观察者模式实现流式输出

## 日志记录

程序运行时会自动记录详细日志到 `logs/agent.log`：

- Agent 的每一轮迭代
- SQL 生成和执行过程
- 错误信息和堆栈跟踪
- 性能指标（耗时、迭代次数等）

可以通过设置 `LOG_LEVEL` 环境变量调整日志级别：
- `DEBUG`：最详细，包含所有调试信息
- `INFO`：标准信息（默认）
- `WARNING`：仅警告和错误
- `ERROR`：仅错误信息

## 总结

修复后的 `main.py` 现在可以：

✅ 正确读取自然语言问题  
✅ 通过 Agent 转化为 SQL 查询  
✅ 执行 SQL 并返回结果  
✅ 运行流程与 `test_agent.py` 一致  
✅ 完全符合现有架构设计  

享受使用 ERP Agent！
