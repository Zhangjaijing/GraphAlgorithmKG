"""
Schema持久化管理器
负责动态Schema的持久化存储和会话管理
"""

import json
import yaml
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import logging

from ..schemas.base_schema import Schema
from .schema_version_manager import SchemaVersionManager, SchemaChangeType
from .config_manager import config_manager

logger = logging.getLogger(__name__)


@dataclass
class SchemaSession:
    """Schema会话信息"""
    session_id: str
    schema_id: str
    schema_name: str
    creation_time: str
    last_access_time: str
    access_count: int = 0
    is_persistent: bool = False
    metadata: Dict[str, Any] = None


class SchemaPersistenceManager:
    """Schema持久化管理器"""
    
    def __init__(self, base_path: str = "ontology"):
        self.base_path = Path(base_path)

        # 从配置管理器获取路径配置
        storage_paths = config_manager.get_section("persistence").get("storage_paths", {})
        self.sessions_path = Path(storage_paths.get("sessions", "ontology/sessions"))
        self.temp_schemas_path = Path(storage_paths.get("temp_schemas", "ontology/temp_schemas"))
        
        # 确保目录存在
        self._ensure_directories()
        
        # 版本管理器
        self.version_manager = SchemaVersionManager(base_path)
        
        # 会话管理
        self.sessions_file = self.sessions_path / "active_sessions.json"
        self.active_sessions: Dict[str, SchemaSession] = self._load_sessions()
        
        # 临时Schema存储
        self.temp_schemas: Dict[str, Schema] = {}
        
        # 从配置管理器获取配置
        persistence_config = config_manager.get_section("persistence")
        self.session_timeout = timedelta(seconds=persistence_config.get("session_timeout", 86400))
        self.max_temp_schemas = persistence_config.get("max_temp_schemas", 100)
        
        self.logger = logging.getLogger(__name__)
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.sessions_path,
            self.temp_schemas_path,
            self.temp_schemas_path / "query_driven",
            self.temp_schemas_path / "evolved",
            self.temp_schemas_path / "merged"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_sessions(self) -> Dict[str, SchemaSession]:
        """加载活动会话"""
        if not self.sessions_file.exists():
            return {}
        
        try:
            with open(self.sessions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    k: SchemaSession(**v) for k, v in data.items()
                }
        except Exception as e:
            self.logger.error(f"加载会话失败: {e}")
            return {}
    
    def _save_sessions(self):
        """保存活动会话"""
        try:
            data = {
                k: asdict(v) for k, v in self.active_sessions.items()
            }
            with open(self.sessions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存会话失败: {e}")
    
    def create_temp_schema(self, schema: Schema, session_id: str = None,
                          schema_type: str = "query_driven") -> str:
        """
        创建临时Schema
        
        Args:
            schema: Schema对象
            session_id: 会话ID
            schema_type: Schema类型 (query_driven, evolved, merged)
            
        Returns:
            str: 临时Schema的标识符
        """
        import uuid
        
        if not session_id:
            session_id = str(uuid.uuid4())
        
        # 生成临时Schema ID
        temp_schema_id = f"temp_{schema_type}_{session_id[:8]}"
        
        # 存储到内存
        self.temp_schemas[temp_schema_id] = schema
        
        # 保存到临时文件
        temp_file = self.temp_schemas_path / schema_type / f"{temp_schema_id}.yaml"
        self._save_temp_schema_file(schema, temp_file)
        
        # 创建或更新会话
        if session_id not in self.active_sessions:
            self.active_sessions[session_id] = SchemaSession(
                session_id=session_id,
                schema_id=temp_schema_id,
                schema_name=schema.name,
                creation_time=datetime.now().isoformat(),
                last_access_time=datetime.now().isoformat(),
                metadata={"schema_type": schema_type}
            )
        else:
            self.active_sessions[session_id].last_access_time = datetime.now().isoformat()
            self.active_sessions[session_id].access_count += 1
        
        self._save_sessions()
        
        # 清理过期的临时Schema
        self._cleanup_expired_schemas()
        
        self.logger.info(f"创建临时Schema: {temp_schema_id}")
        return temp_schema_id
    
    def _save_temp_schema_file(self, schema: Schema, file_path: Path):
        """保存临时Schema文件"""
        schema_data = {
            'metadata': {
                'name': schema.name,
                'version': schema.version,
                'description': schema.description,
                'created_at': datetime.now().isoformat(),
                'is_temporary': True
            },
            'entity_types': {},
            'relation_types': {}
        }
        
        # 转换实体类型
        for et in schema.entity_types:
            schema_data['entity_types'][et.name] = {
                'description': et.description,
                'examples': getattr(et, 'examples', []),
                'keywords': getattr(et, 'keywords', []),
                'patterns': getattr(et, 'patterns', []),
                'aliases': getattr(et, 'aliases', [])
            }
        
        # 转换关系类型
        for rt in schema.relation_types:
            schema_data['relation_types'][rt.name] = {
                'description': rt.description,
                'examples': rt.examples,
                'subject_types': getattr(rt, 'subject_types', ['*']),
                'object_types': getattr(rt, 'object_types', ['*'])
            }
        
        # 保存文件
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(schema_data, f, allow_unicode=True, default_flow_style=False)
    
    def get_temp_schema(self, temp_schema_id: str) -> Optional[Schema]:
        """获取临时Schema"""
        # 首先从内存中查找
        if temp_schema_id in self.temp_schemas:
            return self.temp_schemas[temp_schema_id]
        
        # 从文件中加载
        for schema_type in ["query_driven", "evolved", "merged"]:
            temp_file = self.temp_schemas_path / schema_type / f"{temp_schema_id}.yaml"
            if temp_file.exists():
                schema = self._load_temp_schema_file(temp_file)
                if schema:
                    self.temp_schemas[temp_schema_id] = schema
                    return schema
        
        return None
    
    def _load_temp_schema_file(self, file_path: Path) -> Optional[Schema]:
        """从文件加载临时Schema"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            from ..schemas.base_schema import EntityType, RelationType
            
            # 转换实体类型
            entity_types = []
            for name, config in data.get('entity_types', {}).items():
                entity_types.append(EntityType(
                    name=name,
                    description=config.get('description', ''),
                    examples=config.get('examples', []),
                    keywords=config.get('keywords', []),
                    patterns=config.get('patterns', []),
                    aliases=config.get('aliases', [])
                ))
            
            # 转换关系类型
            relation_types = []
            for name, config in data.get('relation_types', {}).items():
                relation_types.append(RelationType(
                    name=name,
                    description=config.get('description', ''),
                    examples=config.get('examples', []),
                    source_type=config.get('subject_types', ['*'])[0] if config.get('subject_types') else '*',
                    target_type=config.get('object_types', ['*'])[0] if config.get('object_types') else '*'
                ))
            
            metadata = data.get('metadata', {})
            return Schema(
                name=metadata.get('name', 'Temporary Schema'),
                description=metadata.get('description', ''),
                entity_types=entity_types,
                relation_types=relation_types,
                version=metadata.get('version', '1.0.0')
            )
            
        except Exception as e:
            self.logger.error(f"加载临时Schema文件失败: {e}")
            return None
    
    def persist_temp_schema(self, temp_schema_id: str, description: str = "",
                           author: str = "system") -> Optional[str]:
        """
        将临时Schema持久化
        
        Args:
            temp_schema_id: 临时Schema ID
            description: 描述
            author: 作者
            
        Returns:
            Optional[str]: 持久化后的版本号，失败返回None
        """
        schema = self.get_temp_schema(temp_schema_id)
        if not schema:
            self.logger.error(f"临时Schema不存在: {temp_schema_id}")
            return None
        
        try:
            # 确定变更类型
            if temp_schema_id.startswith("temp_query_driven"):
                change_type = SchemaChangeType.CREATED
            elif temp_schema_id.startswith("temp_evolved"):
                change_type = SchemaChangeType.EVOLVED
            elif temp_schema_id.startswith("temp_merged"):
                change_type = SchemaChangeType.MERGED
            else:
                change_type = SchemaChangeType.CREATED
            
            # 使用版本管理器保存
            version = self.version_manager.save_schema(
                schema, change_type, description, author
            )
            
            # 标记会话为持久化
            for session in self.active_sessions.values():
                if session.schema_id == temp_schema_id:
                    session.is_persistent = True
                    break
            
            self._save_sessions()
            
            self.logger.info(f"临时Schema已持久化: {temp_schema_id} -> v{version}")
            return version
            
        except Exception as e:
            self.logger.error(f"持久化失败: {e}")
            return None
    
    def _cleanup_expired_schemas(self):
        """清理过期的临时Schema"""
        current_time = datetime.now()
        expired_sessions = []
        
        for session_id, session in self.active_sessions.items():
            last_access = datetime.fromisoformat(session.last_access_time)
            if current_time - last_access > self.session_timeout and not session.is_persistent:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            session = self.active_sessions[session_id]
            
            # 删除临时文件
            for schema_type in ["query_driven", "evolved", "merged"]:
                temp_file = self.temp_schemas_path / schema_type / f"{session.schema_id}.yaml"
                if temp_file.exists():
                    temp_file.unlink()
            
            # 从内存中移除
            if session.schema_id in self.temp_schemas:
                del self.temp_schemas[session.schema_id]
            
            # 移除会话
            del self.active_sessions[session_id]
            
            self.logger.info(f"清理过期Schema: {session.schema_id}")
        
        if expired_sessions:
            self._save_sessions()
    
    def get_session_info(self, session_id: str) -> Optional[SchemaSession]:
        """获取会话信息"""
        return self.active_sessions.get(session_id)
    
    def list_active_sessions(self) -> List[SchemaSession]:
        """列出所有活动会话"""
        return list(self.active_sessions.values())
    
    def extend_session(self, session_id: str) -> bool:
        """延长会话时间"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id].last_access_time = datetime.now().isoformat()
            self.active_sessions[session_id].access_count += 1
            self._save_sessions()
            return True
        return False


# 全局持久化管理器实例
schema_persistence_manager = SchemaPersistenceManager()
