# 🚀 ERP Agent 数据库快速启动指南

## 📦 生成的文件清单

本次为您生成了以下文件：

### 核心脚本
1. **`init_database.sql`** - 数据库初始化脚本（建表、索引、用户）
2. **`generate_test_data.py`** - Python 测试数据生成脚本（100人、5年数据）
3. **`verify_answers.sql`** - SQL 查询验证脚本（获取10个问题的标准答案）

### 自动化脚本
4. **`setup_database.ps1`** - Windows PowerShell 一键执行脚本

### 文档
5. **`README_DATABASE.md`** - 详细使用说明文档
6. **`STANDARD_ANSWERS.md`** - 标准答案模板（需要填充）
7. **`QUICKSTART.md`** - 本文件（快速启动指南）
8. **`requirements.txt`** - Python 依赖列表

---

## ⚡ 快速开始（3种方式）

### 方式1：一键自动化（推荐）✨

**适合**: 初次使用，希望快速完成初始化

```powershell
# 1. 修改 setup_database.ps1 中的 PostgreSQL 密码（第9行）
# 2. 右键点击 setup_database.ps1 -> 使用 PowerShell 运行
# 或在 PowerShell 中执行：
.\setup_database.ps1
```

**完成后将自动**:
- ✅ 创建数据库和表结构
- ✅ 生成100名员工数据
- ✅ 生成5年工资记录
- ✅ 生成标准答案文件

---

### 方式2：分步手动执行

**适合**: 需要了解每一步细节，或自动化脚本遇到问题

#### 步骤1：安装依赖
```bash
pip install -r requirements.txt
```

#### 步骤2：初始化数据库
```bash
# 方式A: 使用 psql 命令行
psql -U postgres -f init_database.sql

# 方式B: 在 psql 交互界面中
psql -U postgres
\i init_database.sql
```

#### 步骤3：生成测试数据
```bash
# 1. 修改 generate_test_data.py 中的数据库密码（第24行）
# 2. 运行脚本
python generate_test_data.py
```

#### 步骤4：生成标准答案
```bash
psql -U postgres -d erp_agent_db -f verify_answers.sql > standard_answers_output.txt
```

---

### 方式3：Docker 容器（可选）

**适合**: 不想在本机安装 PostgreSQL

```bash
# 1. 启动 PostgreSQL 容器
docker run --name erp-postgres \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres:14

# 2. 等待容器启动（约5秒）
sleep 5

# 3. 执行初始化脚本
docker exec -i erp-postgres psql -U postgres < init_database.sql

# 4. 生成测试数据（修改 generate_test_data.py 后执行）
python generate_test_data.py

# 5. 生成标准答案
docker exec -i erp-postgres psql -U postgres -d erp_agent_db < verify_answers.sql > standard_answers_output.txt
```

---

## 🔍 验证安装

执行以下命令验证数据是否正确导入：

```sql
-- 连接数据库
psql -U postgres -d erp_agent_db

-- 验证员工数量
SELECT COUNT(*) FROM employees;
-- 期望: 100

-- 验证在职员工数量
SELECT COUNT(*) FROM employees WHERE leave_date IS NULL;
-- 期望: 约75

-- 验证工资记录数量
SELECT COUNT(*) FROM salaries;
-- 期望: 3000-5000

-- 验证拖欠工资情况（应有2条）
-- 见 verify_answers.sql 问题10
```

---

## 📊 查看标准答案

初始化完成后，标准答案会保存在 `standard_answers_output.txt` 文件中。

**10个测试问题**:

1. 平均每个员工在公司在职多久？
2. 公司每个部门有多少在职员工？
3. 哪个部门的员工平均级别最高？
4. 每个部门今年和去年各新入职了多少人？
5. 从前年3月到去年5月，A部门的平均工资是多少？
6. 去年A部门和B部门的平均工资哪个高？
7. 今年每个级别的员工平均工资分别是多少？
8. 入职时间一年内、一年到两年、两年到三年的员工最近一个月的平均工资是多少？
9. 从去年到今年涨薪幅度最大的10位员工是谁？
10. 有没有出现过拖欠员工工资的情况？

**操作**:
1. 打开 `standard_answers_output.txt`
2. 查看每个问题的查询结果
3. 将结果填写到 `STANDARD_ANSWERS.md` 文档中
4. 使用这些答案验证 ERP Agent 的回答准确性

---

## 🗄 数据库连接信息

初始化完成后，使用以下信息连接数据库：

### Agent 使用（只读权限）
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'erp_agent_db',
    'user': 'erp_agent_user',
    'password': 'erp_agent_2026'
}
```

### 开发调试使用（完整权限）
```python
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'erp_agent_db',
    'user': 'postgres',
    'password': '你的postgres密码'
}
```

---

## 🎯 测试数据特点

### 员工数据（100人）
- **A部门**: 25人
- **B部门**: 23人
- **C部门**: 20人
- **D部门**: 18人
- **E部门**: 14人

### 级别分布
- **1-3级**（初级）: 50人
- **4-6级**（中级）: 30人
- **7-8级**（高级）: 15人
- **9-10级**（专家）: 5人

### 在职状态
- **在职**: 75人（75%）
- **离职**: 25人（25%）

### 时间跨度
- **2021年**: 15人入职
- **2022年**: 20人入职
- **2023年**: 18人入职
- **2024年**: 22人入职
- **2025年**: 18人入职
- **2026年**: 7人入职（截至1月25日）

### 特殊测试场景

✅ **拖欠工资**（问题10）:
- `EMP088`: 2024年7月在职但无工资记录
- `EMP092`: 2023年11月在职但无工资记录

✅ **高涨薪员工**（问题9）:
- 8名员工在2025年涨薪30-50%

✅ **A部门工资略高**（问题6）:
- A部门平均工资比其他部门高约5%

---

## ❓ 常见问题

### Q1: 连接数据库失败

**错误**: `psycopg2.OperationalError: could not connect to server`

**解决**:
1. 确认 PostgreSQL 服务已启动
2. Windows: 打开"服务"，查找 `postgresql-x64-xx`
3. 检查端口 5432 是否被占用

### Q2: 密码错误

**错误**: `FATAL: password authentication failed`

**解决**:
1. 修改 `generate_test_data.py` 第24行的密码
2. 或修改 `setup_database.ps1` 第9行的密码

### Q3: Python 找不到模块

**错误**: `ModuleNotFoundError: No module named 'psycopg2'`

**解决**:
```bash
pip install psycopg2-binary
```

### Q4: 如何重新初始化？

**步骤**:
1. 删除现有数据库（可选）
   ```sql
   DROP DATABASE erp_agent_db;
   ```
2. 重新执行初始化脚本
   ```bash
   psql -U postgres -f init_database.sql
   python generate_test_data.py
   ```

---

## 📚 相关文档

- **`database_setup.md`** - 数据库设计详细说明
- **`develop.md`** - ERP Agent 需求文档
- **`agent_development.md`** - Agent 实现指南（如果有）
- **`README_DATABASE.md`** - 完整使用说明

---

## 🎉 下一步

数据库初始化完成后，您可以：

1. ✅ **验证数据**: 运行 `verify_answers.sql` 查看标准答案
2. ✅ **测试连接**: 使用提供的连接信息测试数据库连接
3. ✅ **开发 Agent**: 参考 `agent_development.md` 开始开发
4. ✅ **测试问题**: 使用10个标准问题测试 Agent 的回答准确性

---

**版本**: v1.0
**创建日期**: 2026-01-25
**最后更新**: 2026-01-25

如有问题，请参考 `README_DATABASE.md` 或 `database_setup.md` 获取更多信息。
