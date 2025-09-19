"""
增强版Schema检测器

在原有Schema检测功能基础上，添加动态Schema发现与演化功能
采用装饰器模式，保持接口兼容性
"""

from typing import List, Optional, Dict, Any
import logging

from .schema_detector import SchemaDetector, SchemaDetectionResult
from ..discoverers.query_driven_discoverer import QueryDrivenDiscoverer
from ..discoverers.base_discoverer import DiscoveryContext
from ..evolvers.incremental_evolver import IncrementalEvolver
from ..interactions.confirmation_manager import ConfirmationManager
from ..schemas.base_schema import Schema
from .schema_version_manager import SchemaVersionManager, SchemaChangeType
from .schema_persistence_manager import SchemaPersistenceManager
from .schema_merger import SchemaMerger

logger = logging.getLogger(__name__)


class EnhancedSchemaDetector:
    """增强版Schema检测器"""
    
    def __init__(self, base_detector: SchemaDetector = None, config: Dict[str, Any] = None):
        """
        初始化增强版检测器
        
        Args:
            base_detector: 基础Schema检测器，如果为None则创建默认实例
            config: 配置参数
        """
        self.base_detector = base_detector or SchemaDetector()
        self.config = config or {}
        
        # 初始化动态发现组件
        self.query_driven_discoverer = QueryDrivenDiscoverer(config)
        self.incremental_evolver = IncrementalEvolver(config)
        self.confirmation_manager = ConfirmationManager(
            interaction_mode=(config or {}).get('interaction_mode', 'cli')
        )

        # 初始化版本管理和持久化组件
        self.version_manager = SchemaVersionManager()
        self.persistence_manager = SchemaPersistenceManager()
        self.schema_merger = SchemaMerger(self.persistence_manager)
        
        # 配置参数
        config = config or {}
        self.enable_dynamic_discovery = config.get('enable_dynamic_discovery', True)
        self.enable_schema_evolution = config.get('enable_schema_evolution', True)
        self.enable_schema_merging = config.get('enable_schema_merging', True)
        self.confidence_threshold = config.get('confidence_threshold', 0.7)
        
        self.logger = logging.getLogger(__name__)
    
    def detect_schema(self, text: str, use_llm: bool = False,
                     user_query: str = None, documents: List[str] = None,
                     config: dict = None) -> List[SchemaDetectionResult]:
        """
        增强版Schema检测
        
        Args:
            text: 待检测文本
            use_llm: 是否使用LLM
            user_query: 用户查询（新增参数，用于动态发现）
            documents: 相关文档列表（新增参数）
            
        Returns:
            List[SchemaDetectionResult]: 检测结果列表
        """
        # 检查是否强制动态发现
        force_dynamic = (config or {}).get('force_dynamic_discovery', False)

        if force_dynamic and user_query and self.enable_dynamic_discovery:
            print("🔍 强制触发动态Schema发现...")
            discovered_schema = self._discover_schema_from_query(user_query, text, documents)

            if discovered_schema:
                # 为动态生成的Schema创建一个虚拟文件名
                virtual_schema_file = f"dynamic_{discovered_schema.name.lower().replace(' ', '_')}.yaml"

                return [SchemaDetectionResult(
                    schema_file=virtual_schema_file,
                    confidence=0.8,
                    evidence=["强制动态Schema生成"],
                    method="forced_query_driven_discovery",
                    schema=discovered_schema
                )]

        # 1. 尝试原有的Schema检测
        results = self.base_detector.detect_schema(text, seed_knowledge=None, use_llm=use_llm)

        # 2. 如果启用动态发现且没有匹配的Schema
        if (self.enable_dynamic_discovery and
            (not results or max(r.confidence for r in results) < self.confidence_threshold) and
            user_query):

            self.logger.info("启动问题驱动Schema发现")
            discovered_schema = self._discover_schema_from_query(user_query, text, documents)
            
            if discovered_schema:
                # 创建临时Schema并获取ID
                temp_schema_id = self.persistence_manager.create_temp_schema(
                    discovered_schema, schema_type="query_driven"
                )

                # 为动态生成的Schema创建一个虚拟文件名
                virtual_schema_file = f"dynamic_{discovered_schema.name.lower().replace(' ', '_')}.yaml"

                results = [SchemaDetectionResult(
                    schema_file=virtual_schema_file,
                    confidence=0.8,
                    evidence=["问题驱动Schema生成", f"临时ID: {temp_schema_id}"],
                    method="query_driven_discovery",
                    schema=discovered_schema
                )]
        
        # 3. 如果启用Schema演化且匹配到Schema但发现新概念
        elif (self.enable_schema_evolution and results and
              hasattr(results[0], 'schema') and results[0].schema and
              self._has_potential_new_concepts(text, results[0].schema)):
            
            self.logger.info("启动Schema增量演化")
            evolved_schema = self._evolve_schema(results[0].schema, [text])
            
            if evolved_schema:
                # 创建演化后的临时Schema
                temp_schema_id = self.persistence_manager.create_temp_schema(
                    evolved_schema, schema_type="evolved"
                )

                results[0] = SchemaDetectionResult(
                    schema_file=evolved_schema.name,
                    confidence=results[0].confidence,
                    evidence=results[0].evidence + ["Schema演化", f"临时ID: {temp_schema_id}"],
                    method=f"{results[0].method}_evolved",
                    schema=evolved_schema
                )
        
        return results
    
    def _discover_schema_from_query(self, user_query: str, text: str, 
                                  documents: List[str] = None) -> Optional[Schema]:
        """从用户查询发现Schema"""
        try:
            context = DiscoveryContext(
                user_query=user_query,
                documents=[text] + (documents or []),
                confidence_threshold=self.confidence_threshold
            )
            
            discovery_result = self.query_driven_discoverer.discover_schema(context)
            
            if discovery_result.requires_user_confirmation:
                # 用户确认
                confirmed = self.confirmation_manager.confirm_new_concept(discovery_result)
                if not confirmed:
                    return None
            
            self.logger.info(f"成功发现Schema: {discovery_result.schema.name}")
            return discovery_result.schema
            
        except Exception as e:
            self.logger.error(f"Schema发现失败: {e}")
            return None
    
    def _evolve_schema(self, base_schema: Schema, content: List[str]) -> Optional[Schema]:
        """演化Schema"""
        try:
            evolution_result = self.incremental_evolver.evolve_schema(
                base_schema, 
                content,
                auto_confirm=self.config.get('auto_confirm_evolution', False)
            )
            
            if evolution_result.confirmed_concepts:
                self.logger.info(f"Schema演化成功: {evolution_result.evolution_summary}")
                return evolution_result.evolved_schema
            else:
                self.logger.info("未发现需要确认的新概念")
                return base_schema
                
        except Exception as e:
            self.logger.error(f"Schema演化失败: {e}")
            return base_schema
    
    def _has_potential_new_concepts(self, text: str, schema: Schema) -> bool:
        """检查是否有潜在的新概念"""
        # 简单的启发式检查
        existing_concepts = set()
        
        # 收集现有概念
        for et in schema.entity_types:
            existing_concepts.add(et.name.lower())
        
        for rt in schema.relation_types:
            existing_concepts.add(rt.name.lower())
        
        # 检查文本中是否有未覆盖的概念
        import re
        potential_concepts = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
        
        for concept in potential_concepts:
            if concept.lower() not in existing_concepts:
                return True
        
        return False
    
    # 保持原有接口的兼容性方法
    def get_available_schemas(self) -> List[str]:
        """获取可用Schema列表（兼容性方法）"""
        return self.base_detector.get_available_schemas()
    
    def load_schema(self, schema_name: str) -> Schema:
        """加载指定Schema（兼容性方法）"""
        return self.base_detector.load_schema(schema_name)

    def merge_schemas(self, schema_ids: List[str], merge_strategy: str = "intelligent") -> Dict[str, Any]:
        """
        合并多个Schema

        Args:
            schema_ids: 要合并的Schema ID列表
            merge_strategy: 合并策略 (intelligent, conservative, aggressive)

        Returns:
            Dict: 合并结果信息
        """
        if not self.enable_schema_merging:
            return {"error": "Schema合并功能未启用"}

        try:
            # 加载Schema对象
            schemas = []
            for schema_id in schema_ids:
                # 尝试从临时Schema中加载
                schema = self.persistence_manager.get_temp_schema(schema_id)
                if not schema:
                    # 尝试从版本管理器中加载最新版本
                    latest_version = self.version_manager.get_latest_version(schema_id)
                    if latest_version:
                        schema = self.version_manager.load_schema_version(
                            schema_id, latest_version.version
                        )

                if schema:
                    schemas.append(schema)
                else:
                    self.logger.warning(f"无法加载Schema: {schema_id}")

            if len(schemas) < 2:
                return {"error": "需要至少2个有效的Schema进行合并"}

            # 执行合并
            merge_result = self.schema_merger.merge_schemas(schemas, merge_strategy)

            return {
                "success": merge_result.success,
                "temp_schema_id": merge_result.temp_schema_id,
                "conflicts": [
                    {
                        "id": c.conflict_id,
                        "type": c.conflict_type.value,
                        "description": c.description,
                        "auto_resolvable": c.auto_resolvable,
                        "confidence": c.confidence
                    }
                    for c in merge_result.conflicts
                ],
                "merge_summary": merge_result.merge_summary
            }

        except Exception as e:
            self.logger.error(f"Schema合并失败: {e}")
            return {"error": str(e)}

    def persist_temp_schema(self, temp_schema_id: str, description: str = "",
                           author: str = "system") -> Dict[str, Any]:
        """
        持久化临时Schema

        Args:
            temp_schema_id: 临时Schema ID
            description: 描述
            author: 作者

        Returns:
            Dict: 持久化结果
        """
        try:
            version = self.persistence_manager.persist_temp_schema(
                temp_schema_id, description, author
            )

            if version:
                return {
                    "success": True,
                    "version": version,
                    "message": f"Schema已持久化为版本 {version}"
                }
            else:
                return {
                    "success": False,
                    "error": "持久化失败"
                }

        except Exception as e:
            self.logger.error(f"持久化失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_schema_version_history(self, schema_id: str) -> List[Dict[str, Any]]:
        """
        获取Schema版本历史

        Args:
            schema_id: Schema ID

        Returns:
            List[Dict]: 版本历史列表
        """
        try:
            versions = self.version_manager.get_version_history(schema_id)
            return [
                {
                    "version": v.version,
                    "change_type": v.change_type.value,
                    "timestamp": v.timestamp,
                    "author": v.author,
                    "description": v.description,
                    "metadata": v.metadata
                }
                for v in versions
            ]
        except Exception as e:
            self.logger.error(f"获取版本历史失败: {e}")
            return []

    def rollback_schema(self, schema_id: str, target_version: str,
                       author: str = "system") -> Dict[str, Any]:
        """
        回滚Schema到指定版本

        Args:
            schema_id: Schema ID
            target_version: 目标版本
            author: 作者

        Returns:
            Dict: 回滚结果
        """
        try:
            success = self.version_manager.rollback_schema(
                schema_id, target_version, author
            )

            if success:
                return {
                    "success": True,
                    "message": f"Schema已回滚到版本 {target_version}"
                }
            else:
                return {
                    "success": False,
                    "error": "回滚失败"
                }

        except Exception as e:
            self.logger.error(f"回滚失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def compare_schema_versions(self, schema_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """
        比较两个Schema版本

        Args:
            schema_id: Schema ID
            version1: 版本1
            version2: 版本2

        Returns:
            Dict: 比较结果
        """
        try:
            return self.version_manager.compare_versions(schema_id, version1, version2)
        except Exception as e:
            self.logger.error(f"版本比较失败: {e}")
            return {"error": str(e)}

    def get_temp_schema_info(self, temp_schema_id: str) -> Optional[Dict[str, Any]]:
        """
        获取临时Schema信息

        Args:
            temp_schema_id: 临时Schema ID

        Returns:
            Optional[Dict]: Schema信息
        """
        schema = self.persistence_manager.get_temp_schema(temp_schema_id)
        if schema:
            return {
                "name": schema.name,
                "description": schema.description,
                "version": schema.version,
                "entity_count": len(schema.entity_types),
                "relation_count": len(schema.relation_types),
                "entity_types": [et.name for et in schema.entity_types],
                "relation_types": [rt.name for rt in schema.relation_types]
            }
        return None

    def list_active_sessions(self) -> List[Dict[str, Any]]:
        """
        列出所有活动的Schema会话

        Returns:
            List[Dict]: 会话信息列表
        """
        try:
            sessions = self.persistence_manager.list_active_sessions()
            return [
                {
                    "session_id": s.session_id,
                    "schema_id": s.schema_id,
                    "schema_name": s.schema_name,
                    "creation_time": s.creation_time,
                    "last_access_time": s.last_access_time,
                    "access_count": s.access_count,
                    "is_persistent": s.is_persistent,
                    "metadata": s.metadata
                }
                for s in sessions
            ]
        except Exception as e:
            self.logger.error(f"获取会话列表失败: {e}")
            return []

    def get_schema_statistics(self) -> Dict[str, Any]:
        """
        获取Schema统计信息

        Returns:
            Dict: 统计信息
        """
        try:
            return self.version_manager.get_schema_statistics()
        except Exception as e:
            self.logger.error(f"获取统计信息失败: {e}")
            return {"error": str(e)}
    
    def calculate_schema_confidence(self, text: str, schema: Schema) -> float:
        """计算Schema置信度（兼容性方法）"""
        # 由于base_detector可能没有这个方法，我们提供一个简单实现
        try:
            return self.base_detector.calculate_schema_confidence(text, schema)
        except AttributeError:
            # 简单的置信度计算
            return 0.8  # 默认置信度

    def get_best_schema(self, text: str) -> Optional[str]:
        """获取最佳Schema（兼容性方法）"""
        try:
            return self.base_detector.get_best_schema(text)
        except AttributeError:
            # 使用detect_schema的结果
            results = self.detect_schema(text, use_llm=False)
            if results:
                return results[0].schema_file if hasattr(results[0], 'schema_file') else results[0].schema.name
            return None
    
    # 新增的管理方法
    def set_interaction_mode(self, mode: str):
        """设置用户交互模式"""
        self.confirmation_manager.set_interaction_mode(mode)
        self.logger.info(f"交互模式已设置为: {mode}")
    
    def enable_dynamic_features(self, discovery: bool = True, evolution: bool = True):
        """启用/禁用动态功能"""
        self.enable_dynamic_discovery = discovery
        self.enable_schema_evolution = evolution
        self.logger.info(f"动态发现: {'启用' if discovery else '禁用'}, "
                        f"Schema演化: {'启用' if evolution else '禁用'}")
    
    def get_confirmation_history(self):
        """获取用户确认历史"""
        return self.confirmation_manager.get_confirmation_history()
    
    def export_interaction_log(self, filepath: str):
        """导出交互日志"""
        self.confirmation_manager.export_confirmations(filepath)
        self.logger.info(f"交互日志已导出到: {filepath}")


# 为了保持完全的向后兼容性，提供一个工厂函数
def create_enhanced_detector(config: Dict[str, Any] = None) -> EnhancedSchemaDetector:
    """
    创建增强版Schema检测器的工厂函数
    
    Args:
        config: 配置参数
        
    Returns:
        EnhancedSchemaDetector: 增强版检测器实例
    """
    return EnhancedSchemaDetector(config=config)


# 提供一个简单的替换函数，用于现有代码的无缝升级
def upgrade_schema_detector(original_detector: SchemaDetector, 
                          config: Dict[str, Any] = None) -> EnhancedSchemaDetector:
    """
    将原有Schema检测器升级为增强版
    
    Args:
        original_detector: 原有的Schema检测器
        config: 配置参数
        
    Returns:
        EnhancedSchemaDetector: 增强版检测器
    """
    return EnhancedSchemaDetector(base_detector=original_detector, config=config)
