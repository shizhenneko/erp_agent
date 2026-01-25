# ERP Agent 数据库初始化自动化脚本
# 适用于 Windows PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ERP Agent 数据库初始化脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 配置参数
$POSTGRES_USER = "postgres"
$POSTGRES_PASSWORD = "050916"  # 请根据实际情况修改
$DB_NAME = "erp_agent_db"

# 检查 PostgreSQL 是否安装
Write-Host "[1/5] 检查 PostgreSQL 安装..." -ForegroundColor Yellow
try {
    $psqlVersion = psql --version
    Write-Host "✓ PostgreSQL 已安装: $psqlVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ PostgreSQL 未安装或未添加到 PATH" -ForegroundColor Red
    Write-Host "请先安装 PostgreSQL: https://www.postgresql.org/download/windows/" -ForegroundColor Red
    exit 1
}

# 检查 Python 是否安装
Write-Host ""
Write-Host "[2/5] 检查 Python 安装..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version
    Write-Host "✓ Python 已安装: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "✗ Python 未安装或未添加到 PATH" -ForegroundColor Red
    Write-Host "请先安装 Python 3.7+: https://www.python.org/downloads/" -ForegroundColor Red
    exit 1
}

# 安装 Python 依赖
Write-Host ""
Write-Host "[3/5] 安装 Python 依赖..." -ForegroundColor Yellow
try {
    pip install psycopg2-binary -q
    Write-Host "✓ psycopg2-binary 安装成功" -ForegroundColor Green
} catch {
    Write-Host "✗ 安装 psycopg2-binary 失败" -ForegroundColor Red
    Write-Host "请手动执行: pip install psycopg2-binary" -ForegroundColor Red
    exit 1
}

# 执行数据库初始化
Write-Host ""
Write-Host "[4/5] 初始化数据库结构..." -ForegroundColor Yellow
$env:PGPASSWORD = $POSTGRES_PASSWORD

# 步骤1: 连接到 postgres 数据库，创建数据库和用户
Write-Host "  创建数据库和用户..." -ForegroundColor Gray
$createDbScript = @"
DROP DATABASE IF EXISTS $DB_NAME;
CREATE DATABASE $DB_NAME
    WITH 
    ENCODING = 'UTF8'
    TEMPLATE = template0;

DROP USER IF EXISTS erp_agent_user;
CREATE USER erp_agent_user WITH PASSWORD 'erp_agent_2026';
GRANT CONNECT ON DATABASE $DB_NAME TO erp_agent_user;
"@

$createDbScript | psql -U $POSTGRES_USER -d postgres 2>&1 | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ 数据库和用户创建失败" -ForegroundColor Red
    Write-Host "请检查 PostgreSQL 是否运行，以及密码是否正确" -ForegroundColor Red
    exit 1
}

# 步骤2: 连接到 erp_agent_db 数据库，创建表结构
Write-Host "  创建表结构..." -ForegroundColor Gray
$createTableScript = @"
-- 授予 schema 使用权限
GRANT USAGE ON SCHEMA public TO erp_agent_user;

-- 创建员工表
DROP TABLE IF EXISTS salaries CASCADE;
DROP TABLE IF EXISTS employees CASCADE;

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

-- 授予查询权限
GRANT SELECT ON employees TO erp_agent_user;
GRANT SELECT ON salaries TO erp_agent_user;
GRANT USAGE ON SEQUENCE salaries_salary_id_seq TO erp_agent_user;

-- 添加表注释
COMMENT ON TABLE employees IS '员工表：存储员工基本信息';
COMMENT ON TABLE salaries IS '工资表：存储员工每月工资记录';
"@

$createTableScript | psql -U $POSTGRES_USER -d $DB_NAME 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 数据库结构创建成功" -ForegroundColor Green
} else {
    Write-Host "✗ 表结构创建失败" -ForegroundColor Red
    Write-Host "请检查 PostgreSQL 是否运行，以及密码是否正确" -ForegroundColor Red
    exit 1
}

# 生成测试数据
Write-Host ""
Write-Host "[5/5] 生成并导入测试数据..." -ForegroundColor Yellow
Write-Host "    （这可能需要几分钟时间）" -ForegroundColor Gray

# 修改 Python 脚本中的密码配置
$pythonScript = Get-Content "generate_test_data.py" -Raw
$pythonScript = $pythonScript -replace "    'password': 'postgres'  # 请根据实际情况修改", "    'password': '$POSTGRES_PASSWORD'"
$pythonScript | Set-Content "generate_test_data_temp.py"

try {
    python generate_test_data_temp.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 测试数据生成成功（确定性数据）" -ForegroundColor Green
    } else {
        Write-Host "✗ 测试数据生成失败" -ForegroundColor Red
        exit 1
    }
} finally {
    # 清理临时文件
    Remove-Item "generate_test_data_temp.py" -ErrorAction SilentlyContinue
}

# 验证数据并生成标准答案
Write-Host ""
Write-Host "[额外] 生成标准答案..." -ForegroundColor Yellow
psql -U $POSTGRES_USER -d $DB_NAME -f verify_answers.sql > standard_answers_output.txt 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 标准答案已生成: standard_answers_output.txt" -ForegroundColor Green
} else {
    Write-Host "! 标准答案生成可能失败，请手动执行 verify_answers.sql" -ForegroundColor Yellow
}

# 完成
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  初始化完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "数据库信息:" -ForegroundColor White
Write-Host "  - 数据库名: $DB_NAME" -ForegroundColor Gray
Write-Host "  - 主机: localhost" -ForegroundColor Gray
Write-Host "  - 端口: 5432" -ForegroundColor Gray
Write-Host "  - 用户: erp_agent_user" -ForegroundColor Gray
Write-Host "  - 密码: erp_agent_2026" -ForegroundColor Gray
Write-Host ""
Write-Host "下一步:" -ForegroundColor White
Write-Host "  1. 查看 standard_answers_output.txt 获取10个问题的标准答案" -ForegroundColor Gray
Write-Host "  2. 参考 README_DATABASE.md 了解详细信息" -ForegroundColor Gray
Write-Host "  3. 参考 agent_development.md 开始开发 ERP Agent" -ForegroundColor Gray
Write-Host ""

# 清理环境变量
$env:PGPASSWORD = $null
