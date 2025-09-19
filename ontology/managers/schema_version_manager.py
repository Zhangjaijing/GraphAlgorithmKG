"""
Schema版本管理系统
负责Schema的版本控制、持久化存储和历史追踪
"""

import json
import yaml
import hashlib
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict, field
from datetime import datetime
from pathlib import Path
from enum import Enum
import shutil
import logging

from ..schemas.base_schema import Schema, EntityType, RelationType
from .config_manager import config_manager

logger = logging.getLogger(__name__)


class SchemaChangeType(Enum):
    """Schema变更类型"""
    CREATED = "created"
    EVOLVED = "evolved"
    MERGED = "merged"
    OPTIMIZED = "optimized"
    ROLLED_BACK = "rolled_back"


@dataclass
class SchemaVersion:
    """Schema版本信息"""
    version: str
    schema_id: str
    schema_name: str
    change_type: SchemaChangeType
    timestamp: str
    author: str = "system"
    description: str = ""
    parent_version: Optional[str] = None
    file_path: str = ""
    hash_value: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SchemaChangeLog:
    """Schema变更日志"""
    version: str
    timestamp: str
    change_type: SchemaChangeType
    changes: Dict[str, Any]
    author: str = "system"
    description: str = ""


class SchemaVersionManager:
    """Schema版本管理器"""
    
    def __init__(self, base_path: str = "ontology"):
        self.base_path = Path(base_path)

        # 从配置管理器获取路径配置
        storage_paths = config_manager.get_section("persistence").get("storage_paths", {})
        self.schemas_path = Path(storage_paths.get("static_schemas", "ontology/schemas/static")).parent
        self.versions_path = Path(storage_paths.get("versions", "ontology/versions"))
        self.dynamic_path = Path(storage_paths.get("dynamic_schemas", "ontology/schemas/dynamic"))
        
        # 确保目录存在
        self._ensure_directories()
        
        # 初始化日志记录器（必须在其他操作之前）
        self.logger = logging.getLogger(__name__)

        # 版本索引
        self.version_index_path = self.versions_path / "version_index.json"
        self.version_index = self._load_version_index()

        # 变更日志
        self.changelog_path = self.versions_path / "changelog.json"
        self.changelog = self._load_changelog()
    
    def _ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.schemas_path / "static",
            self.schemas_path / "dynamic" / "query_driven",
            self.schemas_path / "dynamic" / "evolved", 
            self.schemas_path / "dynamic" / "merged",
            self.schemas_path / "dynamic" / "optimized",
            self.versions_path / "snapshots",
            self.versions_path / "backups"
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    def _load_version_index(self) -> Dict[str, SchemaVersion]:
        """加载版本索引"""
        if not self.version_index_path.exists():
            return {}
        
        try:
            with open(self.version_index_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                result = {}
                for k, v in data.items():
                    # 转换字符串回枚举类型
                    if 'change_type' in v and isinstance(v['change_type'], str):
                        v['change_type'] = SchemaChangeType(v['change_type'])
                    result[k] = SchemaVersion(**v)
                return result
        except Exception as e:
            self.logger.error(f"加载版本索引失败: {e}")
            return {}
    
    def _save_version_index(self):
        """保存版本索引"""
        try:
            data = {}
            for k, v in self.version_index.items():
                v_dict = asdict(v)
                # 转换枚举类型为字符串
                if 'change_type' in v_dict:
                    v_dict['change_type'] = v_dict['change_type'].value if hasattr(v_dict['change_type'], 'value') else str(v_dict['change_type'])
                data[k] = v_dict

            with open(self.version_index_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存版本索引失败: {e}")
    
    def _load_changelog(self) -> List[SchemaChangeLog]:
        """加载变更日志"""
        if not self.changelog_path.exists():
            return []
        
        try:
            with open(self.changelog_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                result = []
                for item in data:
                    # 转换字符串回枚举类型
                    if 'change_type' in item and isinstance(item['change_type'], str):
                        item['change_type'] = SchemaChangeType(item['change_type'])
                    result.append(SchemaChangeLog(**item))
                return result
        except Exception as e:
            self.logger.error(f"加载变更日志失败: {e}")
            return []
    
    def _save_changelog(self):
        """保存变更日志"""
        try:
            data = []
            for log in self.changelog:
                log_dict = asdict(log)
                # 转换枚举类型为字符串
                if 'change_type' in log_dict:
                    log_dict['change_type'] = log_dict['change_type'].value if hasattr(log_dict['change_type'], 'value') else str(log_dict['change_type'])
                data.append(log_dict)

            with open(self.changelog_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"保存变更日志失败: {e}")
    
    def _calculate_schema_hash(self, schema: Schema) -> str:
        """计算Schema的哈希值"""
        schema_dict = {
            'name': schema.name,
            'entity_types': [et.name for et in schema.entity_types],
            'relation_types': [rt.name for rt in schema.relation_types]
        }
        schema_str = json.dumps(schema_dict, sort_keys=True)
        return hashlib.md5(schema_str.encode()).hexdigest()
    
    def _generate_version_number(self, schema_id: str, change_type: SchemaChangeType) -> str:
        """生成版本号"""
        existing_versions = [
            v.version for v in self.version_index.values() 
            if v.schema_id == schema_id
        ]
        
        if not existing_versions:
            return "1.0.0"
        
        # 解析最新版本号
        latest_version = max(existing_versions, key=lambda v: tuple(map(int, v.split('.'))))
        major, minor, patch = map(int, latest_version.split('.'))
        
        # 根据变更类型决定版本号递增策略
        if change_type in [SchemaChangeType.CREATED, SchemaChangeType.MERGED]:
            major += 1
            minor = 0
            patch = 0
        elif change_type in [SchemaChangeType.EVOLVED, SchemaChangeType.OPTIMIZED]:
            minor += 1
            patch = 0
        else:
            patch += 1
        
        return f"{major}.{minor}.{patch}"
    
    def save_schema(self, schema: Schema, change_type: SchemaChangeType,
                   description: str = "", author: str = "system") -> str:
        """
        保存Schema并创建版本记录
        
        Args:
            schema: Schema对象
            change_type: 变更类型
            description: 变更描述
            author: 作者
            
        Returns:
            str: 版本号
        """
        schema_id = self._generate_schema_id(schema.name)
        version = self._generate_version_number(schema_id, change_type)
        timestamp = datetime.now().isoformat()
        
        # 确定存储路径
        if change_type == SchemaChangeType.CREATED:
            if schema.name.startswith("dynamic_"):
                file_path = self.dynamic_path / "query_driven" / f"{schema_id}_v{version}.yaml"
            else:
                file_path = self.schemas_path / "static" / f"{schema_id}_v{version}.yaml"
        elif change_type == SchemaChangeType.EVOLVED:
            file_path = self.dynamic_path / "evolved" / f"{schema_id}_v{version}.yaml"
        elif change_type == SchemaChangeType.MERGED:
            file_path = self.dynamic_path / "merged" / f"{schema_id}_v{version}.yaml"
        elif change_type == SchemaChangeType.OPTIMIZED:
            file_path = self.dynamic_path / "optimized" / f"{schema_id}_v{version}.yaml"
        else:
            file_path = self.schemas_path / "static" / f"{schema_id}_v{version}.yaml"
        
        # 保存Schema文件
        self._save_schema_file(schema, file_path)
        
        # 计算哈希值
        hash_value = self._calculate_schema_hash(schema)
        
        # 创建版本记录
        schema_version = SchemaVersion(
            version=version,
            schema_id=schema_id,
            schema_name=schema.name,
            change_type=change_type,
            timestamp=timestamp,
            author=author,
            description=description,
            file_path=str(file_path),
            hash_value=hash_value,
            metadata={
                'entity_count': len(schema.entity_types),
                'relation_count': len(schema.relation_types)
            }
        )
        
        # 更新版本索引
        version_key = f"{schema_id}_{version}"
        self.version_index[version_key] = schema_version
        self._save_version_index()
        
        # 记录变更日志
        change_log = SchemaChangeLog(
            version=version,
            timestamp=timestamp,
            change_type=change_type,
            changes=self._detect_changes(schema, schema_id),
            author=author,
            description=description
        )
        self.changelog.append(change_log)
        self._save_changelog()
        
        # 创建快照
        self._create_snapshot(schema_version)
        
        self.logger.info(f"Schema已保存: {schema.name} v{version}")
        return version
    
    def _generate_schema_id(self, schema_name: str) -> str:
        """生成Schema ID"""
        return schema_name.lower().replace(' ', '_').replace('-', '_')
    
    def _save_schema_file(self, schema: Schema, file_path: Path):
        """保存Schema到YAML文件"""
        schema_data = {
            'metadata': {
                'name': schema.name,
                'version': schema.version,
                'description': schema.description,
                'created_at': datetime.now().isoformat(),
                'author': 'system'
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

    def _detect_changes(self, schema: Schema, schema_id: str) -> Dict[str, Any]:
        """检测Schema变更"""
        changes = {
            'added_entities': [],
            'removed_entities': [],
            'added_relations': [],
            'removed_relations': [],
            'modified_entities': [],
            'modified_relations': []
        }

        # 获取最新版本进行比较
        latest_version = self.get_latest_version(schema_id)
        if not latest_version:
            # 新Schema，所有内容都是新增的
            changes['added_entities'] = [et.name for et in schema.entity_types]
            changes['added_relations'] = [rt.name for rt in schema.relation_types]
            return changes

        try:
            old_schema = self.load_schema_version(schema_id, latest_version.version)
            if old_schema:
                # 比较实体类型
                old_entities = {et.name for et in old_schema.entity_types}
                new_entities = {et.name for et in schema.entity_types}

                changes['added_entities'] = list(new_entities - old_entities)
                changes['removed_entities'] = list(old_entities - new_entities)

                # 比较关系类型
                old_relations = {rt.name for rt in old_schema.relation_types}
                new_relations = {rt.name for rt in schema.relation_types}

                changes['added_relations'] = list(new_relations - old_relations)
                changes['removed_relations'] = list(old_relations - new_relations)
        except Exception as e:
            self.logger.warning(f"检测变更时出错: {e}")

        return changes

    def _create_snapshot(self, schema_version: SchemaVersion):
        """创建Schema快照"""
        snapshot_dir = self.versions_path / "snapshots" / schema_version.schema_id
        snapshot_dir.mkdir(parents=True, exist_ok=True)

        snapshot_file = snapshot_dir / f"v{schema_version.version}.yaml"

        try:
            # 复制Schema文件到快照目录
            shutil.copy2(schema_version.file_path, snapshot_file)

            # 创建快照元数据
            metadata_file = snapshot_dir / f"v{schema_version.version}_metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(schema_version), f, ensure_ascii=False, indent=2)

        except Exception as e:
            self.logger.error(f"创建快照失败: {e}")

    def get_latest_version(self, schema_id: str) -> Optional[SchemaVersion]:
        """获取Schema的最新版本"""
        versions = [
            v for v in self.version_index.values()
            if v.schema_id == schema_id
        ]

        if not versions:
            return None

        return max(versions, key=lambda v: tuple(map(int, v.version.split('.'))))

    def get_version_history(self, schema_id: str) -> List[SchemaVersion]:
        """获取Schema的版本历史"""
        versions = [
            v for v in self.version_index.values()
            if v.schema_id == schema_id
        ]

        return sorted(versions, key=lambda v: tuple(map(int, v.version.split('.'))))

    def load_schema_version(self, schema_id: str, version: str) -> Optional[Schema]:
        """加载指定版本的Schema"""
        version_key = f"{schema_id}_{version}"

        if version_key not in self.version_index:
            return None

        schema_version = self.version_index[version_key]
        file_path = Path(schema_version.file_path)

        if not file_path.exists():
            self.logger.error(f"Schema文件不存在: {file_path}")
            return None

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)

            # 转换为Schema对象
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
                name=metadata.get('name', schema_id),
                description=metadata.get('description', ''),
                entity_types=entity_types,
                relation_types=relation_types,
                version=version
            )

        except Exception as e:
            self.logger.error(f"加载Schema版本失败: {e}")
            return None

    def rollback_schema(self, schema_id: str, target_version: str,
                       author: str = "system") -> bool:
        """回滚Schema到指定版本"""
        try:
            # 加载目标版本
            target_schema = self.load_schema_version(schema_id, target_version)
            if not target_schema:
                self.logger.error(f"目标版本不存在: {schema_id} v{target_version}")
                return False

            # 创建回滚版本
            rollback_version = self.save_schema(
                target_schema,
                SchemaChangeType.ROLLED_BACK,
                f"回滚到版本 {target_version}",
                author
            )

            self.logger.info(f"Schema已回滚: {schema_id} v{rollback_version}")
            return True

        except Exception as e:
            self.logger.error(f"回滚失败: {e}")
            return False

    def compare_versions(self, schema_id: str, version1: str, version2: str) -> Dict[str, Any]:
        """比较两个版本的差异"""
        schema1 = self.load_schema_version(schema_id, version1)
        schema2 = self.load_schema_version(schema_id, version2)

        if not schema1 or not schema2:
            return {"error": "版本不存在"}

        # 比较实体类型
        entities1 = {et.name for et in schema1.entity_types}
        entities2 = {et.name for et in schema2.entity_types}

        # 比较关系类型
        relations1 = {rt.name for rt in schema1.relation_types}
        relations2 = {rt.name for rt in schema2.relation_types}

        return {
            "version1": version1,
            "version2": version2,
            "entity_changes": {
                "added": list(entities2 - entities1),
                "removed": list(entities1 - entities2),
                "common": list(entities1 & entities2)
            },
            "relation_changes": {
                "added": list(relations2 - relations1),
                "removed": list(relations1 - relations2),
                "common": list(relations1 & relations2)
            }
        }

    def get_schema_statistics(self) -> Dict[str, Any]:
        """获取Schema统计信息"""
        stats = {
            "total_schemas": len(set(v.schema_id for v in self.version_index.values())),
            "total_versions": len(self.version_index),
            "change_type_distribution": {},
            "recent_changes": []
        }

        # 统计变更类型分布
        for version in self.version_index.values():
            change_type = version.change_type.value
            stats["change_type_distribution"][change_type] = \
                stats["change_type_distribution"].get(change_type, 0) + 1

        # 获取最近的变更
        recent_versions = sorted(
            self.version_index.values(),
            key=lambda v: v.timestamp,
            reverse=True
        )[:10]

        stats["recent_changes"] = [
            {
                "schema_name": v.schema_name,
                "version": v.version,
                "change_type": v.change_type.value,
                "timestamp": v.timestamp,
                "description": v.description
            }
            for v in recent_versions
        ]

        return stats

    def cleanup_old_versions(self, keep_versions: int = 10):
        """清理旧版本，保留指定数量的最新版本"""
        schema_groups = {}

        # 按schema_id分组
        for version in self.version_index.values():
            if version.schema_id not in schema_groups:
                schema_groups[version.schema_id] = []
            schema_groups[version.schema_id].append(version)

        # 清理每个Schema的旧版本
        for schema_id, versions in schema_groups.items():
            if len(versions) <= keep_versions:
                continue

            # 按版本号排序，保留最新的版本
            sorted_versions = sorted(
                versions,
                key=lambda v: tuple(map(int, v.version.split('.'))),
                reverse=True
            )

            versions_to_remove = sorted_versions[keep_versions:]

            for version in versions_to_remove:
                try:
                    # 移动到备份目录而不是删除
                    backup_dir = self.versions_path / "backups" / schema_id
                    backup_dir.mkdir(parents=True, exist_ok=True)

                    file_path = Path(version.file_path)
                    if file_path.exists():
                        backup_file = backup_dir / file_path.name
                        shutil.move(str(file_path), str(backup_file))

                    # 从索引中移除
                    version_key = f"{schema_id}_{version.version}"
                    if version_key in self.version_index:
                        del self.version_index[version_key]

                    self.logger.info(f"已备份旧版本: {schema_id} v{version.version}")

                except Exception as e:
                    self.logger.error(f"清理版本失败: {e}")

        # 保存更新后的索引
        self._save_version_index()


# 全局版本管理器实例
schema_version_manager = SchemaVersionManager()
