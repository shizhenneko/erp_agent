#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent WebSocket 服务
提供 WebSocket 接口供前端调用
"""

import os
import sys
import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# 添加项目根目录到路径（erp_agent 文件夹的父目录）
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 设置当前工作目录为项目根目录
os.chdir(str(project_root))


# 全局 Agent 实例
agent_instance = None


def print_banner():
    """打印启动横幅"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║         ERP Agent WebSocket Service v0.1.0                   ║
    ║          基于 Kimi-K2 的智能数据查询助手                      ║
    ║                    WebSocket API                               ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def load_env():
    """加载环境变量"""
    try:
        from dotenv import load_dotenv
        
        env_paths = [
            project_root / '.env',
            Path(__file__).parent / '.env',
        ]
        
        for env_path in env_paths:
            if env_path.exists():
                load_dotenv(env_path)
                print(f"✓ 已加载环境配置: {env_path}")
                return True
        
        env_example = Path(__file__).parent / 'env.example'
        if env_example.exists():
            print("⚠️  未找到 .env 文件")
            print(f"   请将 {env_example} 复制为 .env 并配置相关参数")
        else:
            print("⚠️  未找到 .env 文件，请从 .env.example 复制并配置")
        return False
    except ImportError:
        print("⚠️  未安装 python-dotenv，请运行: pip install python-dotenv")
        return False


def check_environment():
    """检查环境配置"""
    print("正在检查环境配置...")
    
    required_vars = [
        'MOONSHOT_API_KEY',
        'DB_HOST',
        'DB_NAME',
        'DB_USER',
        'DB_PASSWORD'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ 缺少必需的环境变量: {', '.join(missing_vars)}")
        print("⚠️  请在 .env 文件中配置这些变量")
        return False
    
    print("✓ 环境变量配置完整")
    return True


def test_database_connection():
    """测试数据库连接"""
    print("正在测试数据库连接...")
    
    try:
        import psycopg2
        
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT', 5432)),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM employees")
        count = cursor.fetchone()[0]
        
        cursor.close()
        conn.close()
        
        print(f"✓ 数据库连接成功（共 {count} 名员工）")
        return True
        
    except ImportError:
        print("❌ 未安装 psycopg2，请运行: pip install psycopg2-binary")
        return False
    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False


def get_or_create_agent():
    """获取或创建 Agent 实例（单例模式）"""
    global agent_instance
    
    if agent_instance is None:
        try:
            from erp_agent.core import ERPAgent
            from erp_agent.config import get_llm_config, get_database_config, get_agent_config
            
            llm_config = get_llm_config()
            db_config = get_database_config()
            agent_config = get_agent_config()
            
            agent_instance = ERPAgent(llm_config, db_config, agent_config)
            print("✓ ERP Agent 初始化成功")
        except Exception as e:
            print(f"❌ ERPAgent 初始化失败: {e}")
            raise
    
    return agent_instance


def create_app():
    """创建 FastAPI 应用"""
    app = FastAPI(
        title="ERP Agent WebSocket API",
        version="0.1.0",
        description="基于 ReAct 范式的智能数据查询助手"
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    return app


app = create_app()


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": "ERP Agent WebSocket API",
        "version": "0.1.0",
        "description": "基于 ReAct 范式的智能数据查询助手",
        "endpoints": {
            "websocket": "/ws"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    try:
        agent = get_or_create_agent()
        return {
            "status": "healthy",
            "agent_initialized": agent is not None,
            "timestamp": time.time()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket 端点"""
    await websocket.accept()
    
    client_id = id(websocket)
    print(f"[{client_id}] 客户端已连接")
    
    try:
        agent = get_or_create_agent()
        
        await websocket.send_json({
            "type": "connected",
            "message": "已连接到 ERP Agent 服务",
            "timestamp": time.time()
        })
        
        while True:
            try:
                data = await websocket.receive_json()
                action = data.get("action")
                user_question = data.get("question")
                
                if action == "query" and user_question:
                    print(f"[{client_id}] 收到查询: {user_question[:50]}...")
                    
                    try:
                        await websocket.send_json({
                            "type": "start",
                            "user_question": user_question,
                            "timestamp": time.time()
                        })
                        
                        for chunk in agent.query_stream(user_question):
                            await websocket.send_json({
                                "type": chunk['type'],
                                "data": chunk,
                                "timestamp": chunk.get('timestamp', time.time())
                            })
                            await asyncio.sleep(0.01)
                        
                    except Exception as e:
                        print(f"[{client_id}] 查询处理错误: {e}")
                        await websocket.send_json({
                            "type": "error",
                            "error": str(e),
                            "timestamp": time.time()
                        })
                else:
                    await websocket.send_json({
                        "type!status": "error",
                        "message": "无效的请求格式",
                        "timestamp": time.time()
                    })
                    
            except json.JSONDecodeError as e:
                print(f"[{client_id}] JSON 解析错误: {e}")
                await websocket.send_json({
                    "type": "error",
                    "error": "无效的 JSON 格式",
                    "timestamp": time.time()
                })
                
    except WebSocketDisconnect:
        print(f"[{client_id}] 客户端断开连接")
    except Exception as e:
        print(f"[{client_id}] WebSocket 错误: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    print_banner()
    
    if not load_env():
        print("\n请先配置 .env 文件后再运行")
        return
    
    if not check_environment():
        return
    
    if not test_database_connection():
        return
    
    print("\n✓ 所有检查通过，准备启动 WebSocket 服务！\n")
    
    try:
        get_or_create_agent()
    except Exception as e:
        print(f"\n❌ Agent 初始化失败，无法启动服务: {e}")
        return
    
    print("="*70)
    print("WebSocket 服务已启动！")
    print("="*70)
    print("服务地址: ws://0.0.0.0:8000/ws")
    print("API 文档: http://0.0.0.0:8000/docs")
    print("健康检查: http://0.0.0.0:8000/health")
    print("="*70)
    print("\n按 Ctrl+C 停止服务\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )


if __name__ == "__main__":
    main()
