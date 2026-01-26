# ERP Agent 测试指南

## 快速开始

### 1. 环境准备

确保已经安装所有依赖：
```bash
pip install -r requirements.txt
```

确保 `.env` 文件已配置：
```
MOONSHOT_API_KEY=sk-xxxxx
DB_HOST=localhost
DB_PORT=5432
DB_NAME=erp_agent_db
DB_USER=erp_user
DB_PASSWORD=your_password
```

### 2. 运行测试

#### 选项A：交互式运行（推荐）

```bash
cd erp_agent/tests
python test_agent.py
```

会显示菜单：
```
请选择测试模式:
  1. 运行单元测试（快速，不需要API）
  2. 运行10个测试问题（需要API和数据库）
  3. 运行所有测试
  0. 退出
```

#### 选项B：命令行运行

```bash
# 仅运行单元测试（不需要API，快速）
python erp_agent/tests/test_agent.py unit

# 仅运行10个问题测试（需要API和数据库）
python erp_agent/tests/test_agent.py questions

# 运行所有测试
python erp_agent/tests/test_agent.py all
```

### 3. 查看测试结果

#### 单元测试结果示例：
```
======================================================================
运行单元测试套件
======================================================================
test_calculate_date_offset (test_agent.TestDateUtils) ... ok
test_format_date_for_sql (test_agent.TestDateUtils) ... ok
test_get_current_datetime (test_agent.TestDateUtils) ... ok
...

----------------------------------------------------------------------
Ran 35 tests in 2.456s

OK (skipped=1)

======================================================================
测试统计:
  总测试数: 35
  成功: 34
  失败: 0
  错误: 0
  跳过: 1
======================================================================
```

#### 问题测试结果示例：
```
======================================================================
问题 1/10: 平均每个员工在公司在职多久？
======================================================================

✓ 成功
答案: 根据查询结果，在职员工平均在公司工作约 4.5 年。
迭代次数: 2
耗时: 3.45秒

...

======================================================================
测试问题总结
======================================================================
总问题数: 10
成功: 8
失败: 2
成功率: 80.0%
```

## 测试内容说明

### 单元测试涵盖：

1. **时间工具测试** - 测试所有日期计算功能
2. **配置测试** - 测试数据库、LLM、Agent配置
3. **SQL执行器测试** - 测试SQL验证和执行
4. **Prompt构建器测试** - 测试Prompt构建功能
5. **日志系统测试** - 测试日志记录功能
6. **集成测试** - 测试实际的数据库连接和API调用

### 10个问题测试：

| ID | 问题 | 难度 | 类型 |
|----|------|------|------|
| 1 | 平均每个员工在公司在职多久？ | 中等 | 统计分析 |
| 2 | 公司目前有多少在职员工？ | 简单 | 简单统计 |
| 3 | 每个部门分别有多少在职员工？ | 简单 | 分组统计 |
| 4 | 每个部门今年和去年各新入职了多少人？ | 中等 | 时间分析 |
| 5 | 在职员工中职级最高的5位员工是谁？ | 简单 | 排序查询 |
| 6 | 工资最高的前10名在职员工是谁？ | 简单 | 排序查询 |
| 7 | 去年A部门的平均工资是多少？ | 中等 | 时间分析 |
| 8 | 从前年3月到去年5月，A部门的平均工资是多少？ | 困难 | 时间分析 |
| 9 | 从去年到今年涨薪幅度最大的10位员工是谁？ | 困难 | 复杂分析 |
| 10 | 有没有出现过拖欠员工工资的情况？如果有，是哪些员工？ | 困难 | 复杂分析 |

## 常见问题

### Q1: 单元测试跳过了某些测试？

**A:** 这是正常的。某些集成测试需要数据库连接和API密钥。如果环境变量未配置，这些测试会被跳过而不是失败。

### Q2: 问题测试失败了怎么办？

**A:** 检查以下几点：
1. 数据库中是否有足够的测试数据
2. API配额是否用完
3. 网络连接是否正常
4. 查看具体的错误信息以定位问题

### Q3: 测试运行很慢？

**A:** 
- 单元测试应该在几秒内完成
- 问题测试需要调用API，每个问题可能需要2-5秒
- 10个问题总共大约需要30-50秒

### Q4: 如何只测试特定的组件？

**A:** 使用 unittest 命令：
```bash
# 测试特定类
python -m unittest erp_agent.tests.test_agent.TestDateUtils

# 测试特定方法
python -m unittest erp_agent.tests.test_agent.TestDateUtils.test_get_current_datetime
```

### Q5: 如何查看更详细的测试输出？

**A:** 测试输出已经很详细。如果需要调试，可以：
1. 查看日志文件 `logs/test_agent.log`
2. 在测试代码中添加 `print()` 语句
3. 使用 Python 调试器 `pdb`

## 测试覆盖的组件

### ✅ Config模块
- [x] DatabaseConfig - 数据库配置
- [x] LLMConfig - LLM配置
- [x] AgentConfig - Agent配置

### ✅ Core模块
- [x] ERPAgent - 主控制器
- [x] SQLGenerator - SQL生成器
- [x] SQLExecutor - SQL执行器

### ✅ Utils模块
- [x] date_utils - 时间工具（8个函数）
- [x] logger - 日志工具
- [x] prompt_builder - Prompt构建器

### ✅ Tests模块
- [x] test_questions - 10个测试问题

## 下一步

测试通过后，你可以：

1. **运行主程序**
   ```bash
   python erp_agent/main.py
   ```

2. **查看使用示例**
   ```bash
   python erp_agent/core/example.py
   ```

3. **开始使用Agent**
   ```python
   from erp_agent.core import ERPAgent
   from erp_agent.config import get_llm_config, get_database_config
   
   agent = ERPAgent(get_llm_config(), get_database_config())
   result = agent.query("你的问题")
   print(result['answer'])
   ```

## 报告问题

如果遇到问题，请提供：
1. 完整的错误输出
2. Python版本和操作系统
3. 是否完成了环境配置
4. 具体的复现步骤

祝测试顺利！🎉
