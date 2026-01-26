#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
结果分析模块（LLM驱动版本）

使用 LLM 智能分析 SQL 查询结果，判断是否需要继续查询，生成自然语言答案。
相比规则驱动的方式，LLM 能够更好地理解语义和上下文。
"""

import json
import time
import requests
from decimal import Decimal
from datetime import datetime, date
from typing import Dict, List, Any, Optional, Tuple
from erp_agent.utils.logger import get_logger, log_api_call
from erp_agent.config.llm import LLMConfig


class ResultAnalyzer:
    """
    LLM驱动的结果分析器
    
    功能:
        1. 使用 LLM 智能分析查询结果的完整性和有效性
        2. 基于语义理解判断是否需要进一步查询
        3. 生成自然且有洞察力的答案
        4. 智能提取关键信息和异常
    
    使用示例:
        >>> llm_config = LLMConfig.from_env()
        >>> analyzer = ResultAnalyzer(llm_config)
        >>> analysis = analyzer.analyze_result(sql_result, user_question)
        >>> if analysis['is_sufficient']:
        ...     answer = analyzer.generate_answer_suggestion(sql_result, user_question)
    """
    
    def __init__(self, llm_config: Optional[LLMConfig] = None):
        """
        初始化结果分析器
        
        参数:
            llm_config: LLM 配置对象（可选，如果不提供则从环境变量加载）
        """
        self.logger = get_logger(__name__)
        
        # LLM 配置
        if llm_config is None:
            try:
                self.llm_config = LLMConfig.from_env()
            except Exception as e:
                self.logger.warning(f"无法加载 LLM 配置，将使用降级模式: {e}")
                self.llm_config = None
        else:
            self.llm_config = llm_config
        
        # 分析专用配置
        self.analysis_temperature = 0.3  # 分析时使用较低温度，保持客观
        self.analysis_max_tokens = 1024
        self.max_retries = 2  # 最大重试次数
    
    @staticmethod
    def _serialize_data(data: Any) -> Any:
        """
        将数据转换为 JSON 可序列化的格式
        
        处理 Decimal, datetime, date 等特殊类型
        
        参数:
            data: 任意数据
            
        返回:
            JSON 可序列化的数据
        """
        if isinstance(data, Decimal):
            # Decimal 转为 float
            return float(data)
        elif isinstance(data, (datetime, date)):
            # datetime/date 转为字符串
            return data.isoformat()
        elif isinstance(data, dict):
            # 递归处理字典
            return {k: ResultAnalyzer._serialize_data(v) for k, v in data.items()}
        elif isinstance(data, list):
            # 递归处理列表
            return [ResultAnalyzer._serialize_data(item) for item in data]
        else:
            return data
    
    def analyze_result(
        self,
        sql_result: Dict[str, Any],
        user_question: str,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        使用 LLM 智能分析查询结果
        
        参数:
            sql_result: SQL 执行结果
            user_question: 用户的原始问题
            context: 历史查询上下文
            
        返回:
            Dict: 分析结果
                {
                    'is_sufficient': bool,        # 结果是否足够回答问题
                    'completeness': float,        # 完整性评分 0-1
                    'suggestion': str,            # 建议（继续查询/生成答案）
                    'key_findings': List[str],    # 关键发现
                    'anomalies': List[str],       # 异常情况
                    'next_action': str           # 下一步建议动作
                }
        """
        analysis = {
            'is_sufficient': False,
            'completeness': 0.0,
            'suggestion': '',
            'key_findings': [],
            'anomalies': [],
            'next_action': 'continue_query'
        }
        
        try:
            # 1. 快速检查：SQL是否成功执行
            if not sql_result.get('success', False):
                analysis['suggestion'] = f"查询失败，需要修正SQL: {sql_result.get('error', '')}"
                analysis['next_action'] = 'retry_query'
                return analysis
            
            # 2. 使用 LLM 进行深度分析
            if self.llm_config:
                return self._llm_analyze_result(sql_result, user_question, context)
            else:
                # 降级到简单规则分析
                self.logger.warning("LLM 配置不可用，使用简单规则分析")
                return self._fallback_analyze(sql_result, user_question)
            
        except Exception as e:
            self.logger.error(f"结果分析失败: {e}")
            analysis['suggestion'] = f"分析过程出错: {str(e)}"
            return analysis
    
    def _llm_analyze_result(
        self,
        sql_result: Dict[str, Any],
        user_question: str,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """
        使用 LLM 深度分析查询结果（带完整的错误处理）
        
        参数:
            sql_result: SQL 执行结果
            user_question: 用户问题
            context: 历史上下文
            
        返回:
            Dict: 分析结果
        """
        try:
            # 构建分析 prompt
            prompt = self._build_analysis_prompt(sql_result, user_question, context)
            
            # 调用 LLM
            response = self._call_llm(prompt)
            
            # 解析 LLM 响应
            analysis = self._parse_analysis_response(response)
            
            self.logger.debug(f"LLM 分析成功: 完整性={analysis['completeness']:.2f}, 充分={analysis['is_sufficient']}")
            
            return analysis
            
        except requests.exceptions.Timeout:
            self.logger.error("LLM 分析超时，使用降级分析")
            return self._fallback_analyze(sql_result, user_question)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"LLM API 请求失败: {e}，使用降级分析")
            return self._fallback_analyze(sql_result, user_question)
            
        except Exception as e:
            self.logger.error(f"LLM 分析失败: {e}，使用降级分析")
            import traceback
            self.logger.debug(f"异常详情: {traceback.format_exc()}")
            # 降级到简单规则分析
            return self._fallback_analyze(sql_result, user_question)
    
    def _build_analysis_prompt(
        self,
        sql_result: Dict[str, Any],
        user_question: str,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        构建结果分析的 prompt
        
        参数:
            sql_result: SQL 执行结果
            user_question: 用户问题
            context: 历史上下文
            
        返回:
            str: 完整的 prompt 文本
        """
        data = sql_result.get('data', [])
        row_count = sql_result.get('row_count', 0)
        
        # 限制数据量，避免 prompt 过长
        sample_data = data[:10] if len(data) > 10 else data
        
        # 转换为 JSON 可序列化格式
        sample_data = self._serialize_data(sample_data)
        
        # 构建上下文信息
        context_str = ""
        if context and len(context) > 0:
            context_str = "\n\n## 历史查询上下文\n"
            for i, ctx in enumerate(context[-3:], 1):  # 只取最近3次
                context_str += f"\n### 查询 {i}\n"
                if 'sql' in ctx:
                    context_str += f"SQL: {ctx['sql']}\n"
                if 'result' in ctx:
                    ctx_data = ctx['result'].get('data', [])
                    context_str += f"结果行数: {ctx['result'].get('row_count', 0)}\n"
        
        # 构建完整 prompt
        prompt = f"""你是一个数据分析专家，请分析以下 SQL 查询结果是否充分回答了用户的问题。

## 用户问题
{user_question}

## 查询结果
- 返回行数: {row_count} 行
- 数据样本（最多显示10行）:
```json
{json.dumps(sample_data, ensure_ascii=False, indent=2)}
```

{context_str}

## 分析任务
请从以下几个维度分析这个查询结果：

1. **完整性评分** (0-1分)：这个结果在多大程度上回答了用户的问题？
   - 1.0 表示完全回答了问题
   - 0.5 表示部分回答，还需要更多信息
   - 0.0 表示完全没有回答问题

2. **是否充分** (true/false)：这个结果是否足够生成最终答案？
   - true: 可以基于这个结果生成完整的自然语言答案
   - false: 需要继续查询或补充信息

3. **关键发现** (列表)：从结果中提取3-5个关键发现或洞察
   - 例如：数据规模、数值范围、趋势、异常等

4. **异常情况** (列表)：识别数据中的异常或需要注意的情况
   - 例如：大量NULL值、异常数值、数据缺失等
   - 如果没有异常，返回空列表

5. **建议** (文本)：给出下一步建议
   - 如果结果充分，建议如何生成答案
   - 如果不充分，建议需要什么额外信息

6. **下一步动作** (枚举)：
   - "generate_answer": 可以生成最终答案
   - "continue_query": 需要继续查询
   - "retry_query": 需要修正当前查询

## 输出格式
请严格按照以下 JSON 格式输出（不要包含任何其他文本）：

```json
{{
  "completeness": 0.85,
  "is_sufficient": true,
  "key_findings": [
    "发现1",
    "发现2",
    "发现3"
  ],
  "anomalies": [
    "异常1（如有）"
  ],
  "suggestion": "建议文本",
  "next_action": "generate_answer"
}}
```

请开始分析："""
        
        return prompt
    
    def _call_llm(self, prompt: str, retry_count: int = 0) -> str:
        """
        调用 LLM API（带重试机制）
        
        参数:
            prompt: 提示文本
            retry_count: 当前重试次数
            
        返回:
            str: LLM 响应文本
        """
        start_time = time.time()
        
        url = self.llm_config.get_chat_completion_url()
        headers = self.llm_config.get_api_headers()
        
        data = {
            'model': self.llm_config.model,
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一个专业的数据分析助手，擅长分析SQL查询结果并提供洞察。请始终按照要求的 JSON 格式返回结果。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': self.analysis_temperature,
            'max_tokens': self.analysis_max_tokens
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=self.llm_config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content']
            
            api_time = time.time() - start_time
            
            # 记录 API 调用 - 使用正确的参数
            log_api_call(
                api_name=f"{self.llm_config.model}_result_analysis",
                success=True,
                response_time=api_time,
                request_data={'prompt_length': len(prompt)},
                response_data={'response_length': len(content)}
            )
            
            return content
            
        except requests.exceptions.Timeout as e:
            api_time = time.time() - start_time
            self.logger.error(f"LLM API 调用超时: {e}")
            
            # 超时重试
            if retry_count < self.max_retries:
                self.logger.info(f"重试 LLM 调用 ({retry_count + 1}/{self.max_retries})")
                time.sleep(1)  # 等待1秒后重试
                return self._call_llm(prompt, retry_count + 1)
            else:
                log_api_call(
                    api_name=f"{self.llm_config.model}_result_analysis",
                    success=False,
                    response_time=api_time,
                    error=str(e)
                )
                raise
                
        except requests.exceptions.RequestException as e:
            api_time = time.time() - start_time
            self.logger.error(f"LLM API 调用失败: {e}")
            
            log_api_call(
                api_name=f"{self.llm_config.model}_result_analysis",
                success=False,
                response_time=api_time,
                error=str(e)
            )
            raise
            
        except (KeyError, IndexError) as e:
            api_time = time.time() - start_time
            self.logger.error(f"解析 LLM 响应失败: {e}")
            self.logger.debug(f"响应内容: {result if 'result' in locals() else 'N/A'}")
            
            log_api_call(
                api_name=f"{self.llm_config.model}_result_analysis",
                success=False,
                response_time=api_time,
                error=f"解析失败: {str(e)}"
            )
            raise
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """
        解析 LLM 的分析响应（增强容错性）
        
        参数:
            response: LLM 响应文本
            
        返回:
            Dict: 解析后的分析结果
        """
        try:
            # 方法1: 尝试提取 markdown 代码块中的 JSON
            if '```json' in response:
                json_start = response.find('```json') + 7
                json_end = response.find('```', json_start)
                if json_end > json_start:
                    json_str = response[json_start:json_end].strip()
                    analysis = json.loads(json_str)
                    return self._validate_and_fix_analysis(analysis)
            
            # 方法2: 提取第一个完整的 JSON 对象
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start >= 0 and json_end > json_start:
                json_str = response[json_start:json_end]
                try:
                    analysis = json.loads(json_str)
                    return self._validate_and_fix_analysis(analysis)
                except json.JSONDecodeError:
                    # 方法3: 尝试清理常见的 JSON 格式问题
                    json_str = json_str.replace('\n', ' ').replace('\r', '')
                    # 去除多余的逗号
                    json_str = json_str.replace(',}', '}').replace(',]', ']')
                    analysis = json.loads(json_str)
                    return self._validate_and_fix_analysis(analysis)
            
            raise ValueError("响应中没有找到有效的 JSON 格式")
                
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.error(f"解析 LLM 响应失败: {e}")
            self.logger.debug(f"原始响应前500字符: {response[:500]}")
            
            # 尝试基于关键词进行简单分析
            return self._fallback_parse_response(response)
    
    def _validate_and_fix_analysis(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """
        验证并修复分析结果的格式
        
        参数:
            analysis: 原始分析结果
            
        返回:
            Dict: 修复后的分析结果
        """
        # 设置默认值
        result = {
            'is_sufficient': analysis.get('is_sufficient', False),
            'completeness': analysis.get('completeness', 0.5),
            'suggestion': analysis.get('suggestion', ''),
            'key_findings': analysis.get('key_findings', []),
            'anomalies': analysis.get('anomalies', []),
            'next_action': analysis.get('next_action', 'continue_query')
        }
        
        # 类型转换和验证
        try:
            result['completeness'] = float(result['completeness'])
            # 限制在 0-1 范围内
            result['completeness'] = max(0.0, min(1.0, result['completeness']))
        except (ValueError, TypeError):
            result['completeness'] = 0.5
        
        # 布尔值转换
        if isinstance(result['is_sufficient'], str):
            result['is_sufficient'] = result['is_sufficient'].lower() in ('true', 'yes', '1')
        else:
            result['is_sufficient'] = bool(result['is_sufficient'])
        
        # 确保列表类型
        if not isinstance(result['key_findings'], list):
            result['key_findings'] = []
        if not isinstance(result['anomalies'], list):
            result['anomalies'] = []
        
        # 验证 next_action
        valid_actions = ['generate_answer', 'continue_query', 'retry_query']
        if result['next_action'] not in valid_actions:
            # 根据 is_sufficient 推断
            result['next_action'] = 'generate_answer' if result['is_sufficient'] else 'continue_query'
        
        return result
    
    def _fallback_parse_response(self, response: str) -> Dict[str, Any]:
        """
        当 JSON 解析失败时，基于关键词进行简单分析
        
        参数:
            response: LLM 响应文本
            
        返回:
            Dict: 基本的分析结果
        """
        response_lower = response.lower()
        
        # 尝试检测是否认为结果充分
        is_sufficient = any(keyword in response_lower for keyword in [
            '充分', '足够', '完整', 'sufficient', 'enough', 'complete'
        ])
        
        # 尝试检测是否需要继续查询
        need_continue = any(keyword in response_lower for keyword in [
            '不足', '缺少', '需要更多', '继续', 'insufficient', 'need more', 'continue'
        ])
        
        if need_continue:
            is_sufficient = False
        
        return {
            'is_sufficient': is_sufficient,
            'completeness': 0.7 if is_sufficient else 0.4,
            'suggestion': '基于响应内容推断的建议',
            'key_findings': [],
            'anomalies': ['LLM响应格式不标准，使用降级解析'],
            'next_action': 'generate_answer' if is_sufficient else 'continue_query'
        }
    
    def _fallback_analyze(
        self,
        sql_result: Dict[str, Any],
        user_question: str
    ) -> Dict[str, Any]:
        """
        降级的简单规则分析（当 LLM 不可用时使用）
        
        参数:
            sql_result: SQL 执行结果
            user_question: 用户问题
            
        返回:
            Dict: 分析结果
        """
        data = sql_result.get('data', [])
        row_count = sql_result.get('row_count', 0)
        
        analysis = {
            'is_sufficient': False,
            'completeness': 0.0,
            'suggestion': '',
            'key_findings': [],
            'anomalies': [],
            'next_action': 'continue_query'
        }
        
        # 空结果
        if row_count == 0:
            analysis['suggestion'] = "查询返回空结果"
            analysis['completeness'] = 0.3
            analysis['next_action'] = 'continue_query'
            return analysis
        
        # 有数据，简单认为足够
        analysis['is_sufficient'] = True
        analysis['completeness'] = 0.8
        analysis['next_action'] = 'generate_answer'
        analysis['suggestion'] = f"查询返回 {row_count} 行数据，可以生成答案"
        analysis['key_findings'] = [f"返回了 {row_count} 行数据"]
        
        return analysis
    
    # 注意：以下方法已由 _llm_analyze_result 统一处理，保留仅用于降级场景
    
    def generate_answer_suggestion(
        self,
        sql_result: Dict[str, Any],
        user_question: str,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        使用 LLM 生成自然语言答案（带完整错误处理）
        
        参数:
            sql_result: SQL 执行结果
            user_question: 用户问题
            context: 历史上下文
            
        返回:
            str: 自然语言答案
        """
        if not self.llm_config:
            # 降级到简单格式化
            self.logger.warning("LLM 配置不可用，使用降级答案生成")
            return self._fallback_generate_answer(sql_result, user_question)
        
        try:
            # 构建答案生成 prompt
            prompt = self._build_answer_generation_prompt(
                sql_result, user_question, context
            )
            
            # 调用 LLM
            answer = self._call_llm_for_answer(prompt)
            
            self.logger.debug(f"LLM 答案生成成功，长度: {len(answer)}")
            
            return answer
            
        except requests.exceptions.Timeout:
            self.logger.error("LLM 答案生成超时，使用降级方法")
            return self._fallback_generate_answer(sql_result, user_question)
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"LLM API 请求失败: {e}，使用降级方法")
            return self._fallback_generate_answer(sql_result, user_question)
            
        except Exception as e:
            self.logger.error(f"LLM 答案生成失败: {e}，使用降级方法")
            import traceback
            self.logger.debug(f"异常详情: {traceback.format_exc()}")
            # 降级到简单格式化
            return self._fallback_generate_answer(sql_result, user_question)
    
    def _build_answer_generation_prompt(
        self,
        sql_result: Dict[str, Any],
        user_question: str,
        context: Optional[List[Dict[str, Any]]] = None
    ) -> str:
        """
        构建答案生成的 prompt
        
        参数:
            sql_result: SQL 执行结果
            user_question: 用户问题
            context: 历史上下文
            
        返回:
            str: 完整的 prompt 文本
        """
        data = sql_result.get('data', [])
        row_count = sql_result.get('row_count', 0)
        
        # 限制数据量
        sample_data = data[:20] if len(data) > 20 else data
        
        # 转换为 JSON 可序列化格式
        sample_data = self._serialize_data(sample_data)
        
        prompt = f"""请基于以下查询结果，用自然、专业的语言回答用户的问题。

## 用户问题
{user_question}

## 查询结果
返回行数: {row_count} 行

数据内容:
```json
{json.dumps(sample_data, ensure_ascii=False, indent=2)}
```

## 要求
1. 直接回答用户的问题，语言自然流畅
2. 如果有数值，给出准确的数字
3. 如果有多行数据，进行合理的总结或列举
4. 如果发现有趣的洞察或异常，可以提及
5. 保持简洁，不要过度解释SQL或技术细节
6. 使用中文回答

请开始回答："""
        
        return prompt
    
    def _call_llm_for_answer(self, prompt: str, retry_count: int = 0) -> str:
        """
        调用 LLM 生成答案（带重试机制）
        
        参数:
            prompt: 提示文本
            retry_count: 当前重试次数
            
        返回:
            str: 生成的答案
        """
        start_time = time.time()
        
        url = self.llm_config.get_chat_completion_url()
        headers = self.llm_config.get_api_headers()
        
        # 使用答案生成专用配置
        params = self.llm_config.get_answer_generation_params()
        
        data = {
            'model': params['model'],
            'messages': [
                {
                    'role': 'system',
                    'content': '你是一个专业的数据分析助手，擅长将数据转化为清晰、易懂的自然语言答案。'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'temperature': params['temperature'],
            'max_tokens': params['max_tokens']
        }
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=data,
                timeout=self.llm_config.timeout
            )
            response.raise_for_status()
            
            result = response.json()
            content = result['choices'][0]['message']['content'].strip()
            
            api_time = time.time() - start_time
            
            # 记录 API 调用 - 使用正确的参数
            log_api_call(
                api_name=f"{params['model']}_answer_generation",
                success=True,
                response_time=api_time,
                request_data={'prompt_length': len(prompt)},
                response_data={'response_length': len(content)}
            )
            
            return content
            
        except requests.exceptions.Timeout as e:
            api_time = time.time() - start_time
            self.logger.error(f"LLM 答案生成超时: {e}")
            
            # 超时重试
            if retry_count < self.max_retries:
                self.logger.info(f"重试答案生成 ({retry_count + 1}/{self.max_retries})")
                time.sleep(1)  # 等待1秒后重试
                return self._call_llm_for_answer(prompt, retry_count + 1)
            else:
                log_api_call(
                    api_name=f"{params['model']}_answer_generation",
                    success=False,
                    response_time=api_time,
                    error=str(e)
                )
                raise
                
        except Exception as e:
            api_time = time.time() - start_time
            self.logger.error(f"LLM 答案生成 API 调用失败: {e}")
            
            log_api_call(
                api_name=f"{params.get('model', 'unknown')}_answer_generation",
                success=False,
                response_time=api_time,
                error=str(e)
            )
            raise
    
    def _fallback_generate_answer(
        self,
        sql_result: Dict[str, Any],
        user_question: str
    ) -> str:
        """
        降级的答案生成（当 LLM 不可用时）
        
        参数:
            sql_result: SQL 执行结果
            user_question: 用户问题
            
        返回:
            str: 简单格式化的答案
        """
        data = sql_result.get('data', [])
        row_count = sql_result.get('row_count', 0)
        
        if not data:
            return "查询未返回任何结果。"
        
        if row_count == 1:
            # 单行结果
            row = data[0]
            parts = []
            for col, val in row.items():
                if val is not None:
                    if isinstance(val, float):
                        parts.append(f"{col}: {val:.2f}")
                    else:
                        parts.append(f"{col}: {val}")
            return "查询结果：" + ", ".join(parts)
        
        elif row_count <= 10:
            # 少量结果
            result = f"查询返回 {row_count} 条记录：\n"
            for i, row in enumerate(data, 1):
                row_str = ", ".join([f"{k}: {v}" for k, v in row.items() if v is not None])
                result += f"{i}. {row_str}\n"
            return result.strip()
        
        else:
            # 大量结果
            return f"查询返回 {row_count} 条记录（数据量较大，建议查看详细结果）。"
    
    def should_continue_querying(
        self,
        current_result: Dict[str, Any],
        user_question: str,
        iteration: int,
        max_iterations: int
    ) -> Tuple[bool, str]:
        """
        使用 LLM 智能判断是否应该继续查询
        
        参数:
            current_result: 当前查询结果
            user_question: 用户问题
            iteration: 当前迭代次数
            max_iterations: 最大迭代次数
            
        返回:
            (是否继续, 原因)
        """
        # 硬性限制：已达到最大迭代次数
        if iteration >= max_iterations:
            return False, "达到最大迭代次数"
        
        # 快速判断：查询失败
        if not current_result.get('success', False):
            return True, "查询失败，需要修正SQL"
        
        # 使用 LLM 判断
        if self.llm_config:
            try:
                analysis = self.analyze_result(current_result, user_question)
                
                if analysis['next_action'] == 'generate_answer':
                    return False, "结果充分，可以生成答案"
                elif analysis['next_action'] == 'retry_query':
                    return True, analysis['suggestion']
                elif analysis['next_action'] == 'continue_query':
                    return True, analysis['suggestion']
                else:
                    # 默认行为
                    return False, "继续生成答案"
                    
            except Exception as e:
                self.logger.error(f"LLM 判断失败: {e}")
                # 降级处理
        
        # 降级逻辑：有数据就尝试生成答案
        row_count = current_result.get('row_count', 0)
        if row_count > 0:
            return False, "查询返回有效数据，尝试生成答案"
        else:
            return False, "查询返回空结果，交由LLM判断"
    
    def format_result_for_display(
        self,
        sql_result: Dict[str, Any],
        max_rows: int = 10
    ) -> str:
        """
        格式化查询结果用于显示
        
        参数:
            sql_result: SQL 执行结果
            max_rows: 最多显示的行数
            
        返回:
            str: 格式化的结果字符串
        """
        if not sql_result.get('success', False):
            return f"❌ 查询失败: {sql_result.get('error', '未知错误')}"
        
        data = sql_result.get('data', [])
        row_count = sql_result.get('row_count', 0)
        
        if row_count == 0:
            return "查询成功，但未返回任何数据"
        
        lines = []
        lines.append(f"查询成功，返回 {row_count} 行数据")
        
        if data:
            # 显示列名
            columns = list(data[0].keys())
            lines.append("\n列: " + ", ".join(columns))
            
            # 显示数据
            lines.append("\n数据:")
            display_data = data[:max_rows]
            for i, row in enumerate(display_data, 1):
                row_str = " | ".join([f"{k}: {v}" for k, v in row.items()])
                lines.append(f"  {i}. {row_str}")
            
            if row_count > max_rows:
                lines.append(f"\n（仅显示前 {max_rows} 行，共 {row_count} 行）")
        
        return "\n".join(lines)
    
    def extract_answer_from_result(
        self,
        sql_result: Dict[str, Any],
        user_question: str
    ) -> Optional[str]:
        """
        从查询结果中快速提取简单答案（仅用于极简单的情况）
        
        对于复杂情况，返回 None，由 generate_answer_suggestion 使用 LLM 处理
        
        参数:
            sql_result: SQL 执行结果
            user_question: 用户问题
            
        返回:
            Optional[str]: 如果是极简单情况则返回快速答案，否则返回None让LLM处理
        """
        data = sql_result.get('data', [])
        row_count = sql_result.get('row_count', 0)
        
        # 对于大部分情况，让 LLM 生成更好的答案
        # 只有在极简单的情况下才快速返回
        
        if row_count == 1 and data:
            row = data[0]
            if len(row) == 1:
                col, val = list(row.items())[0]
                if isinstance(val, (int, float)):
                    # 极简单的单值情况，可以快速返回
                    if 'count' in col.lower():
                        return f"共有 {int(val)} 条记录。"
        
        # 其他所有情况都返回 None，让 LLM 生成更好的答案
        return None


# 导出的公共接口
__all__ = ['ResultAnalyzer']


if __name__ == '__main__':
    # 测试代码 - LLM 驱动版本
    print("=== 测试 LLM驱动的 ResultAnalyzer ===\n")
    
    try:
        # 尝试加载 LLM 配置
        llm_config = LLMConfig.from_env()
        print(f"✓ LLM 配置已加载: {llm_config.model}")
        analyzer = ResultAnalyzer(llm_config)
        has_llm = True
    except Exception as e:
        print(f"⚠ LLM 配置加载失败，使用降级模式: {e}")
        analyzer = ResultAnalyzer(None)
        has_llm = False
    
    print()
    
    # 测试1: 分析成功的查询结果
    print("测试1: 分析成功的查询结果")
    mock_result = {
        'success': True,
        'data': [
            {'department_name': 'A部门', 'employee_count': 22},
            {'department_name': 'B部门', 'employee_count': 20},
            {'department_name': 'C部门', 'employee_count': 18}
        ],
        'row_count': 3
    }
    
    analysis = analyzer.analyze_result(
        mock_result,
        "每个部门有多少在职员工？"
    )
    
    print(f"  是否足够: {analysis['is_sufficient']}")
    print(f"  完整性: {analysis['completeness']:.2f}")
    print(f"  建议: {analysis['suggestion']}")
    print(f"  关键发现: {analysis.get('key_findings', [])}")
    print(f"  异常情况: {analysis.get('anomalies', [])}")
    print()
    
    # 测试2: 生成答案
    if has_llm:
        print("测试2: 使用 LLM 生成自然语言答案")
        try:
            answer = analyzer.generate_answer_suggestion(
                mock_result,
                "每个部门有多少在职员工？"
            )
            print(f"  答案: {answer}")
        except Exception as e:
            print(f"  ✗ 答案生成失败: {e}")
    else:
        print("测试2: 跳过（LLM 不可用）")
    print()
    
    # 测试3: 格式化显示
    print("测试3: 格式化显示结果")
    formatted = analyzer.format_result_for_display(mock_result)
    print(formatted)
    print()
    
    # 测试4: 分析空结果
    print("测试4: 分析空结果")
    empty_result = {
        'success': True,
        'data': [],
        'row_count': 0
    }
    
    analysis = analyzer.analyze_result(
        empty_result,
        "有没有拖欠工资的情况？"
    )
    print(f"  是否足够: {analysis['is_sufficient']}")
    print(f"  建议: {analysis['suggestion']}")
    print()
    
    # 测试5: 判断是否继续查询
    print("测试5: 判断是否继续查询")
    should_continue, reason = analyzer.should_continue_querying(
        mock_result,
        "每个部门有多少在职员工？",
        iteration=1,
        max_iterations=5
    )
    print(f"  是否继续: {should_continue}")
    print(f"  原因: {reason}")
    print()
    
    print("=" * 60)
    if has_llm:
        print("✓ 测试完成！（LLM 模式）")
    else:
        print("⚠ 测试完成！（降级模式）")
