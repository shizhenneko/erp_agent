"""
工具模块
包含时间处理工具、Prompt构建工具和日志工具
"""

# 导入泛化的时间工具
from .date_utils import (
    get_current_datetime,
    calculate_date_offset,
    get_date_range_for_period,
    calculate_days_between,
    calculate_months_between,
    get_month_start_end,
    get_quarter_start_end,
    get_year_start_end,
    format_date_for_sql
)

from .prompt_builder import (
    PromptBuilder,
    create_user_message,
    create_system_message,
    create_messages_for_api
)

from .logger import (
    setup_logger,
    get_logger,
    log_sql_execution,
    log_api_call,
    log_agent_iteration,
    log_error_with_context,
    log_performance
)

__all__ = [
    # date_utils (泛化版本)
    'get_current_datetime',
    'calculate_date_offset',
    'get_date_range_for_period',
    'calculate_days_between',
    'calculate_months_between',
    'get_month_start_end',
    'get_quarter_start_end',
    'get_year_start_end',
    'format_date_for_sql',
    
    # prompt_builder
    'PromptBuilder',
    'create_user_message',
    'create_system_message',
    'create_messages_for_api',
    
    # logger
    'setup_logger',
    'get_logger',
    'log_sql_execution',
    'log_api_call',
    'log_agent_iteration',
    'log_error_with_context',
    'log_performance',
]
