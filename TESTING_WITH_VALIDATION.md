# ERP Agent 测试验证指南

## 📋 概述

本文档介绍如何使用增强的测试模块和结果分析功能来验证 ERP Agent 的性能。

## 🆕 新增功能

### 1. 增强的测试问题模块 (`erp_agent/tests/test_questions.py`)

**功能：**
- 包含10个测试问题及其标准答案
- 每个问题都有详细的验证规则
- 支持多种验证类型：数值范围、表格数据、排名、比较等

**示例：**
```python
from erp_agent.tests.test_questions import TEST_QUESTIONS, validate_result

# 获取问题
question = TEST_QUESTIONS[0]  # 问题1
print(question['question'])
print(question['validation'])

# 验证结果
sql_result = {
    'success': True,
    'data': [{'avg_days': 1104.15, 'avg_years': 3.02}],
    'row_count': 1
}

passed, message, details = validate_result(1, sql_result)
print(f"验证结果: {passed}")
print(f"消息: {message}")
```

### 2. 结果分析模块 (`erp_agent/core/result_analyzer.py`)

**功能：**
- 分析SQL查询结果的完整性
- 判断是否需要继续查询
- 生成自然语言答案建议
- 检测数据异常

**示例：**
```python
from erp_agent.core import ResultAnalyzer

analyzer = ResultAnalyzer()

# 分析查询结果
analysis = analyzer.analyze_result(sql_result, user_question)
print(f"是否足够: {analysis['is_sufficient']}")
print(f"完整性: {analysis['completeness']}")

# 生成答案建议
suggestion = analyzer.generate_answer_suggestion(sql_result, user_question)
print(suggestion)
```

### 3. Agent 集成

结果分析模块已经集成到 `ERPAgent` 中，**无需修改调用代码**：

```python
from erp_agent.core import ERPAgent
from erp_agent.config import get_llm_config, get_database_config

llm_config = get_llm_config()
db_config = get_database_config()

agent = ERPAgent(llm_config, db_config)

# 正常使用，结果分析在后台自动进行
result = agent.query("公司有多少在职员工？")
print(result['answer'])
```

## 🧪 运行测试

### 方式1：使用验证测试运行器（推荐）

```bash
python run_validated_tests.py
```

**特点：**
- 运行所有10个测试问题
- 自动验证结果是否符合标准答案
- 显示详细的验证报告
- 统计成功率和验证通过率

**输出示例：**
```
问题 1: 平均每个员工在公司在职多久？
---------------------------------------------------------------------
✓ 查询成功
  答案: 平均每个员工在公司在职 1104.15 天，约 3.02 年。
  迭代次数: 2, 耗时: 3.45秒
  ✓ 验证通过: 验证通过

测试总结
======================================================================
总问题数: 10
查询成功: 9 (90.0%)
验证通过: 8 (80.0%)
```

### 方式2：使用原有测试框架

```bash
python run_tests.py
```

或运行单元测试：

```bash
cd erp_agent
python -m pytest tests/
```

### 方式3：交互式测试

```bash
python erp_agent/main.py

> 平均每个员工在公司在职多久？
> test  # 运行所有测试问题
```

## 📊 验证规则说明

### 1. 数值范围验证 (`numeric_range`)

验证返回的数值是否在期望范围内（支持容差）。

**示例：问题1**
```python
'validation': {
    'type': 'numeric_range',
    'expected': {
        'avg_days': 1104.15,
        'avg_years': 3.02
    },
    'tolerance': 0.1,  # 10%容差
    'row_count': 1
}
```

### 2. 表格数据验证 (`table_data`)

验证返回的表格数据是否匹配预期。

**示例：问题2**
```python
'validation': {
    'type': 'table_data',
    'expected_rows': 5,
    'expected_data': {
        'A部门': 22,
        'B部门': 20,
        'C部门': 18,
        'D部门': 16,
        'E部门': 13
    }
}
```

### 3. 排名验证 (`top_n`)

验证Top N结果的正确性。

**示例：问题9**
```python
'validation': {
    'type': 'top_n',
    'expected_rows': 10,
    'top_employee_ids': ['EMP029', 'EMP032', ...],
    'check_ordering': True  # 检查顺序
}
```

### 4. 比较验证 (`comparison`)

验证比较结果是否正确。

**示例：问题6**
```python
'validation': {
    'type': 'comparison',
    'expected': {
        'A部门': 25802.85,
        'B部门': 24184.73,
        'higher': 'A部门'  # A部门工资更高
    }
}
```

### 5. 存在性检查 (`existence_check`)

检查是否找到了期望的问题记录。

**示例：问题10**
```python
'validation': {
    'type': 'existence_check',
    'expected_rows': 25,
    'has_issues': True,
    'min_rows': 20  # 至少应该找到20条记录
}
```

## 🔍 结果分析功能

### 自动分析

在 Agent 执行过程中，`ResultAnalyzer` 会自动：

1. **评估完整性**：计算结果完整性评分（0-1）
2. **提取关键发现**：自动总结查询结果的关键信息
3. **检测异常**：发现数据中的异常情况（如NULL值过多、负数工资等）
4. **建议下一步**：判断是否需要继续查询还是生成答案

### 查看分析结果

分析结果会记录在日志中：

```python
# 查看日志文件
tail -f logs/agent.log

# 或在代码中获取
result = agent.query("...")
for ctx in result['context']:
    if 'analysis' in ctx:
        print(ctx['analysis'])
```

## 📈 测试报告

### 生成测试报告

```bash
python run_validated_tests.py > test_report.txt
```

### 报告内容

- 每个问题的执行时间
- 查询成功/失败状态
- 验证通过/失败状态
- 失败原因详情
- 总体统计信息

## 🛠 自定义验证规则

### 添加新的测试问题

编辑 `erp_agent/tests/test_questions.py`：

```python
TEST_QUESTIONS.append({
    'id': 11,
    'question': '你的新问题？',
    'category': 'aggregation',
    'difficulty': 'medium',
    'validation': {
        'type': 'numeric_range',  # 或其他验证类型
        'expected': {
            'value': 100.0
        },
        'tolerance': 0.05,
        'row_count': 1
    }
})
```

### 自定义验证函数

```python
def custom_validate(question_id, sql_result):
    """自定义验证函数"""
    if sql_result['row_count'] > 0:
        return True, "验证通过", {}
    return False, "结果为空", {}

# 使用自定义验证
passed, message, details = custom_validate(1, sql_result)
```

## 🐛 调试技巧

### 1. 查看详细日志

```python
# 设置日志级别为 DEBUG
import os
os.environ['LOG_LEVEL'] = 'DEBUG'
```

### 2. 单独测试某个问题

```python
from erp_agent.tests.test_questions import get_question_by_id, validate_result

question = get_question_by_id(1)
print(question)

# 运行测试
result = agent.query(question['question'])

# 验证
sql_result = result['context'][-1]['result']
passed, message, details = validate_result(1, sql_result)
print(f"验证: {passed}, {message}")
```

### 3. 查看SQL执行详情

```python
result = agent.query("...")
for ctx in result['context']:
    print(f"迭代 {ctx['iteration']}:")
    print(f"  SQL: {ctx.get('sql', 'N/A')}")
    print(f"  结果: {ctx.get('result', {}).get('row_count', 0)} 行")
```

## 📝 注意事项

1. **容差设置**：验证时使用的容差默认为5%，可以根据需要调整
2. **问题8跳过**：由于SQL有错误，问题8目前跳过验证
3. **API限流**：运行大量测试时注意API调用限制，建议在测试间添加延迟
4. **数据变化**：如果数据库数据发生变化，需要更新标准答案

## 🎯 最佳实践

1. **定期运行验证测试**：确保代码变更不影响功能
2. **分析失败原因**：仔细查看验证失败的详细信息
3. **调整Prompt**：根据失败模式优化Few-shot示例
4. **监控性能**：关注查询时间和迭代次数的变化
5. **维护标准答案**：数据更新后及时更新验证规则

## 🔗 相关文档

- [测试问题模块](erp_agent/tests/test_questions.py)
- [结果分析模块](erp_agent/core/result_analyzer.py)
- [标准答案](database/standard_answers_output.txt)
- [主README](erp_agent/README.md)

---

**版本**: v0.2.0  
**最后更新**: 2026-01-25
