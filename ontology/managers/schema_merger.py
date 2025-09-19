"""
Schema合并管理器
负责多个Schema的智能合并和冲突解决
"""

from typing import Dict, List, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum
import logging
from difflib import SequenceMatcher

from ..schemas.base_schema import Schema, EntityType, RelationType
from .schema_version_manager import SchemaChangeType
from .schema_persistence_manager import SchemaPersistenceManager

logger = logging.getLogger(__name__)


class ConflictType(Enum):
    """冲突类型"""
    ENTITY_NAME_CONFLICT = "entity_name_conflict"
    RELATION_NAME_CONFLICT = "relation_name_conflict"
    SEMANTIC_CONFLICT = "semantic_conflict"
    TYPE_CONSTRAINT_CONFLICT = "type_constraint_conflict"


@dataclass
class MergeConflict:
    """合并冲突"""
    conflict_id: str
    conflict_type: ConflictType
    description: str
    source_schema: str
    target_schema: str
    conflicting_items: Dict[str, any]
    resolution_options: List[Dict[str, any]]
    auto_resolvable: bool = False
    confidence: float = 0.0


@dataclass
class MergeResult:
    """合并结果"""
    merged_schema: Optional[Schema]
    conflicts: List[MergeConflict]
    merge_summary: Dict[str, any]
    success: bool = False
    temp_schema_id: Optional[str] = None


class SchemaMerger:
    """Schema合并器"""
    
    def __init__(self, persistence_manager: SchemaPersistenceManager = None):
        self.persistence_manager = persistence_manager or SchemaPersistenceManager()
        self.similarity_threshold = 0.8  # 语义相似度阈值
        self.auto_resolve_threshold = 0.9  # 自动解决冲突的置信度阈值
        self.logger = logging.getLogger(__name__)
    
    def merge_schemas(self, schemas: List[Schema], merge_strategy: str = "intelligent") -> MergeResult:
        """
        合并多个Schema
        
        Args:
            schemas: 要合并的Schema列表
            merge_strategy: 合并策略 (intelligent, conservative, aggressive)
            
        Returns:
            MergeResult: 合并结果
        """
        if len(schemas) < 2:
            return MergeResult(
                merged_schema=schemas[0] if schemas else None,
                conflicts=[],
                merge_summary={"message": "需要至少2个Schema进行合并"},
                success=len(schemas) == 1
            )
        
        self.logger.info(f"开始合并{len(schemas)}个Schema，策略: {merge_strategy}")
        
        # 初始化合并结果
        result = MergeResult(
            merged_schema=None,
            conflicts=[],
            merge_summary={
                "total_schemas": len(schemas),
                "merge_strategy": merge_strategy,
                "entity_stats": {},
                "relation_stats": {}
            }
        )
        
        try:
            # 1. 检测冲突
            conflicts = self._detect_conflicts(schemas)
            result.conflicts = conflicts
            
            # 2. 根据策略处理冲突
            if merge_strategy == "intelligent":
                resolved_conflicts = self._resolve_conflicts_intelligently(conflicts)
            elif merge_strategy == "conservative":
                resolved_conflicts = self._resolve_conflicts_conservatively(conflicts)
            elif merge_strategy == "aggressive":
                resolved_conflicts = self._resolve_conflicts_aggressively(conflicts)
            else:
                resolved_conflicts = conflicts
            
            # 3. 执行合并
            merged_schema = self._execute_merge(schemas, resolved_conflicts)
            
            if merged_schema:
                # 4. 创建临时Schema
                temp_schema_id = self.persistence_manager.create_temp_schema(
                    merged_schema, schema_type="merged"
                )
                
                result.merged_schema = merged_schema
                result.temp_schema_id = temp_schema_id
                result.success = True
                
                # 5. 更新统计信息
                result.merge_summary.update({
                    "merged_entities": len(merged_schema.entity_types),
                    "merged_relations": len(merged_schema.relation_types),
                    "conflicts_detected": len(conflicts),
                    "conflicts_resolved": len([c for c in resolved_conflicts if c.auto_resolvable]),
                    "temp_schema_id": temp_schema_id
                })
                
                self.logger.info(f"Schema合并成功: {temp_schema_id}")
            else:
                result.success = False
                self.logger.error("Schema合并失败")
        
        except Exception as e:
            self.logger.error(f"合并过程中出错: {e}")
            result.success = False
            result.merge_summary["error"] = str(e)
        
        return result
    
    def _detect_conflicts(self, schemas: List[Schema]) -> List[MergeConflict]:
        """检测Schema间的冲突"""
        conflicts = []
        
        # 收集所有实体和关系
        all_entities = {}
        all_relations = {}
        
        for i, schema in enumerate(schemas):
            schema_id = f"schema_{i}"
            
            # 收集实体类型
            for entity in schema.entity_types:
                if entity.name not in all_entities:
                    all_entities[entity.name] = []
                all_entities[entity.name].append((schema_id, entity))
            
            # 收集关系类型
            for relation in schema.relation_types:
                if relation.name not in all_relations:
                    all_relations[relation.name] = []
                all_relations[relation.name].append((schema_id, relation))
        
        # 检测实体冲突
        for entity_name, entity_list in all_entities.items():
            if len(entity_list) > 1:
                conflict = self._analyze_entity_conflict(entity_name, entity_list)
                if conflict:
                    conflicts.append(conflict)
        
        # 检测关系冲突
        for relation_name, relation_list in all_relations.items():
            if len(relation_list) > 1:
                conflict = self._analyze_relation_conflict(relation_name, relation_list)
                if conflict:
                    conflicts.append(conflict)
        
        # 检测语义冲突
        semantic_conflicts = self._detect_semantic_conflicts(schemas)
        conflicts.extend(semantic_conflicts)
        
        return conflicts
    
    def _analyze_entity_conflict(self, entity_name: str, entity_list: List[Tuple[str, EntityType]]) -> Optional[MergeConflict]:
        """分析实体冲突"""
        if len(entity_list) < 2:
            return None
        
        # 比较描述的相似度
        descriptions = [entity.description for _, entity in entity_list]
        similarities = []
        
        for i in range(len(descriptions)):
            for j in range(i + 1, len(descriptions)):
                similarity = self._calculate_text_similarity(descriptions[i], descriptions[j])
                similarities.append(similarity)
        
        avg_similarity = sum(similarities) / len(similarities) if similarities else 0
        
        # 如果相似度高，可能是同一概念
        if avg_similarity > self.similarity_threshold:
            return MergeConflict(
                conflict_id=f"entity_{entity_name}",
                conflict_type=ConflictType.ENTITY_NAME_CONFLICT,
                description=f"实体 '{entity_name}' 在多个Schema中有相似定义",
                source_schema=entity_list[0][0],
                target_schema=entity_list[1][0],
                conflicting_items={"entities": entity_list},
                resolution_options=[
                    {"action": "merge", "description": "合并相似定义"},
                    {"action": "rename", "description": "重命名其中一个"},
                    {"action": "keep_all", "description": "保留所有定义"}
                ],
                auto_resolvable=True,
                confidence=avg_similarity
            )
        else:
            # 相似度低，可能是不同概念但名称相同
            return MergeConflict(
                conflict_id=f"entity_{entity_name}",
                conflict_type=ConflictType.SEMANTIC_CONFLICT,
                description=f"实体 '{entity_name}' 在多个Schema中有不同语义",
                source_schema=entity_list[0][0],
                target_schema=entity_list[1][0],
                conflicting_items={"entities": entity_list},
                resolution_options=[
                    {"action": "rename", "description": "重命名以区分语义"},
                    {"action": "manual_review", "description": "需要人工审查"}
                ],
                auto_resolvable=False,
                confidence=1 - avg_similarity
            )
    
    def _analyze_relation_conflict(self, relation_name: str, relation_list: List[Tuple[str, RelationType]]) -> Optional[MergeConflict]:
        """分析关系冲突"""
        if len(relation_list) < 2:
            return None
        
        # 检查类型约束是否一致
        type_constraints = []
        for _, relation in relation_list:
            constraint = (
                getattr(relation, 'source_type', '*'),
                getattr(relation, 'target_type', '*')
            )
            type_constraints.append(constraint)
        
        # 如果类型约束不一致，产生冲突
        if len(set(type_constraints)) > 1:
            return MergeConflict(
                conflict_id=f"relation_{relation_name}",
                conflict_type=ConflictType.TYPE_CONSTRAINT_CONFLICT,
                description=f"关系 '{relation_name}' 的类型约束不一致",
                source_schema=relation_list[0][0],
                target_schema=relation_list[1][0],
                conflicting_items={"relations": relation_list, "constraints": type_constraints},
                resolution_options=[
                    {"action": "use_most_general", "description": "使用最通用的约束"},
                    {"action": "use_most_specific", "description": "使用最具体的约束"},
                    {"action": "manual_review", "description": "需要人工审查"}
                ],
                auto_resolvable=True,
                confidence=0.7
            )
        
        return None
    
    def _detect_semantic_conflicts(self, schemas: List[Schema]) -> List[MergeConflict]:
        """检测语义冲突"""
        conflicts = []
        
        # 检测可能的同义词实体
        for i, schema1 in enumerate(schemas):
            for j, schema2 in enumerate(schemas[i+1:], i+1):
                for entity1 in schema1.entity_types:
                    for entity2 in schema2.entity_types:
                        if entity1.name != entity2.name:
                            similarity = self._calculate_semantic_similarity(entity1, entity2)
                            if similarity > self.similarity_threshold:
                                conflicts.append(MergeConflict(
                                    conflict_id=f"semantic_{entity1.name}_{entity2.name}",
                                    conflict_type=ConflictType.SEMANTIC_CONFLICT,
                                    description=f"实体 '{entity1.name}' 和 '{entity2.name}' 可能表示相同概念",
                                    source_schema=f"schema_{i}",
                                    target_schema=f"schema_{j}",
                                    conflicting_items={"entity1": entity1, "entity2": entity2},
                                    resolution_options=[
                                        {"action": "merge_as_synonyms", "description": "作为同义词合并"},
                                        {"action": "keep_separate", "description": "保持分离"}
                                    ],
                                    auto_resolvable=similarity > 0.9,
                                    confidence=similarity
                                ))
        
        return conflicts
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度"""
        return SequenceMatcher(None, text1.lower(), text2.lower()).ratio()
    
    def _calculate_semantic_similarity(self, entity1: EntityType, entity2: EntityType) -> float:
        """计算实体语义相似度"""
        # 比较描述
        desc_similarity = self._calculate_text_similarity(entity1.description, entity2.description)
        
        # 比较示例
        examples1 = set(getattr(entity1, 'examples', []))
        examples2 = set(getattr(entity2, 'examples', []))
        
        if examples1 and examples2:
            common_examples = len(examples1 & examples2)
            total_examples = len(examples1 | examples2)
            example_similarity = common_examples / total_examples if total_examples > 0 else 0
        else:
            example_similarity = 0
        
        # 比较关键词
        keywords1 = set(getattr(entity1, 'keywords', []))
        keywords2 = set(getattr(entity2, 'keywords', []))
        
        if keywords1 and keywords2:
            common_keywords = len(keywords1 & keywords2)
            total_keywords = len(keywords1 | keywords2)
            keyword_similarity = common_keywords / total_keywords if total_keywords > 0 else 0
        else:
            keyword_similarity = 0
        
        # 加权平均
        return (desc_similarity * 0.5 + example_similarity * 0.3 + keyword_similarity * 0.2)
    
    def _resolve_conflicts_intelligently(self, conflicts: List[MergeConflict]) -> List[MergeConflict]:
        """智能解决冲突"""
        resolved_conflicts = []
        
        for conflict in conflicts:
            if conflict.confidence > self.auto_resolve_threshold:
                # 高置信度自动解决
                if conflict.conflict_type == ConflictType.ENTITY_NAME_CONFLICT:
                    conflict.auto_resolvable = True
                elif conflict.conflict_type == ConflictType.TYPE_CONSTRAINT_CONFLICT:
                    conflict.auto_resolvable = True
                elif conflict.conflict_type == ConflictType.SEMANTIC_CONFLICT and conflict.confidence > 0.95:
                    conflict.auto_resolvable = True
            
            resolved_conflicts.append(conflict)
        
        return resolved_conflicts
    
    def _resolve_conflicts_conservatively(self, conflicts: List[MergeConflict]) -> List[MergeConflict]:
        """保守地解决冲突"""
        # 保守策略：只自动解决非常明确的冲突
        for conflict in conflicts:
            if conflict.confidence > 0.95 and conflict.conflict_type == ConflictType.ENTITY_NAME_CONFLICT:
                conflict.auto_resolvable = True
            else:
                conflict.auto_resolvable = False
        
        return conflicts
    
    def _resolve_conflicts_aggressively(self, conflicts: List[MergeConflict]) -> List[MergeConflict]:
        """激进地解决冲突"""
        # 激进策略：尽可能自动解决冲突
        for conflict in conflicts:
            if conflict.confidence > 0.6:
                conflict.auto_resolvable = True
        
        return conflicts
    
    def _execute_merge(self, schemas: List[Schema], conflicts: List[MergeConflict]) -> Optional[Schema]:
        """执行Schema合并"""
        try:
            # 创建合并后的Schema
            merged_name = f"Merged_Schema_{len(schemas)}_schemas"
            merged_description = f"合并了{len(schemas)}个Schema的结果"
            
            merged_entities = []
            merged_relations = []
            
            # 收集所有实体和关系
            all_entities = {}
            all_relations = {}
            
            for schema in schemas:
                for entity in schema.entity_types:
                    if entity.name not in all_entities:
                        all_entities[entity.name] = []
                    all_entities[entity.name].append(entity)
                
                for relation in schema.relation_types:
                    if relation.name not in all_relations:
                        all_relations[relation.name] = []
                    all_relations[relation.name].append(relation)
            
            # 处理实体合并
            for entity_name, entity_list in all_entities.items():
                merged_entity = self._merge_entities(entity_name, entity_list, conflicts)
                if merged_entity:
                    merged_entities.append(merged_entity)
            
            # 处理关系合并
            for relation_name, relation_list in all_relations.items():
                merged_relation = self._merge_relations(relation_name, relation_list, conflicts)
                if merged_relation:
                    merged_relations.append(merged_relation)
            
            return Schema(
                name=merged_name,
                description=merged_description,
                entity_types=merged_entities,
                relation_types=merged_relations,
                version="1.0.0"
            )
            
        except Exception as e:
            self.logger.error(f"执行合并失败: {e}")
            return None
    
    def _merge_entities(self, entity_name: str, entity_list: List[EntityType], 
                       conflicts: List[MergeConflict]) -> Optional[EntityType]:
        """合并实体类型"""
        if len(entity_list) == 1:
            return entity_list[0]
        
        # 查找相关冲突
        relevant_conflict = None
        for conflict in conflicts:
            if conflict.conflict_id == f"entity_{entity_name}" and conflict.auto_resolvable:
                relevant_conflict = conflict
                break
        
        # 合并策略
        if relevant_conflict and relevant_conflict.conflict_type == ConflictType.ENTITY_NAME_CONFLICT:
            # 合并相似定义
            merged_description = self._merge_descriptions([e.description for e in entity_list])
            merged_examples = list(set(sum([getattr(e, 'examples', []) for e in entity_list], [])))
            merged_keywords = list(set(sum([getattr(e, 'keywords', []) for e in entity_list], [])))
            merged_patterns = list(set(sum([getattr(e, 'patterns', []) for e in entity_list], [])))
            merged_aliases = list(set(sum([getattr(e, 'aliases', []) for e in entity_list], [])))
            
            return EntityType(
                name=entity_name,
                description=merged_description,
                examples=merged_examples,
                keywords=merged_keywords,
                patterns=merged_patterns,
                aliases=merged_aliases
            )
        else:
            # 默认使用第一个定义
            return entity_list[0]
    
    def _merge_relations(self, relation_name: str, relation_list: List[RelationType],
                        conflicts: List[MergeConflict]) -> Optional[RelationType]:
        """合并关系类型"""
        if len(relation_list) == 1:
            return relation_list[0]
        
        # 查找相关冲突
        relevant_conflict = None
        for conflict in conflicts:
            if conflict.conflict_id == f"relation_{relation_name}" and conflict.auto_resolvable:
                relevant_conflict = conflict
                break
        
        # 合并策略
        if relevant_conflict and relevant_conflict.conflict_type == ConflictType.TYPE_CONSTRAINT_CONFLICT:
            # 使用最通用的约束
            merged_description = self._merge_descriptions([r.description for r in relation_list])
            merged_examples = list(set(sum([r.examples for r in relation_list], [])))
            
            return RelationType(
                name=relation_name,
                description=merged_description,
                examples=merged_examples,
                source_type="*",  # 使用最通用的约束
                target_type="*"
            )
        else:
            # 默认使用第一个定义
            return relation_list[0]
    
    def _merge_descriptions(self, descriptions: List[str]) -> str:
        """合并多个描述"""
        if not descriptions:
            return ""
        
        # 去重并合并
        unique_descriptions = list(set(desc.strip() for desc in descriptions if desc.strip()))
        
        if len(unique_descriptions) == 1:
            return unique_descriptions[0]
        elif len(unique_descriptions) > 1:
            return "; ".join(unique_descriptions)
        else:
            return ""


# 全局合并器实例
schema_merger = SchemaMerger()
