#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SQL 生成模块

负责调用 Kimi API，将自然语言问题转换为 SQL 查询。
支持 ReAct 范式的流式输出和多轮迭代。
"""

import json
import time
import requests
from typing import Dict, List, Any, Optional, Generator

from erp_agent.config.llm import LLMConfig
from erp_agent.utils.prompt_builder import PromptBuilder
from erp_agent.utils.date_utils import get_current_datetime
from erp_agent.utils.logger import get_logger, log_api_call


class SQLGenerator:
    """
    SQL 生成器
    
    功能:
        1. 调用 Kimi API 生成 SQL 查询
        2. 支持 ReAct 范式的多轮迭代
        3. 支持流式输出（SSE）
        4. 解析 JSON 格式的响应
        5. 错误处理和重试
    
    属性:
        llm_config (LLMConfig): LLM 配置
        prompt_builder (PromptBuilder): Prompt 构建器
        
    使用示例:
        >>> generator = SQLGenerator(llm_config)
        >>> result = generator.generate("有多少在职员工？")
        >>> print(result['action'])
        'execute_sql'
        >>> print(result['sql'])
        'SELECT COUNT(*) FROM employees WHERE leave_date IS NULL;'
    """
    
    def __init__(
        self, 
        llm_config: LLMConfig,
        prompt_builder: Optional[PromptBuilder] = None
    ):
        """
        初始化 SQL 生成器
        
        参数:
            llm_config: LLM 配置对象
            prompt_builder: Prompt 构建器（可选，默认创建新实例）
        """
        self.llm_config = llm_config
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.logger = get_logger(__name__)
    
    def generate(
        self,
        user_question: str,
        context: Optional[List[Dict[str, Any]]] = None,
        date_info: Optional[Dict[str, Any]] = None,
        error_feedback: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        生成 SQL 查询（或最终答案）
        
        参数:
            user_question: 用户的自然语言问题
            context: 历史上下文（之前的查询和结果）
            date_info: 时间信息（如果为 None 则自动获取）
            error_feedback: 错误反馈信息（用于重试）
            stream: 是否使用流式输出
            
        返回:
            Dict: 包含生成结果的字典
                {
                    'thought': str,              # 思考过程
                    'action': str,               # 'execute_sql' 或 'answer'
                    'sql': Optional[str],        # SQL 语句（如果 action='execute_sql'）
                    'answer': Optional[str],     # 最终答案（如果 action='answer'）
                    'is_final': bool,            # 是否是最终结果
                    'raw_response': str,         # 原始响应
                    'api_time': float            # API 调用时间
                }
        """
        start_time = time.time()
        
        try:
            # 获取时间信息
            if date_info is None:
                date_info = get_current_datetime()
            
            # 构建 Prompt
            system_prompt = self.prompt_builder.build_sql_generation_prompt(
                user_question=user_question,
                date_info=date_info,
                context=context,
                error_feedback=error_feedback
            )
            
            # 调用 API
            if stream:
                # 流式调用（生成器）
                return self._call_api_stream(system_prompt, user_question, start_time)
            else:
                # 非流式调用
                response = self._call_api(system_prompt, user_question)
                api_time = time.time() - start_time
                
                # 解析响应
                result = self._parse_response(response, api_time)
                
                return result
                
        except Exception as e:
            self.logger.error(f"生成 SQL 失败: {e}")
            api_time = time.time() - start_time
            
            return {
                'thought': f"生成失败: {str(e)}",
                'action': 'error',
                'sql': None,
                'answer': None,
                'is_final': False,
                'raw_response': '',
                'api_time': api_time,
                'error': str(e)
            }
    
    def generate_answer(
        self,
        user_question: str,
        sql_history: List[Dict[str, Any]]
    ) -> str:
        """
        基于查询历史生成最终答案
        
        参数:
            user_question: 用户的原始问题
            sql_history: SQL 执行历史
            
        返回:
            str: 自然语言答案
        """
        start_time = time.time()
        
        try:
            # 构建答案生成 Prompt
            prompt = self.prompt_builder.build_answer_generation_prompt(
                user_question=user_question,
                sql_history=sql_history
            )
            
            # 调用 API
            messages = [
                {'role': 'system', 'content': prompt},
                {'role': 'user', 'content': '请基于以上信息回答用户的问题。'}
            ]
            
            response = self._call_api_raw(messages, use_answer_params=True)
            api_time = time.time() - start_time
            
            # 提取答案
            if response and 'choices' in response and len(response['choices']) > 0:
                answer = response['choices'][0]['message']['content'].strip()
                
                log_api_call(
                    api_name=self.llm_config.model,
                    success=True,
                    response_time=api_time
                )
                
                return answer
            else:
                self.logger.error("API 响应格式错误")
                return "抱歉，无法生成答案。"
                
        except Exception as e:
            self.logger.error(f"生成答案失败: {e}")
            return f"抱歉，生成答案时出错: {str(e)}"
    
    def _call_api(
        self,
        system_prompt: str,
        user_question: str
    ) -> str:
        """
        调用 Kimi API（非流式）
        
        参数:
            system_prompt: 系统 Prompt
            user_question: 用户问题
            
        返回:
            str: API 响应内容
        """
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_question}
        ]
        
        response = self._call_api_raw(messages, use_answer_params=False)
        
        if response and 'choices' in response and len(response['choices']) > 0:
            return response['choices'][0]['message']['content']
        else:
            raise ValueError("API 响应格式错误")
    
    def _call_api_stream(
        self,
        system_prompt: str,
        user_question: str,
        start_time: float
    ) -> Generator[Dict[str, Any], None, None]:
        """
        调用 Kimi API（流式）
        
        参数:
            system_prompt: 系统 Prompt
            user_question: 用户问题
            start_time: 开始时间
            
        返回:
            Generator: 生成器，逐步返回部分结果
        """
        messages = [
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': user_question}
        ]
        
        url = self.llm_config.get_chat_completion_url()
        headers = self.llm_config.get_api_headers()
        params = self.llm_config.get_sql_generation_params()
        
        data = {
            **params,
            'messages': messages,
            'stream': True
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=self.llm_config.timeout,
                stream=True
            )
            
            response.raise_for_status()
            
            accumulated_content = ""
            
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8')
                    
                    # 跳过注释和空行
                    if line_str.startswith(':') or not line_str.strip():
                        continue
                    
                    # 解析 SSE 格式
                    if line_str.startswith('data: '):
                        data_str = line_str[6:]  # 移除 "data: " 前缀
                        
                        # 检查是否是结束标记
                        if data_str.strip() == '[DONE]':
                            break
                        
                        try:
                            chunk = json.loads(data_str)
                            
                            if 'choices' in chunk and len(chunk['choices']) > 0:
                                delta = chunk['choices'][0].get('delta', {})
                                content = delta.get('content', '')
                                
                                if content:
                                    accumulated_content += content
                                    
                                    # 返回部分结果
                                    yield {
                                        'type': 'chunk',
                                        'content': content,
                                        'accumulated': accumulated_content
                                    }
                        except json.JSONDecodeError:
                            continue
            
            # 流式完成后，解析最终结果
            api_time = time.time() - start_time
            result = self._parse_response(accumulated_content, api_time)
            result['type'] = 'final'
            
            yield result
            
            log_api_call(
                api_name=self.llm_config.model,
                success=True,
                response_time=api_time
            )
            
        except Exception as e:
            self.logger.error(f"流式 API 调用失败: {e}")
            api_time = time.time() - start_time
            
            yield {
                'type': 'error',
                'error': str(e),
                'api_time': api_time
            }
            
            log_api_call(
                api_name=self.llm_config.model,
                success=False,
                response_time=api_time,
                error=str(e)
            )
    
    def _call_api_raw(
        self,
        messages: List[Dict[str, str]],
        use_answer_params: bool = False
    ) -> Dict[str, Any]:
        """
        调用 Kimi API（底层方法）
        
        参数:
            messages: 消息列表
            use_answer_params: 是否使用答案生成参数（而非 SQL 生成参数）
            
        返回:
            Dict: API 响应 JSON
        """
        url = self.llm_config.get_chat_completion_url()
        headers = self.llm_config.get_api_headers()
        
        if use_answer_params:
            params = self.llm_config.get_answer_generation_params()
        else:
            params = self.llm_config.get_sql_generation_params()
        
        data = {
            **params,
            'messages': messages
        }
        
        # 重试逻辑
        for attempt in range(self.llm_config.max_retries):
            try:
                response = requests.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=self.llm_config.timeout
                )
                
                response.raise_for_status()
                
                return response.json()
                
            except requests.exceptions.RequestException as e:
                self.logger.warning(
                    f"API 调用失败 (尝试 {attempt + 1}/{self.llm_config.max_retries}): {e}"
                )
                
                if attempt < self.llm_config.max_retries - 1:
                    time.sleep(self.llm_config.retry_delay)
                else:
                    raise
    
    def _parse_response(
        self,
        response_text: str,
        api_time: float
    ) -> Dict[str, Any]:
        """
        解析 API 响应，提取 JSON 格式的结果
        
        参数:
            response_text: API 响应文本
            api_time: API 调用时间
            
        返回:
            Dict: 解析后的结果
        """
        try:
            # 尝试从响应中提取 JSON
            json_content = self._extract_json(response_text)
            
            if json_content:
                # 验证必需字段
                result = {
                    'thought': json_content.get('thought', ''),
                    'action': json_content.get('action', 'unknown'),
                    'sql': json_content.get('sql'),
                    'answer': json_content.get('answer'),
                    'is_final': json_content.get('is_final', False),
                    'raw_response': response_text,
                    'api_time': api_time
                }
                
                # 如果 action 是 execute_sql 但没有 sql，标记为错误
                if result['action'] == 'execute_sql' and not result['sql']:
                    result['action'] = 'error'
                    result['error'] = 'action 是 execute_sql 但缺少 sql 字段'
                
                # 如果 action 是 answer 但没有 answer，标记为错误
                if result['action'] == 'answer' and not result['answer']:
                    result['action'] = 'error'
                    result['error'] = 'action 是 answer 但缺少 answer 字段'
                
                return result
            else:
                # 无法提取 JSON，返回错误
                self.logger.error(f"无法从响应中提取 JSON: {response_text[:200]}")
                
                return {
                    'thought': '响应格式错误',
                    'action': 'error',
                    'sql': None,
                    'answer': None,
                    'is_final': False,
                    'raw_response': response_text,
                    'api_time': api_time,
                    'error': '无法解析响应为 JSON 格式'
                }
                
        except Exception as e:
            self.logger.error(f"解析响应失败: {e}")
            
            return {
                'thought': f'解析失败: {str(e)}',
                'action': 'error',
                'sql': None,
                'answer': None,
                'is_final': False,
                'raw_response': response_text,
                'api_time': api_time,
                'error': str(e)
            }
    
    def _extract_json(self, text: str) -> Optional[Dict[str, Any]]:
        """
        从文本中提取 JSON 内容
        
        支持的格式:
            1. 纯 JSON: {"thought": "...", "action": "..."}
            2. Markdown 代码块: ```json\n{...}\n```
            3. 带前后文本的 JSON
        
        参数:
            text: 包含 JSON 的文本
            
        返回:
            Optional[Dict]: 提取的 JSON 对象，如果失败返回 None
        """
        # 移除可能的前后空白
        text = text.strip()
        
        # 方法 1: 尝试直接解析
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass
        
        # 方法 2: 提取 Markdown 代码块中的 JSON
        if '```json' in text:
            start = text.find('```json') + 7
            end = text.find('```', start)
            if end > start:
                json_text = text[start:end].strip()
                try:
                    return json.loads(json_text)
                except json.JSONDecodeError:
                    pass
        
        # 方法 3: 查找第一个 { 到最后一个 }
        first_brace = text.find('{')
        last_brace = text.rfind('}')
        
        if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
            json_text = text[first_brace:last_brace + 1]
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                pass
        
        # 方法 4: 尝试修复常见的 JSON 格式问题
        # 例如：多余的逗号、单引号等
        if first_brace != -1 and last_brace != -1:
            json_text = text[first_brace:last_brace + 1]
            # 替换单引号为双引号（简单处理）
            json_text = json_text.replace("'", '"')
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                pass
        
        return None


# 导出的公共接口
__all__ = ['SQLGenerator']


if __name__ == '__main__':
    # 测试代码
    print("=== 测试 SQLGenerator ===\n")
    
    try:
        from erp_agent.config import get_llm_config
        
        # 加载配置
        llm_config = get_llm_config()
        print(f"LLM 配置: {llm_config}\n")
        
        # 创建生成器
        generator = SQLGenerator(llm_config)
        
        # 测试 1: 简单问题
        print("测试 1: 生成 SQL（简单问题）")
        question = "公司有多少在职员工？"
        print(f"问题: {question}")
        
        result = generator.generate(question)
        
        print(f"思考: {result['thought']}")
        print(f"动作: {result['action']}")
        if result['action'] == 'execute_sql':
            print(f"SQL: {result['sql']}")
        elif result['action'] == 'answer':
            print(f"答案: {result['answer']}")
        print(f"API 时间: {result['api_time']:.2f}秒")
        print(f"是否最终: {result['is_final']}\n")
        
        # 测试 2: 带错误反馈的重试
        print("测试 2: 带错误反馈的重试")
        context = [
            {
                'sql': 'SELECT COUNT(*) FROM employee;',  # 故意错误的表名
                'result': {
                    'success': False,
                    'error': 'relation "employee" does not exist'
                }
            }
        ]
        
        result = generator.generate(
            user_question=question,
            context=context,
            error_feedback='上次查询失败，表名应该是 employees 而不是 employee'
        )
        
        print(f"思考: {result['thought']}")
        print(f"动作: {result['action']}")
        if result['action'] == 'execute_sql':
            print(f"修正后的 SQL: {result['sql']}")
        print()
        
        # 测试 3: 生成答案
        print("测试 3: 生成最终答案")
        sql_history = [
            {
                'sql': 'SELECT COUNT(*) FROM employees WHERE leave_date IS NULL;',
                'result': {
                    'success': True,
                    'data': [{'count': 88}]
                }
            }
        ]
        
        answer = generator.generate_answer(question, sql_history)
        print(f"问题: {question}")
        print(f"答案: {answer}\n")
        
        print("=" * 60)
        print("测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
