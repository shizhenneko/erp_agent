"""
Prompt 构建工具模块

负责读取 Prompt 模板文件,组装完整的 Prompt,动态注入时间信息和 Few-shot 示例。

优化说明:
1. Few-shot 示例策略: 始终加载所有示例，不进行选择，以保证 SQL 查询成功率
2. 时间占位符计算: 按需计算，只计算模板中实际使用的占位符，提高性能
3. 占位符补全: 自动提取模板中的占位符并确保全部被正确填充
"""

import re
from pathlib import Path
from typing import List, Dict, Optional, Any

# 导入泛化的时间工具（支持相对导入和绝对导入）
try:
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
except ImportError:
    # 作为脚本直接运行时使用绝对导入
    from date_utils import (
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


class PromptBuilder:
    """
    Prompt 构建器
    
    属性:
        prompts_dir (Path): prompts 文件夹路径
        schema (str): 数据库 Schema 说明
        examples (str): Few-shot 示例（始终加载所有示例）
        system_prompt_template (str): 系统 Prompt 模板
    
    设计原则:
        1. 简洁性: 移除不必要的复杂度（如 few-shot 选择逻辑）
        2. 高效性: 按需计算时间占位符，避免不必要的计算
        3. 泛化性: 自动检测并填充模板占位符，提高适配性
    """
    
    def __init__(self, prompts_dir: Optional[str] = None):
        """
        初始化 Prompt 构建器
        
        参数:
            prompts_dir: prompts 文件夹路径,默认为项目的 prompts 文件夹
        """
        if prompts_dir is None:
            # 默认路径: 当前文件的上级目录的 prompts 文件夹
            current_file = Path(__file__)
            self.prompts_dir = current_file.parent.parent / 'prompts'
        else:
            self.prompts_dir = Path(prompts_dir)
        
        # 检查文件夹是否存在
        if not self.prompts_dir.exists():
            raise FileNotFoundError(f"Prompts 文件夹不存在: {self.prompts_dir}")
        
        # 延迟加载,只在需要时加载文件
        self._schema = None
        self._examples = None
        self._system_prompt_template = None
    
    def load_schema(self) -> str:
        """
        加载数据库 Schema 说明
        
        返回:
            str: Schema 文本内容
        """
        if self._schema is None:
            schema_file = self.prompts_dir / 'schema.txt'
            if not schema_file.exists():
                raise FileNotFoundError(f"Schema 文件不存在: {schema_file}")
            
            with open(schema_file, 'r', encoding='utf-8') as f:
                self._schema = f.read()
        
        return self._schema
    
    def load_examples(self) -> str:
        """
        加载 Few-shot 示例
        
        返回:
            str: 示例文本内容
        """
        if self._examples is None:
            examples_file = self.prompts_dir / 'examples.txt'
            if not examples_file.exists():
                raise FileNotFoundError(f"Examples 文件不存在: {examples_file}")
            
            with open(examples_file, 'r', encoding='utf-8') as f:
                self._examples = f.read()
        
        return self._examples
    
    def load_system_prompt_template(self) -> str:
        """
        加载系统 Prompt 模板
        
        返回:
            str: 系统 Prompt 模板文本
        """
        if self._system_prompt_template is None:
            system_prompt_file = self.prompts_dir / 'system_prompt.txt'
            if not system_prompt_file.exists():
                raise FileNotFoundError(f"System prompt 文件不存在: {system_prompt_file}")
            
            with open(system_prompt_file, 'r', encoding='utf-8') as f:
                self._system_prompt_template = f.read()
        
        return self._system_prompt_template
    
    def build_sql_generation_prompt(
        self,
        user_question: str,
        date_info: Optional[Dict[str, Any]] = None,
        context: Optional[List[Dict[str, Any]]] = None,
        error_feedback: Optional[str] = None
    ) -> str:
        """
        构建 SQL 生成的完整 Prompt
        
        参数:
            user_question: 用户问题
            date_info: 时间信息字典(来自 get_current_datetime)，如果为 None 则自动获取
            context: 历史上下文(包含之前的 SQL 和结果)
            error_feedback: 错误反馈信息(用于重试)
        
        返回:
            str: 完整的 Prompt 文本
        """
        # 如果没有提供 date_info，则自动获取当前时间
        if date_info is None:
            date_info = get_current_datetime()
        
        # 加载模板和内容
        template = self.load_system_prompt_template()
        schema = self.load_schema()
        # 始终加载所有 few-shot 示例（不进行选择）
        examples = self.load_examples()
        
        # 构建历史上下文文本
        history_context = ""
        if context and len(context) > 0:
            history_context = "\n## 历史执行记录\n\n"
            history_context += "你已经执行过以下查询:\n\n"
            
            for idx, item in enumerate(context, 1):
                history_context += f"### 第 {idx} 轮\n\n"
                
                if 'thought' in item:
                    history_context += f"**思考**: {item['thought']}\n\n"
                
                if 'sql' in item:
                    history_context += f"**SQL**: \n```sql\n{item['sql']}\n```\n\n"
                
                if 'result' in item:
                    result = item['result']
                    if result.get('success'):
                        row_count = result.get('row_count', 0)
                        history_context += f"**执行结果**: 成功,返回 {row_count} 行\n"
                        
                        # 显示部分数据(最多显示前5行)
                        if result.get('data'):
                            data = result['data'][:5]
                            history_context += f"```\n{data}\n```\n\n"
                    else:
                        error = result.get('error', '未知错误')
                        history_context += f"**执行结果**: 失败\n**错误信息**: {error}\n\n"
        
        # 构建错误反馈文本
        error_feedback_text = ""
        if error_feedback:
            error_feedback_text = "\n## ⚠️ 错误反馈\n\n"
            error_feedback_text += "上一次查询执行失败，请根据错误信息修正 SQL：\n\n"
            error_feedback_text += f"```\n{error_feedback}\n```\n\n"
            error_feedback_text += "请分析错误原因，重新生成正确的 SQL 查询。\n"
        
        # 构建迭代指令
        iteration = len(context) + 1 if context else 1
        iteration_instruction = f"\n请开始第 {iteration} 轮推理，严格按照上述 JSON 格式输出。"
        
        # 提取模板中实际使用的占位符
        template_placeholders = self.extract_placeholders(template)
        
        # 按需计算时间占位符（只计算模板中实际使用的）
        time_placeholders = self._calculate_time_placeholders(date_info, template_placeholders)
        
        # 替换模板中的所有占位符
        prompt = template.format(
            schema=schema,
            examples=examples,
            history_context=history_context,
            error_feedback=error_feedback_text,
            user_question=user_question,
            iteration_instruction=iteration_instruction,
            **time_placeholders  # 解包所有时间占位符
        )
        
        return prompt
    
    def build_answer_generation_prompt(
        self,
        user_question: str,
        sql_history: List[Dict[str, Any]]
    ) -> str:
        """
        构建答案生成的 Prompt
        
        参数:
            user_question: 用户的原始问题
            sql_history: SQL 执行历史,包含 SQL 和结果
        
        返回:
            str: 答案生成的 Prompt
        """
        prompt = "# 数据分析助手\n\n"
        prompt += "你是一个数据分析助手。根据 SQL 查询结果回答用户问题。\n\n"
        
        prompt += f"## 用户问题\n\n{user_question}\n\n"
        
        prompt += "## 查询过程\n\n"
        
        for idx, item in enumerate(sql_history, 1):
            prompt += f"### 第 {idx} 次查询\n\n"
            
            if 'sql' in item:
                prompt += f"**SQL**:\n```sql\n{item['sql']}\n```\n\n"
            
            if 'result' in item:
                result = item['result']
                if result.get('success'):
                    prompt += f"**结果**: {result.get('data')}\n\n"
                else:
                    prompt += f"**错误**: {result.get('error')}\n\n"
        
        prompt += "## 回答要求\n\n"
        prompt += "1. 用清晰、友好的中文回答问题\n"
        prompt += "2. 包含具体的数字和统计结果\n"
        prompt += "3. 如果合适，提供简单的洞察或解释\n"
        prompt += "4. 答案简洁明了，避免技术术语\n"
        prompt += "5. 如果数据显示异常或有特殊情况，请指出\n\n"
        
        prompt += "请基于以上查询结果回答用户的问题:\n"
        
        return prompt
    
    def _calculate_time_placeholders(
        self, 
        date_info: Dict[str, Any],
        required_placeholders: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        按需计算时间相关的占位符
        
        参数:
            date_info: 来自 get_current_datetime() 的时间信息
            required_placeholders: 需要计算的占位符列表，如果为 None 则计算所有
        
        返回:
            dict: 包含请求的时间占位符的字典
        """
        # 提取基础信息（总是需要）
        current_date = date_info['current_date']
        year = date_info['year']
        month = date_info['month']
        
        # 初始化结果字典，包含基础信息
        placeholders = {
            'current_date': current_date,
            'year': year,
            'month': month,
        }
        
        # 如果没有指定需要的占位符，则计算所有可能的占位符
        if required_placeholders is None:
            required_placeholders = []
        
        # 按需计算各类占位符
        time_related_fields = set(required_placeholders) if required_placeholders else set()
        
        # 基础时间信息
        if not required_placeholders or 'month_padded' in time_related_fields:
            placeholders['month_padded'] = f"{month:02d}"
        
        if not required_placeholders or 'day' in time_related_fields:
            placeholders['day'] = date_info.get('day', 1)
        
        if not required_placeholders or 'weekday' in time_related_fields:
            placeholders['weekday'] = date_info.get('weekday', '')
        
        if not required_placeholders or 'weekday_cn' in time_related_fields:
            placeholders['weekday_cn'] = date_info.get('weekday_cn', '')
        
        # 相对年份
        if not required_placeholders or 'year_minus_1' in time_related_fields:
            placeholders['year_minus_1'] = year - 1
        
        if not required_placeholders or 'year_minus_2' in time_related_fields:
            placeholders['year_minus_2'] = year - 2
        
        # 相对月份
        if not required_placeholders or 'month_minus_1' in time_related_fields:
            placeholders['month_minus_1'] = month - 1 if month > 1 else 12
        
        if not required_placeholders or 'month_minus_1_padded' in time_related_fields:
            month_minus_1 = month - 1 if month > 1 else 12
            placeholders['month_minus_1_padded'] = f"{month_minus_1:02d}"
        
        # 相对时间点
        if not required_placeholders or 'three_months_ago' in time_related_fields:
            placeholders['three_months_ago'] = calculate_date_offset(current_date, months=-3)
        
        if not required_placeholders or 'six_months_ago' in time_related_fields:
            placeholders['six_months_ago'] = calculate_date_offset(current_date, months=-6)
        
        if not required_placeholders or 'one_year_ago' in time_related_fields:
            placeholders['one_year_ago'] = calculate_date_offset(current_date, years=-1)
        
        # 年份范围
        if not required_placeholders or 'current_year_start' in time_related_fields or 'current_year_end' in time_related_fields:
            current_year_start, current_year_end = get_date_range_for_period(year)
            if not required_placeholders or 'current_year_start' in time_related_fields:
                placeholders['current_year_start'] = current_year_start
            if not required_placeholders or 'current_year_end' in time_related_fields:
                placeholders['current_year_end'] = current_year_end
        
        if not required_placeholders or 'last_year_start' in time_related_fields or 'last_year_end' in time_related_fields:
            year_minus_1 = year - 1
            last_year_start, last_year_end = get_date_range_for_period(year_minus_1)
            if not required_placeholders or 'last_year_start' in time_related_fields:
                placeholders['last_year_start'] = last_year_start
            if not required_placeholders or 'last_year_end' in time_related_fields:
                placeholders['last_year_end'] = last_year_end
        
        # 月份范围
        if not required_placeholders or 'current_month_start' in time_related_fields or 'current_month_end' in time_related_fields:
            current_month_start, current_month_end = get_month_start_end(current_date)
            if not required_placeholders or 'current_month_start' in time_related_fields:
                placeholders['current_month_start'] = current_month_start
            if not required_placeholders or 'current_month_end' in time_related_fields:
                placeholders['current_month_end'] = current_month_end
        
        # 季度范围
        if not required_placeholders or 'current_quarter_start' in time_related_fields or 'current_quarter_end' in time_related_fields:
            current_quarter_start, current_quarter_end = get_quarter_start_end(current_date)
            if not required_placeholders or 'current_quarter_start' in time_related_fields:
                placeholders['current_quarter_start'] = current_quarter_start
            if not required_placeholders or 'current_quarter_end' in time_related_fields:
                placeholders['current_quarter_end'] = current_quarter_end
        
        return placeholders
    
    def format_date_context(self, date_info: Optional[Dict[str, Any]] = None) -> str:
        """
        格式化时间上下文为易读的文本
        
        参数:
            date_info: 时间信息字典，如果为 None 则自动获取当前时间
        
        返回:
            str: 格式化的时间上下文文本
        
        示例输出:
            ========== 时间上下文 ==========
            当前日期: 2026-01-25 (周六)
            当前年份: 2026年
            当前月份: 2026年1月
            
            相对年份:
            - 去年: 2025年 (2025-01-01 至 2025-12-31)
            - 前年: 2024年 (2024-01-01 至 2024-12-31)
            
            相对时间点:
            - 一年前: 2025-01-25
            - 半年前: 2025-07-25
            - 三个月前: 2024-10-25
            
            当前时期范围:
            - 本年度: 2026-01-01 至 2026-12-31
            - 本月份: 2026-01-01 至 2026-01-31
            - 本季度: 2026-01-01 至 2026-03-31
        """
        # 如果没有提供 date_info，则自动获取当前时间
        if date_info is None:
            date_info = get_current_datetime()
        
        # 计算所有需要显示的时间占位符
        required_fields = [
            'weekday_cn', 'year_minus_1', 'year_minus_2',
            'last_year_start', 'last_year_end',
            'one_year_ago', 'six_months_ago', 'three_months_ago',
            'current_year_start', 'current_year_end',
            'current_month_start', 'current_month_end',
            'current_quarter_start', 'current_quarter_end'
        ]
        time_data = self._calculate_time_placeholders(date_info, required_fields)
        
        lines = ["========== 时间上下文 =========="]
        
        # 基础信息
        lines.append(f"当前日期: {time_data['current_date']} ({time_data.get('weekday_cn', '')})")
        lines.append(f"当前年份: {time_data['year']}年")
        lines.append(f"当前月份: {time_data['year']}年{time_data['month']}月")
        lines.append("")
        
        # 相对年份
        lines.append("相对年份:")
        lines.append(f"- 去年: {time_data.get('year_minus_1')}年 ({time_data.get('last_year_start')} 至 {time_data.get('last_year_end')})")
        # 获取前年的日期范围
        year_minus_2_start, year_minus_2_end = get_date_range_for_period(time_data.get('year_minus_2'))
        lines.append(f"- 前年: {time_data.get('year_minus_2')}年 ({year_minus_2_start} 至 {year_minus_2_end})")
        lines.append("")
        
        # 相对时间点
        lines.append("相对时间点:")
        lines.append(f"- 一年前: {time_data.get('one_year_ago')}")
        lines.append(f"- 半年前: {time_data.get('six_months_ago')}")
        lines.append(f"- 三个月前: {time_data.get('three_months_ago')}")
        lines.append("")
        
        # 当前时期范围
        lines.append("当前时期范围:")
        lines.append(f"- 本年度: {time_data.get('current_year_start')} 至 {time_data.get('current_year_end')}")
        lines.append(f"- 本月份: {time_data.get('current_month_start')} 至 {time_data.get('current_month_end')}")
        lines.append(f"- 本季度: {time_data.get('current_quarter_start')} 至 {time_data.get('current_quarter_end')}")
        
        return "\n".join(lines)
    
    def _get_output_format_instruction(self, context: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        获取输出格式说明
        
        参数:
            context: 历史上下文
        
        返回:
            str: 输出格式说明文本
        """
        iteration = len(context) + 1 if context else 1
        
        instruction = "## 输出要求\n\n"
        instruction += f"这是第 {iteration} 轮推理。请按照以下 JSON 格式输出:\n\n"
        instruction += "```json\n"
        instruction += "{\n"
        instruction += '  "thought": "你的思考过程，分析当前情况和策略",\n'
        instruction += '  "action": "execute_sql 或 answer",\n'
        instruction += '  "sql": "如果 action 是 execute_sql，这里填写 SQL 语句",\n'
        instruction += '  "answer": "如果 action 是 answer，这里填写最终答案",\n'
        instruction += '  "is_final": false 或 true\n'
        instruction += "}\n"
        instruction += "```\n\n"
        
        instruction += "**重要说明**:\n"
        instruction += "- 如果还需要查询数据，使用 `action: execute_sql` 并提供 SQL\n"
        instruction += "- 如果已经可以回答问题，使用 `action: answer` 并提供答案，同时设置 `is_final: true`\n"
        instruction += "- `thought` 字段必须包含你的推理过程\n"
        instruction += "- SQL 必须是可以直接执行的完整语句，以分号结尾\n"
        instruction += "- 只输出 JSON，不要有其他文字\n"
        
        return instruction
    
    def get_time_range_description(
        self,
        start_date: str,
        end_date: str,
        date_info: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        生成时间范围的自然语言描述
        
        参数:
            start_date: 开始日期 'YYYY-MM-DD'
            end_date: 结束日期 'YYYY-MM-DD'
            date_info: 当前时间信息（用于相对描述），如果为 None 则自动获取
        
        返回:
            str: 时间范围描述
        
        示例:
            ('2025-01-01', '2025-12-31') -> "2025年全年"
            ('2025-01-01', '2025-03-31') -> "2025年第1季度"
            ('2025-01-01', '2025-01-31') -> "2025年1月"
        """
        if date_info is None:
            date_info = get_current_datetime()
        
        from datetime import datetime
        
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        # 检查是否是整年
        if start.month == 1 and start.day == 1 and end.month == 12 and end.day == 31:
            if start.year == end.year:
                current_year = date_info['year']
                if start.year == current_year:
                    return "今年"
                elif start.year == current_year - 1:
                    return "去年"
                elif start.year == current_year - 2:
                    return "前年"
                else:
                    return f"{start.year}年"
        
        # 检查是否是整月
        if start.day == 1:
            expected_end = get_month_start_end(start_date)[1]
            if end_date == expected_end:
                return f"{start.year}年{start.month}月"
        
        # 检查是否是季度
        quarter_starts = {1: (1, 1), 2: (4, 1), 3: (7, 1), 4: (10, 1)}
        quarter_ends = {1: (3, 31), 2: (6, 30), 3: (9, 30), 4: (12, 31)}
        for q, (sm, sd) in quarter_starts.items():
            em, ed = quarter_ends[q]
            if start.month == sm and start.day == sd and end.month == em and end.day == ed:
                return f"{start.year}年第{q}季度"
        
        # 默认返回日期范围
        return f"{start_date} 至 {end_date}"
    
    def suggest_time_expression_for_query(
        self,
        user_question: str,
        date_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        根据用户问题建议时间表达式的解析方案
        
        参数:
            user_question: 用户问题
            date_info: 当前时间信息，如果为 None 则自动获取
        
        返回:
            dict: 包含时间相关建议的字典
        
        示例:
            问题包含"去年" -> {
                'has_time': True,
                'keywords': ['去年'],
                'suggested_range': ('2025-01-01', '2025-12-31'),
                'description': '去年 (2025年)'
            }
        """
        if date_info is None:
            date_info = get_current_datetime()
        
        result = {
            'has_time': False,
            'keywords': [],
            'suggested_range': None,
            'description': ''
        }
        
        current_date = date_info['current_date']
        year = date_info['year']
        
        # 检测时间关键词
        time_keywords = {
            '今年': (get_date_range_for_period(year), f'今年 ({year}年)'),
            '去年': (get_date_range_for_period(year - 1), f'去年 ({year-1}年)'),
            '前年': (get_date_range_for_period(year - 2), f'前年 ({year-2}年)'),
            '本月': (get_month_start_end(current_date), f'本月 ({year}年{date_info["month"]}月)'),
            '上月': (get_month_start_end(calculate_date_offset(current_date, months=-1)), '上月'),
            '本季度': (get_quarter_start_end(current_date), '本季度'),
            '最近一年': ((calculate_date_offset(current_date, years=-1), current_date), '最近一年'),
            '最近半年': ((calculate_date_offset(current_date, months=-6), current_date), '最近半年'),
            '最近三个月': ((calculate_date_offset(current_date, months=-3), current_date), '最近三个月'),
        }
        
        for keyword, (date_range, desc) in time_keywords.items():
            if keyword in user_question:
                result['has_time'] = True
                result['keywords'].append(keyword)
                result['suggested_range'] = date_range
                result['description'] = desc
                break  # 只匹配第一个
        
        return result
    
    def get_all_examples(self) -> str:
        """
        获取所有 Few-shot 示例
        
        返回:
            str: 所有示例文本
        
        说明:
            为了保证 SQL 查询的成功率，始终返回所有示例。
            不进行示例选择，以确保模型能看到完整的推理模式。
        """
        return self.load_examples()
    
    def extract_placeholders(self, template: str) -> List[str]:
        """
        提取模板中的占位符
        
        参数:
            template: 模板文本
        
        返回:
            list: 占位符列表
        
        示例:
            "{current_date} 和 {current_year}" -> ['current_date', 'current_year']
        """
        pattern = r'\{([^}]+)\}'
        matches = re.findall(pattern, template)
        return matches
    
    def validate_template(self, template: str, required_fields: List[str]) -> bool:
        """
        验证模板是否包含所有必需的占位符
        
        参数:
            template: 模板文本
            required_fields: 必需的字段列表
        
        返回:
            bool: 是否包含所有必需字段
        """
        placeholders = self.extract_placeholders(template)
        return all(field in placeholders for field in required_fields)


def create_user_message(user_question: str) -> Dict[str, str]:
    """
    创建用户消息对象
    
    参数:
        user_question: 用户问题
    
    返回:
        dict: 消息对象，包含 role 和 content
    """
    return {
        "role": "user",
        "content": user_question
    }


def create_system_message(content: str) -> Dict[str, str]:
    """
    创建系统消息对象
    
    参数:
        content: 系统消息内容
    
    返回:
        dict: 消息对象，包含 role 和 content
    """
    return {
        "role": "system",
        "content": content
    }


def create_messages_for_api(
    system_prompt: str,
    user_question: str,
    history: Optional[List[Dict[str, str]]] = None
) -> List[Dict[str, str]]:
    """
    创建 API 调用所需的消息列表
    
    参数:
        system_prompt: 系统 Prompt
        user_question: 用户问题
        history: 历史对话记录
    
    返回:
        list: 消息列表
    """
    messages = [create_system_message(system_prompt)]
    
    # 添加历史记录
    if history:
        messages.extend(history)
    
    # 添加当前用户问题
    messages.append(create_user_message(user_question))
    
    return messages


if __name__ == '__main__':
    # 测试代码
    print("=" * 60)
    print("测试 PromptBuilder - 泛化时间工具集成版本")
    print("=" * 60)
    
    try:
        # 初始化构建器
        builder = PromptBuilder()
        print("\n✓ PromptBuilder 初始化成功")
        
        # 测试加载 Schema
        print("\n" + "=" * 60)
        print("测试 1: 加载数据库 Schema")
        print("=" * 60)
        schema = builder.load_schema()
        print(f"✓ Schema 加载成功")
        print(f"  - 长度: {len(schema)} 字符")
        print(f"  - 前100字符: {schema[:100]}...")
        
        # 测试加载示例
        print("\n" + "=" * 60)
        print("测试 2: 加载 Few-shot 示例")
        print("=" * 60)
        examples = builder.load_examples()
        print(f"✓ Examples 加载成功")
        print(f"  - 长度: {len(examples)} 字符")
        print(f"  - 前100字符: {examples[:100]}...")
        
        # 测试加载系统 Prompt
        print("\n" + "=" * 60)
        print("测试 3: 加载系统 Prompt 模板")
        print("=" * 60)
        system_prompt = builder.load_system_prompt_template()
        print(f"✓ System Prompt 模板加载成功")
        print(f"  - 长度: {len(system_prompt)} 字符")
        print(f"  - 前100字符: {system_prompt[:100]}...")
        
        # 测试占位符提取
        print("\n" + "=" * 60)
        print("测试 4: 提取模板占位符")
        print("=" * 60)
        placeholders = builder.extract_placeholders(system_prompt)
        print(f"✓ 找到 {len(placeholders)} 个占位符:")
        print(f"  {', '.join(placeholders)}")
        
        # 测试时间占位符计算
        print("\n" + "=" * 60)
        print("测试 5: 按需计算时间占位符")
        print("=" * 60)
        date_info = get_current_datetime()
        print(f"✓ 获取当前时间: {date_info['current_date']}")
        # 测试按需计算（只计算部分占位符）
        required = ['year_minus_1', 'month_padded', 'three_months_ago']
        time_placeholders = builder._calculate_time_placeholders(date_info, required)
        print(f"✓ 按需计算了 {len(time_placeholders)} 个时间占位符:")
        for key, value in time_placeholders.items():
            print(f"  - {key}: {value}")
        
        # 测试时间上下文格式化
        print("\n" + "=" * 60)
        print("测试 6: 格式化时间上下文")
        print("=" * 60)
        time_context = builder.format_date_context(date_info)
        print(time_context)
        
        # 测试自动获取时间（不提供 date_info）
        print("\n" + "=" * 60)
        print("测试 7: 自动获取时间信息")
        print("=" * 60)
        time_context_auto = builder.format_date_context()
        print("✓ 成功自动获取并格式化时间上下文")
        
        # 测试构建完整 Prompt（不带历史）
        print("\n" + "=" * 60)
        print("测试 8: 构建完整 Prompt (无历史)")
        print("=" * 60)
        full_prompt = builder.build_sql_generation_prompt(
            user_question="公司有多少在职员工?",
            date_info=date_info
        )
        print(f"✓ Prompt 构建成功")
        print(f"  - 总长度: {len(full_prompt)} 字符")
        print(f"\n--- Prompt 预览 (前800字符) ---")
        print(full_prompt[:800])
        print("...")
        
        # 测试构建 Prompt（带历史上下文）
        print("\n" + "=" * 60)
        print("测试 9: 构建 Prompt (带历史上下文)")
        print("=" * 60)
        context = [
            {
                'thought': '这是一个简单的统计查询',
                'sql': 'SELECT COUNT(*) FROM employees WHERE leave_date IS NULL;',
                'result': {
                    'success': True,
                    'row_count': 1,
                    'data': [{'count': 88}]
                }
            }
        ]
        full_prompt_with_context = builder.build_sql_generation_prompt(
            user_question="各部门分别有多少人?",
            date_info=date_info,
            context=context
        )
        print(f"✓ 带历史的 Prompt 构建成功")
        print(f"  - 总长度: {len(full_prompt_with_context)} 字符")
        print(f"  - 包含 {len(context)} 轮历史")
        
        # 测试构建 Prompt（带错误反馈）
        print("\n" + "=" * 60)
        print("测试 10: 构建 Prompt (带错误反馈)")
        print("=" * 60)
        error_msg = "syntax error at or near 'FORM'"
        full_prompt_with_error = builder.build_sql_generation_prompt(
            user_question="公司有多少在职员工?",
            date_info=date_info,
            error_feedback=error_msg
        )
        print(f"✓ 带错误反馈的 Prompt 构建成功")
        print(f"  - 包含错误信息: {error_msg}")
        
        # 测试答案生成 Prompt
        print("\n" + "=" * 60)
        print("测试 11: 构建答案生成 Prompt")
        print("=" * 60)
        sql_history = [
            {
                'sql': 'SELECT COUNT(*) FROM employees WHERE leave_date IS NULL;',
                'result': {'success': True, 'data': [{'count': 88}]}
            }
        ]
        answer_prompt = builder.build_answer_generation_prompt(
            user_question="公司有多少在职员工?",
            sql_history=sql_history
        )
        print(f"✓ 答案生成 Prompt 构建成功")
        print(f"  - 长度: {len(answer_prompt)} 字符")
        
        # 测试消息创建函数
        print("\n" + "=" * 60)
        print("测试 12: 创建 API 消息")
        print("=" * 60)
        messages = create_messages_for_api(
            system_prompt=full_prompt,
            user_question="公司有多少在职员工?"
        )
        print(f"✓ API 消息创建成功")
        print(f"  - 消息数量: {len(messages)}")
        print(f"  - 消息角色: {[msg['role'] for msg in messages]}")
        
        print("\n" + "=" * 60)
        print("✓✓✓ 所有测试通过! ✓✓✓")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("✗✗✗ 测试失败 ✗✗✗")
        print("=" * 60)
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()
