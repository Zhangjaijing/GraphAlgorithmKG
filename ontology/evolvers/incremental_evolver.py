"""
增量Schema演化器

在现有Schema基础上发现新概念并进行增量更新
"""

from typing import List, Dict, Set, Tuple, Optional
from dataclasses import dataclass
from collections import Counter
import logging

from ..schemas.base_schema import Schema, EntityType, RelationType
from ..interactions.confirmation_manager import ConfirmationManager


@dataclass
class NewConcept:
    """新发现的概念"""
    name: str
    concept_type: str  # 'entity' or 'relation'
    confidence: float
    evidence: List[str]  # 支持证据
    suggested_category: str = None
    source_type: str = None  # 对于关系类型
    target_type: str = None  # 对于关系类型


@dataclass
class EvolutionResult:
    """演化结果"""
    evolved_schema: Schema
    new_concepts: List[NewConcept]
    confirmed_concepts: List[NewConcept]
    rejected_concepts: List[NewConcept]
    evolution_summary: str


class IncrementalEvolver:
    """增量Schema演化器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.confirmation_manager = ConfirmationManager()
        self.logger = logging.getLogger(__name__)
        
        # 配置参数
        self.min_concept_frequency = self.config.get('min_concept_frequency', 3)
        self.confidence_threshold = self.config.get('confidence_threshold', 0.7)
        self.max_new_concepts_per_session = self.config.get('max_new_concepts_per_session', 10)
    
    def evolve_schema(self, base_schema: Schema, new_content: List[str], 
                     auto_confirm: bool = False) -> EvolutionResult:
        """
        演化Schema
        
        Args:
            base_schema: 基础Schema
            new_content: 新的文档内容
            auto_confirm: 是否自动确认新概念
            
        Returns:
            EvolutionResult: 演化结果
        """
        # 1. 检测新概念
        new_concepts = self._detect_new_concepts(base_schema, new_content)
        
        # 2. 过滤和排序新概念
        filtered_concepts = self._filter_and_rank_concepts(new_concepts)
        
        # 3. 用户确认（如果需要）
        if auto_confirm:
            confirmed_concepts = filtered_concepts
            rejected_concepts = []
        else:
            confirmed_concepts, rejected_concepts = self._get_user_confirmation(
                filtered_concepts
            )
        
        # 4. 更新Schema
        evolved_schema = self._integrate_new_concepts(base_schema, confirmed_concepts)
        
        # 5. 生成演化摘要
        summary = self._generate_evolution_summary(
            len(confirmed_concepts), len(rejected_concepts)
        )
        
        return EvolutionResult(
            evolved_schema=evolved_schema,
            new_concepts=new_concepts,
            confirmed_concepts=confirmed_concepts,
            rejected_concepts=rejected_concepts,
            evolution_summary=summary
        )
    
    def _detect_new_concepts(self, base_schema: Schema, content: List[str]) -> List[NewConcept]:
        """检测新概念"""
        new_concepts = []
        
        # 获取现有概念
        existing_entities = {et.name.lower() for et in base_schema.entity_types}
        existing_relations = {rt.name.lower() for rt in base_schema.relation_types}
        
        # 合并所有内容
        all_text = ' '.join(content)
        
        # 检测新实体类型
        new_entities = self._detect_new_entities(all_text, existing_entities)
        new_concepts.extend(new_entities)
        
        # 检测新关系类型
        new_relations = self._detect_new_relations(all_text, existing_relations)
        new_concepts.extend(new_relations)
        
        return new_concepts
    
    def _detect_new_entities(self, text: str, existing_entities: Set[str]) -> List[NewConcept]:
        """检测新实体类型"""
        import re
        
        # 提取可能的实体概念
        # 1. 大写开头的名词短语
        entity_candidates = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        # 2. 技术术语模式
        tech_patterns = [
            r'\b\w+算法\b', r'\b\w+模型\b', r'\b\w+方法\b',
            r'\b\w+系统\b', r'\b\w+框架\b', r'\b\w+架构\b'
        ]
        for pattern in tech_patterns:
            entity_candidates.extend(re.findall(pattern, text))
        
        # 统计频率
        entity_counts = Counter(entity_candidates)
        
        new_entities = []
        for entity, count in entity_counts.items():
            if (entity.lower() not in existing_entities and 
                count >= self.min_concept_frequency):
                
                confidence = min(0.9, count / 10.0)  # 基于频率计算置信度
                
                new_entities.append(NewConcept(
                    name=entity,
                    concept_type='entity',
                    confidence=confidence,
                    evidence=[f"在文档中出现{count}次"],
                    suggested_category=self._suggest_entity_category(entity)
                ))
        
        return new_entities
    
    def _detect_new_relations(self, text: str, existing_relations: Set[str]) -> List[NewConcept]:
        """检测新关系类型"""
        import re
        
        # 关系模式
        relation_patterns = [
            r'(\w+)\s+(?:是|为|属于)\s+(\w+)',
            r'(\w+)\s+(?:具有|拥有|包含)\s+(\w+)',
            r'(\w+)\s+(?:影响|导致|产生)\s+(\w+)',
            r'(\w+)\s+(?:依赖|基于|使用)\s+(\w+)',
            r'(\w+)\s+(?:优于|劣于|等于)\s+(\w+)'
        ]
        
        relation_candidates = []
        for pattern in relation_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                # 推断关系名称
                relation_name = self._infer_relation_name(pattern, match)
                if relation_name:
                    relation_candidates.append((relation_name, match[0], match[1]))
        
        # 统计和过滤
        relation_counts = Counter([r[0] for r in relation_candidates])
        
        new_relations = []
        for relation, count in relation_counts.items():
            if (relation.lower() not in existing_relations and 
                count >= self.min_concept_frequency):
                
                confidence = min(0.8, count / 8.0)
                
                # 找到这个关系的示例
                examples = [r for r in relation_candidates if r[0] == relation]
                source_types = list(set([ex[1] for ex in examples]))
                target_types = list(set([ex[2] for ex in examples]))
                
                new_relations.append(NewConcept(
                    name=relation,
                    concept_type='relation',
                    confidence=confidence,
                    evidence=[f"发现{count}个实例"],
                    source_type=source_types[0] if source_types else 'Entity',
                    target_type=target_types[0] if target_types else 'Entity'
                ))
        
        return new_relations
    
    def _suggest_entity_category(self, entity: str) -> str:
        """建议实体类别"""
        entity_lower = entity.lower()
        
        if any(keyword in entity_lower for keyword in ['算法', 'algorithm']):
            return 'Algorithm'
        elif any(keyword in entity_lower for keyword in ['模型', 'model']):
            return 'Model'
        elif any(keyword in entity_lower for keyword in ['方法', 'method']):
            return 'Method'
        elif any(keyword in entity_lower for keyword in ['系统', 'system']):
            return 'System'
        else:
            return 'Entity'
    
    def _infer_relation_name(self, pattern: str, match: Tuple[str, str]) -> Optional[str]:
        """从模式推断关系名称"""
        if '是|为|属于' in pattern:
            return 'isA'
        elif '具有|拥有|包含' in pattern:
            return 'has'
        elif '影响|导致|产生' in pattern:
            return 'affects'
        elif '依赖|基于|使用' in pattern:
            return 'dependsOn'
        elif '优于|劣于|等于' in pattern:
            return 'comparedWith'
        return None
    
    def _filter_and_rank_concepts(self, concepts: List[NewConcept]) -> List[NewConcept]:
        """过滤和排序概念"""
        # 按置信度过滤
        filtered = [c for c in concepts if c.confidence >= self.confidence_threshold]
        
        # 按置信度排序
        filtered.sort(key=lambda x: x.confidence, reverse=True)
        
        # 限制数量
        return filtered[:self.max_new_concepts_per_session]
    
    def _get_user_confirmation(self, concepts: List[NewConcept]) -> Tuple[List[NewConcept], List[NewConcept]]:
        """获取用户确认"""
        confirmed = []
        rejected = []
        
        for concept in concepts:
            if self.confirmation_manager.confirm_new_concept(concept):
                confirmed.append(concept)
            else:
                rejected.append(concept)
        
        return confirmed, rejected
    
    def _integrate_new_concepts(self, base_schema: Schema, new_concepts: List[NewConcept]) -> Schema:
        """将新概念集成到Schema中"""
        # 复制现有Schema
        new_entity_types = list(base_schema.entity_types)
        new_relation_types = list(base_schema.relation_types)
        
        # 添加新概念
        for concept in new_concepts:
            if concept.concept_type == 'entity':
                new_entity_types.append(EntityType(
                    name=concept.name,
                    description=f"新发现的{concept.suggested_category}实体"
                ))
            elif concept.concept_type == 'relation':
                new_relation_types.append(RelationType(
                    name=concept.name,
                    description=f"新发现的关系类型",
                    source_type=concept.source_type,
                    target_type=concept.target_type
                ))
        
        # 创建新Schema
        return Schema(
            name=f"{base_schema.name} (演化版)",
            description=f"{base_schema.description} - 已添加{len(new_concepts)}个新概念",
            entity_types=new_entity_types,
            relation_types=new_relation_types
        )
    
    def _generate_evolution_summary(self, confirmed_count: int, rejected_count: int) -> str:
        """生成演化摘要"""
        return f"Schema演化完成：确认{confirmed_count}个新概念，拒绝{rejected_count}个概念"
