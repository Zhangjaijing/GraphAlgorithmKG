"""
反馈收集器

收集和管理用户对Schema的各种反馈
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict
import uuid
import time
import json
import logging

from ..evolvers.user_feedback_evolver import UserFeedback, FeedbackType

logger = logging.getLogger(__name__)


@dataclass
class FeedbackSession:
    """反馈会话"""
    session_id: str
    schema_name: str
    start_time: str
    end_time: Optional[str] = None
    feedbacks: List[UserFeedback] = None
    user_id: Optional[str] = None
    
    def __post_init__(self):
        if self.feedbacks is None:
            self.feedbacks = []


class FeedbackCollector:
    """反馈收集器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 当前会话
        self.current_session: Optional[FeedbackSession] = None
        
        # 历史会话
        self.sessions: List[FeedbackSession] = []
        
        # 配置参数
        self.auto_save = config.get('auto_save', True)
        self.save_path = config.get('save_path', 'feedback_data/')
    
    def start_feedback_session(self, schema_name: str, user_id: str = None) -> str:
        """
        开始反馈会话
        
        Args:
            schema_name: Schema名称
            user_id: 用户ID（可选）
            
        Returns:
            str: 会话ID
        """
        session_id = str(uuid.uuid4())
        
        self.current_session = FeedbackSession(
            session_id=session_id,
            schema_name=schema_name,
            start_time=str(time.time()),
            user_id=user_id
        )
        
        self.logger.info(f"开始反馈会话: {session_id} for schema: {schema_name}")
        return session_id
    
    def collect_missing_concept_feedback(self, concept_name: str, description: str,
                                       suggested_change: str = None,
                                       confidence: float = 1.0) -> str:
        """收集缺失概念反馈"""
        return self._add_feedback(
            feedback_type=FeedbackType.CONCEPT_MISSING,
            concept_name=concept_name,
            description=description,
            suggested_change=suggested_change,
            confidence=confidence
        )
    
    def collect_redundant_concept_feedback(self, concept_name: str, description: str,
                                         confidence: float = 1.0) -> str:
        """收集冗余概念反馈"""
        return self._add_feedback(
            feedback_type=FeedbackType.CONCEPT_REDUNDANT,
            concept_name=concept_name,
            description=description,
            confidence=confidence
        )
    
    def collect_incorrect_relation_feedback(self, relation_name: str, description: str,
                                          suggested_change: str = None,
                                          confidence: float = 1.0) -> str:
        """收集错误关系反馈"""
        return self._add_feedback(
            feedback_type=FeedbackType.RELATION_INCORRECT,
            concept_name=relation_name,
            description=description,
            suggested_change=suggested_change,
            confidence=confidence
        )
    
    def collect_classification_feedback(self, entity_name: str, description: str,
                                      suggested_change: str = None,
                                      confidence: float = 1.0) -> str:
        """收集分类错误反馈"""
        return self._add_feedback(
            feedback_type=FeedbackType.CLASSIFICATION_WRONG,
            concept_name=entity_name,
            description=description,
            suggested_change=suggested_change,
            confidence=confidence
        )
    
    def collect_description_feedback(self, concept_name: str, description: str,
                                   suggested_change: str = None,
                                   confidence: float = 1.0) -> str:
        """收集描述改进反馈"""
        return self._add_feedback(
            feedback_type=FeedbackType.DESCRIPTION_UNCLEAR,
            concept_name=concept_name,
            description=description,
            suggested_change=suggested_change,
            confidence=confidence
        )
    
    def collect_custom_feedback(self, feedback_type: str, concept_name: str,
                              description: str, suggested_change: str = None,
                              confidence: float = 1.0) -> str:
        """收集自定义反馈"""
        # 尝试转换为已知的反馈类型
        try:
            fb_type = FeedbackType(feedback_type)
        except ValueError:
            # 如果不是已知类型，使用描述改进作为默认
            fb_type = FeedbackType.DESCRIPTION_UNCLEAR
            self.logger.warning(f"未知反馈类型: {feedback_type}, 使用默认类型")
        
        return self._add_feedback(
            feedback_type=fb_type,
            concept_name=concept_name,
            description=description,
            suggested_change=suggested_change,
            confidence=confidence
        )
    
    def _add_feedback(self, feedback_type: FeedbackType, concept_name: str,
                     description: str, suggested_change: str = None,
                     confidence: float = 1.0) -> str:
        """添加反馈到当前会话"""
        if not self.current_session:
            raise ValueError("没有活动的反馈会话，请先调用start_feedback_session()")
        
        feedback_id = str(uuid.uuid4())
        
        feedback = UserFeedback(
            feedback_id=feedback_id,
            feedback_type=feedback_type,
            concept_name=concept_name,
            description=description,
            suggested_change=suggested_change,
            confidence=confidence,
            timestamp=str(time.time()),
            user_id=self.current_session.user_id
        )
        
        self.current_session.feedbacks.append(feedback)
        
        self.logger.info(f"收集反馈: {feedback_type.value} for {concept_name}")
        
        # 自动保存
        if self.auto_save:
            self._auto_save_session()
        
        return feedback_id
    
    def end_feedback_session(self) -> Optional[FeedbackSession]:
        """结束当前反馈会话"""
        if not self.current_session:
            self.logger.warning("没有活动的反馈会话")
            return None
        
        self.current_session.end_time = str(time.time())
        
        # 保存到历史
        self.sessions.append(self.current_session)
        
        session = self.current_session
        self.current_session = None
        
        self.logger.info(f"结束反馈会话: {session.session_id}, "
                        f"收集了{len(session.feedbacks)}个反馈")
        
        return session
    
    def get_current_session_feedbacks(self) -> List[UserFeedback]:
        """获取当前会话的反馈"""
        if not self.current_session:
            return []
        return self.current_session.feedbacks.copy()
    
    def get_session_by_id(self, session_id: str) -> Optional[FeedbackSession]:
        """根据ID获取会话"""
        for session in self.sessions:
            if session.session_id == session_id:
                return session
        
        if self.current_session and self.current_session.session_id == session_id:
            return self.current_session
        
        return None
    
    def get_all_feedbacks(self) -> List[UserFeedback]:
        """获取所有反馈"""
        all_feedbacks = []
        
        # 历史会话的反馈
        for session in self.sessions:
            all_feedbacks.extend(session.feedbacks)
        
        # 当前会话的反馈
        if self.current_session:
            all_feedbacks.extend(self.current_session.feedbacks)
        
        return all_feedbacks
    
    def get_feedbacks_by_schema(self, schema_name: str) -> List[UserFeedback]:
        """获取特定Schema的反馈"""
        feedbacks = []
        
        for session in self.sessions:
            if session.schema_name == schema_name:
                feedbacks.extend(session.feedbacks)
        
        if (self.current_session and 
            self.current_session.schema_name == schema_name):
            feedbacks.extend(self.current_session.feedbacks)
        
        return feedbacks
    
    def get_feedback_statistics(self) -> Dict[str, Any]:
        """获取反馈统计"""
        all_feedbacks = self.get_all_feedbacks()
        
        from collections import Counter
        
        stats = {
            'total_feedbacks': len(all_feedbacks),
            'total_sessions': len(self.sessions) + (1 if self.current_session else 0),
            'feedback_types': dict(Counter([fb.feedback_type.value for fb in all_feedbacks])),
            'schemas': dict(Counter([session.schema_name for session in self.sessions])),
            'average_confidence': sum(fb.confidence for fb in all_feedbacks) / len(all_feedbacks) if all_feedbacks else 0
        }
        
        return stats
    
    def export_feedbacks(self, filepath: str, schema_name: str = None):
        """导出反馈数据"""
        if schema_name:
            feedbacks = self.get_feedbacks_by_schema(schema_name)
            sessions = [s for s in self.sessions if s.schema_name == schema_name]
        else:
            feedbacks = self.get_all_feedbacks()
            sessions = self.sessions.copy()
            if self.current_session:
                sessions.append(self.current_session)
        
        data = {
            'export_time': str(time.time()),
            'schema_filter': schema_name,
            'sessions': [asdict(session) for session in sessions],
            'feedbacks': [asdict(fb) for fb in feedbacks],
            'statistics': self.get_feedback_statistics()
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"反馈数据已导出到: {filepath}")
    
    def _auto_save_session(self):
        """自动保存当前会话"""
        if not self.current_session:
            return
        
        try:
            import os
            os.makedirs(self.save_path, exist_ok=True)
            
            filepath = f"{self.save_path}/session_{self.current_session.session_id}.json"
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.current_session), f, ensure_ascii=False, indent=2)
                
        except Exception as e:
            self.logger.error(f"自动保存会话失败: {e}")
    
    def clear_all_data(self):
        """清空所有数据"""
        self.current_session = None
        self.sessions.clear()
        self.logger.info("所有反馈数据已清空")
