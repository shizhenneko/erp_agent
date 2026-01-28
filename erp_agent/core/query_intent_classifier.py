#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
查询意图分类器

识别用户查询的意图类型，为不同类型的查询提供差异化的处理策略。
这是架构层面的优化，帮助系统更好地理解查询语义，而不是依赖提示词。
"""

import re
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class QueryIntent(Enum):
    """查询意图类型"""
    STATISTICAL = "statistical"          # 统计查询：计数、求和、平均等
    ENUMERATION = "enumeration"          # 列举查询：列出具体记录
    COMPARISON = "comparison"            # 比较查询：比较不同实体或时间段
    ANOMALY_DETECTION = "anomaly_detection"  # 异常检测：找缺失、异常、拖欠等
    RANKING = "ranking"                  # 排名查询：TOP N、最高、最低等
    TREND_ANALYSIS = "trend_analysis"    # 趋势分析：变化、增长、涨幅等
    AGGREGATION = "aggregation"          # 分组聚合：每个部门、每个级别等
    UNKNOWN = "unknown"                  # 未知类型


@dataclass
class IntentAnalysis:
    """意图分析结果"""
    intent: QueryIntent
    confidence: float  # 0-1之间，置信度
    keywords: List[str]  # 匹配到的关键词
    characteristics: Dict[str, any]  # 查询特征
    processing_hints: Dict[str, any]  # 处理建议


class QueryIntentClassifier:
    """
    查询意图分类器（辅助性、可选）
    
    功能：
    1. 识别用户查询的意图类型（作为辅助信息）
    2. 为不同类型的查询提供处理建议
    3. 特别标识"异常检测"类查询的特殊性
    
    设计理念：
    - 基于关键词和模式匹配提供辅助信息
    - 不作为硬性约束，保持模型泛化能力
    - 为下游组件提供可选的处理建议
    - 未匹配的查询类型(UNKNOWN)不影响正常处理流程
    """
    
    def __init__(self, enable_classification: bool = True):
        """
        初始化分类器
        
        参数:
            enable_classification: 是否启用意图分类（默认True，可设为False完全禁用）
        """
        self.enable_classification = enable_classification
        
        # 定义各类查询的特征模式
        self.intent_patterns = {
            QueryIntent.ANOMALY_DETECTION: {
                'keywords': [
                    '拖欠', '欠薪', '缺失', '遗漏', '断档', '未发', '未支付',
                    '异常', '问题', '错误', '不完整', '缺少', '没有',
                    '漏', '未按时', '延迟', '逾期'
                ],
                'patterns': [
                    r'有没有.*(?:拖欠|欠薪|缺失|遗漏)',
                    r'是否.*(?:缺失|遗漏|不完整)',
                    r'(?:哪些|哪个).*(?:没有|未)',
                    r'检查.*(?:完整性|异常)'
                ],
                'characteristics': {
                    'requires_full_output': True,  # 需要完整输出，不能截断
                    'no_aggregation': True,        # 不应该聚合
                    'each_row_is_issue': True      # 每一行都代表一个问题
                }
            },
            QueryIntent.RANKING: {
                'keywords': [
                    '前', '后', '最', 'TOP', 'top', '排名', '排行',
                    '第一', '第二', '最高', '最低', '最大', '最小'
                ],
                'patterns': [
                    r'(?:前|后)\s*\d+',
                    r'TOP\s*\d+',
                    r'最.*的.*\d+',
                    r'排名.*\d+'
                ],
                'characteristics': {
                    'has_limit': True,
                    'needs_ordering': True,
                    'complete_enumeration': True  # 需要完整列举
                }
            },
            QueryIntent.STATISTICAL: {
                'keywords': [
                    '多少', '总共', '平均', '总数', '总计', '合计',
                    '数量', '个数', '占比', '百分比'
                ],
                'patterns': [
                    r'(?:有|总共|一共)多少',
                    r'平均.*(?:是|为)多少',
                    r'.*的(?:总数|总计|合计)'
                ],
                'characteristics': {
                    'returns_aggregation': True,
                    'usually_few_rows': True
                }
            },
            QueryIntent.COMPARISON: {
                'keywords': [
                    '比较', '对比', '和', '与', '哪个更', '哪个高',
                    '哪个低', '差异', '区别'
                ],
                'patterns': [
                    r'.*和.*(?:哪个|哪些).*(?:高|低|多|少|好|差)',
                    r'(?:比较|对比).*和',
                    r'.*与.*的.*(?:差异|区别)'
                ],
                'characteristics': {
                    'compares_entities': True,
                    'usually_few_rows': True
                }
            },
            QueryIntent.TREND_ANALYSIS: {
                'keywords': [
                    '涨', '降', '增长', '下降', '变化', '趋势',
                    '涨幅', '降幅', '增幅', '变化率', '从.*到'
                ],
                'patterns': [
                    r'从.*到.*(?:涨|降|变化)',
                    r'.*(?:涨幅|降幅|增幅|变化率)',
                    r'.*的.*(?:增长|下降|变化)'
                ],
                'characteristics': {
                    'time_comparison': True,
                    'shows_change': True
                }
            },
            QueryIntent.AGGREGATION: {
                'keywords': [
                    '每个', '各', '分别', '每', '各自', '按',
                    '不同', '各个'
                ],
                'patterns': [
                    r'每个.*(?:有|的|是).*多少',
                    r'各.*分别',
                    r'按.*(?:分组|统计)'
                ],
                'characteristics': {
                    'groups_by_attribute': True,
                    'multiple_rows': True
                }
            },
            QueryIntent.ENUMERATION: {
                'keywords': [
                    '列出', '列举', '显示', '是谁', '有哪些', '包括',
                    '所有', '全部'
                ],
                'patterns': [
                    r'列出.*(?:所有|全部)',
                    r'.*(?:是谁|有哪些|包括哪些)',
                    r'(?:显示|展示).*(?:信息|详情)'
                ],
                'characteristics': {
                    'lists_records': True,
                    'may_have_many_rows': True
                }
            }
        }
    
    def classify(self, user_question: str) -> IntentAnalysis:
        """
        分类用户查询意图（可选、辅助性）
        
        参数:
            user_question: 用户的自然语言问题
            
        返回:
            IntentAnalysis: 意图分析结果
            
        注意:
            - 如果禁用分类或未匹配到任何模式，返回UNKNOWN类型
            - UNKNOWN类型不会影响后续处理，只是缺少辅助信息
        """
        # 如果禁用分类，直接返回UNKNOWN
        if not self.enable_classification:
            return IntentAnalysis(
                intent=QueryIntent.UNKNOWN,
                confidence=0.0,
                keywords=[],
                characteristics={},
                processing_hints={'description': '意图分类已禁用，使用通用处理策略'}
            )
        
        # 计算每种意图的得分
        scores = {}
        matches = {}
        
        for intent, config in self.intent_patterns.items():
            score = 0
            matched_keywords = []
            
            # 关键词匹配
            for keyword in config['keywords']:
                if keyword in user_question:
                    score += 1
                    matched_keywords.append(keyword)
            
            # 模式匹配
            for pattern in config['patterns']:
                if re.search(pattern, user_question):
                    score += 2  # 模式匹配权重更高
                    matched_keywords.append(f"pattern:{pattern[:20]}...")
            
            scores[intent] = score
            matches[intent] = matched_keywords
        
        # 找到得分最高的意图
        if max(scores.values()) == 0:
            # 没有匹配到任何模式 - 这是正常的，说明是新类型的问题
            return IntentAnalysis(
                intent=QueryIntent.UNKNOWN,
                confidence=0.0,
                keywords=[],
                characteristics={},
                processing_hints={
                    'description': '未匹配到预定义模式，使用通用处理策略',
                    'note': '这不是错误，系统会正常处理此类问题'
                }
            )
        
        best_intent = max(scores, key=scores.get)
        best_score = scores[best_intent]
        
        # 计算置信度（简单的归一化）
        confidence = min(best_score / 5.0, 1.0)  # 假设5分为满分
        
        # 【关键改进】只在高置信度时才应用特殊处理建议
        # 低置信度时，退化为UNKNOWN，避免误判
        if confidence < 0.4:
            return IntentAnalysis(
                intent=QueryIntent.UNKNOWN,
                confidence=confidence,
                keywords=matches[best_intent],
                characteristics={},
                processing_hints={
                    'description': f'置信度过低({confidence:.2f})，使用通用处理策略',
                    'weak_match': best_intent.value
                }
            )
        
        # 获取特征和处理建议
        characteristics = self.intent_patterns[best_intent]['characteristics']
        processing_hints = self._generate_processing_hints(best_intent, characteristics)
        
        return IntentAnalysis(
            intent=best_intent,
            confidence=confidence,
            keywords=matches[best_intent],
            characteristics=characteristics,
            processing_hints=processing_hints
        )
    
    def _generate_processing_hints(
        self, 
        intent: QueryIntent, 
        characteristics: Dict
    ) -> Dict[str, any]:
        """
        根据意图类型生成处理建议
        
        参数:
            intent: 查询意图
            characteristics: 查询特征
            
        返回:
            Dict: 处理建议
        """
        hints = {
            'intent_name': intent.value,
            'description': self._get_intent_description(intent)
        }
        
        # 针对异常检测的特殊处理
        if intent == QueryIntent.ANOMALY_DETECTION:
            hints.update({
                'result_handling': {
                    'must_show_all_rows': True,
                    'no_summarization': True,
                    'each_row_is_important': True,
                    'warning': '每一行都代表一个具体的异常/问题，必须完整列出'
                },
                'answer_format': {
                    'list_all_records': True,
                    'include_details': True,
                    'avoid_phrases': ['共有N个', '包括', '等']
                },
                'sql_hints': {
                    'likely_uses': ['LEFT JOIN', 'IS NULL', 'generate_series'],
                    'expected_structure': 'CTE + LEFT JOIN + IS NULL pattern'
                }
            })
        
        # 针对排名查询的特殊处理
        elif intent == QueryIntent.RANKING:
            hints.update({
                'result_handling': {
                    'must_list_all': True,
                    'preserve_order': True,
                    'show_rank': True
                },
                'answer_format': {
                    'table_format': True,
                    'include_all_requested': True
                }
            })
        
        # 针对统计查询
        elif intent == QueryIntent.STATISTICAL:
            hints.update({
                'result_handling': {
                    'single_or_few_values': True,
                    'can_summarize': True
                },
                'answer_format': {
                    'concise': True,
                    'include_units': True
                }
            })
        
        return hints
    
    def _get_intent_description(self, intent: QueryIntent) -> str:
        """获取意图类型的描述"""
        descriptions = {
            QueryIntent.ANOMALY_DETECTION: "异常检测查询：查找缺失、异常、拖欠等问题",
            QueryIntent.RANKING: "排名查询：找出TOP N或排名靠前/靠后的记录",
            QueryIntent.STATISTICAL: "统计查询：计算总数、平均值、占比等统计指标",
            QueryIntent.COMPARISON: "比较查询：对比不同实体或时间段的差异",
            QueryIntent.TREND_ANALYSIS: "趋势分析：分析变化、增长或趋势",
            QueryIntent.AGGREGATION: "分组聚合：按某个属性分组统计",
            QueryIntent.ENUMERATION: "列举查询：列出具体的记录或实体",
            QueryIntent.UNKNOWN: "未知查询类型"
        }
        return descriptions.get(intent, "")


# 导出
__all__ = ['QueryIntentClassifier', 'QueryIntent', 'IntentAnalysis']


if __name__ == '__main__':
    # 测试代码
    print("=== 测试 QueryIntentClassifier ===\n")
    
    classifier = QueryIntentClassifier()
    
    test_questions = [
        "有没有出现过拖欠员工工资的情况？如果有，是哪些员工？",
        "从去年到今年涨薪幅度最大的10位员工是谁？",
        "公司有多少在职员工？",
        "每个部门分别有多少在职员工？",
        "去年A部门和B部门的平均工资哪个高？",
        "列出所有在职员工的姓名和部门"
    ]
    
    for i, question in enumerate(test_questions, 1):
        print(f"测试 {i}: {question}")
        result = classifier.classify(question)
        print(f"  意图: {result.intent.value}")
        print(f"  置信度: {result.confidence:.2f}")
        print(f"  匹配关键词: {result.keywords}")
        print(f"  描述: {result.processing_hints.get('description', '')}")
        
        if result.intent == QueryIntent.ANOMALY_DETECTION:
            print(f"  ⚠️ 特殊处理：")
            print(f"    - 必须显示所有行: {result.processing_hints['result_handling']['must_show_all_rows']}")
            print(f"    - 不能汇总: {result.processing_hints['result_handling']['no_summarization']}")
        
        print()
    
    print("=== 测试完成 ===")
