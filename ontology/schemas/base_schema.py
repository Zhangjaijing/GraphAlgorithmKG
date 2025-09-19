"""
基础Schema数据结构
兼容现有系统的Schema定义
"""

from dataclasses import dataclass, field
from typing import List, Optional
from ontology.managers.dynamic_schema import (
    EntityTypeConfig as EntityType,
    RelationTypeConfig as BaseRelationType
)

@dataclass
class RelationType:
    """关系类型，兼容动态Schema发现"""
    name: str
    description: str = ""
    source_type: str = "Entity"
    target_type: str = "Entity"
    examples: List[str] = field(default_factory=list)

    def __post_init__(self):
        if not self.examples:
            self.examples = []

@dataclass
class Schema:
    """Schema配置类，兼容现有系统"""
    name: str
    description: str = ""
    entity_types: List[EntityType] = field(default_factory=list)
    relation_types: List[RelationType] = field(default_factory=list)
    version: str = "1.0.0"

    def __post_init__(self):
        if not self.entity_types:
            self.entity_types = []
        if not self.relation_types:
            self.relation_types = []

# 为了兼容性，重新导出
__all__ = ['EntityType', 'RelationType', 'Schema']
