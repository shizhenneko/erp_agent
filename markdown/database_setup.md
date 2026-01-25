# PostgreSQL 数据库设计与初始化

## 📋 概述

本文档详细描述 ERP Agent 系统所需的 PostgreSQL 数据库设计、表结构、测试数据生成策略以及初始化步骤。

## 🗄 数据库设计

### 数据库基本信息

- **数据库名称**: `erp_agent_db`
- **字符集**: UTF-8
- **时区**: Asia/Shanghai (或根据实际需求调整)

### 表结构设计

#### 1. 员工表 (employees)

**表名**: `employees`

**字段说明**:

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| employee_id | VARCHAR(20) | PRIMARY KEY | 员工ID，如 EMP001 |
| employee_name | VARCHAR(100) | NOT NULL | 员工姓名 |
| department_name | VARCHAR(50) | NOT NULL | 部门名称（A部门、B部门等）|
| current_level | INTEGER | NOT NULL, CHECK (current_level >= 1 AND current_level <= 10) | 当前级别，1-10级 |
| hire_date | DATE | NOT NULL | 入职日期 |
| leave_date | DATE | NULL | 离职日期，NULL表示在职 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |
| updated_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 记录更新时间 |

**索引**:
- 主键索引：`employee_id`
- 普通索引：`department_name` (加速部门查询)
- 普通索引：`hire_date` (加速时间范围查询)
- 部分索引：`WHERE leave_date IS NULL` (加速在职员工查询)

**约束**:
- `CHECK (leave_date IS NULL OR leave_date >= hire_date)` 确保离职日期晚于入职日期

#### 2. 工资表 (salaries)

**表名**: `salaries`

**字段说明**:

| 字段名 | 数据类型 | 约束 | 说明 |
|--------|---------|------|------|
| salary_id | SERIAL | PRIMARY KEY | 工资记录ID，自增 |
| employee_id | VARCHAR(20) | NOT NULL, FOREIGN KEY | 员工ID，外键关联employees表 |
| payment_date | DATE | NOT NULL | 发薪日期，通常是每月某一天 |
| salary_amount | DECIMAL(10,2) | NOT NULL, CHECK (salary_amount >= 0) | 工资金额，保留两位小数 |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | 记录创建时间 |

**索引**:
- 主键索引：`salary_id`
- 唯一索引：`(employee_id, payment_date)` 防止同一员工同一天重复发薪
- 普通索引：`payment_date` (加速时间范围查询)

**外键约束**:
- `FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE`

## 📊 测试数据设计策略

### 数据量规划

- **员工数量**: 80-100人
- **部门数量**: 5个（A部门、B部门、C部门、D部门、E部门）
- **级别分布**: 1-10级，符合金字塔结构（低级别人多，高级别人少）
- **时间跨度**: 2021年1月 - 2026年1月（5年）
- **工资记录**: 每个在职员工每月一条记录

### 数据分布设计

#### 员工分布
```
部门分布（总100人）：
- A部门：25人（25%）
- B部门：23人（23%）
- C部门：20人（20%）
- D部门：18人（18%）
- E部门：14人（14%）

级别分布：
- 1-3级（初级）：50人（50%）
- 4-6级（中级）：30人（30%）
- 7-8级（高级）：15人（15%）
- 9-10级（专家）：5人（5%）

在职状态：
- 在职员工：75人（75%）
- 离职员工：25人（25%）
```

#### 入职时间分布
```
- 2021年：15人（老员工）
- 2022年：20人
- 2023年：18人
- 2024年：22人（前年）
- 2025年：18人（去年）
- 2026年：7人（今年，截至1月）
```

#### 工资水平设计
```
基础工资（按级别）：
- 1级：6000-8000元
- 2级：8000-10000元
- 3级：10000-12000元
- 4级：12000-15000元
- 5级：15000-18000元
- 6级：18000-22000元
- 7级：22000-28000元
- 8级：28000-35000元
- 9级：35000-45000元
- 10级：45000-60000元

工资变化规律：
- 每年有5-10%的自然增长
- 升职时涨幅15-25%
- 部门间差异：A部门平均工资略高于B部门（用于回答问题6）
```

### 边界情况和特殊场景

为了测试 Agent 的健壮性，需要包含以下特殊场景：

1. **拖欠工资场景**（回答问题10）
   - 员工 EMP088：2024年7月在职但无工资记录
   - 员工 EMP092：2023年11月在职但无工资记录

2. **涨薪幅度大的员工**（回答问题9）
   - 5-8名员工在2025-2026年间涨薪30-50%（升职或特殊调薪）

3. **入职即离职**
   - 2-3名员工入职不到3个月就离职

4. **跨年入职**
   - 部分员工在年底入职（12月），用于测试跨年统计

5. **同月多部门入职**
   - 确保每个部门在2024、2025年都有新入职员工

## 🚀 初始化步骤

### Step 1: 安装 PostgreSQL

**Windows**:
```bash
# 下载 PostgreSQL 安装程序
# https://www.postgresql.org/download/windows/
# 建议版本：PostgreSQL 14 或更高

# 安装时记录：
# - 端口：5432（默认）
# - 超级用户密码：设置一个强密码
```

**验证安装**:
```bash
psql --version
```

### Step 2: 创建数据库和用户

```sql
-- 连接到 PostgreSQL
-- psql -U postgres

-- 创建数据库
CREATE DATABASE erp_agent_db
    WITH 
    ENCODING = 'UTF8'
    LC_COLLATE = 'zh_CN.UTF-8'
    LC_CTYPE = 'zh_CN.UTF-8'
    TEMPLATE = template0;

-- 创建只读用户（用于 Agent 查询，安全考虑）
CREATE USER erp_agent_user WITH PASSWORD 'your_secure_password';

-- 授予连接权限
GRANT CONNECT ON DATABASE erp_agent_db TO erp_agent_user;

-- 切换到 erp_agent_db
\c erp_agent_db

-- 授予 schema 使用权限
GRANT USAGE ON SCHEMA public TO erp_agent_user;
```

### Step 3: 创建表结构

```sql
-- 切换到数据库
\c erp_agent_db

-- 创建员工表
CREATE TABLE employees (
    employee_id VARCHAR(20) PRIMARY KEY,
    employee_name VARCHAR(100) NOT NULL,
    department_name VARCHAR(50) NOT NULL,
    current_level INTEGER NOT NULL CHECK (current_level >= 1 AND current_level <= 10),
    hire_date DATE NOT NULL,
    leave_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT check_leave_date CHECK (leave_date IS NULL OR leave_date >= hire_date)
);

-- 创建工资表
CREATE TABLE salaries (
    salary_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL,
    payment_date DATE NOT NULL,
    salary_amount DECIMAL(10,2) NOT NULL CHECK (salary_amount >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    UNIQUE(employee_id, payment_date)
);

-- 创建索引
CREATE INDEX idx_employees_department ON employees(department_name);
CREATE INDEX idx_employees_hire_date ON employees(hire_date);
CREATE INDEX idx_employees_active ON employees(leave_date) WHERE leave_date IS NULL;
CREATE INDEX idx_salaries_payment_date ON salaries(payment_date);
CREATE INDEX idx_salaries_employee_date ON salaries(employee_id, payment_date);

-- 授予查询权限给 Agent 用户
GRANT SELECT ON employees TO erp_agent_user;
GRANT SELECT ON salaries TO erp_agent_user;
GRANT USAGE ON SEQUENCE salaries_salary_id_seq TO erp_agent_user;
```

### Step 4: 生成测试数据

**方式一：使用 Python 脚本生成**（推荐）

创建 `generate_test_data.py` 脚本：

```python
# 见附录：Python 数据生成脚本模板
# 该脚本会生成符合上述规划的测试数据
```

**方式二：使用 SQL 脚本**

创建 `insert_test_data.sql` 脚本（适合小量数据）

### Step 5: 验证数据完整性

```sql
-- 验证员工数量
SELECT COUNT(*) as total_employees FROM employees;
-- 期望：80-100

-- 验证在职员工数量
SELECT COUNT(*) as active_employees 
FROM employees 
WHERE leave_date IS NULL;
-- 期望：约75

-- 验证各部门人数
SELECT department_name, COUNT(*) as count 
FROM employees 
GROUP BY department_name 
ORDER BY count DESC;

-- 验证工资记录数量
SELECT COUNT(*) as total_salary_records FROM salaries;
-- 期望：数千到数万条（取决于时间跨度）

-- 验证是否有拖欠工资情况（应该有2-3条）
WITH employee_months AS (
    SELECT 
        e.employee_id,
        generate_series(
            DATE_TRUNC('month', e.hire_date),
            DATE_TRUNC('month', COALESCE(e.leave_date, CURRENT_DATE)),
            '1 month'::interval
        )::DATE as month
    FROM employees e
)
SELECT 
    em.employee_id,
    em.month,
    e.employee_name,
    e.department_name
FROM employee_months em
JOIN employees e ON em.employee_id = e.employee_id
LEFT JOIN salaries s ON em.employee_id = s.employee_id 
    AND DATE_TRUNC('month', s.payment_date) = em.month
WHERE s.salary_id IS NULL
    AND em.month < DATE_TRUNC('month', CURRENT_DATE)
ORDER BY em.month DESC;

-- 验证工资范围是否合理
SELECT 
    MIN(salary_amount) as min_salary,
    AVG(salary_amount) as avg_salary,
    MAX(salary_amount) as max_salary
FROM salaries;
```

## 📝 Schema 文档（供 Agent 使用）

以下是提供给 Agent 的详细 Schema 说明，用于 Few-shot Learning：

```markdown
### 数据库 Schema 说明

#### 表1: employees (员工表)
- employee_id (VARCHAR): 员工唯一标识，如 'EMP001'
- employee_name (VARCHAR): 员工姓名
- department_name (VARCHAR): 部门名称，值为 'A部门', 'B部门', 'C部门', 'D部门', 'E部门'
- current_level (INTEGER): 当前职级，范围 1-10，数字越大级别越高
- hire_date (DATE): 入职日期
- leave_date (DATE): 离职日期，NULL 表示该员工仍在职

#### 表2: salaries (工资表)
- salary_id (INTEGER): 工资记录ID，主键
- employee_id (VARCHAR): 员工ID，关联 employees 表
- payment_date (DATE): 发薪日期，通常每月一条记录
- salary_amount (DECIMAL): 工资金额（元）

#### 重要业务规则
1. 在职员工判断：`leave_date IS NULL`
2. 每个员工每月应该有一条工资记录（正常情况）
3. 工资记录仅在员工入职后才会有
4. 离职员工在离职后不再有工资记录

#### 时间相关说明
- 当前日期会在查询时动态提供
- "今年" = 当前年份
- "去年" = 当前年份 - 1
- "前年" = 当前年份 - 2
- "最近一个月" = 最近一个完整的月份
```

## 🔧 维护和管理

### 数据备份

```bash
# 备份数据库
pg_dump -U postgres -d erp_agent_db -F c -f erp_agent_db_backup.dump

# 恢复数据库
pg_restore -U postgres -d erp_agent_db -c erp_agent_db_backup.dump
```

### 性能优化

```sql
-- 定期更新统计信息
ANALYZE employees;
ANALYZE salaries;

-- 检查表大小
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
```

### 常用查询（调试用）

```sql
-- 查看某个员工的完整工资历史
SELECT 
    e.employee_name,
    e.department_name,
    s.payment_date,
    s.salary_amount
FROM employees e
JOIN salaries s ON e.employee_id = s.employee_id
WHERE e.employee_id = 'EMP001'
ORDER BY s.payment_date;

-- 查看2025年的入职员工
SELECT 
    employee_id,
    employee_name,
    department_name,
    hire_date
FROM employees
WHERE EXTRACT(YEAR FROM hire_date) = 2025
ORDER BY hire_date;
```

## 📋 检查清单

完成数据库初始化后，请确认：

- [ ] PostgreSQL 已安装并运行（端口 5432）
- [ ] 数据库 `erp_agent_db` 已创建
- [ ] 用户 `erp_agent_user` 已创建并授权
- [ ] `employees` 表已创建，包含 80-100 条记录
- [ ] `salaries` 表已创建，包含数千条记录
- [ ] 所有索引已创建
- [ ] 测试数据已验证（包含边界情况）
- [ ] Schema 文档已准备好供 Agent 使用
- [ ] 数据库连接信息已记录（host, port, database, user, password）

## 📄 附录：连接信息模板

```python
# database_config.py
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'erp_agent_db',
    'user': 'erp_agent_user',
    'password': 'your_secure_password'
}
```

---

**下一步**: 参考 `agent_development.md` 开始开发 ERP Agent
