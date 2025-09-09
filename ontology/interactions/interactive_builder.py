"""
交互式Schema构建器

支持用户参与的迭代式Schema构建和优化
"""

from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
import logging

from ..schemas.base_schema import Schema, EntityType, RelationType
from .confirmation_manager import ConfirmationManager
from .feedback_collector import FeedbackCollector
from ..discoverers.query_driven_discoverer import QueryDrivenDiscoverer
# 延迟导入避免循环依赖
# from ..evolvers.incremental_evolver import IncrementalEvolver
from ..evolvers.user_feedback_evolver import UserFeedbackEvolver

logger = logging.getLogger(__name__)


@dataclass
class BuildingSession:
    """构建会话"""
    session_id: str
    initial_query: str
    current_schema: Schema
    iteration_count: int = 0
    user_satisfaction: float = 0.0
    build_history: List[Dict] = None
    
    def __post_init__(self):
        if self.build_history is None:
            self.build_history = []


class InteractiveBuilder:
    """交互式Schema构建器"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
        # 初始化组件
        self.confirmation_manager = ConfirmationManager(
            interaction_mode=config.get('interaction_mode', 'cli')
        )
        self.feedback_collector = FeedbackCollector(config)
        self.query_discoverer = QueryDrivenDiscoverer(config)
        # 延迟导入
        from ..evolvers.incremental_evolver import IncrementalEvolver
        self.incremental_evolver = IncrementalEvolver(config)
        self.feedback_evolver = UserFeedbackEvolver(config)
        
        # 配置参数
        self.max_iterations = config.get('max_iterations', 5)
        self.satisfaction_threshold = config.get('satisfaction_threshold', 0.8)
        
        # 当前构建会话
        self.current_session: Optional[BuildingSession] = None
    
    def start_interactive_building(self, user_query: str, documents: List[str],
                                 user_id: str = None) -> str:
        """
        开始交互式Schema构建
        
        Args:
            user_query: 用户查询
            documents: 相关文档
            user_id: 用户ID
            
        Returns:
            str: 会话ID
        """
        import uuid
        session_id = str(uuid.uuid4())
        
        self.logger.info(f"开始交互式Schema构建: {session_id}")
        
        # 1. 初始Schema生成
        initial_schema = self._generate_initial_schema(user_query, documents)
        
        # 2. 创建构建会话
        self.current_session = BuildingSession(
            session_id=session_id,
            initial_query=user_query,
            current_schema=initial_schema
        )
        
        # 3. 开始反馈收集会话
        self.feedback_collector.start_feedback_session(
            schema_name=initial_schema.name,
            user_id=user_id
        )
        
        # 4. 展示初始Schema并收集反馈
        self._present_schema_and_collect_feedback(initial_schema)
        
        return session_id
    
    def continue_building_iteration(self) -> Tuple[Schema, bool]:
        """
        继续构建迭代
        
        Returns:
            Tuple[Schema, bool]: (当前Schema, 是否完成)
        """
        if not self.current_session:
            raise ValueError("没有活动的构建会话")
        
        self.current_session.iteration_count += 1
        
        if self.current_session.iteration_count > self.max_iterations:
            self.logger.info("达到最大迭代次数，结束构建")
            return self.current_session.current_schema, True
        
        # 1. 获取用户反馈
        feedbacks = self.feedback_collector.get_current_session_feedbacks()
        
        if not feedbacks:
            self.logger.info("没有收到用户反馈，结束构建")
            return self.current_session.current_schema, True
        
        # 2. 基于反馈演化Schema
        evolution_result = self.feedback_evolver.evolve_with_feedback(
            self.current_session.current_schema,
            feedbacks
        )
        
        # 3. 更新当前Schema
        self.current_session.current_schema = evolution_result.evolved_schema
        
        # 4. 记录构建历史
        self.current_session.build_history.append({
            'iteration': self.current_session.iteration_count,
            'applied_feedbacks': len(evolution_result.applied_feedbacks),
            'ignored_feedbacks': len(evolution_result.ignored_feedbacks),
            'evolution_summary': evolution_result.evolution_summary
        })
        
        # 5. 检查用户满意度
        satisfaction = self._check_user_satisfaction()
        self.current_session.user_satisfaction = satisfaction
        
        # 6. 决定是否继续
        if satisfaction >= self.satisfaction_threshold:
            self.logger.info(f"用户满意度达到阈值 ({satisfaction:.2f}), 结束构建")
            return self.current_session.current_schema, True
        
        # 7. 展示更新后的Schema并收集新反馈
        self._present_schema_and_collect_feedback(self.current_session.current_schema)
        
        return self.current_session.current_schema, False
    
    def finish_building(self) -> Optional[BuildingSession]:
        """完成构建并返回会话信息"""
        if not self.current_session:
            return None
        
        # 结束反馈收集会话
        self.feedback_collector.end_feedback_session()
        
        session = self.current_session
        self.current_session = None
        
        self.logger.info(f"完成交互式构建: {session.session_id}, "
                        f"迭代{session.iteration_count}次, "
                        f"最终满意度: {session.user_satisfaction:.2f}")
        
        return session
    
    def _generate_initial_schema(self, user_query: str, documents: List[str]) -> Schema:
        """生成初始Schema"""
        from ..discoverers.base_discoverer import DiscoveryContext
        
        context = DiscoveryContext(
            user_query=user_query,
            documents=documents
        )
        
        discovery_result = self.query_discoverer.discover_schema(context)
        return discovery_result.schema
    
    def _present_schema_and_collect_feedback(self, schema: Schema):
        """展示Schema并收集反馈"""
        print(f"\n{'='*60}")
        print(f"📋 当前Schema: {schema.name}")
        print(f"{'='*60}")
        print(f"📝 描述: {schema.description}")
        
        print(f"\n🎯 实体类型 ({len(schema.entity_types)}个):")
        for i, et in enumerate(schema.entity_types, 1):
            print(f"  {i}. {et.name} - {et.description}")
        
        print(f"\n🔗 关系类型 ({len(schema.relation_types)}个):")
        for i, rt in enumerate(schema.relation_types, 1):
            print(f"  {i}. {rt.name} ({rt.source_type} -> {rt.target_type}) - {rt.description}")
        
        # 收集反馈
        self._collect_interactive_feedback(schema)
    
    def _collect_interactive_feedback(self, schema: Schema):
        """交互式收集反馈"""
        print(f"\n💭 请提供反馈 (输入 'done' 完成当前轮次):")
        
        feedback_options = [
            "1. 添加缺失的概念",
            "2. 移除冗余的概念", 
            "3. 修正错误的关系",
            "4. 改进概念分类",
            "5. 改进描述",
            "6. 完成反馈"
        ]
        
        for option in feedback_options:
            print(f"  {option}")
        
        while True:
            try:
                choice = input("\n请选择反馈类型 (1-6): ").strip()
                
                if choice == '6' or choice.lower() == 'done':
                    break
                elif choice == '1':
                    self._collect_missing_concept_feedback()
                elif choice == '2':
                    self._collect_redundant_concept_feedback(schema)
                elif choice == '3':
                    self._collect_relation_feedback(schema)
                elif choice == '4':
                    self._collect_classification_feedback(schema)
                elif choice == '5':
                    self._collect_description_feedback(schema)
                else:
                    print("请输入有效的选项 (1-6)")
                    
            except KeyboardInterrupt:
                print("\n用户中断反馈收集")
                break
            except Exception as e:
                print(f"反馈收集错误: {e}")
    
    def _collect_missing_concept_feedback(self):
        """收集缺失概念反馈"""
        concept_name = input("请输入缺失的概念名称: ").strip()
        if not concept_name:
            return
        
        description = input("请描述为什么需要这个概念: ").strip()
        suggested_change = input("建议的概念定义 (可选): ").strip()
        
        self.feedback_collector.collect_missing_concept_feedback(
            concept_name=concept_name,
            description=description,
            suggested_change=suggested_change if suggested_change else None
        )
        
        print(f"✅ 已记录缺失概念反馈: {concept_name}")
    
    def _collect_redundant_concept_feedback(self, schema: Schema):
        """收集冗余概念反馈"""
        print("当前概念列表:")
        all_concepts = [et.name for et in schema.entity_types] + [rt.name for rt in schema.relation_types]
        
        for i, concept in enumerate(all_concepts, 1):
            print(f"  {i}. {concept}")
        
        try:
            choice = int(input("请选择要移除的概念编号: ").strip()) - 1
            if 0 <= choice < len(all_concepts):
                concept_name = all_concepts[choice]
                description = input("请说明为什么这个概念是冗余的: ").strip()
                
                self.feedback_collector.collect_redundant_concept_feedback(
                    concept_name=concept_name,
                    description=description
                )
                
                print(f"✅ 已记录冗余概念反馈: {concept_name}")
            else:
                print("无效的选择")
        except ValueError:
            print("请输入有效的数字")
    
    def _collect_relation_feedback(self, schema: Schema):
        """收集关系反馈"""
        if not schema.relation_types:
            print("当前Schema没有关系类型")
            return
        
        print("当前关系列表:")
        for i, rt in enumerate(schema.relation_types, 1):
            print(f"  {i}. {rt.name} ({rt.source_type} -> {rt.target_type})")
        
        try:
            choice = int(input("请选择要修正的关系编号: ").strip()) - 1
            if 0 <= choice < len(schema.relation_types):
                relation = schema.relation_types[choice]
                description = input("请描述关系的问题: ").strip()
                suggested_change = input("建议的修正 (JSON格式, 可选): ").strip()
                
                self.feedback_collector.collect_incorrect_relation_feedback(
                    relation_name=relation.name,
                    description=description,
                    suggested_change=suggested_change if suggested_change else None
                )
                
                print(f"✅ 已记录关系反馈: {relation.name}")
            else:
                print("无效的选择")
        except ValueError:
            print("请输入有效的数字")
    
    def _collect_classification_feedback(self, schema: Schema):
        """收集分类反馈"""
        if not schema.entity_types:
            print("当前Schema没有实体类型")
            return
        
        print("当前实体类型:")
        for i, et in enumerate(schema.entity_types, 1):
            print(f"  {i}. {et.name} - {et.description}")
        
        try:
            choice = int(input("请选择要重新分类的实体编号: ").strip()) - 1
            if 0 <= choice < len(schema.entity_types):
                entity = schema.entity_types[choice]
                description = input("请描述分类问题: ").strip()
                suggested_change = input("建议的新分类描述: ").strip()
                
                self.feedback_collector.collect_classification_feedback(
                    entity_name=entity.name,
                    description=description,
                    suggested_change=suggested_change if suggested_change else None
                )
                
                print(f"✅ 已记录分类反馈: {entity.name}")
            else:
                print("无效的选择")
        except ValueError:
            print("请输入有效的数字")
    
    def _collect_description_feedback(self, schema: Schema):
        """收集描述反馈"""
        all_concepts = [(et.name, et.description) for et in schema.entity_types] + \
                      [(rt.name, rt.description) for rt in schema.relation_types]
        
        print("当前概念及描述:")
        for i, (name, desc) in enumerate(all_concepts, 1):
            print(f"  {i}. {name} - {desc}")
        
        try:
            choice = int(input("请选择要改进描述的概念编号: ").strip()) - 1
            if 0 <= choice < len(all_concepts):
                concept_name = all_concepts[choice][0]
                description = input("请说明描述的问题: ").strip()
                suggested_change = input("建议的新描述: ").strip()
                
                self.feedback_collector.collect_description_feedback(
                    concept_name=concept_name,
                    description=description,
                    suggested_change=suggested_change if suggested_change else None
                )
                
                print(f"✅ 已记录描述反馈: {concept_name}")
            else:
                print("无效的选择")
        except ValueError:
            print("请输入有效的数字")
    
    def _check_user_satisfaction(self) -> float:
        """检查用户满意度"""
        try:
            satisfaction = float(input("\n请评价当前Schema的满意度 (0-1, 1为完全满意): ").strip())
            return max(0.0, min(1.0, satisfaction))
        except ValueError:
            print("输入无效，使用默认满意度 0.5")
            return 0.5
    
    def get_building_progress(self) -> Dict[str, Any]:
        """获取构建进度"""
        if not self.current_session:
            return {}
        
        return {
            'session_id': self.current_session.session_id,
            'iteration_count': self.current_session.iteration_count,
            'user_satisfaction': self.current_session.user_satisfaction,
            'schema_name': self.current_session.current_schema.name,
            'entity_count': len(self.current_session.current_schema.entity_types),
            'relation_count': len(self.current_session.current_schema.relation_types),
            'build_history': self.current_session.build_history
        }
