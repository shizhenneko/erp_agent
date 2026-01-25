#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent 测试问题集
包含10个测试问题及其验证规则
"""

# 10个测试问题
TEST_QUESTIONS = [
    {
        'id': 1,
        'question': '平均每个员工在公司在职多久？',
        'category': 'simple',
        'description': '计算所有员工（包括已离职）的平均在职时长',
        'expected_type': 'numeric',
        'validation': {
            'type': 'range',
            'min': 500,  # 至少500天
            'max': 2000,  # 不超过2000天
            'unit': 'days'
        },
        'complexity': 'medium',
        'keywords': ['在职时长', '平均', 'CASE', 'CURRENT_DATE']
    },
    {
        'id': 2,
        'question': '公司目前有多少在职员工？',
        'category': 'simple',
        'description': '统计 leave_date 为 NULL 的员工数量',
        'expected_type': 'numeric',
        'validation': {
            'type': 'range',
            'min': 80,
            'max': 95,
            'unit': 'count'
        },
        'complexity': 'easy',
        'keywords': ['在职', 'COUNT', 'leave_date IS NULL']
    },
    {
        'id': 3,
        'question': '每个部门分别有多少在职员工？',
        'category': 'simple',
        'description': '按部门分组统计在职员工数量',
        'expected_type': 'table',
        'validation': {
            'type': 'columns',
            'required_columns': ['department_name', 'count'],
            'row_count_min': 5,
            'row_count_max': 5
        },
        'complexity': 'easy',
        'keywords': ['部门', 'GROUP BY', '在职', 'COUNT']
    },
    {
        'id': 4,
        'question': '每个部门今年和去年各新入职了多少人？',
        'category': 'time_comparison',
        'description': '按部门分组，分别统计2026年和2025年的新入职人数',
        'expected_type': 'table',
        'validation': {
            'type': 'columns',
            'required_columns': ['department_name', 'hires_2026', 'hires_2025'],
            'row_count_min': 5,
            'row_count_max': 5
        },
        'complexity': 'medium',
        'keywords': ['部门', '今年', '去年', 'CASE', 'EXTRACT(YEAR)']
    },
    {
        'id': 5,
        'question': '在职员工中职级最高的5位员工是谁？',
        'category': 'ranking',
        'description': '筛选在职员工，按职级降序排列，取前5名',
        'expected_type': 'table',
        'validation': {
            'type': 'columns',
            'required_columns': ['employee_name', 'current_level'],
            'row_count_min': 5,
            'row_count_max': 5,
            'order': 'current_level DESC'
        },
        'complexity': 'easy',
        'keywords': ['在职', '职级', 'ORDER BY', 'LIMIT 5']
    },
    {
        'id': 6,
        'question': '工资最高的前10名在职员工是谁？',
        'category': 'ranking',
        'description': '关联员工和工资表，获取每个在职员工的最新工资，按工资降序取前10',
        'expected_type': 'table',
        'validation': {
            'type': 'columns',
            'required_columns': ['employee_name', 'salary_amount'],
            'row_count_min': 10,
            'row_count_max': 10,
            'order': 'salary_amount DESC'
        },
        'complexity': 'medium',
        'keywords': ['在职', '工资', 'JOIN', '最新', 'ORDER BY', 'LIMIT 10']
    },
    {
        'id': 7,
        'question': '去年A部门的平均工资是多少？',
        'category': 'aggregation',
        'description': '关联员工和工资表，筛选A部门和2025年，计算平均工资',
        'expected_type': 'numeric',
        'validation': {
            'type': 'range',
            'min': 15000,
            'max': 30000,
            'unit': 'amount'
        },
        'complexity': 'medium',
        'keywords': ['A部门', '去年', '平均工资', 'JOIN', 'AVG', 'EXTRACT(YEAR)']
    },
    {
        'id': 8,
        'question': '从前年3月到去年5月，A部门的平均工资是多少？',
        'category': 'time_range',
        'description': '关联员工和工资表，筛选A部门和2024-03-01至2025-05-31的工资记录，计算平均值',
        'expected_type': 'numeric',
        'validation': {
            'type': 'range',
            'min': 15000,
            'max': 30000,
            'unit': 'amount'
        },
        'complexity': 'medium',
        'keywords': ['A部门', '前年', '去年', '平均工资', 'BETWEEN', 'JOIN']
    },
    {
        'id': 9,
        'question': '从去年到今年涨薪幅度最大的10位员工是谁？',
        'category': 'complex',
        'description': '需要计算每个员工2025年和2026年的平均工资，计算涨薪比例，排序取前10',
        'expected_type': 'table',
        'validation': {
            'type': 'columns',
            'required_columns': ['employee_name', 'increase_percentage'],
            'row_count_min': 10,
            'row_count_max': 10,
            'order': 'increase_percentage DESC'
        },
        'complexity': 'hard',
        'keywords': ['去年', '今年', '涨薪', 'CTE', 'JOIN', '比例', 'ORDER BY']
    },
    {
        'id': 10,
        'question': '有没有出现过拖欠员工工资的情况？如果有，是哪些员工？',
        'category': 'complex',
        'description': '生成每个员工应发工资的月份，检查是否有缺失的工资记录',
        'expected_type': 'table',
        'validation': {
            'type': 'exists',
            'expect_rows': True,  # 应该有结果（数据中故意设计了2条拖欠记录）
            'row_count_min': 2,
            'row_count_max': 2
        },
        'complexity': 'hard',
        'keywords': ['拖欠工资', 'generate_series', 'LEFT JOIN', 'IS NULL']
    }
]


def get_question_by_id(question_id: int) -> dict:
    """
    根据问题ID获取问题详情
    
    Args:
        question_id: 问题ID (1-10)
        
    Returns:
        问题字典，如果未找到返回 None
    """
    for q in TEST_QUESTIONS:
        if q['id'] == question_id:
            return q
    return None


def get_questions_by_category(category: str) -> list:
    """
    根据类别获取问题列表
    
    Args:
        category: 问题类别 (simple/time_comparison/ranking/aggregation/time_range/complex)
        
    Returns:
        问题列表
    """
    return [q for q in TEST_QUESTIONS if q['category'] == category]


def get_questions_by_complexity(complexity: str) -> list:
    """
    根据复杂度获取问题列表
    
    Args:
        complexity: 复杂度 (easy/medium/hard)
        
    Returns:
        问题列表
    """
    return [q for q in TEST_QUESTIONS if q['complexity'] == complexity]


def validate_result(question_id: int, result: any) -> dict:
    """
    验证查询结果是否符合预期
    
    Args:
        question_id: 问题ID
        result: 查询结果
        
    Returns:
        验证结果字典:
        {
            'valid': True/False,
            'message': '验证信息',
            'details': {...}
        }
    """
    question = get_question_by_id(question_id)
    if not question:
        return {
            'valid': False,
            'message': f'未找到问题ID {question_id}',
            'details': {}
        }
    
    validation = question['validation']
    
    # 根据验证类型进行不同的验证
    if validation['type'] == 'range':
        # 数值范围验证
        if not isinstance(result, (int, float)):
            return {
                'valid': False,
                'message': f'结果类型错误，期望数值类型，实际为 {type(result)}',
                'details': {'result': result}
            }
        
        if result < validation['min'] or result > validation['max']:
            return {
                'valid': False,
                'message': f'结果超出预期范围 [{validation["min"]}, {validation["max"]}]',
                'details': {
                    'result': result,
                    'min': validation['min'],
                    'max': validation['max'],
                    'unit': validation.get('unit', '')
                }
            }
        
        return {
            'valid': True,
            'message': '验证通过',
            'details': {
                'result': result,
                'unit': validation.get('unit', '')
            }
        }
    
    elif validation['type'] == 'columns':
        # 表格列验证
        if not isinstance(result, list):
            return {
                'valid': False,
                'message': '结果类型错误，期望列表类型',
                'details': {}
            }
        
        if len(result) == 0:
            return {
                'valid': False,
                'message': '结果为空',
                'details': {}
            }
        
        # 检查行数
        if len(result) < validation['row_count_min'] or len(result) > validation['row_count_max']:
            return {
                'valid': False,
                'message': f'行数不符合预期 [{validation["row_count_min"]}, {validation["row_count_max"]}]',
                'details': {
                    'row_count': len(result),
                    'expected_min': validation['row_count_min'],
                    'expected_max': validation['row_count_max']
                }
            }
        
        # 检查列名
        first_row = result[0]
        if isinstance(first_row, dict):
            actual_columns = set(first_row.keys())
            required_columns = set(validation['required_columns'])
            
            if not required_columns.issubset(actual_columns):
                missing = required_columns - actual_columns
                return {
                    'valid': False,
                    'message': f'缺少必需列: {missing}',
                    'details': {
                        'required_columns': validation['required_columns'],
                        'actual_columns': list(actual_columns)
                    }
                }
        
        return {
            'valid': True,
            'message': '验证通过',
            'details': {
                'row_count': len(result)
            }
        }
    
    elif validation['type'] == 'exists':
        # 存在性验证
        if not isinstance(result, list):
            return {
                'valid': False,
                'message': '结果类型错误，期望列表类型',
                'details': {}
            }
        
        expect_rows = validation['expect_rows']
        has_rows = len(result) > 0
        
        if expect_rows and not has_rows:
            return {
                'valid': False,
                'message': '期望有结果但结果为空',
                'details': {}
            }
        
        if not expect_rows and has_rows:
            return {
                'valid': False,
                'message': '期望无结果但有结果返回',
                'details': {'row_count': len(result)}
            }
        
        # 检查行数
        if 'row_count_min' in validation and len(result) < validation['row_count_min']:
            return {
                'valid': False,
                'message': f'行数少于预期最小值 {validation["row_count_min"]}',
                'details': {'row_count': len(result)}
            }
        
        if 'row_count_max' in validation and len(result) > validation['row_count_max']:
            return {
                'valid': False,
                'message': f'行数多于预期最大值 {validation["row_count_max"]}',
                'details': {'row_count': len(result)}
            }
        
        return {
            'valid': True,
            'message': '验证通过',
            'details': {'row_count': len(result)}
        }
    
    else:
        return {
            'valid': False,
            'message': f'未知的验证类型: {validation["type"]}',
            'details': {}
        }


def print_all_questions():
    """打印所有测试问题"""
    print("="*80)
    print("ERP Agent 测试问题集")
    print("="*80)
    
    for q in TEST_QUESTIONS:
        print(f"\n问题 {q['id']}: {q['question']}")
        print(f"  类别: {q['category']}")
        print(f"  复杂度: {q['complexity']}")
        print(f"  描述: {q['description']}")
        print(f"  关键词: {', '.join(q['keywords'])}")
    
    print("\n" + "="*80)


if __name__ == '__main__':
    # 打印所有问题
    print_all_questions()
    
    # 统计信息
    print("\n统计信息:")
    print(f"  问题总数: {len(TEST_QUESTIONS)}")
    print(f"  简单问题: {len(get_questions_by_complexity('easy'))} 个")
    print(f"  中等问题: {len(get_questions_by_complexity('medium'))} 个")
    print(f"  困难问题: {len(get_questions_by_complexity('hard'))} 个")
