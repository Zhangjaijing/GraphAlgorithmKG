"""
Schema演化器模块

提供Schema动态演化功能：
- 增量演化：在现有Schema基础上发现新概念
- 概念漂移检测：检测领域概念的变化
- 用户反馈演化：基于用户反馈优化Schema
"""

from .incremental_evolver import IncrementalEvolver
from .concept_drift_detector import ConceptDriftDetector
from .user_feedback_evolver import UserFeedbackEvolver

__all__ = [
    'IncrementalEvolver',
    'ConceptDriftDetector', 
    'UserFeedbackEvolver'
]
