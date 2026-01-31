@echo off
chcp 65001 >nul
echo ═══════════════════════════════════════════════════════════════
echo      启动 ERP Agent WebSocket 后端服务
echo ═══════════════════════════════════════════════════════════════
echo.

cd /d "%~dp0erp_agent"

echo 正在启动后端服务...
echo.

python main.py

pause
