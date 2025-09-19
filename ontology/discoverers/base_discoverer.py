"""
基础Schema发现器接口

定义所有Schema发现器的通用接口和基础功能
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import logging

from ..schemas.base_schema import Schema

logger = logging.getLogger(__name__)


@dataclass
class DiscoveryContext:
    """Schema发现上下文"""
    user_query: Optional[str] = None
    documents: List[str] = None
    existing_schemas: List[Schema] = None
    domain_hints: List[str] = None
    confidence_threshold: float = 0.7


@dataclass
class DiscoveryResult:
    """Schema发现结果"""
    schema: Schema
    confidence: float
    discovery_method: str
    reasoning: str
    suggested_concepts: List[str] = None
    requires_user_confirmation: bool = False


class BaseSchemaDiscoverer(ABC):
    """基础Schema发现器抽象类"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.logger = logging.getLogger(self.__class__.__name__)
    
    @abstractmethod
    def discover_schema(self, context: DiscoveryContext) -> DiscoveryResult:
        """
        发现Schema的核心方法
        
        Args:
            context: 发现上下文，包含用户查询、文档等信息
            
        Returns:
            DiscoveryResult: 发现的Schema及相关信息
        """
        pass
    
    def validate_discovery_result(self, result: DiscoveryResult) -> bool:
        """验证发现结果的有效性"""
        if not result.schema:
            return False
        
        if result.confidence < self.config.get('min_confidence', 0.5):
            return False
        
        # 检查Schema基本结构
        if not result.schema.entity_types or not result.schema.relation_types:
            return False
        
        return True
    
    def _extract_key_concepts(self, text: str) -> List[str]:
        """从文本中提取关键概念"""
        # 简单的关键词提取，可以扩展为更复杂的NLP方法
        import re
        from collections import Counter
        
        # 提取名词性短语
        words = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # 统计频率并返回高频概念
        concept_counts = Counter(words)
        return [concept for concept, count in concept_counts.most_common(10)]
    
    def _calculate_semantic_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的语义相似度"""
        # 简单的词汇重叠相似度，可以扩展为更复杂的语义相似度计算
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
