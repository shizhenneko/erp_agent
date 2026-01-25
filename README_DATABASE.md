# ERP Agent 数据库初始化使用说明

## 📋 概述

本文档说明如何快速完成 ERP Agent 数据库的初始化和测试数据生成。

## 🚀 快速开始

### 前置要求

1. **PostgreSQL 已安装** (版本 12 或更高)
   - Windows: https://www.postgresql.org/download/windows/
   - 默认端口: 5432
   - 确保记住超级用户 `postgres` 的密码

2. **Python 3.7+** (用于生成测试数据)
   - 需要安装 `psycopg2` 库

### 步骤一：安装 Python 依赖

```bash
pip install psycopg2-binary
```

### 步骤二：初始化数据库结构

**方法1: 使用 psql 命令行**

```bash
# 1. 进入 psql
psql -U postgres

# 2. 执行初始化脚本
\i init_database.sql

# 3. 连接到新创建的数据库
\c erp_agent_db
```

**方法2: 直接执行 SQL 文件**

```bash
psql -U postgres -f init_database.sql
psql -U postgres -d erp_agent_db -f init_database.sql
```

### 步骤三：生成并导入测试数据

1. **修改数据库连接配置**

编辑 `generate_test_data.py` 文件，修改以下配置：

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'erp_agent_db',
    'user': 'postgres',
    'password': '你的postgres密码'  # 修改为你的密码
}
```

2. **运行数据生成脚本**

```bash
python generate_test_data.py
```

脚本将自动：
- 生成 100 名员工数据
- 生成 5 年内的工资记录（2021-2026）
- 插入测试数据到数据库
- 验证数据完整性

### 步骤四：验证测试问题答案

执行验证脚本，获取10个测试问题的标准答案：

```bash
psql -U postgres -d erp_agent_db -f verify_answers.sql > standard_answers.txt
```

或者在 psql 内执行：

```sql
\c erp_agent_db
\i verify_answers.sql
```

## 📊 生成的数据特点

### 员工数据（100人）

- **部门分布**:
  - A部门: 25人
  - B部门: 23人
  - C部门: 20人
  - D部门: 18人
  - E部门: 14人

- **级别分布**:
  - 1-3级（初级）: 50人
  - 4-6级（中级）: 30人
  - 7-8级（高级）: 15人
  - 9-10级（专家）: 5人

- **在职状态**:
  - 在职: 75人 (75%)
  - 离职: 25人 (25%)

- **入职时间分布**:
  - 2021年: 15人
  - 2022年: 20人
  - 2023年: 18人
  - 2024年: 22人
  - 2025年: 18人
  - 2026年: 7人

### 工资数据

- **发薪规则**: 每月25号发薪
- **时间跨度**: 2021-01 至 2026-01
- **工资范围**: 6,000-60,000元（根据级别）
- **增长规律**:
  - 每年自然增长 5-10%
  - 特殊涨薪员工（8人）在2025年涨薪30-50%

### 特殊测试场景

为了测试 Agent 的健壮性，包含以下特殊场景：

1. **拖欠工资场景**（问题10）:
   - `EMP088`: 2024年7月在职但无工资记录
   - `EMP092`: 2023年11月在职但无工资记录

2. **高涨薪员工**（问题9）:
   - 8名员工在2025年涨薪幅度达到30-50%

3. **A部门工资略高**（问题6）:
   - A部门平均工资比其他部门高约5%

## 🔍 验证数据完整性

执行以下 SQL 验证数据：

```sql
-- 1. 检查员工总数
SELECT COUNT(*) FROM employees;
-- 期望: 100

-- 2. 检查在职员工数
SELECT COUNT(*) FROM employees WHERE leave_date IS NULL;
-- 期望: 约75

-- 3. 检查各部门人数
SELECT department_name, COUNT(*) 
FROM employees 
GROUP BY department_name 
ORDER BY department_name;

-- 4. 检查工资记录数
SELECT COUNT(*) FROM salaries;
-- 期望: 3000-5000条

-- 5. 检查拖欠工资情况
-- 见 verify_answers.sql 中的问题10
```

## 📝 10个测试问题

1. 平均每个员工在公司在职多久？
2. 公司每个部门有多少在职员工？
3. 哪个部门的员工平均级别最高？
4. 每个部门今年和去年各新入职了多少人？
5. 从前年3月到去年5月，A部门的平均工资是多少？
6. 去年A部门和B部门的平均工资哪个高？
7. 今年每个级别的员工平均工资分别是多少？
8. 入职时间一年内、一年到两年、两年到三年的员工最近一个月的平均工资是多少？
9. 从去年到今年涨薪幅度最大的10位员工是谁？
10. 有没有出现过拖欠员工工资的情况，也就是某个月员工在职但是没有发薪？

## 🗄 数据库连接信息

初始化完成后，使用以下信息连接数据库：

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'erp_agent_db',
    'user': 'erp_agent_user',    # 只读用户（用于Agent）
    'password': 'erp_agent_2026'
}
```

或使用超级用户（开发时）：

```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'erp_agent_db',
    'user': 'postgres',
    'password': '你的postgres密码'
}
```

## 🔧 常见问题

### 1. 连接被拒绝

```
psycopg2.OperationalError: could not connect to server
```

**解决方案**:
- 确认 PostgreSQL 服务已启动
- Windows: 检查服务管理器中的 postgresql-x64-xx 服务
- 检查端口 5432 是否被占用

### 2. 编码错误

```
UnicodeDecodeError: 'utf-8' codec can't decode
```

**解决方案**:
- 确保 Python 脚本使用 UTF-8 编码保存
- 在脚本开头添加: `# -*- coding: utf-8 -*-`

### 3. 权限不足

```
ERROR: permission denied for table employees
```

**解决方案**:
- 确保已执行 `init_database.sql` 中的授权语句
- 或使用 `postgres` 超级用户连接

### 4. psycopg2 安装失败

```
ERROR: Failed building wheel for psycopg2
```

**解决方案**:
- 安装二进制版本: `pip install psycopg2-binary`
- 或安装编译依赖后再安装

## 📋 检查清单

初始化完成后，请确认：

- [x] PostgreSQL 服务运行正常（端口 5432）
- [x] 数据库 `erp_agent_db` 已创建
- [x] 用户 `erp_agent_user` 已创建并授权
- [x] `employees` 表包含 100 条记录
- [x] `salaries` 表包含数千条记录
- [x] 所有索引已创建
- [x] 测试数据已验证（包含拖欠工资等特殊场景）
- [x] 10个问题的标准答案已记录

## 🔄 重新初始化

如需重新生成数据：

```bash
# 1. 重新执行初始化脚本（会删除现有数据）
psql -U postgres -f init_database.sql

# 2. 重新生成测试数据
python generate_test_data.py

# 3. 重新验证答案
psql -U postgres -d erp_agent_db -f verify_answers.sql
```

## 📞 技术支持

如有问题，请参考：
- `database_setup.md` - 详细的数据库设计文档
- `develop.md` - Agent 开发需求文档
- `agent_development.md` - Agent 实现指南

---

**下一步**: 参考 `agent_development.md` 开始开发 ERP Agent
