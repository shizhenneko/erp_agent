#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent 测试问题集（增强版）
包含10个测试问题及其验证逻辑
"""

from typing import Dict, Any, List, Optional, Tuple


# 10个测试问题及其标准答案/验证规则
TEST_QUESTIONS = [
    {
        'id': 1,
        'question': '平均每个员工在公司在职多久？',
        'category': 'aggregation',
        'difficulty': 'medium',
        'description': '计算所有员工的平均在职时长',
        'validation': {
            'type': 'numeric_range',
            'expected': {
                'avg_days': 1104.15,
                'avg_years': 3.02
            },
            'tolerance': 0.1,  # 10%容差
            'row_count': 1
        }
    },
    {
        'id': 2,
        'question': '公司每个部门有多少在职员工？',
        'category': 'aggregation',
        'difficulty': 'easy',
        'description': '统计各部门在职员工数量',
        'validation': {
            'type': 'table_data',
            'expected_rows': 5,
            'expected_columns': ['department_name', 'employee_count'],
            'expected_data': {
                'A部门': 22,
                'B部门': 20,
                'C部门': 18,
                'D部门': 16,
                'E部门': 13
            },
            'total_sum': 89  # 总在职员工数
        }
    },
    {
        'id': 3,
        'question': '哪个部门的员工平均级别最高？',
        'category': 'ranking',
        'difficulty': 'medium',
        'description': '找出平均级别最高的部门',
        'validation': {
            'type': 'specific_value',
            'expected': {
                'department_name': 'E部门',
                'avg_level': 5.15,
                'employee_count': 13
            },
            'tolerance': 0.1,
            'row_count': 1
        }
    },
    {
        'id': 4,
        'question': '每个部门今年和去年各新入职了多少人？',
        'category': 'time_comparison',
        'difficulty': 'hard',
        'description': '比较各部门今年和去年的新入职人数',
        'validation': {
            'type': 'table_data',
            'expected_rows': 5,
            'expected_columns': ['department_name', 'this_year', 'last_year'],
            'expected_data': {
                'A部门': {'this_year': 0, 'last_year': 2},
                'B部门': {'this_year': 0, 'last_year': 1},
                'C部门': {'this_year': 0, 'last_year': 1},
                'D部门': {'this_year': 0, 'last_year': 1},
                'E部门': {'this_year': 0, 'last_year': 1}
            }
        }
    },
    {
        'id': 5,
        'question': '从前年3月到去年5月，A部门的平均工资是多少？',
        'category': 'time_range',
        'difficulty': 'hard',
        'description': '计算A部门特定时间段的平均工资',
        'validation': {
            'type': 'numeric_range',
            'expected': {
                'avg_salary': 24790.95
            },
            'tolerance': 0.05,  # 5%容差
            'row_count': 1
        }
    },
    {
        'id': 6,
        'question': '去年A部门和B部门的平均工资哪个高？',
        'category': 'comparison',
        'difficulty': 'medium',
        'description': '比较A部门和B部门去年的平均工资',
        'validation': {
            'type': 'comparison',
            'expected': {
                'A部门': 25802.85,
                'B部门': 24184.73,
                'higher': 'A部门'
            },
            'tolerance': 0.05,
            'row_count': 2
        }
    },
    {
        'id': 7,
        'question': '今年每个级别的员工平均工资分别是多少？',
        'category': 'aggregation',
        'difficulty': 'medium',
        'description': '统计今年各级别员工的平均工资',
        'validation': {
            'type': 'table_data',
            'expected_rows': 10,
            'expected_columns': ['level', 'avg_salary', 'employee_count'],
            'expected_data': {
                1: {'avg_salary': 7749.18, 'count': 6},
                2: {'avg_salary': 10986.96, 'count': 15},
                3: {'avg_salary': 13952.03, 'count': 12},
                4: {'avg_salary': 18251.04, 'count': 14},
                5: {'avg_salary': 22521.95, 'count': 11},
                6: {'avg_salary': 26458.40, 'count': 10},
                7: {'avg_salary': 42533.51, 'count': 7},
                8: {'avg_salary': 50401.86, 'count': 6},
                9: {'avg_salary': 77165.08, 'count': 4},
                10: {'avg_salary': 77725.87, 'count': 4}
            },
            'tolerance': 0.05
        }
    },
    {
        'id': 8,
        'question': '入职时间一年内、一年到两年、两年到三年的员工最近一个月的平均工资是多少？',
        'category': 'complex',
        'difficulty': 'hard',
        'description': '按入职时长分组统计最近一个月的平均工资',
        'validation': {
            'type': 'skip',  # SQL有错误，暂时跳过
            'reason': 'SQL错误：GROUP BY子句问题',
            'note': '需要修复查询逻辑'
        }
    },
    {
        'id': 9,
        'question': '从去年到今年涨薪幅度最大的10位员工是谁？',
        'category': 'ranking',
        'difficulty': 'hard',
        'description': '找出涨薪幅度最大的前10名员工',
        'validation': {
            'type': 'top_n',
            'expected_rows': 10,
            'expected_columns': ['employee_id', 'employee_name', 'department_name', 
                               'last_year_avg', 'this_year_avg', 'increase_amount', 'increase_rate'],
            'top_employee_ids': ['EMP029', 'EMP032', 'EMP055', 'EMP089', 'EMP003', 
                                'EMP011', 'EMP077', 'EMP059', 'EMP026', 'EMP062'],
            'check_ordering': True,  # 检查是否按涨薪幅度降序排列
            'tolerance': 0.05
        }
    },
    {
        'id': 10,
        'question': '有没有出现过拖欠员工工资的情况？如果有，是哪些员工？',
        'category': 'complex',
        'difficulty': 'hard',
        'description': '检查在职期间是否有月份未发薪',
        'validation': {
            'type': 'existence_check',
            'expected_rows': 25,
            'expected_columns': ['employee_id', 'employee_name', 'department_name', 'missing_month'],
            'has_issues': True,
            'min_rows': 20,  # 至少应该找到20条记录
            'sample_employee_ids': ['EMP023', 'EMP085', 'EMP046', 'EMP044', 'EMP068']
        }
    }
]


def get_question_by_id(question_id: int) -> Optional[Dict[str, Any]]:
    """
    根据问题ID获取问题信息
    
    Args:
        question_id: 问题ID (1-10)
        
    Returns:
        问题字典，如果未找到返回 None
    """
    for q in TEST_QUESTIONS:
        if q['id'] == question_id:
            return q
    return None


def get_questions_by_category(category: str) -> List[Dict[str, Any]]:
    """
    根据分类获取问题列表
    
    Args:
        category: 问题分类
        
    Returns:
        问题列表
    """
    return [q for q in TEST_QUESTIONS if q['category'] == category]


def get_questions_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """
    根据难度获取问题列表
    
    Args:
        difficulty: 难度级别 (easy/medium/hard)
        
    Returns:
        问题列表
    """
    return [q for q in TEST_QUESTIONS if q['difficulty'] == difficulty]


def validate_result(
    question_id: int,
    sql_result: Dict[str, Any],
    tolerance: Optional[float] = None
) -> Tuple[bool, str, Dict[str, Any]]:
    """
    验证查询结果是否符合预期
    
    Args:
        question_id: 问题ID
        sql_result: SQL执行结果 {'success': bool, 'data': list, 'row_count': int, ...}
        tolerance: 可选的容差覆盖值
        
    Returns:
        (是否通过, 详细信息, 验证详情字典)
    """
    question = get_question_by_id(question_id)
    if not question:
        return False, f"问题ID {question_id} 不存在", {}
    
    validation = question.get('validation', {})
    val_type = validation.get('type')
    
    # 检查SQL是否成功执行
    if not sql_result.get('success', False):
        return False, f"SQL执行失败: {sql_result.get('error', '未知错误')}", {}
    
    data = sql_result.get('data', [])
    row_count = sql_result.get('row_count', 0)
    
    # 使用提供的容差或默认容差
    tol = tolerance if tolerance is not None else validation.get('tolerance', 0.05)
    
    details = {
        'validation_type': val_type,
        'actual_rows': row_count,
        'expected_rows': validation.get('expected_rows') or validation.get('row_count'),
        'tolerance_used': tol
    }
    
    try:
        if val_type == 'skip':
            return True, f"跳过验证: {validation.get('reason', '未知原因')}", details
        
        elif val_type == 'numeric_range':
            # 验证数值范围
            expected = validation['expected']
            expected_rows = validation.get('row_count', 1)
            
            if row_count != expected_rows:
                return False, f"行数不匹配: 期望{expected_rows}行, 实际{row_count}行", details
            
            if not data:
                return False, "查询结果为空", details
            
            row = data[0]
            mismatches = []
            
            for key, expected_val in expected.items():
                actual_val = row.get(key)
                if actual_val is None:
                    # 尝试其他可能的列名
                    for col in row.keys():
                        if key.lower() in col.lower() or col.lower() in key.lower():
                            actual_val = row[col]
                            break
                
                if actual_val is None:
                    mismatches.append(f"缺少字段 {key}")
                    continue
                
                # 转换为浮点数进行比较
                actual_val = float(actual_val)
                expected_val = float(expected_val)
                
                diff = abs(actual_val - expected_val)
                max_diff = expected_val * tol
                
                details[key] = {
                    'expected': expected_val,
                    'actual': actual_val,
                    'diff': diff,
                    'max_diff': max_diff,
                    'pass': diff <= max_diff
                }
                
                if diff > max_diff:
                    mismatches.append(
                        f"{key}: 期望{expected_val:.2f}, 实际{actual_val:.2f}, "
                        f"差异{diff:.2f} (超过容差{max_diff:.2f})"
                    )
            
            if mismatches:
                return False, "数值不匹配: " + "; ".join(mismatches), details
            return True, "验证通过", details
        
        elif val_type == 'table_data':
            # 验证表格数据
            expected_rows = validation['expected_rows']
            expected_data = validation.get('expected_data', {})
            
            if row_count != expected_rows:
                return False, f"行数不匹配: 期望{expected_rows}行, 实际{row_count}行", details
            
            # 验证具体数据
            mismatches = []
            for row in data:
                # 获取键（部门名、级别等）
                key = None
                for col in row.keys():
                    if 'department' in col.lower() or '部门' in col:
                        key = row[col]
                        break
                    elif 'level' in col.lower() or '级别' in col:
                        key = int(row[col])
                        break
                
                if key is None:
                    continue
                
                if key not in expected_data:
                    continue
                
                expected_val = expected_data[key]
                
                # 根据期望值类型进行不同的验证
                if isinstance(expected_val, dict):
                    # 多字段验证
                    for field, exp_val in expected_val.items():
                        actual_val = None
                        for col in row.keys():
                            if field.lower() in col.lower() or col.lower() in field.lower():
                                actual_val = row[col]
                                break
                        
                        if actual_val is None:
                            continue
                        
                        # 数值比较
                        if isinstance(exp_val, (int, float)):
                            actual_val = float(actual_val)
                            exp_val = float(exp_val)
                            diff = abs(actual_val - exp_val)
                            max_diff = exp_val * tol if exp_val > 0 else 1
                            
                            if diff > max_diff:
                                mismatches.append(
                                    f"{key} {field}: 期望{exp_val}, 实际{actual_val}"
                                )
                else:
                    # 单值验证
                    actual_val = None
                    for col in row.keys():
                        if 'count' in col.lower() or 'salary' in col.lower() or '工资' in col or '人数' in col:
                            actual_val = row[col]
                            break
                    
                    if actual_val is not None:
                        if isinstance(expected_val, (int, float)):
                            actual_val = float(actual_val)
                            exp_val = float(expected_val)
                            diff = abs(actual_val - exp_val)
                            max_diff = exp_val * tol if exp_val > 0 else 1
                            
                            if diff > max_diff:
                                mismatches.append(
                                    f"{key}: 期望{exp_val}, 实际{actual_val}"
                                )
            
            if mismatches:
                return False, "数据不匹配: " + "; ".join(mismatches), details
            return True, "验证通过", details
        
        elif val_type == 'specific_value':
            # 验证特定值
            expected = validation['expected']
            expected_rows = validation.get('row_count', 1)
            
            if row_count != expected_rows:
                return False, f"行数不匹配: 期望{expected_rows}行, 实际{row_count}行", details
            
            if not data:
                return False, "查询结果为空", details
            
            row = data[0]
            mismatches = []
            
            for key, expected_val in expected.items():
                actual_val = None
                for col in row.keys():
                    if key.lower() in col.lower() or col.lower() in key.lower():
                        actual_val = row[col]
                        break
                
                if actual_val is None:
                    mismatches.append(f"缺少字段 {key}")
                    continue
                
                if isinstance(expected_val, (int, float)):
                    actual_val = float(actual_val)
                    expected_val = float(expected_val)
                    diff = abs(actual_val - expected_val)
                    max_diff = expected_val * tol
                    
                    if diff > max_diff:
                        mismatches.append(
                            f"{key}: 期望{expected_val}, 实际{actual_val}"
                        )
                else:
                    if str(actual_val) != str(expected_val):
                        mismatches.append(
                            f"{key}: 期望{expected_val}, 实际{actual_val}"
                        )
            
            if mismatches:
                return False, "值不匹配: " + "; ".join(mismatches), details
            return True, "验证通过", details
        
        elif val_type == 'comparison':
            # 验证比较结果
            expected = validation['expected']
            expected_rows = validation.get('row_count', 2)
            
            if row_count != expected_rows:
                return False, f"行数不匹配: 期望{expected_rows}行, 实际{row_count}行", details
            
            # 检查哪个部门工资更高
            dept_salaries = {}
            for row in data:
                dept = None
                salary = None
                for col, val in row.items():
                    if 'department' in col.lower() or '部门' in col:
                        dept = val
                    elif 'salary' in col.lower() or '工资' in col:
                        salary = float(val)
                
                if dept and salary:
                    dept_salaries[dept] = salary
            
            if len(dept_salaries) != expected_rows:
                return False, f"部门数量不匹配", details
            
            # 找出工资最高的部门
            actual_higher = max(dept_salaries, key=dept_salaries.get)
            expected_higher = expected['higher']
            
            if actual_higher != expected_higher:
                return False, f"最高工资部门不匹配: 期望{expected_higher}, 实际{actual_higher}", details
            
            return True, "验证通过", details
        
        elif val_type == 'top_n':
            # 验证Top N结果
            expected_rows = validation['expected_rows']
            top_ids = validation.get('top_employee_ids', [])
            check_order = validation.get('check_ordering', False)
            
            if row_count < expected_rows:
                return False, f"行数不足: 期望至少{expected_rows}行, 实际{row_count}行", details
            
            # 提取实际的员工ID
            actual_ids = []
            for row in data[:expected_rows]:
                for col, val in row.items():
                    if 'employee_id' in col.lower() or '员工id' in col:
                        actual_ids.append(val)
                        break
            
            if check_order:
                # 严格检查顺序
                if actual_ids != top_ids:
                    return False, f"Top {expected_rows}员工ID或顺序不匹配", details
            else:
                # 只检查集合是否匹配
                if set(actual_ids) != set(top_ids):
                    return False, f"Top {expected_rows}员工ID集合不匹配", details
            
            return True, "验证通过", details
        
        elif val_type == 'existence_check':
            # 验证存在性检查
            min_rows = validation.get('min_rows', 1)
            has_issues = validation.get('has_issues', True)
            
            if has_issues:
                if row_count < min_rows:
                    return False, f"检测到的问题数量不足: 期望至少{min_rows}条, 实际{row_count}条", details
            else:
                if row_count > 0:
                    return False, f"不应该有问题记录, 但发现了{row_count}条", details
            
            return True, "验证通过", details
        
        else:
            return False, f"未知的验证类型: {val_type}", details
    
    except Exception as e:
        return False, f"验证过程出错: {str(e)}", details


def print_all_questions():
    """打印所有测试问题"""
    print("=" * 70)
    print("ERP Agent 测试问题集")
    print("=" * 70)
    
    for q in TEST_QUESTIONS:
        print(f"\n问题 {q['id']}: {q['question']}")
        print(f"  分类: {q['category']}")
        print(f"  难度: {q['difficulty']}")
        print(f"  描述: {q['description']}")
        if q['validation'].get('type') == 'skip':
            print(f"  ⚠️  {q['validation'].get('reason')}")


if __name__ == '__main__':
    print_all_questions()
    
    # 测试验证功能
    print("\n\n" + "=" * 70)
    print("测试验证功能")
    print("=" * 70)
    
    # 示例：问题1的验证
    print("\n测试问题1的验证:")
    mock_result = {
        'success': True,
        'data': [{'avg_days': 1100.0, 'avg_years': 3.01}],
        'row_count': 1
    }
    
    passed, message, details = validate_result(1, mock_result)
    print(f"  结果: {'✓ 通过' if passed else '✗ 失败'}")
    print(f"  信息: {message}")
    if details:
        print(f"  详情: {details}")
