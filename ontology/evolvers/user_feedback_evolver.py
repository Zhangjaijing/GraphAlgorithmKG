"""
用户反馈驱动的Schema演化器

基于用户反馈持续优化Schema结构
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import json

from ..schemas.base_schema import Schema, EntityType, RelationType

logger = logging.getLogger(__name__)


class FeedbackType(Enum):
    """反馈类型"""
    CONCEPT_MISSING = "concept_missing"
    CONCEPT_REDUNDANT = "concept_redundant"
    RELATION_INCORRECT = "relation_incorrect"
    CLASSIFICATION_WRONG = "classification_wrong"
    DESCRIPTION_UNCLEAR = "description_unclear"


@dataclass
class UserFeedback:
    """用户反馈"""
    feedback_id: str
    feedback_type: FeedbackType
    concept_name: str
    description: str
    suggested_change: Optional[str] = None
    confidence: float = 1.0
    timestamp: str = None
    user_id: str = None


@dataclass
class FeedbackEvolutionResult:
    """反馈演化结果"""
    evolved_schema: Schema
    applied_feedbacks: List[UserFeedback]
    ignored_feedbacks: List[UserFeedback]
    evolution_summary: str


class UserFeedbackEvolver:
    """用户反馈驱动的Schema演化器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 配置参数
        self.min_feedback_confidence = config.get('min_feedback_confidence', 0.5)
        self.max_feedbacks_per_evolution = config.get('max_feedbacks_per_evolution', 20)
        
        # 反馈历史
        self.feedback_history: List[UserFeedback] = []
    
    def evolve_with_feedback(self, base_schema: Schema, 
                           feedbacks: List[UserFeedback]) -> FeedbackEvolutionResult:
        """
        基于用户反馈演化Schema
        
        Args:
            base_schema: 基础Schema
            feedbacks: 用户反馈列表
            
        Returns:
            FeedbackEvolutionResult: 演化结果
        """
        # 1. 过滤和排序反馈
        valid_feedbacks = self._filter_feedbacks(feedbacks)
        
        # 2. 应用反馈
        evolved_schema = self._apply_feedbacks(base_schema, valid_feedbacks)
        
        # 3. 分类处理结果
        applied_feedbacks = []
        ignored_feedbacks = []
        
        for feedback in valid_feedbacks:
            if self._is_feedback_applied(feedback, base_schema, evolved_schema):
                applied_feedbacks.append(feedback)
            else:
                ignored_feedbacks.append(feedback)
        
        # 4. 更新历史
        self.feedback_history.extend(applied_feedbacks)
        
        # 5. 生成摘要
        summary = self._generate_evolution_summary(applied_feedbacks, ignored_feedbacks)
        
        return FeedbackEvolutionResult(
            evolved_schema=evolved_schema,
            applied_feedbacks=applied_feedbacks,
            ignored_feedbacks=ignored_feedbacks,
            evolution_summary=summary
        )
    
    def _filter_feedbacks(self, feedbacks: List[UserFeedback]) -> List[UserFeedback]:
        """过滤和排序反馈"""
        # 过滤低置信度反馈
        valid_feedbacks = [
            fb for fb in feedbacks 
            if fb.confidence >= self.min_feedback_confidence
        ]
        
        # 按置信度排序
        valid_feedbacks.sort(key=lambda x: x.confidence, reverse=True)
        
        # 限制数量
        return valid_feedbacks[:self.max_feedbacks_per_evolution]
    
    def _apply_feedbacks(self, base_schema: Schema, feedbacks: List[UserFeedback]) -> Schema:
        """应用反馈到Schema"""
        # 复制Schema
        new_entity_types = list(base_schema.entity_types)
        new_relation_types = list(base_schema.relation_types)
        
        for feedback in feedbacks:
            try:
                if feedback.feedback_type == FeedbackType.CONCEPT_MISSING:
                    self._add_missing_concept(feedback, new_entity_types, new_relation_types)
                
                elif feedback.feedback_type == FeedbackType.CONCEPT_REDUNDANT:
                    self._remove_redundant_concept(feedback, new_entity_types, new_relation_types)
                
                elif feedback.feedback_type == FeedbackType.RELATION_INCORRECT:
                    self._fix_incorrect_relation(feedback, new_relation_types)
                
                elif feedback.feedback_type == FeedbackType.CLASSIFICATION_WRONG:
                    self._fix_classification(feedback, new_entity_types)
                
                elif feedback.feedback_type == FeedbackType.DESCRIPTION_UNCLEAR:
                    self._improve_description(feedback, new_entity_types, new_relation_types)
                
            except Exception as e:
                self.logger.warning(f"应用反馈失败 {feedback.feedback_id}: {e}")
        
        return Schema(
            name=f"{base_schema.name} (用户反馈优化版)",
            description=f"{base_schema.description} - 基于用户反馈优化",
            entity_types=new_entity_types,
            relation_types=new_relation_types
        )
    
    def _add_missing_concept(self, feedback: UserFeedback, 
                           entity_types: List[EntityType], 
                           relation_types: List[RelationType]):
        """添加缺失概念"""
        concept_name = feedback.concept_name
        
        # 检查是否已存在
        if any(et.name == concept_name for et in entity_types):
            return
        
        # 根据建议的变更添加概念
        if feedback.suggested_change:
            try:
                change_data = json.loads(feedback.suggested_change)
                if change_data.get('type') == 'entity':
                    entity_types.append(EntityType(
                        name=concept_name,
                        description=change_data.get('description', f"用户建议添加的{concept_name}实体")
                    ))
                elif change_data.get('type') == 'relation':
                    relation_types.append(RelationType(
                        name=concept_name,
                        description=change_data.get('description', f"用户建议添加的{concept_name}关系"),
                        source_type=change_data.get('source_type', 'Entity'),
                        target_type=change_data.get('target_type', 'Entity')
                    ))
            except json.JSONDecodeError:
                # 如果不是JSON格式，默认添加为实体
                entity_types.append(EntityType(
                    name=concept_name,
                    description=feedback.description
                ))
    
    def _remove_redundant_concept(self, feedback: UserFeedback,
                                entity_types: List[EntityType],
                                relation_types: List[RelationType]):
        """移除冗余概念"""
        concept_name = feedback.concept_name
        
        # 从实体类型中移除
        entity_types[:] = [et for et in entity_types if et.name != concept_name]
        
        # 从关系类型中移除
        relation_types[:] = [rt for rt in relation_types if rt.name != concept_name]
    
    def _fix_incorrect_relation(self, feedback: UserFeedback,
                              relation_types: List[RelationType]):
        """修正错误关系"""
        relation_name = feedback.concept_name
        
        for rt in relation_types:
            if rt.name == relation_name:
                if feedback.suggested_change:
                    try:
                        change_data = json.loads(feedback.suggested_change)
                        rt.description = change_data.get('description', rt.description)
                        rt.source_type = change_data.get('source_type', rt.source_type)
                        rt.target_type = change_data.get('target_type', rt.target_type)
                    except json.JSONDecodeError:
                        rt.description = feedback.description
                break
    
    def _fix_classification(self, feedback: UserFeedback,
                          entity_types: List[EntityType]):
        """修正分类错误"""
        entity_name = feedback.concept_name
        
        for et in entity_types:
            if et.name == entity_name:
                if feedback.suggested_change:
                    et.description = feedback.suggested_change
                else:
                    et.description = feedback.description
                break
    
    def _improve_description(self, feedback: UserFeedback,
                           entity_types: List[EntityType],
                           relation_types: List[RelationType]):
        """改进描述"""
        concept_name = feedback.concept_name
        
        # 更新实体描述
        for et in entity_types:
            if et.name == concept_name:
                et.description = feedback.suggested_change or feedback.description
                return
        
        # 更新关系描述
        for rt in relation_types:
            if rt.name == concept_name:
                rt.description = feedback.suggested_change or feedback.description
                return
    
    def _is_feedback_applied(self, feedback: UserFeedback, 
                           old_schema: Schema, new_schema: Schema) -> bool:
        """检查反馈是否被应用"""
        concept_name = feedback.concept_name
        
        if feedback.feedback_type == FeedbackType.CONCEPT_MISSING:
            # 检查概念是否被添加
            old_has = any(et.name == concept_name for et in old_schema.entity_types) or \
                     any(rt.name == concept_name for rt in old_schema.relation_types)
            new_has = any(et.name == concept_name for et in new_schema.entity_types) or \
                     any(rt.name == concept_name for rt in new_schema.relation_types)
            return not old_has and new_has
        
        elif feedback.feedback_type == FeedbackType.CONCEPT_REDUNDANT:
            # 检查概念是否被移除
            old_has = any(et.name == concept_name for et in old_schema.entity_types) or \
                     any(rt.name == concept_name for rt in old_schema.relation_types)
            new_has = any(et.name == concept_name for et in new_schema.entity_types) or \
                     any(rt.name == concept_name for rt in new_schema.relation_types)
            return old_has and not new_has
        
        else:
            # 对于其他类型的反馈，简单检查Schema是否有变化
            return len(new_schema.entity_types) != len(old_schema.entity_types) or \
                   len(new_schema.relation_types) != len(old_schema.relation_types)
    
    def _generate_evolution_summary(self, applied: List[UserFeedback], 
                                  ignored: List[UserFeedback]) -> str:
        """生成演化摘要"""
        summary_parts = []
        
        if applied:
            summary_parts.append(f"应用了{len(applied)}个用户反馈")
            
            # 按类型统计
            from collections import Counter
            type_counts = Counter([fb.feedback_type.value for fb in applied])
            for feedback_type, count in type_counts.items():
                type_name = {
                    'concept_missing': '添加缺失概念',
                    'concept_redundant': '移除冗余概念',
                    'relation_incorrect': '修正错误关系',
                    'classification_wrong': '修正分类错误',
                    'description_unclear': '改进描述'
                }.get(feedback_type, feedback_type)
                
                summary_parts.append(f"{type_name}: {count}个")
        
        if ignored:
            summary_parts.append(f"忽略了{len(ignored)}个低置信度反馈")
        
        return "，".join(summary_parts) if summary_parts else "未应用任何反馈"
    
    def get_feedback_statistics(self) -> Dict[str, int]:
        """获取反馈统计"""
        from collections import Counter
        
        type_counts = Counter([fb.feedback_type.value for fb in self.feedback_history])
        return dict(type_counts)
    
    def export_feedback_history(self, filepath: str):
        """导出反馈历史"""
        data = {
            'feedbacks': [
                {
                    'feedback_id': fb.feedback_id,
                    'feedback_type': fb.feedback_type.value,
                    'concept_name': fb.concept_name,
                    'description': fb.description,
                    'suggested_change': fb.suggested_change,
                    'confidence': fb.confidence,
                    'timestamp': fb.timestamp,
                    'user_id': fb.user_id
                }
                for fb in self.feedback_history
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"反馈历史已导出到: {filepath}")
