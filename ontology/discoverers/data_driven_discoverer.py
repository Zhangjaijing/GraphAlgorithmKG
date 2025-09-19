"""
数据驱动Schema发现器

从文档内容中自动发现概念结构，无需用户查询
"""

from typing import List, Dict, Set
from collections import Counter, defaultdict
import re
import logging

from .base_discoverer import BaseSchemaDiscoverer, DiscoveryContext, DiscoveryResult
from ..schemas.base_schema import Schema, EntityType, RelationType

logger = logging.getLogger(__name__)


class DataDrivenDiscoverer(BaseSchemaDiscoverer):
    """数据驱动的Schema发现器"""
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        
        # 配置参数
        self.min_concept_frequency = config.get('min_concept_frequency', 3)
        self.max_concepts = config.get('max_concepts', 20)
        self.similarity_threshold = config.get('similarity_threshold', 0.7)
    
    def discover_schema(self, context: DiscoveryContext) -> DiscoveryResult:
        """从数据中发现Schema"""
        if not context.documents:
            raise ValueError("DataDrivenDiscoverer requires documents in context")
        
        # 合并所有文档
        all_text = ' '.join(context.documents)
        
        # 1. 发现实体类型
        entity_types = self._discover_entity_types(all_text)
        
        # 2. 发现关系类型
        relation_types = self._discover_relation_types(all_text, entity_types)
        
        # 3. 构建Schema
        schema = Schema(
            name="Data-Driven Schema",
            description="从数据中自动发现的Schema",
            entity_types=entity_types,
            relation_types=relation_types
        )
        
        # 4. 计算置信度
        confidence = self._calculate_discovery_confidence(entity_types, relation_types)
        
        result = DiscoveryResult(
            schema=schema,
            confidence=confidence,
            discovery_method="data_driven",
            reasoning=f"从{len(context.documents)}个文档中发现{len(entity_types)}个实体类型和{len(relation_types)}个关系类型",
            requires_user_confirmation=True
        )
        
        return result
    
    def _discover_entity_types(self, text: str) -> List[EntityType]:
        """发现实体类型"""
        # 1. 提取候选实体
        candidates = self._extract_entity_candidates(text)
        
        # 2. 聚类相似实体
        clustered_entities = self._cluster_entities(candidates)
        
        # 3. 生成实体类型
        entity_types = []
        for cluster_name, entities in clustered_entities.items():
            if len(entities) >= self.min_concept_frequency:
                entity_types.append(EntityType(
                    name=cluster_name,
                    description=f"包含{len(entities)}个实例的实体类型"
                ))
        
        return entity_types[:self.max_concepts]
    
    def _extract_entity_candidates(self, text: str) -> List[str]:
        """提取实体候选"""
        candidates = []
        
        # 1. 大写开头的名词短语
        noun_phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        candidates.extend(noun_phrases)
        
        # 2. 技术术语模式
        tech_patterns = [
            r'\b\w+算法\b', r'\b\w+模型\b', r'\b\w+方法\b',
            r'\b\w+系统\b', r'\b\w+框架\b', r'\b\w+网络\b'
        ]
        
        for pattern in tech_patterns:
            matches = re.findall(pattern, text)
            candidates.extend(matches)
        
        # 3. 过滤和统计
        candidate_counts = Counter(candidates)
        return [candidate for candidate, count in candidate_counts.items() 
                if count >= self.min_concept_frequency]
    
    def _cluster_entities(self, candidates: List[str]) -> Dict[str, List[str]]:
        """聚类相似实体"""
        clusters = defaultdict(list)
        
        # 简单的基于后缀的聚类
        for candidate in candidates:
            cluster_key = self._get_cluster_key(candidate)
            clusters[cluster_key].append(candidate)
        
        return dict(clusters)
    
    def _get_cluster_key(self, entity: str) -> str:
        """获取聚类键"""
        entity_lower = entity.lower()
        
        # 基于常见后缀分类
        if any(suffix in entity_lower for suffix in ['算法', 'algorithm']):
            return 'Algorithm'
        elif any(suffix in entity_lower for suffix in ['模型', 'model']):
            return 'Model'
        elif any(suffix in entity_lower for suffix in ['方法', 'method']):
            return 'Method'
        elif any(suffix in entity_lower for suffix in ['系统', 'system']):
            return 'System'
        elif any(suffix in entity_lower for suffix in ['网络', 'network']):
            return 'Network'
        else:
            # 使用首个单词作为类别
            first_word = entity.split()[0] if ' ' in entity else entity
            return first_word.title()
    
    def _discover_relation_types(self, text: str, entity_types: List[EntityType]) -> List[RelationType]:
        """发现关系类型"""
        relation_types = []
        
        # 关系模式
        relation_patterns = [
            (r'(\w+)\s+(?:是|为|属于)\s+(\w+)', 'isA', '是...的关系'),
            (r'(\w+)\s+(?:具有|拥有|包含)\s+(\w+)', 'has', '具有...的关系'),
            (r'(\w+)\s+(?:使用|采用|应用)\s+(\w+)', 'uses', '使用...的关系'),
            (r'(\w+)\s+(?:优于|超过|胜过)\s+(\w+)', 'betterThan', '优于...的关系'),
            (r'(\w+)\s+(?:基于|依赖|建立在)\s+(\w+)', 'basedOn', '基于...的关系')
        ]
        
        for pattern, relation_name, description in relation_patterns:
            matches = re.findall(pattern, text)
            if len(matches) >= self.min_concept_frequency:
                relation_types.append(RelationType(
                    name=relation_name,
                    description=description,
                    source_type='Entity',
                    target_type='Entity'
                ))
        
        return relation_types
    
    def _calculate_discovery_confidence(self, entity_types: List[EntityType], 
                                      relation_types: List[RelationType]) -> float:
        """计算发现置信度"""
        # 基于发现的概念数量计算置信度
        total_concepts = len(entity_types) + len(relation_types)
        
        if total_concepts == 0:
            return 0.0
        elif total_concepts < 3:
            return 0.4
        elif total_concepts < 6:
            return 0.6
        elif total_concepts < 10:
            return 0.8
        else:
            return 0.9
