#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent 测试数据生成脚本（确定性版本）
生成100名员工和对应的工资记录
时间跨度: 2021-01-01 至 2026-01-25
特点：无随机性，每次运行生成相同数据
"""

import psycopg2
from datetime import datetime, date, timedelta
from decimal import Decimal

# 数据库连接配置
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,
    'database': 'erp_agent_db',
    'user': 'postgres',
    'password': 'postgres'  # 请根据实际情况修改
}

# 100名员工的固定配置（确定性分配）
EMPLOYEES_CONFIG = [
    # A部门 - 25人
    # 格式: (编号, 姓名, 部门, 级别, 入职日期, 是否离职)
    (1, "张伟", "A部门", 5, date(2021, 3, 15), False),
    (2, "王芳", "A部门", 3, date(2022, 6, 20), False),
    (3, "李娜", "A部门", 7, date(2021, 1, 10), False),
    (4, "刘强", "A部门", 4, date(2023, 9, 5), False),
    (5, "陈静", "A部门", 2, date(2024, 2, 1), False),
    (6, "杨洋", "A部门", 6, date(2022, 4, 12), False),
    (7, "赵敏", "A部门", 8, date(2021, 7, 25), False),
    (8, "黄磊", "A部门", 3, date(2023, 11, 8), False),
    (9, "周杰", "A部门", 5, date(2022, 8, 30), False),
    (10, "吴悠", "A部门", 2, date(2024, 5, 15), False),
    (11, "徐帆", "A部门", 9, date(2021, 2, 20), False),
    (12, "孙丽", "A部门", 4, date(2023, 3, 10), False),
    (13, "朱军", "A部门", 1, date(2025, 1, 5), False),
    (14, "高峰", "A部门", 6, date(2022, 10, 18), False),
    (15, "郑爽", "A部门", 3, date(2024, 7, 22), False),
    (16, "谢娜", "A部门", 5, date(2021, 9, 12), False),
    (17, "何炅", "A部门", 7, date(2022, 1, 25), False),
    (18, "宋佳", "A部门", 2, date(2023, 6, 30), False),
    (19, "韩雪", "A部门", 4, date(2024, 11, 8), False),
    (20, "曹云", "A部门", 10, date(2021, 5, 5), False),
    (21, "许晴", "A部门", 1, date(2025, 8, 20), False),
    (22, "邓超", "A部门", 6, date(2022, 12, 15), True),  # 已离职
    (23, "冯巩", "A部门", 3, date(2023, 4, 1), True),   # 已离职
    (24, "于谦", "A部门", 5, date(2021, 11, 28), True),  # 已离职
    (25, "马云", "A部门", 8, date(2022, 7, 10), False),
    
    # B部门 - 23人
    (26, "沈腾", "B部门", 4, date(2021, 4, 15), False),
    (27, "贾玲", "B部门", 2, date(2022, 8, 20), False),
    (28, "岳云鹏", "B部门", 6, date(2021, 6, 5), False),
    (29, "郭德纲", "B部门", 9, date(2021, 1, 20), False),
    (30, "林志玲", "B部门", 3, date(2023, 2, 14), False),
    (31, "范冰冰", "B部门", 5, date(2022, 5, 8), False),
    (32, "李冰冰", "B部门", 7, date(2021, 9, 22), False),
    (33, "章子怡", "B部门", 4, date(2023, 7, 18), False),
    (34, "赵薇", "B部门", 2, date(2024, 3, 25), False),
    (35, "周星驰", "B部门", 10, date(2021, 3, 1), False),
    (36, "成龙", "B部门", 8, date(2022, 11, 30), False),
    (37, "李连杰", "B部门", 6, date(2023, 10, 12), False),
    (38, "甄子丹", "B部门", 3, date(2024, 6, 5), False),
    (39, "吴京", "B部门", 5, date(2021, 12, 20), False),
    (40, "胡歌", "B部门", 4, date(2022, 4, 8), False),
    (41, "霍建华", "B部门", 2, date(2023, 9, 15), False),
    (42, "杨幂", "B部门", 7, date(2021, 8, 28), False),
    (43, "刘诗诗", "B部门", 3, date(2024, 1, 10), False),
    (44, "唐嫣", "B部门", 5, date(2022, 6, 22), True),   # 已离职
    (45, "赵丽颖", "B部门", 1, date(2025, 3, 18), False),
    (46, "迪丽热巴", "B部门", 4, date(2023, 5, 30), True),  # 已离职
    (47, "杨紫", "B部门", 6, date(2021, 10, 5), True),   # 已离职
    (48, "张艺兴", "B部门", 2, date(2024, 9, 12), False),
    
    # C部门 - 20人
    (49, "易烊千玺", "C部门", 3, date(2021, 2, 28), False),
    (50, "王一博", "C部门", 5, date(2022, 7, 15), False),
    (51, "肖战", "C部门", 4, date(2023, 1, 8), False),
    (52, "李现", "C部门", 2, date(2024, 4, 20), False),
    (53, "邓伦", "C部门", 6, date(2021, 8, 10), False),
    (54, "罗云熙", "C部门", 3, date(2022, 10, 25), False),
    (55, "任嘉伦", "C部门", 7, date(2021, 5, 18), False),
    (56, "白敬亭", "C部门", 4, date(2023, 8, 5), False),
    (57, "刘昊然", "C部门", 5, date(2022, 3, 12), False),
    (58, "吴磊", "C部门", 2, date(2024, 10, 30), False),
    (59, "王俊凯", "C部门", 8, date(2021, 11, 8), False),
    (60, "王源", "C部门", 3, date(2023, 4, 22), False),
    (61, "刘宪华", "C部门", 6, date(2022, 9, 15), False),
    (62, "陈伟霆", "C部门", 4, date(2021, 7, 5), False),
    (63, "黄子韬", "C部门", 1, date(2025, 5, 10), False),
    (64, "鹿晗", "C部门", 5, date(2022, 1, 28), False),
    (65, "张若昀", "C部门", 2, date(2024, 8, 18), False),
    (66, "宋威龙", "C部门", 9, date(2021, 4, 25), False),
    (67, "许凯", "C部门", 3, date(2023, 12, 10), True),   # 已离职
    (68, "龚俊", "C部门", 6, date(2022, 5, 20), True),   # 已离职
    
    # D部门 - 18人
    (69, "张哲瀚", "D部门", 4, date(2021, 3, 8), False),
    (70, "檀健次", "D部门", 2, date(2022, 8, 15), False),
    (71, "侯明昊", "D部门", 5, date(2023, 2, 20), False),
    (72, "宋祖儿", "D部门", 3, date(2024, 6, 10), False),
    (73, "关晓彤", "D部门", 7, date(2021, 10, 28), False),
    (74, "欧阳娜娜", "D部门", 4, date(2022, 4, 5), False),
    (75, "文淇", "D部门", 6, date(2023, 9, 18), False),
    (76, "张子枫", "D部门", 2, date(2024, 12, 25), False),
    (77, "周冬雨", "D部门", 8, date(2021, 6, 12), False),
    (78, "谭松韵", "D部门", 3, date(2022, 11, 8), False),
    (79, "吴倩", "D部门", 5, date(2023, 5, 15), False),
    (80, "程潇", "D部门", 4, date(2021, 9, 30), False),
    (81, "孟美岐", "D部门", 1, date(2025, 2, 14), False),
    (82, "吴宣仪", "D部门", 6, date(2022, 7, 22), False),
    (83, "杨超越", "D部门", 2, date(2024, 3, 5), False),
    (84, "李宇春", "D部门", 10, date(2021, 1, 15), False),
    (85, "周笔畅", "D部门", 5, date(2023, 10, 20), True),  # 已离职
    (86, "张靓颖", "D部门", 3, date(2022, 6, 8), True),   # 已离职
    
    # E部门 - 14人
    (87, "华晨宇", "E部门", 4, date(2021, 5, 10), False),
    (88, "毛不易", "E部门", 2, date(2022, 9, 25), False),  # 有拖欠工资
    (89, "陈奕迅", "E部门", 9, date(2021, 2, 18), False),
    (90, "林俊杰", "E部门", 6, date(2023, 7, 5), False),
    (91, "周杰伦", "E部门", 10, date(2021, 11, 20), False),
    (92, "王力宏", "E部门", 5, date(2022, 3, 30), False),  # 有拖欠工资
    (93, "蔡依林", "E部门", 7, date(2023, 11, 15), False),
    (94, "邓紫棋", "E部门", 3, date(2024, 5, 8), False),
    (95, "田馥甄", "E部门", 4, date(2021, 8, 22), False),
    (96, "孙燕姿", "E部门", 8, date(2022, 12, 10), False),
    (97, "梁静茹", "E部门", 2, date(2023, 6, 18), False),
    (98, "张惠妹", "E部门", 6, date(2024, 10, 5), False),
    (99, "林宥嘉", "E部门", 1, date(2025, 4, 12), False),
    (100, "李荣浩", "E部门", 5, date(2021, 7, 28), True),  # 已离职
]

# 工资基础金额（按级别，确定性）
SALARY_BASE = {
    1: 7000.00,
    2: 9000.00,
    3: 11000.00,
    4: 13500.00,
    5: 16500.00,
    6: 20000.00,
    7: 25000.00,
    8: 31500.00,
    9: 40000.00,
    10: 52500.00
}

# A部门工资系数
A_DEPT_MULTIPLIER = 1.05

# 年度涨薪比例（确定性）
ANNUAL_RAISE_RATE = 0.075  # 固定7.5%

# 高涨薪员工（固定8人）- 这些员工在2025年6月涨薪40%
HIGH_RAISE_EMPLOYEES = [
    'EMP003', 'EMP011', 'EMP029', 'EMP032', 
    'EMP055', 'EMP059', 'EMP077', 'EMP089'
]

# 拖欠工资记录（确定性）
MISSING_SALARIES = [
    ('EMP088', date(2024, 7, 25)),  # 毛不易 2024年7月
    ('EMP092', date(2023, 11, 25))  # 王力宏 2023年11月
]


def connect_db():
    """连接数据库"""
    return psycopg2.connect(**DB_CONFIG)


def calculate_leave_date(hire_date, emp_id):
    """计算离职日期（确定性）"""
    # 根据员工编号计算离职日期，保证一致性
    emp_num = int(emp_id[3:])
    
    # 使用确定性算法
    months_after_hire = 12 + (emp_num * 7) % 24  # 12-36个月之间
    leave_date = hire_date + timedelta(days=months_after_hire * 30)
    
    # 确保不超过当前日期
    if leave_date > date(2026, 1, 25):
        leave_date = date(2025, 6, 15)
    
    return leave_date


def generate_employees():
    """生成员工数据（确定性）"""
    employees = []
    
    for config in EMPLOYEES_CONFIG:
        emp_num, emp_name, dept, level, hire_date, has_left = config
        emp_id = f"EMP{emp_num:03d}"
        
        # 计算离职日期
        leave_date = None
        if has_left:
            leave_date = calculate_leave_date(hire_date, emp_id)
        
        employees.append({
            'employee_id': emp_id,
            'employee_name': emp_name,
            'department_name': dept,
            'current_level': level,
            'hire_date': hire_date,
            'leave_date': leave_date
        })
    
    return employees


def generate_salaries(employees):
    """生成工资记录（确定性）"""
    salaries = []
    missing_set = set(MISSING_SALARIES)
    
    for emp in employees:
        emp_id = emp['employee_id']
        hire_date = emp['hire_date']
        leave_date = emp['leave_date']
        level = emp['current_level']
        dept = emp['department_name']
        
        # 基础工资（确定性）
        base_salary = Decimal(str(SALARY_BASE[level]))
        if dept == 'A部门':
            base_salary = base_salary * Decimal(str(A_DEPT_MULTIPLIER))
        
        # 生成每月工资记录
        current_date = date(hire_date.year, hire_date.month, 25)  # 每月25号发薪
        if current_date < hire_date:
            # 如果25号早于入职日期，发薪推迟到下个月
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 25)
            else:
                current_date = date(current_date.year, current_date.month + 1, 25)
        
        end_date = leave_date if leave_date else date(2026, 1, 25)
        
        current_salary = base_salary
        last_raise_year = hire_date.year - 1  # 确保第一年1月就能涨薪
        
        while current_date <= end_date:
            # 检查是否是拖欠工资月份
            if (emp_id, current_date) in missing_set:
                # 跳过这个月的工资
                pass
            else:
                # 每年1月涨薪
                if current_date.month == 1 and current_date.year > last_raise_year:
                    current_salary = current_salary * Decimal(str(1 + ANNUAL_RAISE_RATE))
                    last_raise_year = current_date.year
                
                # 特殊高涨薪
                if emp_id in HIGH_RAISE_EMPLOYEES and current_date == date(2025, 6, 25):
                    current_salary = current_salary * Decimal('1.40')  # 涨薪40%
                
                salaries.append({
                    'employee_id': emp_id,
                    'payment_date': current_date,
                    'salary_amount': round(float(current_salary), 2)
                })
            
            # 下一个月
            if current_date.month == 12:
                current_date = date(current_date.year + 1, 1, 25)
            else:
                current_date = date(current_date.year, current_date.month + 1, 25)
    
    return salaries


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
    
    # 4. 级别分布
    cursor.execute("""
        SELECT current_level, COUNT(*) 
        FROM employees 
        GROUP BY current_level 
        ORDER BY current_level
    """)
    print(f"4. 级别分布:")
    for row in cursor.fetchall():
        print(f"   级别{row[0]}: {row[1]}人")
    
    # 5. 工资记录总数
    cursor.execute("SELECT COUNT(*) FROM salaries")
    total_sal = cursor.fetchone()[0]
    print(f"5. 工资记录总数: {total_sal}")
    
    # 6. 拖欠工资验证
    print(f"6. 拖欠工资验证:")
    for emp_id, payment_date in MISSING_SALARIES:
        cursor.execute("""
            SELECT COUNT(*) FROM salaries 
            WHERE employee_id = %s AND payment_date = %s
        """, (emp_id, payment_date))
        count = cursor.fetchone()[0]
        status = "✗ 已记录（错误）" if count > 0 else "✓ 未记录（正确）"
        cursor.execute("SELECT employee_name FROM employees WHERE employee_id = %s", (emp_id,))
        name = cursor.fetchone()[0]
        print(f"   {emp_id} ({name}) {payment_date}: {status}")
    
    # 7. 工资范围
    cursor.execute("""
        SELECT 
            MIN(salary_amount) as min_salary,
            AVG(salary_amount) as avg_salary,
            MAX(salary_amount) as max_salary
        FROM salaries
    """)
    row = cursor.fetchone()
    print(f"7. 工资统计:")
    print(f"   最低工资: ¥{row[0]:,.2f}")
    print(f"   平均工资: ¥{row[1]:,.2f}")
    print(f"   最高工资: ¥{row[2]:,.2f}")
    
    # 8. 高涨薪员工验证
    print(f"8. 高涨薪员工（2025年6月）验证:")
    for emp_id in HIGH_RAISE_EMPLOYEES[:3]:  # 只显示前3个
        cursor.execute("""
            SELECT s1.salary_amount, s2.salary_amount,
                   ROUND((s2.salary_amount - s1.salary_amount) / s1.salary_amount * 100, 2) as raise_pct
            FROM salaries s1
            JOIN salaries s2 ON s1.employee_id = s2.employee_id
            WHERE s1.employee_id = %s 
              AND s1.payment_date = '2025-05-25'
              AND s2.payment_date = '2025-06-25'
        """, (emp_id,))
        result = cursor.fetchone()
        if result:
            cursor.execute("SELECT employee_name FROM employees WHERE employee_id = %s", (emp_id,))
            name = cursor.fetchone()[0]
            print(f"   {emp_id} ({name}): ¥{result[0]:.2f} → ¥{result[1]:.2f} (+{result[2]}%)")
    print(f"   ... 共 {len(HIGH_RAISE_EMPLOYEES)} 人")
    
    cursor.close()
    print("="*60)


def main():
    """主函数"""
    print("ERP Agent 测试数据生成（确定性版本）")
    print("="*60)
    
    # 连接数据库
    print("正在连接数据库...")
    conn = connect_db()
    print("✓ 数据库连接成功")
    
    # 生成员工数据
    print("\n正在生成员工数据...")
    employees = generate_employees()
    print(f"✓ 生成 {len(employees)} 名员工（确定性）")
    
    # 生成工资数据
    print("\n正在生成工资数据...")
    salaries = generate_salaries(employees)
    print(f"✓ 生成 {len(salaries)} 条工资记录（确定性）")
    
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
    print("\n说明：")
    print("  - 本版本使用确定性算法，每次运行生成完全相同的数据")
    print("  - 适合用于测试验证，确保标准答案的一致性")


if __name__ == '__main__':
    main()
