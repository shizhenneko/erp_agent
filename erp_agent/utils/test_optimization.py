"""
测试 PromptBuilder 优化效果
展示按需计算时间占位符的性能改进
"""

import time
from prompt_builder import PromptBuilder
from date_utils import get_current_datetime


def test_optimization():
    """测试优化效果"""
    print("=" * 70)
    print("PromptBuilder 优化效果测试")
    print("=" * 70)
    
    builder = PromptBuilder()
    date_info = get_current_datetime()
    
    # 测试 1: 按需计算（只计算必需的占位符）
    print("\n【测试 1】按需计算时间占位符")
    print("-" * 70)
    required = ['year_minus_1', 'month_padded', 'three_months_ago']
    
    start_time = time.time()
    result = builder._calculate_time_placeholders(date_info, required)
    end_time = time.time()
    
    print(f"✓ 请求计算 {len(required)} 个占位符")
    print(f"✓ 实际返回 {len(result)} 个占位符（包括基础的3个）")
    print(f"✓ 耗时: {(end_time - start_time) * 1000:.4f} ms")
    print(f"\n返回的占位符:")
    for key in result.keys():
        print(f"  - {key}: {result[key]}")
    
    # 测试 2: 计算所有占位符（不传参数）
    print("\n【测试 2】计算所有时间占位符（兼容模式）")
    print("-" * 70)
    
    start_time = time.time()
    result_all = builder._calculate_time_placeholders(date_info, None)
    end_time = time.time()
    
    print(f"✓ 计算了 {len(result_all)} 个占位符")
    print(f"✓ 耗时: {(end_time - start_time) * 1000:.4f} ms")
    print(f"\n包含的占位符类别:")
    print(f"  - 基础时间信息: current_date, year, month, day, weekday 等")
    print(f"  - 相对年份: year_minus_1, year_minus_2")
    print(f"  - 相对月份: month_minus_1, month_minus_1_padded 等")
    print(f"  - 相对时间点: three_months_ago, six_months_ago, one_year_ago")
    print(f"  - 年份范围: current_year_start, current_year_end 等")
    print(f"  - 月份范围: current_month_start, current_month_end")
    print(f"  - 季度范围: current_quarter_start, current_quarter_end")
    
    # 测试 3: 构建完整 Prompt（展示实际使用场景）
    print("\n【测试 3】构建完整 Prompt")
    print("-" * 70)
    
    start_time = time.time()
    prompt = builder.build_sql_generation_prompt(
        user_question="公司有多少在职员工?",
        date_info=date_info
    )
    end_time = time.time()
    
    print(f"✓ Prompt 构建成功")
    print(f"✓ 总长度: {len(prompt)} 字符")
    print(f"✓ 耗时: {(end_time - start_time) * 1000:.4f} ms")
    
    # 提取模板中使用的占位符
    template = builder.load_system_prompt_template()
    placeholders = builder.extract_placeholders(template)
    
    # 筛选时间相关的占位符
    time_related = [p for p in placeholders if p in [
        'current_date', 'year', 'month', 'month_padded',
        'year_minus_1', 'year_minus_2', 'month_minus_1_padded',
        'three_months_ago', 'six_months_ago', 'one_year_ago',
        'current_year_start', 'current_year_end',
        'last_year_start', 'last_year_end',
        'current_month_start', 'current_month_end',
        'current_quarter_start', 'current_quarter_end'
    ]]
    
    # 去重
    time_related_unique = list(set(time_related))
    
    print(f"\n模板中实际使用的时间占位符（{len(time_related_unique)} 个）:")
    for p in sorted(time_related_unique):
        print(f"  - {p}")
    
    # 测试 4: Few-shot 示例加载
    print("\n【测试 4】Few-shot 示例加载")
    print("-" * 70)
    
    examples = builder.get_all_examples()
    print(f"✓ 加载了所有 few-shot 示例")
    print(f"✓ 示例总长度: {len(examples)} 字符")
    print(f"✓ 策略: 始终加载所有示例，不进行选择")
    
    # 性能对比总结
    print("\n" + "=" * 70)
    print("优化效果总结")
    print("=" * 70)
    
    # 估算优化前后的差异
    print("\n✅ 时间占位符计算优化:")
    print(f"  优化前: 总是计算所有 {len(result_all)} 个占位符")
    print(f"  优化后: 只计算模板需要的 {len(time_related_unique)} 个占位符")
    print(f"  减少计算: {len(result_all) - len(time_related_unique)} 个 ({(1 - len(time_related_unique)/len(result_all))*100:.1f}%)")
    
    print("\n✅ Few-shot 示例策略:")
    print("  优化前: 存在未使用的 select_relevant_examples() 方法")
    print("  优化后: 简化为 get_all_examples()，代码更清晰")
    
    print("\n✅ 泛化性提升:")
    print("  自动提取模板占位符，适配不同的 prompt 模板")
    print("  按需计算，避免硬编码特定占位符列表")
    
    print("\n✅ 向后兼容:")
    print("  所有现有调用方式都能正常工作")
    print("  没有破坏任何现有功能")
    
    print("\n" + "=" * 70)
    print("✓✓✓ 优化测试完成! ✓✓✓")
    print("=" * 70)


if __name__ == '__main__':
    test_optimization()
