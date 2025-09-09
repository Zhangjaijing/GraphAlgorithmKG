"""
问题驱动Schema发现器

根据用户查询意图自动生成定制化Schema
"""

import json
import re
from typing import List, Dict, Optional
from dataclasses import dataclass

from .base_discoverer import BaseSchemaDiscoverer, DiscoveryContext, DiscoveryResult
from ..schemas.base_schema import Schema, EntityType, RelationType
from pipeline.llm_client import LLMClient


class QueryDrivenDiscoverer(BaseSchemaDiscoverer):
    """问题驱动的Schema发现器"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.llm_client = LLMClient()
        
        # 查询意图模式
        self.intent_patterns = {
            'performance': ['性能', '效率', '速度', '时间复杂度', '空间复杂度'],
            'comparison': ['比较', '对比', '差异', '优劣', 'vs', '相比'],
            'relationship': ['关系', '联系', '影响', '依赖', '关联'],
            'classification': ['分类', '类型', '种类', '归类', '分组'],
            'evolution': ['发展', '演化', '历史', '变化', '趋势']
        }
    
    def discover_schema(self, context: DiscoveryContext) -> DiscoveryResult:
        """根据用户查询发现Schema"""
        if not context.user_query:
            raise ValueError("QueryDrivenDiscoverer requires user_query in context")
        
        # 1. 分析查询意图
        intent = self._analyze_query_intent(context.user_query)
        
        # 2. 提取关键概念
        key_concepts = self._extract_query_concepts(context.user_query)
        
        # 3. 生成Schema
        schema = self._generate_schema_from_intent(intent, key_concepts, context)
        
        # 4. 构建结果
        result = DiscoveryResult(
            schema=schema,
            confidence=0.8,  # 基于LLM生成，置信度较高
            discovery_method="query_driven",
            reasoning=f"基于用户查询意图'{intent}'和关键概念{key_concepts}生成Schema",
            suggested_concepts=key_concepts,
            requires_user_confirmation=False  # 暂时设为False避免交互
        )
        
        return result
    
    def _analyze_query_intent(self, query: str) -> str:
        """分析查询意图"""
        query_lower = query.lower()
        
        # 计算每种意图的匹配分数
        intent_scores = {}
        for intent, keywords in self.intent_patterns.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > 0:
                intent_scores[intent] = score
        
        # 返回得分最高的意图，默认为'relationship'
        return max(intent_scores.items(), key=lambda x: x[1])[0] if intent_scores else 'relationship'
    
    def _extract_query_concepts(self, query: str) -> List[str]:
        """从查询中提取关键概念"""
        # 使用正则表达式提取可能的概念
        concepts = []
        
        # 提取引号中的内容
        quoted_concepts = re.findall(r'"([^"]*)"', query)
        concepts.extend(quoted_concepts)
        
        # 提取大写开头的词组
        capitalized_concepts = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', query)
        concepts.extend(capitalized_concepts)
        
        # 提取常见的技术术语
        tech_terms = re.findall(r'\b(?:算法|模型|方法|技术|系统|框架|架构)\b', query)
        concepts.extend(tech_terms)
        
        return list(set(concepts))  # 去重
    
    def _generate_schema_from_intent(self, intent: str, concepts: List[str], 
                                   context: DiscoveryContext) -> Schema:
        """根据意图和概念生成Schema"""
        
        # 构建LLM提示
        prompt = self._build_schema_generation_prompt(intent, concepts, context)
        
        # 调用LLM生成Schema
        try:
            # 尝试不同的LLM调用方法
            if hasattr(self.llm_client, 'generate_response'):
                response = self.llm_client.generate_response(prompt)
            elif hasattr(self.llm_client, 'generate'):
                response = self.llm_client.generate(prompt)
            else:
                # 如果没有LLM客户端，使用默认Schema
                self.logger.warning("LLM客户端不可用，使用默认Schema")
                return self._create_default_schema(intent, concepts)

            # 清理响应，提取JSON部分
            response = response.strip()
            if response.startswith('```json'):
                response = response[7:]
            if response.endswith('```'):
                response = response[:-3]
            response = response.strip()

            # 如果响应为空或无效，使用默认Schema
            if not response or response == '':
                self.logger.warning("LLM返回空响应，使用默认Schema")
                return self._create_default_schema(intent, concepts)

            try:
                schema_dict = json.loads(response)
            except json.JSONDecodeError:
                self.logger.warning(f"JSON解析失败，原始响应: {response[:100]}...")
                return self._create_default_schema(intent, concepts)

            # 转换为Schema对象
            schema = self._dict_to_schema(schema_dict)
            return schema

        except Exception as e:
            self.logger.warning(f"LLM Schema生成失败: {e}, 使用默认Schema")
            return self._create_default_schema(intent, concepts)
    
    def _build_schema_generation_prompt(self, intent: str, concepts: List[str], 
                                      context: DiscoveryContext) -> str:
        """构建Schema生成提示"""
        
        sample_text = context.documents[0][:500] if context.documents else ""
        
        prompt = f"""
请根据以下信息生成一个知识图谱Schema：

用户查询意图: {intent}
关键概念: {concepts}
示例文本: {sample_text}

请生成一个JSON格式的Schema，包含：
1. entity_types: 实体类型列表，每个包含name和description
2. relation_types: 关系类型列表，每个包含name、description、source_type、target_type

要求：
- 实体类型应该覆盖用户关心的核心概念
- 关系类型应该反映用户的查询意图
- 描述要简洁明确

示例格式：
{{
    "name": "用户定制Schema",
    "description": "基于用户查询生成的Schema",
    "entity_types": [
        {{"name": "Algorithm", "description": "算法实体"}},
        {{"name": "Performance", "description": "性能指标"}}
    ],
    "relation_types": [
        {{"name": "hasPerformance", "description": "具有性能", "source_type": "Algorithm", "target_type": "Performance"}}
    ]
}}

请只返回JSON，不要其他内容：
"""
        return prompt
    
    def _dict_to_schema(self, schema_dict: Dict) -> Schema:
        """将字典转换为Schema对象"""
        entity_types = [
            EntityType(name=et['name'], description=et.get('description', ''))
            for et in schema_dict.get('entity_types', [])
        ]
        
        relation_types = [
            RelationType(
                name=rt['name'],
                description=rt.get('description', ''),
                source_type=rt.get('source_type', 'Entity'),
                target_type=rt.get('target_type', 'Entity')
            )
            for rt in schema_dict.get('relation_types', [])
        ]
        
        return Schema(
            name=schema_dict.get('name', 'Generated Schema'),
            description=schema_dict.get('description', ''),
            entity_types=entity_types,
            relation_types=relation_types
        )
    
    def _create_default_schema(self, intent: str, concepts: List[str]) -> Schema:
        """创建默认Schema"""
        # 基于意图创建基础的实体和关系类型
        entity_types = [EntityType(name=concept, description=f"{concept}实体") 
                       for concept in concepts[:5]]  # 限制数量
        
        # 添加通用实体类型
        if not any(et.name == 'Entity' for et in entity_types):
            entity_types.append(EntityType(name='Entity', description='通用实体'))
        
        # 基于意图创建关系类型
        relation_types = []
        if intent == 'performance':
            relation_types.append(RelationType(
                name='hasPerformance', 
                description='具有性能指标',
                source_type='Entity',
                target_type='Entity'
            ))
        elif intent == 'comparison':
            relation_types.append(RelationType(
                name='comparedWith',
                description='与...比较',
                source_type='Entity', 
                target_type='Entity'
            ))
        else:
            relation_types.append(RelationType(
                name='relatedTo',
                description='相关联',
                source_type='Entity',
                target_type='Entity'
            ))
        
        return Schema(
            name=f"Default {intent.title()} Schema",
            description=f"基于{intent}意图的默认Schema",
            entity_types=entity_types,
            relation_types=relation_types
        )
