-- =====================================================
-- ERP Agent 测试问题验证脚本
-- 生成10个问题的标准答案
-- 执行方式: psql -U postgres -d erp_agent_db -f verify_answers.sql
-- =====================================================

\echo '====================================================================='
\echo 'ERP Agent 测试问题标准答案验证'
\echo '执行时间:' 
\echo '====================================================================='
\echo ''

-- =====================================================
-- 问题1: 平均每个员工在公司在职多久？
-- =====================================================
\echo '【问题1】平均每个员工在公司在职多久？'
\echo '---------------------------------------------------------------------'

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

\echo ''
\echo ''

-- =====================================================
-- 问题2: 公司每个部门有多少在职员工？
-- =====================================================
\echo '【问题2】公司每个部门有多少在职员工？'
\echo '---------------------------------------------------------------------'

SELECT 
    department_name AS 部门,
    COUNT(*) AS 在职员工数
FROM employees
WHERE leave_date IS NULL
GROUP BY department_name
ORDER BY department_name;

\echo ''
\echo ''

-- =====================================================
-- 问题3: 哪个部门的员工平均级别最高？
-- =====================================================
\echo '【问题3】哪个部门的员工平均级别最高？'
\echo '---------------------------------------------------------------------'

SELECT 
    department_name AS 部门,
    ROUND(AVG(current_level), 2) AS 平均级别,
    COUNT(*) AS 员工数
FROM employees
WHERE leave_date IS NULL
GROUP BY department_name
ORDER BY AVG(current_level) DESC
LIMIT 1;

\echo ''
\echo ''

-- =====================================================
-- 问题4: 每个部门今年和去年各新入职了多少人？
-- =====================================================
\echo '【问题4】每个部门今年和去年各新入职了多少人？'
\echo '---------------------------------------------------------------------'

SELECT 
    department_name AS 部门,
    COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM hire_date) = 2026) AS 今年入职人数,
    COUNT(*) FILTER (WHERE EXTRACT(YEAR FROM hire_date) = 2025) AS 去年入职人数
FROM employees
GROUP BY department_name
ORDER BY department_name;

\echo ''
\echo ''

-- =====================================================
-- 问题5: 从前年3月到去年5月，A部门的平均工资是多少？
-- =====================================================
\echo '【问题5】从前年3月到去年5月，A部门的平均工资是多少？'
\echo '说明：前年=2024年，去年=2025年，时间范围：2024-03-01 至 2025-05-31'
\echo '---------------------------------------------------------------------'

SELECT 
    ROUND(AVG(s.salary_amount), 2) AS A部门平均工资
FROM salaries s
JOIN employees e ON s.employee_id = e.employee_id
WHERE e.department_name = 'A部门'
    AND s.payment_date >= '2024-03-01'
    AND s.payment_date <= '2025-05-31';

\echo ''
\echo ''

-- =====================================================
-- 问题6: 去年A部门和B部门的平均工资哪个高？
-- =====================================================
\echo '【问题6】去年A部门和B部门的平均工资哪个高？'
\echo '说明：去年=2025年'
\echo '---------------------------------------------------------------------'

SELECT 
    e.department_name AS 部门,
    ROUND(AVG(s.salary_amount), 2) AS 去年平均工资
FROM salaries s
JOIN employees e ON s.employee_id = e.employee_id
WHERE e.department_name IN ('A部门', 'B部门')
    AND EXTRACT(YEAR FROM s.payment_date) = 2025
GROUP BY e.department_name
ORDER BY AVG(s.salary_amount) DESC;

\echo ''
\echo ''

-- =====================================================
-- 问题7: 今年每个级别的员工平均工资分别是多少？
-- =====================================================
\echo '【问题7】今年每个级别的员工平均工资分别是多少？'
\echo '说明：今年=2026年'
\echo '---------------------------------------------------------------------'

SELECT 
    e.current_level AS 级别,
    ROUND(AVG(s.salary_amount), 2) AS 平均工资,
    COUNT(DISTINCT e.employee_id) AS 员工数
FROM salaries s
JOIN employees e ON s.employee_id = e.employee_id
WHERE EXTRACT(YEAR FROM s.payment_date) = 2026
GROUP BY e.current_level
ORDER BY e.current_level;

\echo ''
\echo ''

-- =====================================================
-- 问题8: 入职时间一年内、一年到两年、两年到三年的员工最近一个月的平均工资是多少？
-- =====================================================
\echo '【问题8】入职时间一年内、一年到两年、两年到三年的员工最近一个月的平均工资是多少？'
\echo '说明：最近一个月=2025年12月（最后完整月份）'
\echo '---------------------------------------------------------------------'

WITH latest_month AS (
    SELECT MAX(DATE_TRUNC('month', payment_date)) AS month
    FROM salaries
    WHERE payment_date < DATE_TRUNC('month', CURRENT_DATE)
),
employee_tenure AS (
    SELECT 
        e.employee_id,
        e.employee_name,
        e.hire_date,
        EXTRACT(EPOCH FROM (CURRENT_DATE - e.hire_date)) / 86400 / 365.25 AS years_employed
    FROM employees e
    WHERE e.leave_date IS NULL
)
SELECT 
    CASE 
        WHEN et.years_employed <= 1 THEN '入职一年内'
        WHEN et.years_employed > 1 AND et.years_employed <= 2 THEN '入职一年到两年'
        WHEN et.years_employed > 2 AND et.years_employed <= 3 THEN '入职两年到三年'
        ELSE '入职三年以上'
    END AS 入职时长分组,
    ROUND(AVG(s.salary_amount), 2) AS 平均工资,
    COUNT(DISTINCT et.employee_id) AS 员工数
FROM employee_tenure et
JOIN salaries s ON et.employee_id = s.employee_id
JOIN latest_month lm ON DATE_TRUNC('month', s.payment_date) = lm.month
WHERE et.years_employed <= 3
GROUP BY 
    CASE 
        WHEN et.years_employed <= 1 THEN '入职一年内'
        WHEN et.years_employed > 1 AND et.years_employed <= 2 THEN '入职一年到两年'
        WHEN et.years_employed > 2 AND et.years_employed <= 3 THEN '入职两年到三年'
        ELSE '入职三年以上'
    END
ORDER BY 
    CASE 
        WHEN et.years_employed <= 1 THEN 1
        WHEN et.years_employed > 1 AND et.years_employed <= 2 THEN 2
        WHEN et.years_employed > 2 AND et.years_employed <= 3 THEN 3
        ELSE 4
    END;

\echo ''
\echo ''

-- =====================================================
-- 问题9: 从去年到今年涨薪幅度最大的10位员工是谁？
-- =====================================================
\echo '【问题9】从去年到今年涨薪幅度最大的10位员工是谁？'
\echo '说明：比较2025年和2026年同月工资涨幅'
\echo '---------------------------------------------------------------------'

WITH salary_2025 AS (
    SELECT 
        employee_id,
        AVG(salary_amount) AS avg_salary_2025
    FROM salaries
    WHERE EXTRACT(YEAR FROM payment_date) = 2025
    GROUP BY employee_id
),
salary_2026 AS (
    SELECT 
        employee_id,
        AVG(salary_amount) AS avg_salary_2026
    FROM salaries
    WHERE EXTRACT(YEAR FROM payment_date) = 2026
    GROUP BY employee_id
)
SELECT 
    e.employee_id AS 员工ID,
    e.employee_name AS 员工姓名,
    e.department_name AS 部门,
    ROUND(s25.avg_salary_2025, 2) AS 去年平均工资,
    ROUND(s26.avg_salary_2026, 2) AS 今年平均工资,
    ROUND(s26.avg_salary_2026 - s25.avg_salary_2025, 2) AS 涨薪金额,
    ROUND((s26.avg_salary_2026 - s25.avg_salary_2025) / s25.avg_salary_2025 * 100, 2) AS 涨薪幅度百分比
FROM salary_2025 s25
JOIN salary_2026 s26 ON s25.employee_id = s26.employee_id
JOIN employees e ON s25.employee_id = e.employee_id
ORDER BY (s26.avg_salary_2026 - s25.avg_salary_2025) / s25.avg_salary_2025 DESC
LIMIT 10;

\echo ''
\echo ''

-- =====================================================
-- 问题10: 有没有出现过拖欠员工工资的情况？
-- =====================================================
\echo '【问题10】有没有出现过拖欠员工工资的情况？'
\echo '说明：检查在职期间是否有月份未发薪'
\echo '---------------------------------------------------------------------'

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
    em.employee_id AS 员工ID,
    em.employee_name AS 员工姓名,
    em.department_name AS 部门,
    TO_CHAR(em.month, 'YYYY-MM') AS 欠薪月份
FROM employee_months em
LEFT JOIN salaries s ON em.employee_id = s.employee_id 
    AND DATE_TRUNC('month', s.payment_date) = em.month
WHERE s.salary_id IS NULL
    AND em.month < DATE_TRUNC('month', CURRENT_DATE)
ORDER BY em.month DESC, em.employee_id;

\echo ''
\echo '====================================================================='
\echo '验证完成'
\echo '====================================================================='
