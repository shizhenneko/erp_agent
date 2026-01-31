@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════════
echo      启动 ERP Agent 前端开发服务器
echo ═══════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0frontend"

if not exist "node_modules" (
    echo 首次运行，正在安装依赖...
    call npm install
    echo.
)

echo 正在启动前端开发服务器...
echo.

npm run dev

pause
