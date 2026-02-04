# ERP Agent 提示词优化重构文档

## 1. 问题概述

### 1.1 当前问题

当前系统的提示词文件存在以下问题：

**A. system_prompt.txt 问题（386行）**：
1. **时间信息冗余**：时间相关的说明占据约150行，可通过简洁的 system_hint 方式传递
2. **占位符过多**：模板中包含约20个时间相关占位符，每次请求都需要计算和填充
3. **业务规则重复**：跨期对比规则、完整性检测规则与 examples.txt 中的内容重复

**B. examples.txt 问题（833行）- 最大优化空间**：
1. **示例过于详细**：9个完整示例，每个包含完整JSON输出、模拟执行结果、详细学习点
2. **与 system_prompt.txt 重复**：时间处理说明、易错点提醒在两个文件中都有
3. **SQL工具箱冗余**：约50行的SQL语法表格，LLM本身已熟悉这些内容
4. **警告重复**：同样的 "⚠️" 警告在多处出现

**C. 维护困难**：
- 时间逻辑分散在 `prompt_builder.py`、`date_utils.py` 和 `system_prompt.txt` 多个文件中
- 修改一个规则需要同步更新多个文件

### 1.2 优化目标（极简方案）

1. **极简提示词**：只传递当前日期 + 核心易错点提醒，让 LLM 自己计算时间
2. **大幅减少 Token 消耗**：目标减少 **60-70%** 的提示词总长度
3. **删除冗余代码**：删除约 300 行时间计算相关代码
4. **精简 examples.txt**：从 833 行精简到约 300 行（减少 **64%**）
5. **信任 LLM 能力**：LLM 完全能够自己进行时间计算和SQL构建

### 1.3 当前状态概览

| 文件 | 当前行数 | 目标行数 | 减少比例 |
|------|---------|---------|---------|
| `system_prompt.txt` | 386行 | ~180行 | **-53%** |
| `examples.txt` | 833行 | ~300行 | **-64%** |
| `schema.txt` | 107行 | 107行 | 保持不变 |
| **总计** | **1326行** | **~587行** | **-56%** |

---

## 2. 修改方案详述

### 2.1 架构变更概览

```
修改前（复杂）:
┌─────────────────────────────────────────────────────────────────┐
│ system_prompt.txt (386行)                                        │
│   ├── 时间推理约束 (~50行)                                        │
│   ├── 时间计算规则 (~100行)                                       │
│   ├── 时间占位符 {year}, {month}, {year_minus_1}... (20+个)      │
│   └── 其他业务规则                                                │
└─────────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│ prompt_builder.py (~900行)                                       │
│   └── _calculate_time_placeholders() 计算20+个占位符 (~150行)    │
└─────────────────────────────────────────────────────────────────┘

修改后（极简）:
┌─────────────────────────────────────────────────────────────────┐
│ system_prompt.txt (约230行)                                      │
│   ├── {time_hint} 单一占位符（5行内容）                           │
│   └── 其他业务规则（保持不变）                                    │
└─────────────────────────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────────────────────────┐
│ date_utils.py                                                    │
│   └── format_time_hint() 极简函数（约20行）                       │
│       只返回: 当前日期 + 3条易错点提醒                            │
└─────────────────────────────────────────────────────────────────┘

核心变化: 
- 删除 ~150行 时间说明
- 删除 ~150行 时间计算代码
- 新增 ~20行 极简函数
- LLM 自己进行时间计算（无需我们预计算）
```

### 2.2 System Hint 设计（极简方案）

**核心思想**：LLM 本身具备时间计算能力，我们只需要：
1. 告诉 LLM **当前日期**（唯一必须的信息）
2. 提醒几个**关键易错点**（防止常见错误）
3. **让 LLM 自己判断**是否需要时间计算，以及如何计算

**新的时间提示格式（极简版）**:

```
【当前时间】{current_date}

【时间计算易错点提醒】
1. "最近一个月"在统计场景中指最后一个完整月份，不是进行中的月份
2. 检测类问题（"有没有"、"是否存在"）应查询全部历史，不要自作主张限制时间范围
3. 在 thought 中展示你的时间推理过程
```

**为什么这样更好**：

| 对比项 | 预计算所有时间（旧方案） | 只提供当前日期（新方案） |
|--------|------------------------|------------------------|
| Token 消耗 | 高（计算20+个时间值） | 极低（只有日期+3条提醒） |
| 灵活性 | 低（固定的时间范围） | 高（LLM按需计算） |
| 适用性 | 所有查询都带时间信息 | 只在需要时才处理时间 |
| LLM 理解 | 可能信息过载 | 简洁明了 |
| 维护成本 | 高（需要维护计算逻辑） | 低（只维护易错点列表） |

**示例对比**：

查询："公司有多少在职员工？"（不涉及时间）
- 旧方案：仍然传递20+个时间占位符（浪费）
- 新方案：LLM 看到当前日期，判断此查询不需要时间条件，直接查询

查询："去年第三季度的平均工资"（涉及时间）
- 旧方案：LLM 从预计算的 `{year_minus_1}` 中获取去年
- 新方案：LLM 看到当前日期 2026-02-04，自己计算去年=2025，Q3=7-9月

---

## 3. 具体修改文件清单

### 3.1 文件: `erp_agent/utils/date_utils.py`

#### 3.1.1 新增函数: `format_time_hint()`（极简版）

**功能描述**: 生成极简的时间提示信息，只包含当前日期和关键易错点提醒。

**设计原则**:
- **最小化信息**: 只传递 LLM 无法自己获取的信息（当前日期）
- **信任 LLM**: 让 LLM 自己进行时间计算，不预计算所有可能的时间范围
- **防错提醒**: 只提醒几个容易出错的关键点

**函数签名**:
```python
def format_time_hint(date_info: Optional[Dict[str, Any]] = None) -> str:
    """
    生成极简的时间提示信息（只含当前日期和易错点提醒）
    
    参数:
        date_info: 时间信息字典，如果为 None 则自动获取当前时间
    
    返回:
        str: 格式化的时间提示信息（约5-8行）
    
    示例输出:
        【当前时间】2026-02-04
        
        【时间计算易错点】
        1. "最近一个月"统计应使用最后一个完整月份
        2. 检测类问题应查询全部历史，不要限制时间
        3. 在thought中展示时间推理过程
    """
```

**实现要点**:
```python
def format_time_hint(date_info: Optional[Dict[str, Any]] = None) -> str:
    """
    生成极简的时间提示信息
    
    设计思路:
        - LLM 能够进行基本的日期计算（年份加减、季度判断等）
        - 我们只需提供当前日期作为计算基准
        - 只提醒几个实践中发现的易错点
    """
    if date_info is None:
        date_info = get_current_datetime()
    
    current_date = date_info['current_date']
    
    # 极简提示：只有当前日期 + 易错点提醒
    hint = f"""【当前时间】{current_date}

【时间计算易错点】
1. "最近一个月"在统计场景中指最后一个完整月份，不是进行中的月份
2. 检测类问题（"有没有"、"是否存在"、"出现过"）应查询全部历史数据，不要自作主张限制为"最近几个月"
3. 在 thought 中明确展示时间推理过程（如："当前2026年，去年=2025年"）"""
    
    return hint
```

**为什么这样设计**:

```
问题: "去年第三季度的平均工资是多少？"

LLM 的推理过程（我们期望的）:
thought: "当前日期是2026-02-04，所以：
- 去年 = 2026 - 1 = 2025年
- 第三季度 = 7月1日到9月30日
- 查询范围: 2025-07-01 到 2025-09-30"

这种推理 LLM 完全能够自己完成，不需要我们预先计算好告诉它。
```

#### 3.1.2 更新公共导出

在文件末尾的 `__all__` 列表中添加新函数:
```python
__all__ = [
    'get_current_datetime',
    'calculate_date_offset',
    'get_date_range_for_period',
    'calculate_days_between',
    'calculate_months_between',
    'get_month_start_end',
    'get_quarter_start_end',
    'get_year_start_end',
    'format_date_for_sql',
    'format_time_hint',  # 新增
]
```

---

### 3.2 文件: `erp_agent/utils/prompt_builder.py`

#### 3.2.1 简化 `build_sql_generation_prompt()` 方法

**修改前**: 计算20+个时间占位符，逐一替换模板中的占位符
**修改后**: 只生成极简的时间提示（当前日期+易错点）

**修改内容**:

```python
def build_sql_generation_prompt(
    self,
    user_question: str,
    date_info: Optional[Dict[str, Any]] = None,
    context: Optional[List[Dict[str, Any]]] = None,
    error_feedback: Optional[str] = None
) -> str:
    """
    构建 SQL 生成的完整 Prompt（极简版）
    
    变更说明:
        - 移除了所有单独的时间占位符 ({year}, {month}, {year_minus_1} 等)
        - 使用 format_time_hint() 生成极简时间提示（只有当前日期+易错点）
        - 让 LLM 自己进行时间计算，而不是预计算所有可能的时间
    """
    if date_info is None:
        date_info = get_current_datetime()
    
    # 加载模板和内容
    template = self.load_system_prompt_template()
    schema = self.load_schema()
    examples = self.load_examples()
    
    # 【核心变更】生成极简时间提示（只有当前日期+易错点）
    time_hint = format_time_hint(date_info)
    
    # 构建历史上下文文本
    history_context = self._build_history_context(context)
    
    # 构建错误反馈文本
    error_feedback_text = self._build_error_feedback(error_feedback)
    
    # 构建迭代指令
    iteration = len(context) + 1 if context else 1
    iteration_instruction = f"\n请开始第 {iteration} 轮推理，严格按照上述 JSON 格式输出。"
    
    # 【极简】只有5个占位符，没有任何时间计算相关的占位符
    prompt = template.format(
        schema=schema,
        examples=examples,
        time_hint=time_hint,  # 极简时间提示
        history_context=history_context,
        error_feedback=error_feedback_text,
        user_question=user_question,
        iteration_instruction=iteration_instruction
    )
    
    return prompt
```

#### 3.2.2 删除 `_calculate_time_placeholders()` 方法

**此方法可以完全删除**，因为：
- 新架构不再需要预计算时间占位符
- 时间计算交给 LLM 自己完成
- 如果有特殊需要，`date_utils.py` 中的工具函数仍然可用

```python
# 删除以下方法（约100行代码）
# def _calculate_time_placeholders(self, date_info, required_placeholders):
#     ...

# 同时删除以下方法（不再需要）
# def extract_placeholders(self, template):
#     ...
```

**代码精简效果**:
- `prompt_builder.py` 预计减少 150+ 行代码
- 移除复杂的占位符提取和计算逻辑
- 代码更易于理解和维护

#### 3.2.3 新增辅助方法

将历史上下文构建和错误反馈构建提取为独立方法，提高代码可读性:

```python
def _build_history_context(self, context: Optional[List[Dict[str, Any]]]) -> str:
    """
    构建历史上下文文本
    
    参数:
        context: 历史上下文列表
    
    返回:
        str: 格式化的历史上下文文本
    """
    if not context or len(context) == 0:
        return ""
    
    history_context = "\n## 历史执行记录\n\n"
    history_context += "你已经执行过以下查询:\n\n"
    
    for idx, item in enumerate(context, 1):
        history_context += f"### 第 {idx} 轮\n\n"
        # ... 现有逻辑保持不变
    
    return history_context


def _build_error_feedback(self, error_feedback: Optional[str]) -> str:
    """
    构建错误反馈文本
    
    参数:
        error_feedback: 错误反馈信息
    
    返回:
        str: 格式化的错误反馈文本
    """
    if not error_feedback:
        return ""
    
    return f"""
## ⚠️ 错误反馈

上一次查询执行失败，请根据错误信息修正 SQL：

```
{error_feedback}
```

请分析错误原因，重新生成正确的 SQL 查询。
"""
```

---

### 3.3 文件: `erp_agent/prompts/system_prompt.txt`

#### 3.3.1 大幅简化时间部分

**删除内容** (约150行):
- "## ⚠️ 时间推理约束（最重要！）" 整个章节（约50行）
- "## 时间上下文和计算工具" 整个章节（约100行）
- 所有单独的时间占位符 (`{year}`, `{month}`, `{year_minus_1}`, `{three_months_ago}` 等约20个)
- 各种时间计算示例和规则说明
- examples.txt 中的时间相关示例也可以简化（移除预计算的年份占位符）

**替换为** (仅1个占位符):
```
## 时间信息

{time_hint}
```

就这么简单！`{time_hint}` 会被替换为：
```
【当前时间】2026-02-04

【时间计算易错点】
1. "最近一个月"在统计场景中指最后一个完整月份，不是进行中的月份
2. 检测类问题（"有没有"、"是否存在"、"出现过"）应查询全部历史数据，不要自作主张限制为"最近几个月"
3. 在 thought 中明确展示时间推理过程（如："当前2026年，去年=2025年"）
```

#### 3.3.2 简化后的模板结构（极简版）

```
# 系统 Prompt 模板

你是一个专业的 PostgreSQL SQL 专家...

## 你的能力范围（保持不变，可精简）

## 工作方式：逐步推理（保持不变，可精简）

## 重要约束（保持不变）

## 时间信息
{time_hint}

## 数据库 Schema
{schema}

## 业务规则（保持不变）

## SQL 推理方法论
{examples}

## 输出格式（保持不变）

{history_context}
{error_feedback}

## 当前任务
**用户问题**: {user_question}
{iteration_instruction}
```

**占位符对比**:

| 修改前 | 修改后 |
|--------|--------|
| `{year}` | ❌ 删除 |
| `{month}` | ❌ 删除 |
| `{year_minus_1}` | ❌ 删除 |
| `{year_minus_2}` | ❌ 删除 |
| `{month_padded}` | ❌ 删除 |
| `{month_minus_1_padded}` | ❌ 删除 |
| `{current_date}` | ❌ 删除 |
| `{three_months_ago}` | ❌ 删除 |
| `{six_months_ago}` | ❌ 删除 |
| `{one_year_ago}` | ❌ 删除 |
| ... (还有10+个) | ❌ 删除 |
| - | `{time_hint}` ✅ 新增（唯一） |

#### 3.3.3 简化业务规则部分

**删除内容**（约30行）:
- "跨期对比规则"中的完整SQL示例代码（与examples.txt重复）
- "数据完整性检测规则"中的详细解释（压缩为简洁提醒）

**替换为**（约10行）:
```
### 业务规则速查

| 场景 | 规则 |
|------|------|
| 在职员工 | `leave_date IS NULL` |
| 检测类问题 | 查询全部历史，不限制时间范围 |
| 跨期对比 | CTE分期统计 → JOIN → 计算变化率 |
| 完整性检测 | generate_series + LEFT JOIN + IS NULL |
| 排名查询 | 使用 LIMIT |
| 异常检测 | **不用** LIMIT，返回全部 |
```

---

### 3.4 文件: `erp_agent/prompts/examples.txt`（重点简化）

#### 3.4.1 简化策略：从"完整示例"到"模式摘要"

**核心理念**：LLM 已经熟悉 ReAct 框架和 SQL 语法，不需要手把手教学。我们只需要：
1. 展示**特定于本系统的模式**（不是通用SQL教学）
2. 提醒**容易出错的点**
3. 保留**最小必要的示例**

**删除内容**（约533行）：

| 删除项 | 原因 | 行数 |
|--------|------|------|
| 示例1: 单表统计 | LLM已知基础SQL | ~50行 |
| 示例3: 多表关联 | LLM已知JOIN语法 | ~50行 |
| 示例4: 分组比较 | LLM已知GROUP BY | ~50行 |
| 示例5: 分步探索 | 与其他示例重复 | ~60行 |
| 示例6: 窗口函数 | LLM已知窗口函数 | ~50行 |
| 示例7: 异常检测 | 可合并到示例9 | ~50行 |
| 通用SQL技术工具箱 | LLM已知SQL语法 | ~50行 |
| ReAct框架总结 | 重复system_prompt | ~40行 |
| 重复的警告和提醒 | 集中到一处 | ~80行 |
| 详细的JSON输出示例 | 简化为模式描述 | ~50行 |

**保留内容**（约300行）：

| 保留项 | 原因 |
|--------|------|
| 示例2: 时间推理 | 本系统的核心难点 |
| 示例2B: 完整月份 | 容易出错的关键点 |
| 示例8: 跨期对比 | 本系统特有的复杂模式 |
| 示例9: 完整性检测 | 本系统特有的复杂模式 |
| 核心原则说明 | 精简版，约20行 |

#### 3.4.2 简化后的 examples.txt 结构

```markdown
# SQL 推理模式速查

## 核心原则（必读）

1. **时间推理**：在 thought 中明确展示计算过程（"当前2026年，去年=2025年"）
2. **完整周期**：统计场景的"最近一个月"指最后一个完整月份
3. **检测类问题**：查询全部历史，不要自作主张限制时间范围
4. **独立思考**：基于 Schema 推理，不要照搬示例中的具体年份或表名

---

## 模式1: 时间范围查询

**场景**: "去年第三季度的平均工资"

**推理要点**:
- 在 thought 中明确：当前年份 → 去年 = 当前-1 → 季度日期范围
- 使用具体日期，不要使用相对函数

**模式**:
```sql
WHERE date BETWEEN '{计算出的开始日期}' AND '{计算出的结束日期}'
```

---

## 模式2: 完整月份统计

**场景**: "最近一个月的平均订单金额"

**关键判断**:
- 当前月份是否已结束？
- 未结束 → 使用上一个完整月份
- 已结束 → 使用当前月份

**模式**:
```sql
WHERE DATE_TRUNC('month', date) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
```

---

## 模式3: 跨期对比

**场景**: "从去年到今年增长最快的员工"

**技术要点**:
1. 两个 CTE 分别计算各期数据
2. INNER JOIN 只保留两期都有数据的对象
3. 计算变化率：(新值-旧值)/旧值*100

**模式**:
```sql
WITH period_a AS (SELECT id, SUM(value) AS val_a FROM t WHERE year = {去年} GROUP BY id),
     period_b AS (SELECT id, SUM(value) AS val_b FROM t WHERE year = {今年} GROUP BY id)
SELECT a.id, ROUND((b.val_b - a.val_a) / a.val_a * 100, 2) AS growth_rate
FROM period_a a JOIN period_b b ON a.id = b.id
ORDER BY growth_rate DESC;
```

---

## 模式4: 完整性检测（找缺失）

**场景**: "有没有员工工资发放缺失"

**关键要点**:
- ⚠️ 必须查询**全部历史**，不要限制为"最近N个月"
- 生成"应该有"的完整序列
- LEFT JOIN 实际数据，IS NULL 找缺失

**模式**:
```sql
WITH expected AS (
    SELECT e.id, generate_series(
        DATE_TRUNC('month', e.start_date),
        DATE_TRUNC('month', COALESCE(e.end_date, CURRENT_DATE)),
        '1 month'::interval
    )::DATE AS expected_month
    FROM entities e
)
SELECT ex.id, ex.expected_month AS missing_month
FROM expected ex
LEFT JOIN actual_records ar ON ex.id = ar.id 
    AND DATE_TRUNC('month', ar.date) = ex.expected_month
WHERE ar.id IS NULL
    AND ex.expected_month < DATE_TRUNC('month', CURRENT_DATE);
```

---

## 输出格式

```json
{
  "thought": "推理过程（必须展示时间计算）",
  "action": "execute_sql",
  "sql": "SELECT ...;",
  "is_final": false
}
```

```json
{
  "thought": "基于结果得出结论",
  "action": "answer", 
  "answer": "自然语言答案",
  "is_final": true
}
```
```

#### 3.4.3 简化对比

| 项目 | 修改前 | 修改后 |
|------|--------|--------|
| 总行数 | 833行 | ~300行 |
| 完整示例数 | 9个 | 4个模式 |
| JSON输出示例 | 每个示例2-3个 | 统一2个 |
| SQL工具箱 | 50行表格 | 删除 |
| 重复警告 | 分散在10+处 | 集中在1处 |
| 执行结果模拟 | 每个示例都有 | 删除 |

---

### 3.6 文件: `erp_agent/core/sql_generator.py`

**修改内容**: 无需大的修改，但需要更新导入

```python
# 更新导入
from erp_agent.utils.date_utils import get_current_datetime, format_time_hint
```

---

## 4. 接口变更说明

### 4.1 新增接口

| 模块 | 函数 | 功能 | 参数 | 返回值 |
|------|------|------|------|--------|
| `date_utils` | `format_time_hint()` | 生成时间提示信息块 | `date_info: Optional[Dict]` | `str` |

### 4.2 修改接口

| 模块 | 函数 | 变更类型 | 说明 |
|------|------|----------|------|
| `prompt_builder` | `build_sql_generation_prompt()` | 内部重构 | 接口保持不变，内部使用极简时间提示 |

### 4.3 删除的接口

| 模块 | 函数/方法 | 删除原因 |
|------|-----------|----------|
| `prompt_builder` | `_calculate_time_placeholders()` | 不再需要预计算时间，LLM自己计算 |
| `prompt_builder` | `extract_placeholders()` | 不再需要提取大量占位符 |
| `prompt_builder` | `format_date_context()` | 被极简的 `format_time_hint()` 替代 |
| `prompt_builder` | `suggest_time_expression_for_query()` | LLM自己处理时间表达式 |
| `prompt_builder` | `get_time_range_description()` | LLM自己生成时间描述 |

### 4.4 向后兼容性

- 所有外部接口保持不变
- `SQLGenerator.generate()` 方法签名不变
- `ERPAgent.query()` 方法签名不变
- 只有内部实现发生变化

---

## 5. 单元测试

### 5.1 测试文件: `erp_agent/tests/test_date_utils.py`

需要新增以下测试用例:

```python
"""
date_utils 模块单元测试（极简方案）

测试覆盖:
- get_current_datetime()
- format_time_hint()  # 新增的极简版
"""

import unittest
from erp_agent.utils.date_utils import (
    get_current_datetime,
    format_time_hint,
)


class TestFormatTimeHint(unittest.TestCase):
    """format_time_hint() 函数测试（极简版）"""
    
    def test_format_time_hint_contains_current_date(self):
        """测试: 包含当前日期"""
        date_info = {
            'current_date': '2026-02-04',
            'year': 2026,
            'month': 2,
        }
        
        result = format_time_hint(date_info)
        
        # 验证包含当前日期
        self.assertIn('2026-02-04', result)
        
    def test_format_time_hint_contains_key_reminders(self):
        """测试: 包含关键易错点提醒"""
        result = format_time_hint()
        
        # 验证包含三个关键提醒
        self.assertIn('最近一个月', result)
        self.assertIn('完整月份', result)
        self.assertIn('检测类问题', result)
        self.assertIn('thought', result)
        
    def test_format_time_hint_is_minimal(self):
        """测试: 输出足够精简"""
        result = format_time_hint()
        
        # 极简版应该很短（约300-500字符）
        self.assertLess(len(result), 600)
        # 但不能太短
        self.assertGreater(len(result), 200)
        
    def test_format_time_hint_no_precomputed_values(self):
        """测试: 不包含预计算的时间值（如去年=2025）"""
        date_info = {
            'current_date': '2026-02-04',
            'year': 2026,
            'month': 2,
        }
        
        result = format_time_hint(date_info)
        
        # 不应该包含预计算的年份值
        self.assertNotIn('2025-01-01', result)
        self.assertNotIn('2024-01-01', result)
        # 不应该包含预计算的月份偏移
        self.assertNotIn('2025-11-04', result)
        
    def test_format_time_hint_auto_date(self):
        """测试: 自动获取当前日期"""
        result = format_time_hint()  # 不传参数
        
        self.assertIsInstance(result, str)
        self.assertIn('当前时间', result)


if __name__ == '__main__':
    unittest.main()
```

### 5.2 测试文件: `erp_agent/tests/test_prompt_builder.py`

需要新增以下测试用例:

```python
"""
prompt_builder 模块单元测试（极简方案）

测试覆盖:
- build_sql_generation_prompt() 极简重构后的行为
- 验证不再包含预计算的时间值
"""

import unittest
from erp_agent.utils.prompt_builder import PromptBuilder


class TestPromptBuilderMinimal(unittest.TestCase):
    """PromptBuilder 极简方案测试"""
    
    def setUp(self):
        self.builder = PromptBuilder()
        
    def test_build_prompt_contains_current_date_only(self):
        """测试: Prompt 只包含当前日期，不包含预计算的相对时间"""
        date_info = {
            'current_date': '2026-02-04',
            'year': 2026,
            'month': 2,
        }
        
        prompt = self.builder.build_sql_generation_prompt(
            user_question="公司有多少在职员工？",
            date_info=date_info
        )
        
        # 验证包含当前日期
        self.assertIn('2026-02-04', prompt)
        
        # 验证不包含预计算的时间范围
        self.assertNotIn('2025-01-01', prompt)  # 不应该有去年起始日期
        self.assertNotIn('2025-12-31', prompt)  # 不应该有去年结束日期
        self.assertNotIn('2025-11-04', prompt)  # 不应该有3个月前的日期
        
    def test_build_prompt_contains_key_reminders(self):
        """测试: Prompt 包含关键易错点提醒"""
        prompt = self.builder.build_sql_generation_prompt(
            user_question="测试问题"
        )
        
        # 验证包含易错点提醒
        self.assertIn('最近一个月', prompt)
        self.assertIn('检测类问题', prompt)
        
    def test_build_prompt_significantly_shorter(self):
        """测试: Prompt 长度显著减少"""
        prompt = self.builder.build_sql_generation_prompt(
            user_question="测试问题"
        )
        
        # 极简方案下 Prompt 应该更短
        # 原来约20000字符，现在目标减少50%以上
        self.assertLess(len(prompt), 12000)
        
    def test_build_prompt_no_time_placeholders(self):
        """测试: 不再使用大量时间占位符"""
        # 这个测试确保模板中不再有 {year}, {month} 等占位符
        # 只有 {time_hint} 一个时间相关占位符
        prompt = self.builder.build_sql_generation_prompt(
            user_question="去年的平均工资是多少？"
        )
        
        # 即使问题涉及时间，也不应该包含预计算的年份边界
        self.assertNotIn('year_minus_1', prompt)
        self.assertNotIn('three_months_ago', prompt)


class TestPromptBuilderHelperMethods(unittest.TestCase):
    """PromptBuilder 辅助方法测试"""
    
    def setUp(self):
        self.builder = PromptBuilder()
        
    def test_build_history_context_empty(self):
        """测试: 空历史上下文"""
        result = self.builder._build_history_context(None)
        self.assertEqual(result, "")
        
    def test_build_history_context_with_data(self):
        """测试: 有数据的历史上下文"""
        context = [
            {
                'thought': '思考内容',
                'sql': 'SELECT 1;',
                'result': {'success': True, 'row_count': 1, 'data': [{'?column?': 1}]}
            }
        ]
        
        result = self.builder._build_history_context(context)
        
        self.assertIn('第 1 轮', result)
        self.assertIn('SELECT 1', result)


if __name__ == '__main__':
    unittest.main()
```

### 5.3 集成测试: `erp_agent/tests/test_integration.py`

```python
"""
集成测试

验证重构后系统的端到端功能
"""

import unittest
from unittest.mock import Mock, patch

from erp_agent.core.sql_generator import SQLGenerator
from erp_agent.config.llm import LLMConfig


class TestSQLGeneratorIntegration(unittest.TestCase):
    """SQLGenerator 集成测试"""
    
    @patch('erp_agent.core.sql_generator.requests.post')
    def test_generate_with_new_time_context(self, mock_post):
        """测试: 使用新时间上下文的 SQL 生成"""
        # 模拟 API 响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'choices': [{
                'message': {
                    'content': '{"thought": "测试", "action": "execute_sql", "sql": "SELECT 1;", "is_final": false}'
                }
            }]
        }
        mock_response.raise_for_status = Mock()
        mock_post.return_value = mock_response
        
        # 创建生成器
        llm_config = LLMConfig(
            api_key="test_key",
            base_url="https://test.api.com",
            model="test-model"
        )
        generator = SQLGenerator(llm_config)
        
        # 执行生成
        result = generator.generate("公司有多少在职员工？")
        
        # 验证结果
        self.assertEqual(result['action'], 'execute_sql')
        self.assertIsNotNone(result['sql'])


if __name__ == '__main__':
    unittest.main()
```

### 5.4 运行测试

```bash
# 运行所有单元测试
python -m pytest erp_agent/tests/ -v

# 运行特定测试文件
python -m pytest erp_agent/tests/test_date_utils.py -v
python -m pytest erp_agent/tests/test_prompt_builder.py -v

# 运行并生成覆盖率报告
python -m pytest erp_agent/tests/ --cov=erp_agent --cov-report=html
```

---

## 6. 文档重要性说明

### 6.1 为什么文档很重要

1. **知识传承**: 记录修改的动机、方案和实现细节，便于后续维护者理解
2. **降低风险**: 详细的文档可以防止重复犯错或遗漏关键细节
3. **团队协作**: 使团队成员能够快速了解变更，减少沟通成本
4. **代码审查**: 为 Code Review 提供背景信息和评审依据

### 6.2 文档规范建议

#### 代码注释规范

```python
def format_time_hint(date_info: Optional[Dict[str, Any]] = None) -> str:
    """
    生成极简的时间提示信息（只含当前日期和易错点提醒）
    
    设计理念:
        - 信任 LLM 的时间计算能力
        - 只传递 LLM 无法自己获取的信息（当前日期）
        - 只提醒容易出错的关键点
    
    参数:
        date_info: 时间信息字典，如果为 None 则自动获取当前时间
    
    返回:
        str: 极简的时间提示（约5行文本）
    
    示例:
        >>> hint = format_time_hint({'current_date': '2026-02-04'})
        >>> print(hint)
        【当前时间】2026-02-04
        
        【时间计算易错点】
        1. "最近一个月"在统计场景中指最后一个完整月份...
    
    变更历史:
        - 2026-02-04: 新增，采用极简方案替代原有的多占位符方案
    """
```

#### 提交信息规范

```
feat(prompt): 极简化时间提示，让LLM自己计算时间

核心变更:
- 新增 format_time_hint() 生成极简时间提示（只有当前日期+3条易错点提醒）
- 删除 system_prompt.txt 中约150行的时间说明
- 删除 prompt_builder.py 中约150行的时间占位符计算逻辑
- 删除20+个时间占位符，只保留1个 {time_hint}

设计理念:
- 信任LLM的时间计算能力
- 只传递LLM无法自己获取的信息（当前日期）
- 只提醒容易出错的关键点

Breaking Change: 无（外部接口保持不变）
Related Issue: #xxx
```

### 6.3 后续修改者须知

1. **修改前**: 
   - 阅读本文档了解当前架构
   - 运行现有单元测试确保基线正确
   
2. **修改时**:
   - 遵循现有代码风格
   - 为新增功能编写单元测试
   - 更新相关文档
   
3. **修改后**:
   - 运行全部测试确保没有回归
   - 更新本文档记录变更
   - 提交有意义的 commit message

---

## 7. 实施步骤

### 7.1 实施顺序

1. **阶段一: 准备** (预估工作量: 1小时)
   - [ ] 创建功能分支 `git checkout -b feat/prompt-optimization`
   - [ ] 备份现有 prompt 文件
   - [ ] 编写测试用例（先写测试）

2. **阶段二: 时间系统简化** (预估工作量: 3小时)
   - [ ] 在 `date_utils.py` 中实现极简的 `format_time_hint()` 函数（约20行）
   - [ ] 简化 `prompt_builder.py`，删除 `_calculate_time_placeholders()` 等方法
   - [ ] 简化 `system_prompt.txt` 中的时间部分，删除约150行内容

3. **阶段三: examples.txt 大幅简化** (预估工作量: 3小时)
   - [ ] 删除基础示例（示例1、3、4、5、6、7）
   - [ ] 保留并精简核心示例（示例2、2B、8、9）
   - [ ] 删除"SQL技术工具箱"部分
   - [ ] 删除重复的警告和提醒，集中到开头
   - [ ] 将完整示例转换为"模式摘要"格式
   - [ ] 删除模拟的执行结果

4. **阶段四: system_prompt.txt 业务规则简化** (预估工作量: 1小时)
   - [ ] 删除跨期对比规则中的完整SQL示例
   - [ ] 压缩数据完整性检测规则
   - [ ] 删除与 examples.txt 重复的内容

5. **阶段五: 测试验证** (预估工作量: 2小时)
   - [ ] 运行单元测试
   - [ ] 手动测试关键场景:
     - 不涉及时间: "公司有多少在职员工？"
     - 相对时间: "去年的平均工资是多少？"
     - 完整月份: "最近一个月的平均工资"
     - 跨期对比: "今年比去年工资增长最快的员工"
     - 检测类: "有没有员工工资拖欠？"

6. **阶段六: 收尾** (预估工作量: 1小时)
   - [ ] 代码审查
   - [ ] 更新文档
   - [ ] 合并到主分支

**总预估工作量**: 约 1.5 个工作日

### 7.2 回滚方案

如果新方案出现问题：

1. `git revert` 回退提交
2. 或者从备份恢复 `system_prompt.txt` 和 `prompt_builder.py`

**风险评估**: 低风险，因为外部接口完全不变，只是内部实现简化

---

## 8. 预期效果

### 8.1 性能提升（极简方案 + examples.txt 简化）

| 指标 | 修改前 | 修改后 | 改善幅度 |
|------|--------|--------|----------|
| **system_prompt.txt 行数** | ~386行 | ~180行 | **-53%** |
| **examples.txt 行数** | ~833行 | ~300行 | **-64%** |
| **Prompt 文件总行数** | ~1326行 | ~587行 | **-56%** |
| 时间相关说明行数 | ~150行 | ~5行 | **-97%** |
| 时间占位符数量 | 20+ | 1 | **-95%** |
| Prompt 总字符数 | ~35000 | ~15000 | **-57%** |
| prompt_builder.py 行数 | ~900行 | ~600行 | **-33%** |
| 时间计算函数调用 | 20+次 | 0次 | **-100%** |
| 完整示例数 | 9个 | 4个模式 | **-56%** |

### 8.2 Token 消耗对比

| 查询类型 | 修改前 Token | 修改后 Token | 节省 |
|----------|-------------|-------------|------|
| 不涉及时间的查询 | ~8000 | ~3500 | **56%** |
| 涉及时间的查询 | ~8000 | ~3500 | **56%** |
| 复杂多轮查询 | ~10000 | ~4500 | **55%** |

**说明**: 
- 极简方案对所有查询都有同等的优化效果
- examples.txt 简化贡献了约 30% 的 Token 节省
- 不再预计算可能用不到的时间信息

### 8.3 可维护性提升

- **代码量减少**: 删除约300行时间相关的复杂逻辑
- **单一职责**: `format_time_hint()` 只做一件事：输出当前日期+提醒
- **易于理解**: 新开发者可以在5分钟内理解时间处理逻辑
- **易于修改**: 如果需要新增易错点提醒，只需修改一个地方

### 8.4 LLM 体验提升

| 方面 | 修改前 | 修改后 |
|------|--------|--------|
| 上下文窗口占用 | 高 | 低 |
| 信息过载风险 | 有 | 无 |
| 推理灵活性 | 低（被预计算值限制） | 高（自由计算） |
| 错误定位 | 难（不知道是哪个占位符出错） | 易（推理过程透明） |

---

## 9. 附录

### 9.1 相关文件清单

| 文件路径 | 修改类型 | 变更量 | 说明 |
|----------|----------|--------|------|
| `erp_agent/utils/date_utils.py` | 新增函数 | +20行 | 添加极简的 `format_time_hint()` |
| `erp_agent/utils/prompt_builder.py` | 删除+简化 | -150行 | 删除时间计算逻辑 |
| `erp_agent/prompts/system_prompt.txt` | 大幅简化 | **-206行** | 删除时间说明+简化业务规则 |
| `erp_agent/prompts/examples.txt` | **重点简化** | **-533行** | 从9个示例精简为4个模式 |
| `erp_agent/tests/test_date_utils.py` | 新增 | +50行 | 单元测试 |
| `erp_agent/tests/test_prompt_builder.py` | 更新 | 修改 | 适配新方案 |

**净效果**: 
- Prompt 文件减少约 **739行**（从 1326 行到 587 行）
- 代码文件减少约 **280行**
- **总计减少约 1000+ 行**

### 9.2 极简方案的核心代码

整个时间处理的核心代码只有这么多：

```python
# date_utils.py 中新增（约20行）
def format_time_hint(date_info: Optional[Dict] = None) -> str:
    if date_info is None:
        date_info = get_current_datetime()
    
    return f"""【当前时间】{date_info['current_date']}

【时间计算易错点】
1. "最近一个月"在统计场景中指最后一个完整月份，不是进行中的月份
2. 检测类问题（"有没有"、"是否存在"）应查询全部历史数据
3. 在 thought 中展示时间推理过程"""
```

```
# system_prompt.txt 中的时间部分（约5行）
## 时间信息

{time_hint}
```

**就这么简单！**

### 9.3 简化后的 examples.txt 完整模板

```markdown
# SQL 推理模式速查

## 核心原则（必读）

1. **时间推理**：在 thought 中明确展示计算过程（"当前2026年，去年=2025年"）
2. **完整周期**：统计场景的"最近一个月"指最后一个完整月份，不是进行中的月份
3. **检测类问题**：查询全部历史，不要自作主张限制为"最近N个月"
4. **独立思考**：基于 Schema 推理，不要照搬示例中的具体年份或表名

---

## 模式1: 时间范围查询

**场景**: "去年第三季度的平均工资"

**推理要点**:
- 在 thought 中明确：当前年份 → 去年 = 当前-1 → 季度日期范围
- 使用具体日期，不要用 CURRENT_DATE - INTERVAL 形式

**SQL模式**:
```sql
WHERE payment_date BETWEEN '{计算出的开始日期}' AND '{计算出的结束日期}'
-- 例如: WHERE payment_date BETWEEN '2025-07-01' AND '2025-09-30'
```

---

## 模式2: 完整月份统计

**场景**: "最近一个月的平均工资"

**关键判断**:
- 当前月份是否已结束？
- 未结束 → 使用上一个完整月份
- 已结束 → 使用当前月份

**SQL模式**:
```sql
WHERE DATE_TRUNC('month', payment_date) = DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
```

---

## 模式3: 跨期对比

**场景**: "从去年到今年工资增长最快的员工"

**技术要点**:
1. 两个 CTE 分别计算各期**整期**数据（不是单月）
2. INNER JOIN 只保留两期都有数据的对象
3. 计算变化率：(新值-旧值)/旧值*100

**SQL模式**:
```sql
WITH year_a AS (
    SELECT employee_id, AVG(salary_amount) AS avg_salary
    FROM salaries WHERE EXTRACT(YEAR FROM payment_date) = {去年}
    GROUP BY employee_id
),
year_b AS (
    SELECT employee_id, AVG(salary_amount) AS avg_salary
    FROM salaries WHERE EXTRACT(YEAR FROM payment_date) = {今年}
    GROUP BY employee_id
)
SELECT e.employee_name,
       ROUND((b.avg_salary - a.avg_salary) / a.avg_salary * 100, 2) AS growth_rate
FROM year_a a
JOIN year_b b ON a.employee_id = b.employee_id
JOIN employees e ON a.employee_id = e.employee_id
ORDER BY growth_rate DESC;
```

---

## 模式4: 完整性检测（找缺失）

**场景**: "有没有员工工资发放缺失"

**⚠️ 关键要点**:
- 必须查询**全部历史**（从入职到离职/当前），不要限制为"最近N个月"
- 生成"应该有"的完整序列
- LEFT JOIN 实际数据，IS NULL 找缺失

**SQL模式**:
```sql
WITH expected_months AS (
    SELECT 
        e.employee_id,
        e.employee_name,
        generate_series(
            DATE_TRUNC('month', e.hire_date),
            DATE_TRUNC('month', COALESCE(e.leave_date, CURRENT_DATE)),
            '1 month'::interval
        )::DATE AS expected_month
    FROM employees e
)
SELECT 
    em.employee_id,
    em.employee_name,
    TO_CHAR(em.expected_month, 'YYYY-MM') AS missing_month
FROM expected_months em
LEFT JOIN salaries s ON em.employee_id = s.employee_id 
    AND DATE_TRUNC('month', s.payment_date) = em.expected_month
WHERE s.salary_id IS NULL
    AND em.expected_month < DATE_TRUNC('month', CURRENT_DATE)
ORDER BY em.expected_month DESC, em.employee_id;
```

---

## 输出格式

**执行SQL时**:
```json
{
  "thought": "推理过程（必须展示时间计算，如'当前2026年，去年=2025年'）",
  "action": "execute_sql",
  "sql": "SELECT ...;",
  "is_final": false
}
```

**给出答案时**:
```json
{
  "thought": "基于查询结果得出结论",
  "action": "answer",
  "answer": "用自然语言直接回答用户问题",
  "is_final": true
}
```
```

**行数对比**: 从 833 行精简到约 120 行核心内容

### 9.4 参考资料

- [OpenAI Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)
- [ReAct: Synergizing Reasoning and Acting in Language Models](https://arxiv.org/abs/2210.03629)
- 极简主义设计原则: "能省则省，只保留必要的信息"

---

**文档版本**: 3.0（极简方案 + examples.txt 简化）  
**创建日期**: 2026-02-04  
**最后更新**: 2026-02-04  
**作者**: ERP Agent 开发团队

---

## 10. 总结

### 核心思想

**旧方案**: 
- 我们替 LLM 预计算所有可能需要的时间值 → 复杂、冗余、浪费
- 提供大量完整示例手把手教学 → LLM 已经具备这些能力

**新方案**: 
- 只告诉 LLM 当前日期，让它自己计算 → 简洁、灵活、高效
- 只展示本系统特有的模式，不教通用SQL → 精准、高效

### 优化对比总览

| 维度 | 修改前 | 修改后 | 改善 |
|------|--------|--------|------|
| Prompt 总行数 | 1326行 | ~587行 | **-56%** |
| Token 消耗 | ~8000 | ~3500 | **-56%** |
| 时间占位符 | 20+ | 1 | **-95%** |
| 完整示例 | 9个 | 4个模式 | **-56%** |
| 维护复杂度 | 高 | 低 | 显著降低 |

### 一句话总结

> **信任 LLM 的能力：只传递它无法获取的信息（当前日期），只展示它不知道的模式（本系统特有），只提醒它容易犯错的地方。**

### 设计原则

1. **极简主义**: 能省则省，只保留必要信息
2. **信任 LLM**: LLM 已经熟悉 SQL 和 ReAct，不需要基础教学
3. **聚焦特殊性**: 只强调本系统特有的规则和易错点
4. **单一来源**: 每条规则只在一个地方定义，避免重复和不一致
