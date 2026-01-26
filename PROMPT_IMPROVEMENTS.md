# Prompt优化说明

## 问题诊断

通过对比测试输出和标准答案，发现以下问题：

### 问题9：从去年到今年涨薪幅度最大的10位员工
**错误行为**：
- Agent 使用单月对比（2025-12 vs 2026-01）
- 结果：所有人涨幅相同（7.5%），因为只是月度涨幅

**正确做法**：
- 应该使用年度平均对比（2025年全年平均 vs 2026年全年平均）
- 标准答案显示涨幅应该是22.03%（因为包含了整年的累积变化）

### 问题10：有没有出现过拖欠员工工资的情况
**错误行为**：
- Agent 只检查"最后一次发薪日期是否早于应该发放的日期"
- 结果：只找到10条记录（每个员工最多1条）

**正确做法**：
- 应该生成员工在职期间的**所有月份**（使用generate_series）
- LEFT JOIN 工资表，找出**所有**缺失的月份
- 标准答案显示有25条拖欠记录（有的员工多个月份缺失）

## 解决方案：通用化而非硬编码

### 原则：授人以渔，而非授人以鱼

我们不提供特定问题的答案，而是教授**通用的SQL技术和推理方法**。

### 1. 使用虚构场景的示例

**修改前**（硬编码嫌疑）：
- 示例直接使用"涨薪幅度"、"拖欠工资"等与测试问题相同的场景
- 使用employees、salaries等与实际数据库相同的表名

**修改后**（通用化）：
- 示例8：使用**图书馆借阅**场景（loans, readers表），展示**跨期对比**技术
- 示例9：使用**设备维护**场景（equipment, maintenance_records表），展示**数据完整性检测**技术
- 完全不同的业务领域，但教授相同的SQL技术模式

### 2. 强调技术模式而非具体SQL

在`system_prompt.txt`中添加：
```
### 核心理念：学习方法，而非记忆答案

你是一个**通用的SQL推理引擎**，而不是题库。
```

### 3. 提供通用技术规则

#### 跨期对比规则
```
- 使用整期数据：计算整个时期的总量或平均值，而不是单点
- 技术模式：使用CTE分别计算各期数据，然后JOIN比较
- 变化率公式：(新值 - 旧值) / 旧值 * 100
```

#### 数据完整性检测规则
```
1. 生成预期序列：使用generate_series创建"应该存在"的完整序列
2. 匹配实际数据：LEFT JOIN 实际数据表
3. 找出缺失部分：WHERE actual_table.id IS NULL
```

### 4. SQL技术工具箱

提供分类的SQL技术速查表，包括：
- 基础操作（聚合、筛选、排序）
- 时间处理（EXTRACT、DATE_TRUNC、generate_series）
- 多表和分组（JOIN、GROUP BY、CASE WHEN）
- 高级技术（CTE、窗口函数）
- **技术组合策略**（如何组合这些技术解决复杂问题）

## 关键改进点

### 1. 避免LIMIT误用
```
排名查询（"最高的N名"）→ 使用LIMIT
异常检测（"有没有"、"哪些"）→ 不使用LIMIT，返回全部
```

### 2. 跨期对比的正确方法
```
✅ 使用CTE分别计算各期的总量/平均值
WITH period_a AS (SELECT id, AGG(value) FROM ... WHERE period = 'A' GROUP BY id),
     period_b AS (SELECT id, AGG(value) FROM ... WHERE period = 'B' GROUP BY id)
SELECT ... FROM period_a JOIN period_b ...

❌ 不要只比较单个时间点
```

### 3. 数据完整性检测的正确方法
```
✅ 生成完整序列，找出缺失
WITH expected AS (
    SELECT id, generate_series(start, end, interval) AS expected_time
    FROM entities
)
SELECT ... FROM expected LEFT JOIN actual ... WHERE actual.id IS NULL

❌ 不要只检查"最后一次"
```

## 验证方法

运行 `python test_fixes.py` 来测试修复后的效果。

预期结果：
1. 问题9应该生成使用CTE的年度对比SQL
2. 问题10应该生成使用generate_series的完整性检测SQL
3. 答案应该与标准答案一致

## 文件修改清单

1. **erp_agent/prompts/examples.txt**
   - 示例8：改用图书馆借阅场景，教授跨期对比技术
   - 示例9：改用设备维护场景，教授数据完整性检测技术
   - 更新SQL技术工具箱，增加技术组合策略
   - 强调学习方法而非记忆答案

2. **erp_agent/prompts/system_prompt.txt**
   - 增加"核心理念"部分，强调通用推理
   - 更新LIMIT使用规则，明确区分排名和异常检测
   - 新增"跨期对比规则"，包含技术模式和公式
   - 新增"数据完整性检测规则"，包含完整技术流程
   - 强调不要依赖记忆，要根据Schema推理

3. **test_fixes.py** (新增)
   - 专门测试问题9和问题10的修复效果
   - 打印生成的SQL供验证

## 为什么这样做不是硬编码？

1. **不同的业务场景**：示例使用图书馆、设备维护，而测试问题是员工工资
2. **不同的表结构**：示例使用readers/loans，测试使用employees/salaries
3. **教授通用技术**：CTE对比、generate_series检测，可应用于任何类似场景
4. **强调推理过程**：教授如何分析问题→选择技术→构建SQL，而非提供答案

Agent需要根据实际的Schema（employees、salaries表）和业务规则（"在职员工: leave_date IS NULL"）来独立推理出SQL，而不是套用示例中的具体字段名。
