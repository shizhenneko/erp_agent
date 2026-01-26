#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ERP Agent 主控制器

实现 ReAct 范式的多轮迭代 Agent，支持流式处理。
负责协调 SQL 生成、执行和结果分析的完整流程。
"""

import time
from typing import Dict, List, Any, Optional, Generator
from dataclasses import dataclass, field

from erp_agent.config.llm import LLMConfig, AgentConfig
from erp_agent.config.database import DatabaseConfig
from erp_agent.core.sql_generator import SQLGenerator
from erp_agent.core.sql_executor import SQLExecutor
from erp_agent.core.result_analyzer import ResultAnalyzer
from erp_agent.utils.prompt_builder import PromptBuilder
from erp_agent.utils.date_utils import get_current_datetime
from erp_agent.utils.logger import (
    get_logger, 
    setup_logger,
    log_agent_iteration
)


@dataclass
class AgentState:
    """
    Agent 执行状态
    
    记录 Agent 执行过程中的所有状态信息
    """
    user_question: str
    iteration: int = 0
    context: List[Dict[str, Any]] = field(default_factory=list)
    final_answer: Optional[str] = None
    success: bool = False
    total_time: float = 0.0
    error: Optional[str] = None


class ERPAgent:
    """
    ERP Agent 主控制器
    
    实现 ReAct (Reasoning + Acting) 范式的 Agent:
        1. Thought（思考）：分析当前情况，决定下一步策略
        2. Action（行动）：执行 SQL 查询或给出最终答案
        3. Observation（观察）：查看执行结果
        4. 循环迭代，直到问题解决或达到最大迭代次数
    
    功能:
        - 多轮迭代查询
        - 错误自动重试
        - 流式输出支持
        - 完整的日志记录
    
    属性:
        llm_config (LLMConfig): LLM 配置
        db_config (DatabaseConfig): 数据库配置
        agent_config (AgentConfig): Agent 配置
        sql_generator (SQLGenerator): SQL 生成器
        sql_executor (SQLExecutor): SQL 执行器
        prompt_builder (PromptBuilder): Prompt 构建器
        
    使用示例:
        >>> agent = ERPAgent(llm_config, db_config, agent_config)
        >>> result = agent.query("公司有多少在职员工？")
        >>> print(result['answer'])
        '公司目前有 88 名在职员工。'
        >>> print(result['iterations'])
        2
    """
    
    def __init__(
        self,
        llm_config: LLMConfig,
        db_config: DatabaseConfig,
        agent_config: Optional[AgentConfig] = None,
        prompt_builder: Optional[PromptBuilder] = None
    ):
        """
        初始化 ERP Agent
        
        参数:
            llm_config: LLM 配置
            db_config: 数据库配置
            agent_config: Agent 配置（可选，默认使用环境变量）
            prompt_builder: Prompt 构建器（可选，默认创建新实例）
        """
        self.llm_config = llm_config
        self.db_config = db_config
        self.agent_config = agent_config or AgentConfig.from_env()
        
        # 初始化日志
        setup_logger(
            log_level=self.agent_config.log_level,
            log_file=self.agent_config.log_file
        )
        self.logger = get_logger(__name__)
        
        # 初始化组件
        self.prompt_builder = prompt_builder or PromptBuilder()
        self.sql_generator = SQLGenerator(llm_config, self.prompt_builder)
        self.sql_executor = SQLExecutor(db_config)
        self.result_analyzer = ResultAnalyzer(llm_config)  # 使用 LLM 驱动的结果分析器
        
        self.logger.info("ERP Agent 已初始化")
        self.logger.info(f"最大迭代次数: {self.agent_config.max_iterations}")
    
    def query(
        self,
        user_question: str,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        执行查询（非流式）
        
        参数:
            user_question: 用户的自然语言问题
            stream: 是否使用流式输出（保留参数，实际使用 query_stream）
            
        返回:
            Dict: 包含查询结果的字典
                {
                    'success': bool,              # 是否成功
                    'answer': str,                # 最终答案
                    'iterations': int,            # 迭代次数
                    'context': List[Dict],        # 执行上下文
                    'total_time': float,          # 总执行时间
                    'error': Optional[str]        # 错误信息
                }
        """
        if stream:
            # 如果请求流式输出，收集所有结果后返回
            final_result = None
            for chunk in self.query_stream(user_question):
                if chunk['type'] == 'final':
                    final_result = chunk
            return final_result if final_result else self._create_error_result(
                user_question, "流式查询未返回最终结果"
            )
        
        start_time = time.time()
        
        try:
            # 初始化状态
            state = AgentState(user_question=user_question)
            
            # 获取时间信息
            date_info = get_current_datetime()
            
            self.logger.info(f"开始处理问题: {user_question}")
            
            # 主循环
            while state.iteration < self.agent_config.max_iterations:
                state.iteration += 1
                
                self.logger.info(f"===== 第 {state.iteration} 轮迭代 =====")
                
                # 1. 生成 SQL 或答案
                gen_result = self.sql_generator.generate(
                    user_question=user_question,
                    context=state.context,
                    date_info=date_info,
                    error_feedback=self._get_error_feedback(state.context)
                )
                
                # 检查生成是否出错
                if gen_result['action'] == 'error':
                    self.logger.error(f"生成失败: {gen_result.get('error', '未知错误')}")
                    
                    # 如果是第一轮就失败，返回错误
                    if state.iteration == 1:
                        state.error = gen_result.get('error', '生成失败')
                        break
                    
                    # 否则尝试继续
                    continue
                
                # 记录思考过程
                thought = gen_result.get('thought', '')
                action = gen_result.get('action', '')
                
                self.logger.info(f"Thought: {thought}")
                self.logger.info(f"Action: {action}")
                
                # 2. 执行动作
                if action == 'execute_sql':
                    # 执行 SQL 查询
                    sql = gen_result.get('sql', '')
                    
                    if not sql:
                        self.logger.error("action 是 execute_sql 但缺少 sql")
                        continue
                    
                    self.logger.info(f"执行 SQL: {sql[:200]}...")
                    
                    exec_result = self.sql_executor.execute(sql)
                    
                    # 记录上下文
                    state.context.append({
                        'iteration': state.iteration,
                        'thought': thought,
                        'action': action,
                        'sql': sql,
                        'result': exec_result
                    })
                    
                    # 分析查询结果（辅助判断）
                    result_analysis = self.result_analyzer.analyze_result(
                        exec_result, user_question, state.context
                    )
                    
                    # 记录迭代日志
                    result_summary = self._summarize_result(exec_result)
                    log_agent_iteration(
                        iteration=state.iteration,
                        user_question=user_question,
                        sql=sql,
                        result_summary=result_summary,
                        next_action="继续迭代"
                    )
                    
                    # 记录分析结果（用于调试）
                    if result_analysis.get('is_sufficient'):
                        self.logger.info(
                            f"结果分析: 完整性 {result_analysis['completeness']:.2f}, "
                            f"建议: {result_analysis['suggestion']}"
                        )
                    
                    # 如果执行失败，记录错误但继续下一轮（让 LLM 修正）
                    if not exec_result['success']:
                        self.logger.warning(
                            f"SQL 执行失败: {exec_result['error']}，将在下一轮重试"
                        )
                
                elif action == 'answer':
                    # 给出最终答案
                    answer = gen_result.get('answer', '')
                    
                    if not answer:
                        self.logger.error("action 是 answer 但缺少 answer")
                        continue
                    
                    state.final_answer = answer
                    state.success = True
                    
                    self.logger.info(f"最终答案: {answer}")
                    
                    # 记录上下文
                    state.context.append({
                        'iteration': state.iteration,
                        'thought': thought,
                        'action': action,
                        'answer': answer
                    })
                    
                    log_agent_iteration(
                        iteration=state.iteration,
                        user_question=user_question,
                        sql="N/A",
                        result_summary="生成最终答案",
                        next_action="完成"
                    )
                    
                    break
                
                else:
                    self.logger.warning(f"未知的 action: {action}")
                    continue
                
                # 检查是否标记为最终结果
                if gen_result.get('is_final', False):
                    if not state.final_answer and action == 'answer':
                        state.final_answer = gen_result.get('answer', '')
                        state.success = True
                    break
            
            # 循环结束后的处理
            state.total_time = time.time() - start_time
            
            if not state.success:
                if state.iteration >= self.agent_config.max_iterations:
                    self.logger.warning(f"达到最大迭代次数 ({self.agent_config.max_iterations})")
                    state.error = f"达到最大迭代次数 ({self.agent_config.max_iterations})，未能完成查询"
                    
                    # 尝试基于现有结果生成答案
                    if state.context and self._has_successful_query(state.context):
                        try:
                            state.final_answer = self._generate_fallback_answer(
                                user_question, state.context
                            )
                            state.success = True
                            state.error = None
                        except Exception as e:
                            self.logger.error(f"生成备用答案失败: {e}")
                elif state.error:
                    self.logger.error(f"查询失败: {state.error}")
                else:
                    state.error = "未知错误"
            
            # 构建返回结果
            result = {
                'success': state.success,
                'answer': state.final_answer or "抱歉，无法回答该问题。",
                'iterations': state.iteration,
                'context': state.context,
                'total_time': state.total_time,
                'error': state.error
            }
            
            self.logger.info(
                f"查询完成 - 成功: {state.success}, "
                f"迭代: {state.iteration}次, "
                f"耗时: {state.total_time:.2f}秒"
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"查询过程中发生异常: {e}")
            import traceback
            traceback.print_exc()
            
            return self._create_error_result(user_question, str(e))
    
    def query_stream(
        self,
        user_question: str
    ) -> Generator[Dict[str, Any], None, None]:
        """
        执行查询（流式输出）
        
        逐步返回执行过程中的状态更新，适合实时展示
        
        参数:
            user_question: 用户的自然语言问题
            
        返回:
            Generator: 生成器，逐步返回执行状态
                每个 chunk 的格式:
                {
                    'type': str,  # 'iteration_start', 'thought', 'action', 
                                  # 'sql_executing', 'sql_result', 'answer', 'final'
                    'iteration': int,
                    'data': Any,
                    'timestamp': float
                }
        """
        start_time = time.time()
        
        try:
            # 初始化状态
            state = AgentState(user_question=user_question)
            
            # 获取时间信息
            date_info = get_current_datetime()
            
            yield {
                'type': 'start',
                'user_question': user_question,
                'timestamp': time.time()
            }
            
            # 主循环
            while state.iteration < self.agent_config.max_iterations:
                state.iteration += 1
                
                yield {
                    'type': 'iteration_start',
                    'iteration': state.iteration,
                    'timestamp': time.time()
                }
                
                # 1. 生成 SQL 或答案
                gen_result = self.sql_generator.generate(
                    user_question=user_question,
                    context=state.context,
                    date_info=date_info,
                    error_feedback=self._get_error_feedback(state.context),
                    stream=False  # 内部不使用流式
                )
                
                # 检查生成是否出错
                if gen_result['action'] == 'error':
                    yield {
                        'type': 'error',
                        'iteration': state.iteration,
                        'error': gen_result.get('error', '未知错误'),
                        'timestamp': time.time()
                    }
                    
                    if state.iteration == 1:
                        state.error = gen_result.get('error', '生成失败')
                        break
                    
                    continue
                
                # 输出思考过程
                thought = gen_result.get('thought', '')
                action = gen_result.get('action', '')
                
                yield {
                    'type': 'thought',
                    'iteration': state.iteration,
                    'thought': thought,
                    'timestamp': time.time()
                }
                
                yield {
                    'type': 'action',
                    'iteration': state.iteration,
                    'action': action,
                    'timestamp': time.time()
                }
                
                # 2. 执行动作
                if action == 'execute_sql':
                    sql = gen_result.get('sql', '')
                    
                    if not sql:
                        yield {
                            'type': 'error',
                            'iteration': state.iteration,
                            'error': 'action 是 execute_sql 但缺少 sql',
                            'timestamp': time.time()
                        }
                        continue
                    
                    yield {
                        'type': 'sql_executing',
                        'iteration': state.iteration,
                        'sql': sql,
                        'timestamp': time.time()
                    }
                    
                    exec_result = self.sql_executor.execute(sql)
                    
                    yield {
                        'type': 'sql_result',
                        'iteration': state.iteration,
                        'result': exec_result,
                        'timestamp': time.time()
                    }
                    
                    # 记录上下文
                    state.context.append({
                        'iteration': state.iteration,
                        'thought': thought,
                        'action': action,
                        'sql': sql,
                        'result': exec_result
                    })
                    
                    # 分析查询结果（辅助判断）
                    result_analysis = self.result_analyzer.analyze_result(
                        exec_result, user_question, state.context
                    )
                    
                    # 可以选择性地输出分析结果
                    if result_analysis.get('is_sufficient'):
                        yield {
                            'type': 'analysis',
                            'iteration': state.iteration,
                            'analysis': result_analysis,
                            'timestamp': time.time()
                        }
                
                elif action == 'answer':
                    answer = gen_result.get('answer', '')
                    
                    if not answer:
                        yield {
                            'type': 'error',
                            'iteration': state.iteration,
                            'error': 'action 是 answer 但缺少 answer',
                            'timestamp': time.time()
                        }
                        continue
                    
                    state.final_answer = answer
                    state.success = True
                    
                    yield {
                        'type': 'answer',
                        'iteration': state.iteration,
                        'answer': answer,
                        'timestamp': time.time()
                    }
                    
                    # 记录上下文
                    state.context.append({
                        'iteration': state.iteration,
                        'thought': thought,
                        'action': action,
                        'answer': answer
                    })
                    
                    break
                
                # 检查是否标记为最终结果
                if gen_result.get('is_final', False):
                    if not state.final_answer and action == 'answer':
                        state.final_answer = gen_result.get('answer', '')
                        state.success = True
                    break
            
            # 循环结束后的处理
            state.total_time = time.time() - start_time
            
            if not state.success:
                if state.iteration >= self.agent_config.max_iterations:
                    state.error = f"达到最大迭代次数 ({self.agent_config.max_iterations})"
                    
                    # 尝试基于现有结果生成答案
                    if state.context and self._has_successful_query(state.context):
                        try:
                            state.final_answer = self._generate_fallback_answer(
                                user_question, state.context
                            )
                            state.success = True
                            state.error = None
                        except Exception as e:
                            self.logger.error(f"生成备用答案失败: {e}")
            
            # 返回最终结果
            yield {
                'type': 'final',
                'success': state.success,
                'answer': state.final_answer or "抱歉，无法回答该问题。",
                'iterations': state.iteration,
                'context': state.context,
                'total_time': state.total_time,
                'error': state.error,
                'timestamp': time.time()
            }
            
        except Exception as e:
            self.logger.error(f"流式查询过程中发生异常: {e}")
            
            yield {
                'type': 'final',
                'success': False,
                'answer': f"查询失败: {str(e)}",
                'iterations': 0,
                'context': [],
                'total_time': time.time() - start_time,
                'error': str(e),
                'timestamp': time.time()
            }
    
    def _get_error_feedback(
        self,
        context: List[Dict[str, Any]]
    ) -> Optional[str]:
        """
        从上下文中提取错误反馈信息
        
        参数:
            context: 执行上下文
            
        返回:
            Optional[str]: 错误反馈信息
        """
        if not context:
            return None
        
        # 获取最后一次执行
        last_exec = context[-1]
        
        if 'result' in last_exec and not last_exec['result'].get('success', False):
            error = last_exec['result'].get('error', '')
            return f"上一次查询失败，错误信息: {error}"
        
        return None
    
    def _summarize_result(self, exec_result: Dict[str, Any]) -> str:
        """
        总结执行结果
        
        参数:
            exec_result: 执行结果
            
        返回:
            str: 结果摘要
        """
        if exec_result['success']:
            row_count = exec_result['row_count']
            exec_time = exec_result['execution_time']
            return f"成功，返回 {row_count} 行，耗时 {exec_time:.3f}秒"
        else:
            return f"失败，错误: {exec_result['error']}"
    
    def _has_successful_query(self, context: List[Dict[str, Any]]) -> bool:
        """
        检查上下文中是否有成功的查询
        
        参数:
            context: 执行上下文
            
        返回:
            bool: 是否有成功的查询
        """
        for item in context:
            if 'result' in item and item['result'].get('success', False):
                return True
        return False
    
    def _generate_fallback_answer(
        self,
        user_question: str,
        context: List[Dict[str, Any]]
    ) -> str:
        """
        生成备用答案（当达到最大迭代次数但有成功的查询时）
        
        参数:
            user_question: 用户问题
            context: 执行上下文
            
        返回:
            str: 生成的答案
        """
        # 提取成功的查询
        sql_history = []
        for item in context:
            if 'result' in item and item['result'].get('success', False):
                sql_history.append({
                    'sql': item.get('sql', ''),
                    'result': item['result']
                })
        
        if sql_history:
            # 尝试使用result_analyzer提取简单答案
            last_result = sql_history[-1]['result']
            simple_answer = self.result_analyzer.extract_answer_from_result(
                last_result, user_question
            )
            
            if simple_answer:
                self.logger.info("使用 ResultAnalyzer 提取的简单答案")
                return simple_answer
            
            # 否则调用LLM生成答案
            return self.sql_generator.generate_answer(user_question, sql_history)
        else:
            return "抱歉，无法回答该问题。"
    
    def _create_error_result(
        self,
        user_question: str,
        error: str
    ) -> Dict[str, Any]:
        """
        创建错误结果
        
        参数:
            user_question: 用户问题
            error: 错误信息
            
        返回:
            Dict: 错误结果
        """
        return {
            'success': False,
            'answer': f"查询失败: {error}",
            'iterations': 0,
            'context': [],
            'total_time': 0.0,
            'error': error
        }
    
    def test_connection(self) -> bool:
        """
        测试数据库连接
        
        返回:
            bool: 连接是否成功
        """
        return self.sql_executor.test_connection()


# 导出的公共接口
__all__ = ['ERPAgent', 'AgentState']


if __name__ == '__main__':
    # 测试代码
    print("=== 测试 ERPAgent ===\n")
    
    try:
        from erp_agent.config import get_llm_config, get_database_config, get_agent_config
        
        # 加载配置
        llm_config = get_llm_config()
        db_config = get_database_config()
        agent_config = get_agent_config()
        
        print(f"LLM 配置: {llm_config}")
        print(f"数据库配置: {db_config}")
        print(f"Agent 配置: {agent_config.to_dict()}\n")
        
        # 创建 Agent
        agent = ERPAgent(llm_config, db_config, agent_config)
        
        # 测试连接
        print("测试数据库连接...")
        if agent.test_connection():
            print("✓ 数据库连接成功\n")
        else:
            print("✗ 数据库连接失败\n")
            exit(1)
        
        # 测试简单查询
        print("=" * 60)
        print("测试简单查询")
        print("=" * 60)
        question = "公司有多少在职员工？"
        print(f"问题: {question}\n")
        
        result = agent.query(question)
        
        print(f"成功: {result['success']}")
        print(f"答案: {result['answer']}")
        print(f"迭代次数: {result['iterations']}")
        print(f"总耗时: {result['total_time']:.2f}秒")
        
        if result['error']:
            print(f"错误: {result['error']}")
        
        print(f"\n执行上下文:")
        for i, ctx in enumerate(result['context'], 1):
            print(f"  第 {i} 轮:")
            print(f"    思考: {ctx.get('thought', 'N/A')[:80]}...")
            print(f"    动作: {ctx.get('action', 'N/A')}")
            if 'sql' in ctx:
                print(f"    SQL: {ctx['sql'][:80]}...")
            if 'answer' in ctx:
                print(f"    答案: {ctx['answer'][:80]}...")
        
        # 测试流式查询
        print("\n" + "=" * 60)
        print("测试流式查询")
        print("=" * 60)
        question2 = "每个部门分别有多少在职员工？"
        print(f"问题: {question2}\n")
        
        for chunk in agent.query_stream(question2):
            chunk_type = chunk['type']
            
            if chunk_type == 'start':
                print(f"[开始] 问题: {chunk['user_question']}")
            
            elif chunk_type == 'iteration_start':
                print(f"\n[第 {chunk['iteration']} 轮]")
            
            elif chunk_type == 'thought':
                print(f"  思考: {chunk['thought'][:80]}...")
            
            elif chunk_type == 'action':
                print(f"  动作: {chunk['action']}")
            
            elif chunk_type == 'sql_executing':
                print(f"  执行SQL: {chunk['sql'][:80]}...")
            
            elif chunk_type == 'sql_result':
                result_data = chunk['result']
                if result_data['success']:
                    print(f"  结果: 成功，{result_data['row_count']} 行")
                else:
                    print(f"  结果: 失败，{result_data['error']}")
            
            elif chunk_type == 'answer':
                print(f"  答案: {chunk['answer']}")
            
            elif chunk_type == 'final':
                print(f"\n[完成]")
                print(f"  成功: {chunk['success']}")
                print(f"  最终答案: {chunk['answer']}")
                print(f"  迭代次数: {chunk['iterations']}")
                print(f"  总耗时: {chunk['total_time']:.2f}秒")
            
            elif chunk_type == 'error':
                print(f"  错误: {chunk['error']}")
        
        print("\n" + "=" * 60)
        print("所有测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
