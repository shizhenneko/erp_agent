# ERP Agent 数据库初始化自动化脚本
# 适用于 Windows PowerShell

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  ERP Agent 数据库初始化脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 配置参数
$POSTGRES_USER = "postgres"
$POSTGRES_PASSWORD = "postgres"  # 请根据实际情况修改
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

# 创建数据库和表结构
psql -U $POSTGRES_USER -f init_database.sql 2>&1 | Out-Null
if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ 数据库结构创建成功" -ForegroundColor Green
} else {
    Write-Host "✗ 数据库结构创建失败" -ForegroundColor Red
    Write-Host "请检查 PostgreSQL 是否运行，以及密码是否正确" -ForegroundColor Red
    exit 1
}

# 生成测试数据
Write-Host ""
Write-Host "[5/5] 生成并导入测试数据..." -ForegroundColor Yellow
Write-Host "    （这可能需要几分钟时间）" -ForegroundColor Gray

# 修改 Python 脚本中的密码配置
$pythonScript = Get-Content "generate_test_data.py" -Raw
$pythonScript = $pythonScript -replace "'password': 'postgres'", "'password': '$POSTGRES_PASSWORD'"
$pythonScript | Set-Content "generate_test_data_temp.py"

try {
    python generate_test_data_temp.py
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ 测试数据生成成功" -ForegroundColor Green
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
