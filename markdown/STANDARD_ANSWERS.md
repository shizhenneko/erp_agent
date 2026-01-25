# ERP Agent 测试问题标准答案

> **重要说明**: 本文档记录基于测试数据的标准答案，用于验证 ERP Agent 的回答准确性。
> 
> 生成时间: 2026-01-25
> 数据库: erp_agent_db
> 员工数: 100人
> 时间跨度: 2021-01-01 至 2026-01-25

---

## 使用说明

1. **生成标准答案**: 
   ```bash
   psql -U postgres -d erp_agent_db -f verify_answers.sql > answers_output.txt
   ```

2. **验证 Agent 回答**:
   - 运行 Agent 对每个问题生成答案
   - 对比 Agent 答案与本文档中的标准答案
   - 允许小幅误差（如小数点后几位）

3. **答案更新**:
   - 如果重新生成测试数据，需要重新运行验证脚本更新本文档

---

## 问题与标准答案

### 问题 1: 平均每个员工在公司在职多久？

**SQL 查询**:
```sql
SELECT 
    ROUND(AVG(
        CASE 
            WHEN leave_date IS NULL THEN 
                EXTRACT(EPOCH FROM (CURRENT_DATE - hire_date)) / 86400
            ELSE 
                EXTRACT(EPOCH FROM (leave_date - hire_date)) / 86400
        END
    ), 2) AS avg_days,
    ROUND(AVG(
        CASE 
            WHEN leave_date IS NULL THEN 
                EXTRACT(EPOCH FROM (CURRENT_DATE - hire_date)) / 86400 / 365.25
            ELSE 
                EXTRACT(EPOCH FROM (leave_date - hire_date)) / 86400 / 365.25
        END
    ), 2) AS avg_years
FROM employees;
```

**标准答案**:
```
待填充 - 执行 verify_answers.sql 后填写
平均天数: _______ 天
平均年数: _______ 年
```

**验证要点**:
- 在职员工计算到当前日期（2026-01-25）
- 离职员工计算到离职日期
- 结果应该在 1.5-3 年之间（根据数据分布）

---

### 问题 2: 公司每个部门有多少在职员工？

**SQL 查询**:
```sql
SELECT 
    department_name AS 部门,
    COUNT(*) AS 在职员工数
FROM employees
WHERE leave_date IS NULL
GROUP BY department_name
ORDER BY department_name;
```

**标准答案**:
```
待填充 - 执行 verify_answers.sql 后填写

A部门: _____ 人
B部门: _____ 人
C部门: _____ 人
D部门: _____ 人
E部门: _____ 人

总计: 约75人（75%在职率）
```

**验证要点**:
- 只统计 `leave_date IS NULL` 的员工
- 各部门人数加起来约等于75人

---

### 问题 3: 哪个部门的员工平均级别最高？

**SQL 查询**:
```sql
SELECT 
    department_name AS 部门,
    ROUND(AVG(current_level), 2) AS 平均级别,
    COUNT(*) AS 员工数
FROM employees
WHERE leave_date IS NULL
GROUP BY department_name
ORDER BY AVG(current_level) DESC
LIMIT 1;
```

**标准答案**:
```
待填充 - 执行 verify_answers.sql 后填写

部门: _______
平均级别: _______
员工数: _______
```

**验证要点**:
- 只统计在职员工
- 平均级别应该在 1-10 之间
- 由于随机分配，每次生成结果可能不同

---

### 问题 4: 每个部门今年和去年各新入职了多少人？

**SQL 查询**:
```sql
SELECT 
    department_name AS 部门,
    COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM hire_date) = 2026) AS 今年入职人数,
    COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM hire_date) = 2025) AS 去年入职人数
FROM employees
GROUP BY department_name
ORDER BY department_name;
```

**标准答案**:
```
待填充 - 执行 verify_answers.sql 后填写

A部门: 今年 _____ 人, 去年 _____ 人
B部门: 今年 _____ 人, 去年 _____ 人
C部门: 今年 _____ 人, 去年 _____ 人
D部门: 今年 _____ 人, 去年 _____ 人
E部门: 今年 _____ 人, 去年 _____ 人

今年总计: 7人
去年总计: 18人
```

**验证要点**:
- 今年（2026年）入职总计应为 7 人
- 去年（2025年）入职总计应为 18 人

---

### 问题 5: 从前年3月到去年5月，A部门的平均工资是多少？

**SQL 查询**:
```sql
SELECT 
    ROUND(AVG(s.salary_amount), 2) AS A部门平均工资
FROM salaries s
JOIN employees e ON s.employee_id = e.employee_id
WHERE e.department_name = 'A部门'
    AND s.payment_date >= '2024-03-01'
    AND s.payment_date <= '2025-05-31';
```

**标准答案**:
```
待填充 - 执行 verify_answers.sql 后填写

时间范围: 2024-03-01 至 2025-05-31
A部门平均工资: ¥ _________
```

**验证要点**:
- 前年 = 2024年，去年 = 2025年
- 时间范围: 2024-03-01 至 2025-05-31（共15个月）
- A部门工资应略高于平均水平

---

### 问题 6: 去年A部门和B部门的平均工资哪个高？

**SQL 查询**:
```sql
SELECT 
    e.department_name AS 部门,
    ROUND(AVG(s.salary_amount), 2) AS 去年平均工资
FROM salaries s
JOIN employees e ON s.employee_id = e.employee_id
WHERE e.department_name IN ('A部门', 'B部门')
    AND EXTRACT(YEAR FROM s.payment_date) = 2025
GROUP BY e.department_name
ORDER BY AVG(s.salary_amount) DESC;
```

**标准答案**:
```
待填充 - 执行 verify_answers.sql 后填写

A部门: ¥ _________
B部门: ¥ _________

结论: _______ 部门工资更高
```

**验证要点**:
- 去年 = 2025年
- A部门工资应该比B部门高约5%（按设计）

---

### 问题 7: 今年每个级别的员工平均工资分别是多少？

**SQL 查询**:
```sql
SELECT 
    e.current_level AS 级别,
    ROUND(AVG(s.salary_amount), 2) AS 平均工资,
    COUNT(DISTINCT e.employee_id) AS 员工数
FROM salaries s
JOIN employees e ON s.employee_id = e.employee_id
WHERE EXTRACT(YEAR FROM s.payment_date) = 2026
GROUP BY e.current_level
ORDER BY e.current_level;
```

**标准答案**:
```
待填充 - 执行 verify_answers.sql 后填写

级别1: ¥ _________ (___人)
级别2: ¥ _________ (___人)
级别3: ¥ _________ (___人)
级别4: ¥ _________ (___人)
级别5: ¥ _________ (___人)
级别6: ¥ _________ (___人)
级别7: ¥ _________ (___人)
级别8: ¥ _________ (___人)
级别9: ¥ _________ (___人)
级别10: ¥ _________ (___人)
```

**验证要点**:
- 今年 = 2026年
- 级别越高，平均工资越高
- 工资范围应符合设计（1级约6-8K，10级约45-60K）

---

### 问题 8: 入职时间一年内、一年到两年、两年到三年的员工最近一个月的平均工资是多少？

**SQL 查询**:
```sql
WITH latest_month AS (
    SELECT MAX(DATE_TRUNC('month', payment_date)) AS month
    FROM salaries
    WHERE payment_date < DATE_TRUNC('month', CURRENT_DATE)
),
employee_tenure AS (
    SELECT 
        e.employee_id,
        EXTRACT(EPOCH FROM (CURRENT_DATE - e.hire_date)) / 86400 / 365.25 AS years_employed
    FROM employees e
    WHERE e.leave_date IS NULL
)
SELECT 
    CASE 
        WHEN et.years_employed <= 1 THEN '入职一年内'
        WHEN et.years_employed > 1 AND et.years_employed <= 2 THEN '入职一年到两年'
        WHEN et.years_employed > 2 AND et.years_employed <= 3 THEN '入职两年到三年'
    END AS 入职时长分组,
    ROUND(AVG(s.salary_amount), 2) AS 平均工资,
    COUNT(DISTINCT et.employee_id) AS 员工数
FROM employee_tenure et
JOIN salaries s ON et.employee_id = s.employee_id
JOIN latest_month lm ON DATE_TRUNC('month', s.payment_date) = lm.month
WHERE et.years_employed <= 3
GROUP BY CASE 
    WHEN et.years_employed <= 1 THEN '入职一年内'
    WHEN et.years_employed > 1 AND et.years_employed <= 2 THEN '入职一年到两年'
    WHEN et.years_employed > 2 AND et.years_employed <= 3 THEN '入职两年到三年'
END
ORDER BY CASE 
    WHEN et.years_employed <= 1 THEN 1
    WHEN et.years_employed > 1 AND et.years_employed <= 2 THEN 2
    ELSE 3
END;
```

**标准答案**:
```
待填充 - 执行 verify_answers.sql 后填写

最近一个月: 2025年12月

入职一年内: ¥ _________ (___人)
入职一年到两年: ¥ _________ (___人)
入职两年到三年: ¥ _________ (___人)
```

**验证要点**:
- 最近一个月 = 最后一个完整月份（2025年12月）
- 入职时间越长，工资可能越高（但也受级别影响）
- 只统计在职员工

---

### 问题 9: 从去年到今年涨薪幅度最大的10位员工是谁？

**SQL 查询**:
```sql
WITH salary_2025 AS (
    SELECT employee_id, AVG(salary_amount) AS avg_salary_2025
    FROM salaries
    WHERE EXTRACT(YEAR FROM payment_date) = 2025
    GROUP BY employee_id
),
salary_2026 AS (
    SELECT employee_id, AVG(salary_amount) AS avg_salary_2026
    FROM salaries
    WHERE EXTRACT(YEAR FROM payment_date) = 2026
    GROUP BY employee_id
)
SELECT 
    e.employee_id, e.employee_name, e.department_name,
    ROUND(s25.avg_salary_2025, 2) AS 去年平均工资,
    ROUND(s26.avg_salary_2026, 2) AS 今年平均工资,
    ROUND((s26.avg_salary_2026 - s25.avg_salary_2025) / s25.avg_salary_2025 * 100, 2) AS 涨薪幅度百分比
FROM salary_2025 s25
JOIN salary_2026 s26 ON s25.employee_id = s26.employee_id
JOIN employees e ON s25.employee_id = e.employee_id
ORDER BY (s26.avg_salary_2026 - s25.avg_salary_2025) / s25.avg_salary_2025 DESC
LIMIT 10;
```

**标准答案**:
```
待填充 - 执行 verify_answers.sql 后填写

Top 10 涨薪幅度最大员工:

1. _______ (______) - _______部门: 涨幅 _____%
2. _______ (______) - _______部门: 涨幅 _____%
3. _______ (______) - _______部门: 涨幅 _____%
4. _______ (______) - _______部门: 涨幅 _____%
5. _______ (______) - _______部门: 涨幅 _____%
6. _______ (______) - _______部门: 涨幅 _____%
7. _______ (______) - _______部门: 涨幅 _____%
8. _______ (______) - _______部门: 涨幅 _____%
9. _______ (______) - _______部门: 涨幅 _____%
10. _______ (______) - _______部门: 涨幅 _____%
```

**验证要点**:
- 比较2025年和2026年的平均工资
- 涨幅最大的员工应该是特别设置的高涨薪员工（30-50%涨幅）
- 前8名应该是涨幅30-50%的员工

---

### 问题 10: 有没有出现过拖欠员工工资的情况？

**SQL 查询**:
```sql
WITH employee_months AS (
    SELECT 
        e.employee_id,
        e.employee_name,
        e.department_name,
        generate_series(
            DATE_TRUNC('month', e.hire_date),
            DATE_TRUNC('month', COALESCE(e.leave_date, CURRENT_DATE)),
            '1 month'::interval
        )::DATE as month
    FROM employees e
)
SELECT 
    em.employee_id, em.employee_name, em.department_name,
    TO_CHAR(em.month, 'YYYY-MM') AS 欠薪月份
FROM employee_months em
LEFT JOIN salaries s ON em.employee_id = s.employee_id 
    AND DATE_TRUNC('month', s.payment_date) = em.month
WHERE s.salary_id IS NULL
    AND em.month < DATE_TRUNC('month', CURRENT_DATE)
ORDER BY em.month DESC, em.employee_id;
```

**标准答案**:
```
待填充 - 执行 verify_answers.sql 后填写

结论: 是，存在拖欠工资情况

拖欠记录:
1. EMP088 (员工姓名) - A部门 - 2024-07
2. EMP092 (员工姓名) - B部门 - 2023-11

共 2 条拖欠记录
```

**验证要点**:
- 必须找到 EMP088 在 2024年7月 的拖欠记录
- 必须找到 EMP092 在 2023年11月 的拖欠记录
- 这两条是特意设置的测试数据

---

## 数据一致性验证

### 基础统计

```sql
-- 员工总数
SELECT COUNT(*) FROM employees;
-- 期望: 100

-- 在职员工数
SELECT COUNT(*) FROM employees WHERE leave_date IS NULL;
-- 期望: 约75

-- 工资记录总数
SELECT COUNT(*) FROM salaries;
-- 期望: 3000-5000条
```

### 数据质量检查

```sql
-- 1. 检查是否有员工没有工资记录（除了拖欠的两条）
SELECT e.employee_id, e.employee_name
FROM employees e
LEFT JOIN salaries s ON e.employee_id = s.employee_id
WHERE s.salary_id IS NULL
AND e.employee_id NOT IN ('EMP088', 'EMP092');
-- 期望: 0条

-- 2. 检查工资是否在合理范围
SELECT MIN(salary_amount), MAX(salary_amount)
FROM salaries;
-- 期望: 最低约6000，最高约60000

-- 3. 检查是否有未来日期的工资记录
SELECT COUNT(*) FROM salaries
WHERE payment_date > CURRENT_DATE;
-- 期望: 0条
```

---

## 附录：填写说明

**如何填写标准答案**:

1. 初始化数据库并导入测试数据后，执行:
   ```bash
   psql -U postgres -d erp_agent_db -f verify_answers.sql > answers_output.txt
   ```

2. 打开 `answers_output.txt` 文件

3. 将输出的结果逐一填写到本文档对应的"标准答案"部分

4. 保存本文档，作为验证 Agent 的标准答案库

5. 如果重新生成测试数据，需要重新执行步骤1-4

---

**文档版本**: v1.0
**更新日期**: 待填充（数据生成后）
**数据生成脚本**: generate_test_data.py
**验证脚本**: verify_answers.sql
