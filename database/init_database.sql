-- =====================================================
-- ERP Agent 数据库初始化脚本
-- =====================================================
-- 创建数据库: erp_agent_db
-- 字符集: UTF-8
-- 创建日期: 2026-01-25
-- =====================================================

-- 连接到 PostgreSQL 后执行
-- psql -U postgres

-- 1. 创建数据库
DROP DATABASE IF EXISTS erp_agent_db;
CREATE DATABASE erp_agent_db
    WITH 
    ENCODING = 'UTF8'
    TEMPLATE = template0;

-- 2. 创建用户（用于 Agent 查询）
DROP USER IF EXISTS erp_agent_user;
CREATE USER erp_agent_user WITH PASSWORD 'erp_agent_2026';

-- 3. 授予连接权限
GRANT CONNECT ON DATABASE erp_agent_db TO erp_agent_user;

-- 连接到 erp_agent_db 数据库后执行以下命令
-- \c erp_agent_db

-- 4. 授予 schema 使用权限
GRANT USAGE ON SCHEMA public TO erp_agent_user;

-- =====================================================
-- 表结构创建
-- =====================================================

-- 5. 创建员工表
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

-- 6. 创建工资表
CREATE TABLE salaries (
    salary_id SERIAL PRIMARY KEY,
    employee_id VARCHAR(20) NOT NULL,
    payment_date DATE NOT NULL,
    salary_amount DECIMAL(10,2) NOT NULL CHECK (salary_amount >= 0),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id) ON DELETE CASCADE,
    UNIQUE(employee_id, payment_date)
);

-- =====================================================
-- 创建索引
-- =====================================================

-- 员工表索引
CREATE INDEX idx_employees_department ON employees(department_name);
CREATE INDEX idx_employees_hire_date ON employees(hire_date);
CREATE INDEX idx_employees_active ON employees(leave_date) WHERE leave_date IS NULL;

-- 工资表索引
CREATE INDEX idx_salaries_payment_date ON salaries(payment_date);
CREATE INDEX idx_salaries_employee_date ON salaries(employee_id, payment_date);

-- =====================================================
-- 授予查询权限
-- =====================================================

GRANT SELECT ON employees TO erp_agent_user;
GRANT SELECT ON salaries TO erp_agent_user;
GRANT USAGE ON SEQUENCE salaries_salary_id_seq TO erp_agent_user;

-- =====================================================
-- 添加表注释
-- =====================================================

COMMENT ON TABLE employees IS '员工表：存储员工基本信息';
COMMENT ON TABLE salaries IS '工资表：存储员工每月工资记录';

-- =====================================================
-- 验证表创建（仅在交互式 psql 中使用）
-- =====================================================
-- 如需验证，请手动连接数据库后执行：
-- \d employees
-- \d salaries
-- \di
