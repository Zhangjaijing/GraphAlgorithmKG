"""
用户交互管理模块

提供用户交互功能：
- 反馈收集：收集用户对Schema的反馈
- 确认管理：管理用户对新概念的确认
- 交互式构建：支持交互式Schema构建
"""

from .feedback_collector import FeedbackCollector
from .confirmation_manager import ConfirmationManager
from .interactive_builder import InteractiveBuilder

__all__ = [
    'FeedbackCollector',
    'ConfirmationManager',
    'InteractiveBuilder'
]
