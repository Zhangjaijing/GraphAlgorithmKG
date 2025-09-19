"""
确认管理器

管理用户对新概念、Schema变更等的确认流程
"""

from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class ConfirmationRequest:
    """确认请求"""
    id: str
    type: str  # 'new_concept', 'schema_merge', 'concept_removal'
    title: str
    description: str
    options: List[str]
    default_option: str = None
    metadata: Dict[str, Any] = None


@dataclass
class ConfirmationResponse:
    """确认响应"""
    request_id: str
    selected_option: str
    user_feedback: str = None
    timestamp: str = None


class ConfirmationManager:
    """确认管理器"""
    
    def __init__(self, interaction_mode: str = 'cli'):
        """
        初始化确认管理器
        
        Args:
            interaction_mode: 交互模式 ('cli', 'web', 'auto')
        """
        self.interaction_mode = interaction_mode
        self.pending_requests: Dict[str, ConfirmationRequest] = {}
        self.responses: List[ConfirmationResponse] = []
        self.logger = logging.getLogger(__name__)
    
    def confirm_new_concept(self, concept) -> bool:
        """确认新概念"""
        if self.interaction_mode == 'auto':
            return concept.confidence > 0.8
        
        request = ConfirmationRequest(
            id=f"concept_{concept.name}",
            type='new_concept',
            title=f"发现新概念: {concept.name}",
            description=f"""
概念名称: {concept.name}
概念类型: {concept.concept_type}
置信度: {concept.confidence:.2f}
证据: {', '.join(concept.evidence)}
建议分类: {getattr(concept, 'suggested_category', 'N/A')}
            """.strip(),
            options=['确认添加', '拒绝', '修改后添加'],
            default_option='确认添加'
        )
        
        response = self._get_user_response(request)
        return response.selected_option == '确认添加'
    
    def confirm_schema_merge(self, source_schema, target_schema, conflicts: List) -> Dict[str, str]:
        """确认Schema合并"""
        if self.interaction_mode == 'auto':
            # 自动解决：选择置信度更高的选项
            return {conflict.id: conflict.options[0] for conflict in conflicts}
        
        resolutions = {}
        for conflict in conflicts:
            request = ConfirmationRequest(
                id=f"merge_conflict_{conflict.id}",
                type='schema_merge',
                title=f"Schema合并冲突: {conflict.description}",
                description=f"""
源Schema: {source_schema.name}
目标Schema: {target_schema.name}
冲突详情: {conflict.details}
                """.strip(),
                options=conflict.options,
                default_option=conflict.options[0]
            )
            
            response = self._get_user_response(request)
            resolutions[conflict.id] = response.selected_option
        
        return resolutions
    
    def confirm_concept_removal(self, concept_name: str, reason: str) -> bool:
        """确认概念移除"""
        if self.interaction_mode == 'auto':
            return True  # 自动确认移除
        
        request = ConfirmationRequest(
            id=f"remove_{concept_name}",
            type='concept_removal',
            title=f"移除概念: {concept_name}",
            description=f"""
概念名称: {concept_name}
移除原因: {reason}
            """.strip(),
            options=['确认移除', '保留'],
            default_option='确认移除'
        )
        
        response = self._get_user_response(request)
        return response.selected_option == '确认移除'
    
    def _get_user_response(self, request: ConfirmationRequest) -> ConfirmationResponse:
        """获取用户响应"""
        self.pending_requests[request.id] = request
        
        if self.interaction_mode == 'cli':
            return self._cli_interaction(request)
        elif self.interaction_mode == 'web':
            return self._web_interaction(request)
        else:
            # 自动模式，返回默认选项
            return ConfirmationResponse(
                request_id=request.id,
                selected_option=request.default_option or request.options[0]
            )
    
    def _cli_interaction(self, request: ConfirmationRequest) -> ConfirmationResponse:
        """命令行交互"""
        print(f"\n{'='*50}")
        print(f"🤔 {request.title}")
        print(f"{'='*50}")
        print(request.description)
        print(f"\n选项:")
        
        for i, option in enumerate(request.options, 1):
            marker = " (默认)" if option == request.default_option else ""
            print(f"  {i}. {option}{marker}")
        
        while True:
            try:
                user_input = input(f"\n请选择 (1-{len(request.options)}) 或按回车选择默认: ").strip()
                
                if not user_input and request.default_option:
                    selected_option = request.default_option
                    break
                elif user_input.isdigit():
                    choice_idx = int(user_input) - 1
                    if 0 <= choice_idx < len(request.options):
                        selected_option = request.options[choice_idx]
                        break
                    else:
                        print(f"请输入 1-{len(request.options)} 之间的数字")
                else:
                    print("请输入有效的数字")
                    
            except KeyboardInterrupt:
                print("\n用户取消操作")
                selected_option = request.options[-1]  # 选择最后一个选项（通常是取消/拒绝）
                break
            except Exception as e:
                print(f"输入错误: {e}")
        
        # 询问额外反馈
        feedback = input("额外反馈 (可选): ").strip()
        
        response = ConfirmationResponse(
            request_id=request.id,
            selected_option=selected_option,
            user_feedback=feedback if feedback else None
        )
        
        self.responses.append(response)
        return response
    
    def _web_interaction(self, request: ConfirmationRequest) -> ConfirmationResponse:
        """Web界面交互（占位符实现）"""
        # 这里应该实现Web界面交互逻辑
        # 目前返回默认选项
        self.logger.warning("Web交互模式尚未实现，使用默认选项")
        
        return ConfirmationResponse(
            request_id=request.id,
            selected_option=request.default_option or request.options[0]
        )
    
    def get_confirmation_history(self) -> List[ConfirmationResponse]:
        """获取确认历史"""
        return self.responses.copy()
    
    def export_confirmations(self, filepath: str):
        """导出确认记录"""
        data = {
            'responses': [
                {
                    'request_id': r.request_id,
                    'selected_option': r.selected_option,
                    'user_feedback': r.user_feedback,
                    'timestamp': r.timestamp
                }
                for r in self.responses
            ]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        self.logger.info(f"确认记录已导出到: {filepath}")
    
    def set_interaction_mode(self, mode: str):
        """设置交互模式"""
        if mode not in ['cli', 'web', 'auto']:
            raise ValueError("交互模式必须是 'cli', 'web', 或 'auto'")
        
        self.interaction_mode = mode
        self.logger.info(f"交互模式已设置为: {mode}")
