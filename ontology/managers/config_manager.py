"""
Schema系统配置管理器
负责加载、管理和提供系统配置
"""

import yaml
import os
from typing import Dict, Any, Optional
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: str = "ontology/configs/schema_system_config.yaml"):
        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if not self.config_path.exists():
            logger.warning(f"配置文件不存在: {self.config_path}，使用默认配置")
            self.config = self._get_default_config()
            return
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                self.config = yaml.safe_load(f)
            logger.info(f"配置文件加载成功: {self.config_path}")
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}，使用默认配置")
            self.config = self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "version_management": {
                "version_strategy": "semantic",
                "retention_policy": {
                    "keep_versions": 10,
                    "cleanup_interval": 86400,
                    "backup_old_versions": True
                },
                "snapshots": {
                    "enabled": True,
                    "auto_create": True,
                    "compression": False
                }
            },
            "persistence": {
                "session_timeout": 86400,
                "max_temp_schemas": 100,
                "auto_cleanup": True,
                "storage_paths": {
                    "static_schemas": "ontology/schemas/static",
                    "dynamic_schemas": "ontology/schemas/dynamic",
                    "temp_schemas": "ontology/temp_schemas",
                    "versions": "ontology/versions",
                    "sessions": "ontology/sessions"
                }
            },
            "dynamic_discovery": {
                "query_driven": {
                    "enabled": True,
                    "confidence_threshold": 0.7,
                    "max_concepts_per_query": 20,
                    "llm_model": "default"
                },
                "data_driven": {
                    "enabled": True,
                    "min_frequency": 3,
                    "similarity_threshold": 0.8,
                    "clustering_method": "hierarchical"
                },
                "rag_enhanced": {
                    "enabled": False,
                    "knowledge_base_path": "",
                    "retrieval_top_k": 5
                }
            },
            "schema_evolution": {
                "incremental": {
                    "enabled": True,
                    "auto_confirm_threshold": 0.9,
                    "max_new_concepts_per_iteration": 10,
                    "concept_drift_detection": True
                },
                "user_feedback": {
                    "enabled": True,
                    "feedback_weight": 0.8,
                    "min_feedback_count": 3,
                    "learning_rate": 0.1
                }
            },
            "schema_merging": {
                "default_strategy": "intelligent",
                "conflict_detection": {
                    "similarity_threshold": 0.8,
                    "auto_resolve_threshold": 0.9,
                    "semantic_analysis": True
                },
                "optimization": {
                    "remove_duplicates": True,
                    "merge_similar_concepts": True,
                    "optimize_hierarchy": True
                }
            },
            "interaction": {
                "confirmation": {
                    "mode": "cli",
                    "timeout": 300,
                    "default_action": "skip"
                },
                "feedback": {
                    "enabled": True,
                    "collection_method": "interactive",
                    "feedback_types": ["quality", "relevance", "completeness"]
                }
            },
            "quality_control": {
                "validation": {
                    "min_entity_types": 2,
                    "min_relation_types": 1,
                    "max_entity_types": 100,
                    "max_relation_types": 50,
                    "require_descriptions": True,
                    "require_examples": False
                },
                "consistency": {
                    "check_naming_conventions": True,
                    "check_semantic_consistency": True,
                    "check_type_constraints": True,
                    "check_circular_dependencies": False
                }
            },
            "performance": {
                "caching": {
                    "enabled": True,
                    "cache_size": 1000,
                    "cache_ttl": 3600
                },
                "concurrency": {
                    "max_workers": 4,
                    "batch_size": 100,
                    "timeout": 300
                },
                "memory": {
                    "max_memory_usage": "1GB",
                    "gc_threshold": 0.8,
                    "cleanup_interval": 1800
                }
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "files": {
                    "schema_operations": "logs/schema_operations.log",
                    "version_management": "logs/version_management.log",
                    "merge_operations": "logs/merge_operations.log",
                    "error_log": "logs/schema_errors.log"
                },
                "rotation": {
                    "max_size": "10MB",
                    "backup_count": 5
                }
            }
        }
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key_path: 配置键路径，用点分隔，如 "version_management.retention_policy.keep_versions"
            default: 默认值
            
        Returns:
            配置值
        """
        keys = key_path.split('.')
        value = self.config
        
        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def set(self, key_path: str, value: Any):
        """
        设置配置值
        
        Args:
            key_path: 配置键路径
            value: 配置值
        """
        keys = key_path.split('.')
        config = self.config
        
        # 导航到目标位置
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]
        
        # 设置值
        config[keys[-1]] = value
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """
        获取配置段
        
        Args:
            section: 配置段名称
            
        Returns:
            配置段字典
        """
        return self.config.get(section, {})
    
    def update_section(self, section: str, updates: Dict[str, Any]):
        """
        更新配置段
        
        Args:
            section: 配置段名称
            updates: 更新内容
        """
        if section not in self.config:
            self.config[section] = {}
        
        self.config[section].update(updates)
    
    def save_config(self, config_path: Optional[str] = None):
        """
        保存配置到文件
        
        Args:
            config_path: 配置文件路径，如果为None则使用原路径
        """
        save_path = Path(config_path) if config_path else self.config_path
        
        try:
            save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, allow_unicode=True, default_flow_style=False)
            logger.info(f"配置已保存到: {save_path}")
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
    
    def reload_config(self):
        """重新加载配置"""
        self._load_config()
    
    def validate_config(self) -> Dict[str, Any]:
        """
        验证配置的有效性
        
        Returns:
            验证结果
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 检查必需的配置段
        required_sections = [
            "version_management",
            "persistence", 
            "dynamic_discovery",
            "schema_evolution",
            "schema_merging"
        ]
        
        for section in required_sections:
            if section not in self.config:
                validation_result["errors"].append(f"缺少必需的配置段: {section}")
                validation_result["valid"] = False
        
        # 检查存储路径
        storage_paths = self.get("persistence.storage_paths", {})
        for path_name, path_value in storage_paths.items():
            if not path_value:
                validation_result["warnings"].append(f"存储路径为空: {path_name}")
        
        # 检查阈值范围
        thresholds = [
            ("dynamic_discovery.query_driven.confidence_threshold", 0.0, 1.0),
            ("schema_evolution.incremental.auto_confirm_threshold", 0.0, 1.0),
            ("schema_merging.conflict_detection.similarity_threshold", 0.0, 1.0),
            ("schema_merging.conflict_detection.auto_resolve_threshold", 0.0, 1.0)
        ]
        
        for threshold_path, min_val, max_val in thresholds:
            threshold_val = self.get(threshold_path)
            if threshold_val is not None:
                if not (min_val <= threshold_val <= max_val):
                    validation_result["errors"].append(
                        f"阈值超出范围 [{min_val}, {max_val}]: {threshold_path} = {threshold_val}"
                    )
                    validation_result["valid"] = False
        
        return validation_result
    
    def get_environment_overrides(self) -> Dict[str, Any]:
        """
        获取环境变量覆盖的配置
        
        Returns:
            环境变量配置字典
        """
        env_overrides = {}
        
        # 定义环境变量映射
        env_mappings = {
            "SCHEMA_LOG_LEVEL": "logging.level",
            "SCHEMA_SESSION_TIMEOUT": "persistence.session_timeout",
            "SCHEMA_MAX_TEMP_SCHEMAS": "persistence.max_temp_schemas",
            "SCHEMA_CONFIDENCE_THRESHOLD": "dynamic_discovery.query_driven.confidence_threshold",
            "SCHEMA_AUTO_CONFIRM_THRESHOLD": "schema_evolution.incremental.auto_confirm_threshold"
        }
        
        for env_var, config_path in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # 尝试转换类型
                try:
                    if env_value.lower() in ['true', 'false']:
                        env_value = env_value.lower() == 'true'
                    elif env_value.isdigit():
                        env_value = int(env_value)
                    elif '.' in env_value and env_value.replace('.', '').isdigit():
                        env_value = float(env_value)
                except ValueError:
                    pass  # 保持字符串类型
                
                env_overrides[config_path] = env_value
        
        return env_overrides
    
    def apply_environment_overrides(self):
        """应用环境变量覆盖"""
        overrides = self.get_environment_overrides()
        for config_path, value in overrides.items():
            self.set(config_path, value)
            logger.info(f"应用环境变量覆盖: {config_path} = {value}")


# 全局配置管理器实例
config_manager = ConfigManager()
