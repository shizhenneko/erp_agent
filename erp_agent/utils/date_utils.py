"""
泛化的时间处理工具模块

提供基础的日期计算能力，让 LLM 自己理解和推理时间表达式。
工具只负责提供计算能力，不解析自然语言。

设计理念：
- 模型负责：理解用户的时间表达式（"去年"、"最近3个月"等）
- 工具负责：提供基础的日期计算 API（偏移、范围、差值等）
"""

from datetime import datetime, timedelta
from calendar import monthrange
from typing import Tuple, Optional, Dict


def get_current_datetime() -> Dict[str, any]:
    """
    获取当前时间信息
    
    返回当前的年、月、日、星期等详细信息，供模型参考使用
    
    返回:
        dict: 包含当前时间各个维度的信息
    
    示例:
        当前时间为 2026-01-25 14:30:00 时:
        {
            'current_date': '2026-01-25',
            'current_datetime': '2026-01-25 14:30:00',
            'year': 2026,
            'month': 1,
            'day': 25,
            'weekday': 'Saturday',
            'weekday_cn': '周六',
            'hour': 14,
            'minute': 30
        }
    """
    now = datetime.now()
    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    
    return {
        'current_date': now.strftime('%Y-%m-%d'),
        'current_datetime': now.strftime('%Y-%m-%d %H:%M:%S'),
        'year': now.year,
        'month': now.month,
        'day': now.day,
        'weekday': now.strftime('%A'),
        'weekday_cn': weekday_names[now.weekday()],
        'hour': now.hour,
        'minute': now.minute
    }


def calculate_date_offset(
    base_date: str,
    years: int = 0,
    months: int = 0,
    days: int = 0
) -> str:
    """
    从基准日期计算偏移后的日期
    
    支持正负偏移量，正数表示未来，负数表示过去
    
    参数:
        base_date: 基准日期，格式 'YYYY-MM-DD'
        years: 年份偏移量（默认0）
        months: 月份偏移量（默认0）
        days: 天数偏移量（默认0）
    
    返回:
        str: 计算后的日期，格式 'YYYY-MM-DD'
    
    示例:
        calculate_date_offset('2026-01-25', years=-1)
        # -> '2025-01-25'（去年今天）
        
        calculate_date_offset('2026-01-25', months=-3)
        # -> '2025-10-25'（3个月前）
        
        calculate_date_offset('2026-01-25', days=30)
        # -> '2026-02-24'（30天后）
        
        calculate_date_offset('2026-01-31', months=-1)
        # -> '2025-12-31'（自动处理月末）
    """
    dt = datetime.strptime(base_date, '%Y-%m-%d')
    
    # 计算年份和月份偏移
    target_year = dt.year + years
    target_month = dt.month + months
    
    # 处理月份溢出
    while target_month > 12:
        target_month -= 12
        target_year += 1
    while target_month < 1:
        target_month += 12
        target_year -= 1
    
    # 确保日期有效（处理月末的情况，如1月31日 -> 2月末）
    max_day = monthrange(target_year, target_month)[1]
    target_day = min(dt.day, max_day)
    
    # 创建新日期并加上天数偏移
    result = datetime(target_year, target_month, target_day)
    result += timedelta(days=days)
    
    return result.strftime('%Y-%m-%d')


def get_date_range_for_period(
    year: int,
    month: Optional[int] = None,
    quarter: Optional[int] = None
) -> Tuple[str, str]:
    """
    获取指定时期的日期范围
    
    可以获取整年、某月、某季度的起止日期
    
    参数:
        year: 年份（必需）
        month: 月份 1-12（可选）
        quarter: 季度 1-4（可选）
    
    返回:
        tuple: (开始日期, 结束日期)，格式 'YYYY-MM-DD'
    
    优先级: month > quarter > 整年
    
    示例:
        get_date_range_for_period(2026)
        # -> ('2026-01-01', '2026-12-31')
        
        get_date_range_for_period(2026, month=3)
        # -> ('2026-03-01', '2026-03-31')
        
        get_date_range_for_period(2026, quarter=2)
        # -> ('2026-04-01', '2026-06-30')
        
        get_date_range_for_period(2024, month=2)
        # -> ('2024-02-01', '2024-02-29')（自动处理闰年）
    """
    if month is not None:
        # 返回指定月份的范围
        if not 1 <= month <= 12:
            raise ValueError(f"月份必须在 1-12 之间，得到: {month}")
        days = monthrange(year, month)[1]
        return (
            f"{year}-{month:02d}-01",
            f"{year}-{month:02d}-{days:02d}"
        )
    elif quarter is not None:
        # 返回指定季度的范围
        if not 1 <= quarter <= 4:
            raise ValueError(f"季度必须在 1-4 之间，得到: {quarter}")
        start_month = (quarter - 1) * 3 + 1
        end_month = quarter * 3
        end_days = monthrange(year, end_month)[1]
        return (
            f"{year}-{start_month:02d}-01",
            f"{year}-{end_month:02d}-{end_days:02d}"
        )
    else:
        # 返回整年的范围
        return (
            f"{year}-01-01",
            f"{year}-12-31"
        )


def calculate_days_between(date1: str, date2: str) -> int:
    """
    计算两个日期之间的天数差
    
    参数:
        date1: 第一个日期，格式 'YYYY-MM-DD'
        date2: 第二个日期，格式 'YYYY-MM-DD'
    
    返回:
        int: 天数差（date2 - date1），可以是负数
    
    示例:
        calculate_days_between('2026-01-01', '2026-01-31')
        # -> 30
        
        calculate_days_between('2026-01-31', '2026-01-01')
        # -> -30
        
        calculate_days_between('2025-01-01', '2026-01-01')
        # -> 365
    """
    d1 = datetime.strptime(date1, '%Y-%m-%d')
    d2 = datetime.strptime(date2, '%Y-%m-%d')
    return (d2 - d1).days


def calculate_months_between(date1: str, date2: str) -> int:
    """
    计算两个日期之间的月份差（粗略计算）
    
    参数:
        date1: 第一个日期，格式 'YYYY-MM-DD'
        date2: 第二个日期，格式 'YYYY-MM-DD'
    
    返回:
        int: 月份差（date2 - date1）
    
    示例:
        calculate_months_between('2026-01-25', '2026-03-25')
        # -> 2
        
        calculate_months_between('2025-01-25', '2026-01-25')
        # -> 12
    """
    d1 = datetime.strptime(date1, '%Y-%m-%d')
    d2 = datetime.strptime(date2, '%Y-%m-%d')
    
    return (d2.year - d1.year) * 12 + (d2.month - d1.month)


def get_month_start_end(date: str) -> Tuple[str, str]:
    """
    获取指定日期所在月份的起止日期
    
    参数:
        date: 日期，格式 'YYYY-MM-DD'
    
    返回:
        tuple: (月初日期, 月末日期)
    
    示例:
        get_month_start_end('2026-01-15')
        # -> ('2026-01-01', '2026-01-31')
        
        get_month_start_end('2024-02-20')
        # -> ('2024-02-01', '2024-02-29')（闰年）
    """
    dt = datetime.strptime(date, '%Y-%m-%d')
    days = monthrange(dt.year, dt.month)[1]
    return (
        f"{dt.year}-{dt.month:02d}-01",
        f"{dt.year}-{dt.month:02d}-{days:02d}"
    )


def get_quarter_start_end(date: str) -> Tuple[str, str]:
    """
    获取指定日期所在季度的起止日期
    
    参数:
        date: 日期，格式 'YYYY-MM-DD'
    
    返回:
        tuple: (季度开始日期, 季度结束日期)
    
    示例:
        get_quarter_start_end('2026-01-15')
        # -> ('2026-01-01', '2026-03-31')（第1季度）
        
        get_quarter_start_end('2026-11-20')
        # -> ('2026-10-01', '2026-12-31')（第4季度）
    """
    dt = datetime.strptime(date, '%Y-%m-%d')
    quarter = (dt.month - 1) // 3 + 1
    return get_date_range_for_period(dt.year, quarter=quarter)


def get_year_start_end(date: str) -> Tuple[str, str]:
    """
    获取指定日期所在年份的起止日期
    
    参数:
        date: 日期，格式 'YYYY-MM-DD'
    
    返回:
        tuple: (年初日期, 年末日期)
    
    示例:
        get_year_start_end('2026-06-15')
        # -> ('2026-01-01', '2026-12-31')
    """
    dt = datetime.strptime(date, '%Y-%m-%d')
    return get_date_range_for_period(dt.year)


def format_date_for_sql(date_str: str) -> str:
    """
    将各种格式的日期字符串标准化为 SQL 格式
    
    参数:
        date_str: 日期字符串，支持多种格式
    
    返回:
        str: 标准 SQL 日期格式 'YYYY-MM-DD'
    
    示例:
        format_date_for_sql("2026/1/5") -> "2026-01-05"
        format_date_for_sql("2026-1-5") -> "2026-01-05"
        format_date_for_sql("2026.1.5") -> "2026-01-05"
        format_date_for_sql("20260105") -> "2026-01-05"
    """
    # 尝试多种日期格式
    formats = [
        '%Y-%m-%d',
        '%Y/%m/%d',
        '%Y.%m.%d',
        '%Y%m%d',
        '%Y-%m-%d %H:%M:%S',
        '%Y/%m/%d %H:%M:%S'
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # 如果都失败了,尝试解析更灵活的格式
    try:
        # 替换分隔符为统一的 -
        normalized = date_str.strip()
        for sep in ['/', '.', ' ']:
            normalized = normalized.replace(sep, '-')
        # 分割年月日
        parts = normalized.split('-')
        if len(parts) >= 3:
            year, month, day = parts[0], parts[1], parts[2]
            # 补零
            return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
    except:
        pass
    
    # 如果还是失败,返回原字符串
    return date_str


if __name__ == '__main__':
    # 测试代码
    print("=== 测试 get_current_datetime ===")
    current = get_current_datetime()
    for key, value in current.items():
        print(f"{key}: {value}")
    
    print("\n=== 测试 calculate_date_offset ===")
    base_date = current['current_date']
    test_cases = [
        (base_date, {'years': -1}, "去年今天"),
        (base_date, {'months': -3}, "3个月前"),
        (base_date, {'days': 30}, "30天后"),
        (base_date, {'years': -2, 'months': 3}, "2年零3个月前"),
    ]
    
    for base, offset, desc in test_cases:
        result = calculate_date_offset(base, **offset)
        print(f"{desc}: {result}")
    
    print("\n=== 测试 get_date_range_for_period ===")
    test_cases = [
        (2026, None, None, "2026年全年"),
        (2026, 3, None, "2026年3月"),
        (2026, 2, None, "2026年2月（非闰年）"),
        (2024, 2, None, "2024年2月（闰年）"),
        (2026, None, 1, "2026年第1季度"),
        (2026, None, 4, "2026年第4季度"),
    ]
    
    for year, month, quarter, desc in test_cases:
        start, end = get_date_range_for_period(year, month, quarter)
        print(f"{desc}: {start} 到 {end}")
    
    print("\n=== 测试 calculate_days_between ===")
    test_cases = [
        ('2026-01-01', '2026-01-31', "1月1日到31日"),
        ('2025-01-01', '2026-01-01', "2025年到2026年"),
        ('2026-01-31', '2026-01-01', "反向计算"),
    ]
    
    for date1, date2, desc in test_cases:
        days = calculate_days_between(date1, date2)
        print(f"{desc}: {days} 天")
    
    print("\n=== 测试 calculate_months_between ===")
    test_cases = [
        ('2026-01-25', '2026-03-25', "2个月"),
        ('2025-01-25', '2026-01-25', "12个月"),
        ('2024-01-01', '2026-01-01', "24个月"),
    ]
    
    for date1, date2, desc in test_cases:
        months = calculate_months_between(date1, date2)
        print(f"{desc}: {months} 个月")
    
    print("\n=== 测试 get_month_start_end ===")
    test_cases = [
        '2026-01-15',
        '2024-02-20',  # 闰年
        '2026-12-31',
    ]
    
    for date in test_cases:
        start, end = get_month_start_end(date)
        print(f"{date} 所在月: {start} 到 {end}")
    
    print("\n=== 测试 format_date_for_sql ===")
    test_dates = [
        "2026/1/5",
        "2026-1-5",
        "2026.1.5",
        "20260105"
    ]
    
    for date_str in test_dates:
        formatted = format_date_for_sql(date_str)
        print(f"{date_str} -> {formatted}")
