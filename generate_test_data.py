#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent 测试数据生成脚本
生成100名员工和对应的工资记录
时间跨度: 2021-01-01 至 2026-01-25
"""

import psycopg2
from datetime import datetime, date, timedelta
from decimal import Decimal
import random

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'erp_agent_db',
    'user': 'postgres',
    'password': 'postgres'  # 请根据实际情况修改
}

# 中文姓名列表（100个）
CHINESE_NAMES = [
    "张伟", "王芳", "李娜", "刘强", "陈静",
    "杨洋", "赵敏", "黄磊", "周杰", "吴悠",
    "徐帆", "孙丽", "朱军", "高峰", "郑爽",
    "谢娜", "何炅", "宋佳", "韩雪", "曹云",
    "许晴", "邓超", "冯巩", "于谦", "史蒂夫",
    "马云", "沈腾", "贾玲", "岳云鹏", "郭德纲",
    "林志玲", "范冰冰", "李冰冰", "章子怡", "赵薇",
    "周星驰", "成龙", "李连杰", "甄子丹", "吴京",
    "胡歌", "霍建华", "杨幂", "刘诗诗", "唐嫣",
    "赵丽颖", "迪丽热巴", "杨紫", "张艺兴", "易烊千玺",
    "王一博", "肖战", "李现", "邓伦", "罗云熙",
    "任嘉伦", "白敬亭", "刘昊然", "吴磊", "王俊凯",
    "王源", "刘宪华", "陈伟霆", "黄子韬", "鹿晗",
    "吴亦凡", "张若昀", "宋威龙", "许凯", "龚俊",
    "张哲瀚", "檀健次", "侯明昊", "宋祖儿", "关晓彤",
    "欧阳娜娜", "文淇", "张子枫", "周冬雨", "谭松韵",
    "吴倩", "程潇", "孟美岐", "吴宣仪", "杨超越",
    "李宇春", "周笔畅", "张靓颖", "华晨宇", "毛不易",
    "陈奕迅", "林俊杰", "周杰伦", "王力宏", "蔡依林",
    "邓紫棋", "田馥甄", "孙燕姿", "梁静茹", "张惠妹"
]

# 部门信息
DEPARTMENTS = {
    'A部门': 25,
    'B部门': 23,
    'C部门': 20,
    'D部门': 18,
    'E部门': 14
}

# 级别分布
LEVEL_DISTRIBUTION = {
    (1, 3): 50,  # 初级：50人
    (4, 6): 30,  # 中级：30人
    (7, 8): 15,  # 高级：15人
    (9, 10): 5   # 专家：5人
}

# 入职年份分布
HIRE_YEAR_DISTRIBUTION = {
    2021: 15,
    2022: 20,
    2023: 18,
    2024: 22,
    2025: 18,
    2026: 7
}

# 工资基础范围（按级别）
SALARY_RANGES = {
    1: (6000, 8000),
    2: (8000, 10000),
    3: (10000, 12000),
    4: (12000, 15000),
    5: (15000, 18000),
    6: (18000, 22000),
    7: (22000, 28000),
    8: (28000, 35000),
    9: (35000, 45000),
    10: (45000, 60000)
}


def connect_db():
    """连接数据库"""
    return psycopg2.connect(**DB_CONFIG)


def generate_employees():
    """生成员工数据"""
    employees = []
    employee_id = 1
    name_index = 0
    
    # 按部门生成
    for dept_name, dept_count in DEPARTMENTS.items():
        for _ in range(dept_count):
            emp_id = f"EMP{employee_id:03d}"
            emp_name = CHINESE_NAMES[name_index % len(CHINESE_NAMES)]
            name_index += 1
            
            # 分配级别（按分布）
            level = assign_level()
            
            # 分配入职日期
            hire_date = assign_hire_date()
            
            # 25%的员工已离职
            leave_date = None
            if random.random() < 0.25:
                # 离职日期在入职后至少3个月
                days_after_hire = random.randint(90, 1500)
                potential_leave = hire_date + timedelta(days=days_after_hire)
                if potential_leave < date(2026, 1, 25):
                    leave_date = potential_leave
            
            employees.append({
                'employee_id': emp_id,
                'employee_name': emp_name,
                'department_name': dept_name,
                'current_level': level,
                'hire_date': hire_date,
                'leave_date': leave_date
            })
            
            employee_id += 1
    
    return employees


def assign_level():
    """按分布分配级别"""
    if not hasattr(assign_level, 'level_pool'):
        assign_level.level_pool = []
        for (min_level, max_level), count in LEVEL_DISTRIBUTION.items():
            for _ in range(count):
                assign_level.level_pool.append(random.randint(min_level, max_level))
        random.shuffle(assign_level.level_pool)
    
    return assign_level.level_pool.pop() if assign_level.level_pool else 5


def assign_hire_date():
    """按分布分配入职日期"""
    if not hasattr(assign_hire_date, 'date_pool'):
        assign_hire_date.date_pool = []
        for year, count in HIRE_YEAR_DISTRIBUTION.items():
            for _ in range(count):
                if year == 2026:
                    month = 1
                    day = random.randint(1, 25)
                else:
                    month = random.randint(1, 12)
                    day = random.randint(1, 28)
                assign_hire_date.date_pool.append(date(year, month, day))
        random.shuffle(assign_hire_date.date_pool)
    
    return assign_hire_date.date_pool.pop() if assign_hire_date.date_pool else date(2023, 6, 15)


def generate_salaries(employees):
    """生成工资记录"""
    salaries = []
    
    # 记录哪些员工涨薪幅度大（用于问题9）
    high_raise_employees = random.sample(
        [e for e in employees if e['leave_date'] is None or e['leave_date'] > date(2024, 12, 31)],
        min(8, len([e for e in employees if e['leave_date'] is None]))
    )
    high_raise_ids = {e['employee_id'] for e in high_raise_employees}
    
    for emp in employees:
        emp_id = emp['employee_id']
        hire_date = emp['hire_date']
        leave_date = emp['leave_date']
        level = emp['current_level']
        dept = emp['department_name']
        
        # 基础工资
        base_salary = get_base_salary(level, dept)
        
        # 生成每月工资记录
        current_date = date(hire_date.year, hire_date.month, 25)  # 每月25号发薪
        if current_date < hire_date:
            current_date = (current_date.replace(day=1) + timedelta(days=32)).replace(day=25)
        
        end_date = leave_date if leave_date else date(2026, 1, 25)
        
        current_salary = base_salary
        last_raise_month = None
        
        while current_date <= end_date:
            # 特殊处理：拖欠工资场景
            skip_payment = False
            if emp_id == 'EMP088' and current_date == date(2024, 7, 25):
                skip_payment = True
            elif emp_id == 'EMP092' and current_date == date(2023, 11, 25):
                skip_payment = True
            
            if not skip_payment:
                # 每年自然增长5-10%
                if current_date.month == 1 and last_raise_month != current_date:
                    growth_rate = random.uniform(0.05, 0.10)
                    current_salary = current_salary * (1 + growth_rate)
                    last_raise_month = current_date
                
                # 高涨薪员工：2025年某月涨薪30-50%
                if emp_id in high_raise_ids and current_date.year == 2025 and current_date.month == 6:
                    raise_rate = random.uniform(0.30, 0.50)
                    current_salary = current_salary * (1 + raise_rate)
                
                salaries.append({
                    'employee_id': emp_id,
                    'payment_date': current_date,
                    'salary_amount': round(current_salary, 2)
                })
            
            # 下一个月
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 25)
            else:
                current_date = date(current_date.year, current_date.month + 1, 25)
    
    return salaries


def get_base_salary(level, department):
    """获取基础工资（A部门略高于B部门）"""
    min_sal, max_sal = SALARY_RANGES[level]
    base = random.uniform(min_sal, max_sal)
    
    # A部门工资平均高5%
    if department == 'A部门':
        base = base * 1.05
    
    return base


def insert_employees(conn, employees):
    """插入员工数据"""
    cursor = conn.cursor()
    
    for emp in employees:
        cursor.execute("""
            INSERT INTO employees 
            (employee_id, employee_name, department_name, current_level, hire_date, leave_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            emp['employee_id'],
            emp['employee_name'],
            emp['department_name'],
            emp['current_level'],
            emp['hire_date'],
            emp['leave_date']
        ))
    
    conn.commit()
    cursor.close()
    print(f"✓ 成功插入 {len(employees)} 条员工记录")


def insert_salaries(conn, salaries):
    """批量插入工资数据"""
    cursor = conn.cursor()
    
    # 批量插入
    batch_size = 1000
    for i in range(0, len(salaries), batch_size):
        batch = salaries[i:i + batch_size]
        
        values = []
        for sal in batch:
            values.append(cursor.mogrify("(%s, %s, %s)", (
                sal['employee_id'],
                sal['payment_date'],
                sal['salary_amount']
            )).decode('utf-8'))
        
        query = f"""
            INSERT INTO salaries (employee_id, payment_date, salary_amount)
            VALUES {','.join(values)}
        """
        cursor.execute(query)
        conn.commit()
        print(f"✓ 已插入 {i + len(batch)}/{len(salaries)} 条工资记录")
    
    cursor.close()
    print(f"✓ 成功插入 {len(salaries)} 条工资记录")


def verify_data(conn):
    """验证数据完整性"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("数据验证报告")
    print("="*60)
    
    # 1. 员工总数
    cursor.execute("SELECT COUNT(*) FROM employees")
    total_emp = cursor.fetchone()[0]
    print(f"1. 员工总数: {total_emp}")
    
    # 2. 在职员工数
    cursor.execute("SELECT COUNT(*) FROM employees WHERE leave_date IS NULL")
    active_emp = cursor.fetchone()[0]
    print(f"2. 在职员工数: {active_emp}")
    
    # 3. 各部门人数
    cursor.execute("""
        SELECT department_name, COUNT(*) 
        FROM employees 
        GROUP BY department_name 
        ORDER BY department_name
    """)
    print(f"3. 各部门人数分布:")
    for row in cursor.fetchall():
        print(f"   {row[0]}: {row[1]}人")
    
    # 4. 工资记录总数
    cursor.execute("SELECT COUNT(*) FROM salaries")
    total_sal = cursor.fetchone()[0]
    print(f"4. 工资记录总数: {total_sal}")
    
    # 5. 拖欠工资情况
    cursor.execute("""
        WITH employee_months AS (
            SELECT 
                e.employee_id,
                generate_series(
                    DATE_TRUNC('month', e.hire_date),
                    DATE_TRUNC('month', COALESCE(e.leave_date, '2026-01-25'::date)),
                    '1 month'::interval
                )::DATE as month
            FROM employees e
        )
        SELECT 
            em.employee_id,
            em.month,
            e.employee_name
        FROM employee_months em
        JOIN employees e ON em.employee_id = e.employee_id
        LEFT JOIN salaries s ON em.employee_id = s.employee_id 
            AND DATE_TRUNC('month', s.payment_date) = em.month
        WHERE s.salary_id IS NULL
            AND em.month < DATE_TRUNC('month', '2026-01-25'::date)
        ORDER BY em.month DESC
        LIMIT 10
    """)
    print(f"5. 拖欠工资情况（前10条）:")
    missing_count = 0
    for row in cursor.fetchall():
        print(f"   {row[0]} ({row[2]}) - {row[1]}")
        missing_count += 1
    print(f"   共发现 {missing_count} 条拖欠记录")
    
    # 6. 工资范围
    cursor.execute("""
        SELECT 
            MIN(salary_amount) as min_salary,
            AVG(salary_amount) as avg_salary,
            MAX(salary_amount) as max_salary
        FROM salaries
    """)
    row = cursor.fetchone()
    print(f"6. 工资统计:")
    print(f"   最低工资: ¥{row[0]:,.2f}")
    print(f"   平均工资: ¥{row[1]:,.2f}")
    print(f"   最高工资: ¥{row[2]:,.2f}")
    
    cursor.close()
    print("="*60)


def main():
    """主函数"""
    print("ERP Agent 测试数据生成开始...")
    print("="*60)
    
    # 连接数据库
    print("正在连接数据库...")
    conn = connect_db()
    print("✓ 数据库连接成功")
    
    # 生成员工数据
    print("\n正在生成员工数据...")
    employees = generate_employees()
    print(f"✓ 生成 {len(employees)} 名员工")
    
    # 生成工资数据
    print("\n正在生成工资数据...")
    salaries = generate_salaries(employees)
    print(f"✓ 生成 {len(salaries)} 条工资记录")
    
    # 插入数据
    print("\n正在插入员工数据...")
    insert_employees(conn, employees)
    
    print("\n正在插入工资数据...")
    insert_salaries(conn, salaries)
    
    # 验证数据
    verify_data(conn)
    
    # 关闭连接
    conn.close()
    print("\n✓ 数据生成完成！")


if __name__ == '__main__':
    main()
