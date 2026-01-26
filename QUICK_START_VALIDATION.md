# ERP Agent 验证功能快速开始指南

## 🚀 5分钟快速开始

### 步骤1: 验证集成是否成功

```bash
python quick_test.py
```

**期望输出:**
```
✓ 核心模块导入成功
✓ 测试模块导入成功
✓ 配置模块导入成功
✓ 结果分析器实例化成功
✓ 验证函数执行成功
...
🎉 所有测试通过！系统集成成功。
```

### 步骤2: 运行单个验证测试

```python
# test_single_question.py
from erp_agent.core import ERPAgent
from erp_agent.config import get_llm_config, get_database_config
from erp_agent.tests.test_questions import validate_result

# 初始化Agent
agent = ERPAgent(get_llm_config(), get_database_config())

# 测试问题2
result = agent.query("公司每个部门有多少在职员工？")
print(f"答案: {result['answer']}\n")

# 验证结果
sql_result = result['context'][-1]['result']
passed, message, details = validate_result(2, sql_result)

print(f"验证结果: {'✓ 通过' if passed else '✗ 失败'}")
print(f"消息: {message}")
if details:
    print(f"详情: {details}")
```

### 步骤3: 运行完整测试套件

```bash
python run_validated_tests.py
```

**输出示例:**
```
问题 1: 平均每个员工在公司在职多久？
---------------------------------------------------------------------
✓ 查询成功
  答案: 平均每个员工在公司在职 1104.15 天...
  迭代次数: 2, 耗时: 3.45秒
  ✓ 验证通过: 验证通过

...

测试总结
======================================================================
总问题数: 10
查询成功: 9 (90.0%)
验证通过: 8 (80.0%)
```

## 📋 新功能清单

### 1. 增强的测试问题模块

**文件:** `erp_agent/tests/test_questions.py`

**功能:**
- ✅ 10个测试问题，每个都有详细的验证规则
- ✅ 6种验证类型（数值范围、表格数据、排名等）
- ✅ 自动验证查询结果是否符合标准答案
- ✅ 支持自定义容差

**使用示例:**
```python
from erp_agent.tests.test_questions import TEST_QUESTIONS, validate_result

# 查看问题
question = TEST_QUESTIONS[0]
print(question['question'])
print(question['validation'])

# 验证结果
passed, message, details = validate_result(1, sql_result)
```

### 2. 结果分析模块

**文件:** `erp_agent/core/result_analyzer.py`

**功能:**
- ✅ 自动分析查询结果的完整性
- ✅ 提取关键发现
- ✅ 检测数据异常（NULL值、负数工资等）
- ✅ 生成答案建议
- ✅ 判断是否需要继续查询

**使用示例:**
```python
from erp_agent.core import ResultAnalyzer

analyzer = ResultAnalyzer()

# 分析结果
analysis = analyzer.analyze_result(sql_result, user_question)
print(f"完整性: {analysis['completeness']:.2f}")
print(f"建议: {analysis['suggestion']}")

# 生成答案建议
suggestion = analyzer.generate_answer_suggestion(sql_result, user_question)
print(suggestion)
```

### 3. Agent自动集成

**无需修改代码！** 结果分析已经自动集成到Agent中：

```python
# 正常使用，结果分析在后台自动进行
from erp_agent.core import ERPAgent
from erp_agent.config import get_llm_config, get_database_config

agent = ERPAgent(get_llm_config(), get_database_config())
result = agent.query("你的问题")
print(result['answer'])

# 结果分析会自动记录在日志中
```

## 🔍 验证规则说明

### 问题1: 平均在职时长
- **类型:** `numeric_range`
- **验证:** 平均天数 1104.15±10%

### 问题2: 各部门在职员工数
- **类型:** `table_data`
- **验证:** 5个部门的具体人数（A:22, B:20, C:18, D:16, E:13）

### 问题3: 平均级别最高的部门
- **类型:** `specific_value`
- **验证:** E部门，平均级别5.15

### 问题4: 新入职人数
- **类型:** `table_data`
- **验证:** 每个部门今年和去年的入职人数

### 问题5: A部门平均工资
- **类型:** `numeric_range`
- **验证:** 24790.95±5%

### 问题6: 部门工资比较
- **类型:** `comparison`
- **验证:** A部门工资高于B部门

### 问题7: 各级别平均工资
- **类型:** `table_data`
- **验证:** 10个级别的平均工资

### 问题8: 入职时长分组工资
- **类型:** `skip`
- **原因:** SQL错误，暂时跳过

### 问题9: 涨薪幅度最大员工
- **类型:** `top_n`
- **验证:** Top 10员工ID及顺序

### 问题10: 拖欠工资情况
- **类型:** `existence_check`
- **验证:** 至少找到20条拖欠记录

## 🛠 常见任务

### 任务1: 查看某个问题的详细信息

```python
from erp_agent.tests.test_questions import get_question_by_id

question = get_question_by_id(5)
print(f"问题: {question['question']}")
print(f"分类: {question['category']}")
print(f"难度: {question['difficulty']}")
print(f"验证规则: {question['validation']}")
```

### 任务2: 运行特定类别的问题

```python
from erp_agent.tests.test_questions import get_questions_by_category

# 获取所有聚合类问题
agg_questions = get_questions_by_category('aggregation')
for q in agg_questions:
    print(f"问题 {q['id']}: {q['question']}")
```

### 任务3: 自定义验证容差

```python
# 使用更严格的容差（1%）
passed, message, details = validate_result(
    question_id=1,
    sql_result=result,
    tolerance=0.01  # 1%容差
)
```

### 任务4: 查看分析详情

```python
from erp_agent.core import ResultAnalyzer

analyzer = ResultAnalyzer()

# 详细分析
analysis = analyzer.analyze_result(sql_result, question)

print("完整性评分:", analysis['completeness'])
print("是否足够:", analysis['is_sufficient'])
print("关键发现:", analysis['key_findings'])
print("异常情况:", analysis['anomalies'])
print("下一步建议:", analysis['next_action'])
```

### 任务5: 格式化显示结果

```python
from erp_agent.core import ResultAnalyzer

analyzer = ResultAnalyzer()

# 格式化显示（最多显示5行）
formatted = analyzer.format_result_for_display(sql_result, max_rows=5)
print(formatted)
```

## 📊 理解验证结果

### 验证通过示例

```
✓ 验证通过: 验证通过
详情: {
    'validation_type': 'numeric_range',
    'actual_rows': 1,
    'expected_rows': 1,
    'tolerance_used': 0.1,
    'avg_days': {
        'expected': 1104.15,
        'actual': 1100.0,
        'diff': 4.15,
        'max_diff': 110.415,
        'pass': True
    }
}
```

### 验证失败示例

```
✗ 验证失败: 数值不匹配: avg_days: 期望1104.15, 实际900.0, 差异204.15 (超过容差110.42)
详情: {
    'validation_type': 'numeric_range',
    'actual_rows': 1,
    'expected_rows': 1,
    'avg_days': {
        'expected': 1104.15,
        'actual': 900.0,
        'diff': 204.15,
        'max_diff': 110.415,
        'pass': False
    }
}
```

## 🐛 故障排除

### 问题: 导入失败

```python
ImportError: cannot import name 'ResultAnalyzer' from 'erp_agent.core'
```

**解决方案:**
1. 检查 `erp_agent/core/result_analyzer.py` 是否存在
2. 检查 `erp_agent/core/__init__.py` 是否包含 ResultAnalyzer 导入
3. 运行 `python quick_test.py` 验证集成

### 问题: 验证总是失败

```
✗ 验证失败: 行数不匹配
```

**解决方案:**
1. 检查SQL查询是否正确执行
2. 查看实际返回的数据结构
3. 调整验证规则或容差

```python
# 查看实际返回数据
print("SQL结果:", sql_result)
print("数据:", sql_result['data'])
print("行数:", sql_result['row_count'])
```

### 问题: 日志中看不到分析结果

```
# 设置日志级别为INFO或DEBUG
import os
os.environ['LOG_LEVEL'] = 'INFO'
```

## 📚 相关文档

- **详细文档:** [TESTING_WITH_VALIDATION.md](TESTING_WITH_VALIDATION.md)
- **修改说明:** [CHANGES_SUMMARY.md](CHANGES_SUMMARY.md)
- **主README:** [erp_agent/README.md](erp_agent/README.md)
- **标准答案:** [database/standard_answers_output.txt](database/standard_answers_output.txt)

## ✅ 验证清单

在提交或部署之前，请确认：

- [ ] `python quick_test.py` 全部通过
- [ ] `python run_validated_tests.py` 至少80%验证通过
- [ ] 查看日志文件 `logs/agent.log` 确认没有错误
- [ ] 所有新增文件已提交到Git
- [ ] 环境变量配置正确（`.env` 文件）

## 🎯 下一步

1. **运行完整测试:** `python run_validated_tests.py`
2. **查看详细结果:** 分析哪些问题通过，哪些失败
3. **调优Prompt:** 根据失败模式优化 Few-shot 示例
4. **持续监控:** 定期运行验证测试，确保性能稳定

---

**版本:** v0.2.0  
**最后更新:** 2026-01-25  
**状态:** ✅ 已完成集成
