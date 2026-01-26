"""
日志工具模块

提供统一的日志记录接口,支持多级别日志和日志文件管理。
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from loguru import logger


# 全局日志配置状态
_logger_configured = False


def setup_logger(
    log_level: str = "INFO",
    log_file: str = "logs/agent.log",
    rotation: str = "10 MB",
    retention: str = "7 days",
    enable_console: bool = True
) -> None:
    """
    配置日志系统
    
    参数:
        log_level: 日志级别 (DEBUG/INFO/WARNING/ERROR)
        log_file: 日志文件路径
        rotation: 日志轮转策略 (文件大小或时间)
        retention: 日志保留时间
        enable_console: 是否启用控制台输出
    
    功能:
        - 配置控制台日志输出(彩色、格式化)
        - 配置文件日志输出(包含详细信息)
        - 设置日志轮转和清理策略
    """
    global _logger_configured
    
    if _logger_configured:
        return
    
    # 移除默认的 logger 配置
    logger.remove()
    
    # 控制台日志格式
    console_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
        "<level>{message}</level>"
    )
    
    # 文件日志格式(更详细)
    file_format = (
        "{time:YYYY-MM-DD HH:mm:ss.SSS} | "
        "{level: <8} | "
        "{name}:{function}:{line} | "
        "{message}"
    )
    
    # 添加控制台输出
    if enable_console:
        logger.add(
            sys.stdout,
            format=console_format,
            level=log_level,
            colorize=True
        )
    
    # 确保日志目录存在
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # 添加文件输出
    logger.add(
        log_file,
        format=file_format,
        level=log_level,
        rotation=rotation,
        retention=retention,
        encoding='utf-8',
        enqueue=True  # 异步写入
    )
    
    _logger_configured = True
    logger.info(f"日志系统已初始化 [级别: {log_level}, 文件: {log_file}]")


def get_logger(name: Optional[str] = None):
    """
    获取日志记录器
    
    参数:
        name: 模块名称,用于标识日志来源
    
    返回:
        logger: loguru.Logger 对象
    
    使用示例:
        logger = get_logger(__name__)
        logger.info("这是一条信息")
        logger.error("这是一条错误信息")
    """
    # 如果未配置,使用默认配置
    if not _logger_configured:
        setup_logger()
    
    # loguru 的 logger 是全局单例,但可以通过 bind 添加上下文
    if name:
        return logger.bind(module=name)
    return logger


def log_sql_execution(
    sql: str,
    success: bool,
    execution_time: float,
    row_count: Optional[int] = None,
    error: Optional[str] = None
) -> None:
    """
    记录 SQL 执行日志
    
    参数:
        sql: 执行的 SQL 语句
        success: 是否成功
        execution_time: 执行时间(秒)
        row_count: 返回行数
        error: 错误信息(如果失败)
    """
    log = get_logger("sql_executor")
    
    # 截断过长的 SQL(保留前200个字符)
    sql_preview = sql[:200] + "..." if len(sql) > 200 else sql
    sql_preview = sql_preview.replace('\n', ' ').strip()
    
    if success:
        log.info(
            f"SQL执行成功 | 耗时: {execution_time:.3f}s | 行数: {row_count} | SQL: {sql_preview}"
        )
    else:
        log.error(
            f"SQL执行失败 | 耗时: {execution_time:.3f}s | 错误: {error} | SQL: {sql_preview}"
        )


def log_api_call(
    api_name: str,
    success: bool,
    response_time: float,
    request_data: Optional[Dict[str, Any]] = None,
    response_data: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> None:
    """
    记录 API 调用日志
    
    参数:
        api_name: API 名称(如 "kimi-k2")
        success: 是否成功
        response_time: 响应时间(秒)
        request_data: 请求数据(敏感信息会被脱敏)
        response_data: 响应数据(敏感信息会被脱敏)
        error: 错误信息(如果失败)
    """
    log = get_logger("api_client")
    
    # 脱敏处理
    safe_request = _sanitize_data(request_data) if request_data else {}
    safe_response = _sanitize_data(response_data) if response_data else {}
    
    if success:
        log.info(
            f"API调用成功 | API: {api_name} | 耗时: {response_time:.3f}s"
        )
        log.debug(f"请求数据: {safe_request}")
        log.debug(f"响应数据: {safe_response}")
    else:
        log.error(
            f"API调用失败 | API: {api_name} | 耗时: {response_time:.3f}s | 错误: {error}"
        )
        log.debug(f"请求数据: {safe_request}")


def log_agent_iteration(
    iteration: int,
    user_question: str,
    sql: str,
    result_summary: str,
    next_action: str
) -> None:
    """
    记录 Agent 迭代过程
    
    参数:
        iteration: 迭代次数
        user_question: 用户问题
        sql: 生成的 SQL
        result_summary: 结果摘要
        next_action: 下一步动作(完成/重试/继续查询)
    """
    log = get_logger("agent")
    
    # 截断过长的内容
    sql_preview = sql[:150] + "..." if len(sql) > 150 else sql
    sql_preview = sql_preview.replace('\n', ' ').strip()
    
    log.info(f"===== 迭代 {iteration} =====")
    log.info(f"用户问题: {user_question}")
    log.info(f"生成SQL: {sql_preview}")
    log.info(f"结果摘要: {result_summary}")
    log.info(f"下一步: {next_action}")
    log.info("=" * 50)


def _sanitize_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    脱敏处理敏感数据
    
    参数:
        data: 原始数据字典
    
    返回:
        脱敏后的数据字典
    """
    if not isinstance(data, dict):
        return data
    
    sensitive_keys = ['api_key', 'password', 'token', 'secret', 'authorization']
    
    sanitized = {}
    for key, value in data.items():
        # 检查是否是敏感字段
        if any(sk in key.lower() for sk in sensitive_keys):
            # 保留前后各2个字符
            if isinstance(value, str) and len(value) > 8:
                sanitized[key] = f"{value[:2]}***{value[-2:]}"
            else:
                sanitized[key] = "***"
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_data(value)
        elif isinstance(value, list):
            sanitized[key] = [_sanitize_data(item) if isinstance(item, dict) else item for item in value]
        else:
            sanitized[key] = value
    
    return sanitized


def log_error_with_context(
    error: Exception,
    context: Dict[str, Any],
    module_name: str = "unknown"
) -> None:
    """
    记录带上下文的错误信息
    
    参数:
        error: 异常对象
        context: 上下文信息
        module_name: 模块名称
    """
    log = get_logger(module_name)
    
    log.error(f"发生错误: {type(error).__name__}: {str(error)}")
    log.error(f"上下文信息: {context}")
    log.exception(error)  # 记录完整的堆栈跟踪


def log_performance(
    operation: str,
    duration: float,
    details: Optional[Dict[str, Any]] = None
) -> None:
    """
    记录性能指标
    
    参数:
        operation: 操作名称
        duration: 持续时间(秒)
        details: 额外详情
    """
    log = get_logger("performance")
    
    details_str = f" | 详情: {details}" if details else ""
    log.info(f"性能指标 | 操作: {operation} | 耗时: {duration:.3f}s{details_str}")


if __name__ == '__main__':
    # 测试代码
    print("=== 测试日志系统 ===")
    
    # 配置日志
    setup_logger(log_level="DEBUG")
    
    # 获取日志记录器
    logger_test = get_logger("test")
    
    # 测试不同级别的日志
    logger_test.debug("这是一条调试信息")
    logger_test.info("这是一条普通信息")
    logger_test.warning("这是一条警告信息")
    logger_test.error("这是一条错误信息")
    
    # 测试 SQL 日志
    print("\n=== 测试 SQL 日志 ===")
    log_sql_execution(
        sql="SELECT * FROM employees WHERE department = 'A部门'",
        success=True,
        execution_time=0.05,
        row_count=10
    )
    
    log_sql_execution(
        sql="SELECT * FROM invalid_table",
        success=False,
        execution_time=0.01,
        error="relation \"invalid_table\" does not exist"
    )
    
    # 测试 API 日志
    print("\n=== 测试 API 日志 ===")
    log_api_call(
        api_name="kimi-k2",
        success=True,
        response_time=1.2,
        request_data={"prompt": "测试提示", "api_key": "sk-1234567890abcdef"},
        response_data={"result": "成功"}
    )
    
    # 测试 Agent 迭代日志
    print("\n=== 测试 Agent 迭代日志 ===")
    log_agent_iteration(
        iteration=1,
        user_question="有多少在职员工?",
        sql="SELECT COUNT(*) FROM employees WHERE leave_date IS NULL",
        result_summary="查询成功,返回1行数据",
        next_action="完成"
    )
    
    print("\n日志测试完成,请查看 logs/agent.log 文件")
