# Schema系统使用指南

## 🎯 系统概述

Schema系统是本项目的核心功能，支持动态Schema发现、演化、合并和优化，实现从"静态预定义"到"智能自适应"的升级。

## 🚀 快速开始

### 基础使用
```python
from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder

# 创建构建器
builder = SchemaBasedKGBuilder()

# 构建知识图谱（自动检测Schema）
kg = builder.build_knowledge_graph("document.txt")
```

### 指定用户查询
```python
# 带用户查询的构建（启用动态Schema生成）
kg = builder.build_knowledge_graph(
    document_path="document.txt",
    user_query="我想了解算法性能关系"
)
```

## 🔄 四种核心场景

### 场景1: 问题驱动Schema生成
- **触发**: 无匹配Schema + 用户查询
- **方案**: LLM分析生成定制Schema
- **适用**: 全新领域、定制需求

### 场景2: Schema增量演化
- **触发**: 现有Schema + 发现新概念
- **方案**: 概念识别 + 用户确认 + Schema扩展
- **适用**: 领域扩展、知识增长

### 场景3: Schema自动合并
- **触发**: 多个相似Schema冲突
- **方案**: 冲突检测 + 语义对齐 + 自动合并
- **适用**: Schema整合、统一建模

### 场景4: 交互式优化
- **触发**: 用户对Schema不满意
- **方案**: 主动询问 + 迭代优化
- **适用**: Schema精细化、质量提升

## 🔧 高级配置

### 启用动态功能
```python
from ontology.managers.enhanced_schema_detector import EnhancedSchemaDetector

# 创建增强检测器
detector = EnhancedSchemaDetector()

# 启用动态功能
detector.enable_dynamic_features(
    discovery=True,    # 启用Schema发现
    evolution=True     # 启用Schema演化
)

# 设置交互模式
detector.set_interaction_mode("cli")  # cli, web, auto
```

### 自定义Schema模板
```python
# 创建自定义Schema模板
custom_schema = {
    "name": "custom_domain",
    "entity_types": [
        {"name": "CustomEntity", "properties": ["name", "type"]},
        {"name": "CustomConcept", "properties": ["description"]}
    ],
    "relation_types": [
        {"name": "custom_relation", "domain": "CustomEntity", "range": "CustomConcept"}
    ]
}

# 使用自定义Schema
kg = builder.build_knowledge_graph(
    document_path="document.txt",
    custom_schema=custom_schema
)
```

## 📊 性能指标

### 检测准确率
- **静态Schema检测**: 95%+
- **动态Schema生成**: 85%+
- **Schema演化检测**: 90%+

### 处理速度
- **Schema检测**: <1秒
- **动态生成**: <30秒
- **演化处理**: <10秒

## 🔗 相关文档

- [技术架构](../development/technical_architecture.md) - 详细技术实现
- [API接口](../development/API_INTERFACES.md) - 完整接口文档
- [本体指南](ONTOLOGY_GUIDE.md) - 本体设计方法
- [快速开始](../quick-start/) - 5分钟上手指南

### 场景4: 交互式Schema优化
**触发条件**: 用户对当前Schema不满意  
**技术方案**: 主动询问 + 细化建议 + 迭代优化  
**适用场景**: Schema精细化、用户定制、质量提升

## 🏗️ 架构设计

### 系统架构
```
ontology/
├── schemas/                    # Schema存储
│   ├── static/                # 静态预定义Schema
│   ├── dynamic/               # 动态生成Schema
│   │   ├── query_driven/      # 问题驱动生成
│   │   ├── evolved/           # 增量演化
│   │   ├── merged/            # 自动合并
│   │   └── optimized/         # 交互优化
│   ├── general/               # 通用Schema
│   └── spatiotemporal/        # 时空Schema
├── versions/                   # 版本管理
├── sessions/                   # 会话管理
├── temp_schemas/              # 临时Schema
└── managers/                  # 管理器
    ├── enhanced_schema_detector.py
    ├── schema_version_manager.py
    ├── schema_persistence_manager.py
    └── schema_merger.py
```

### 核心组件

#### EnhancedSchemaDetector
扩展原有Schema检测功能，支持动态发现：
```python
class EnhancedSchemaDetector:
    def detect_schema(self, text, use_llm=False, user_query=None):
        # 1. 常规Schema检测
        results = self.base_detector.detect_schema(text, use_llm)
        
        # 2. 动态Schema发现
        if not results and user_query:
            return self._dynamic_discovery(text, user_query)
        
        # 3. Schema演化
        elif results and self._has_new_concepts(text, results[0].schema):
            return self._evolve_schema(results[0], text)
        
        return results
```

#### SchemaMerger
处理Schema冲突和合并：
```python
class SchemaMerger:
    def merge_schemas(self, schemas, merge_strategy='intelligent'):
        # 1. 冲突检测
        conflicts = self._detect_conflicts(schemas)
        
        # 2. 语义对齐
        alignments = self._semantic_alignment(conflicts)
        
        # 3. 自动合并
        merged_schema = self._merge_with_strategy(schemas, alignments)
        
        return MergeResult(merged_schema, conflicts, summary)
```

## 📝 Schema设计指南

### 设计理念
- **配置驱动**: 所有Schema定义在YAML配置文件中
- **自动集成**: LLM Prompt自动从Schema生成
- **版本管理**: 内置版本控制和变更追踪
- **易于维护**: 修改Schema只需编辑配置文件

### 配置文件结构
```yaml
metadata:
  name: "领域知识图谱本体"
  version: "1.0.0"
  description: "领域描述"
  author: "作者"

entity_types:
  EntityName:
    description: "实体描述"
    examples: ["示例1", "示例2"]
    keywords: ["关键词1", "关键词2"]
    patterns: ["正则表达式"]
    aliases: ["别名1", "别名2"]
    color: "#FF6B6B"

relation_types:
  relation_name:
    description: "关系描述"
    examples: ["(实体1, relation, 实体2)"]
    subject_types: ["主语类型"]
    object_types: ["宾语类型"]
    keywords: ["关键词"]
```

### 支持的本体类型

#### 1. 通用知识图谱本体
- **文件**: `ontology/schemas/general/schema_config.yaml`
- **领域**: 通用架构和框架概念
- **主要实体**: Algorithm, Framework, Task, Paradigm, Technique, Metric
- **测试准确率**: 88.9%

#### 2. 时空本体
- **文件**: `ontology/schemas/spatiotemporal/spatiotemporal_schema.yaml`
- **领域**: 时空概念和DO-DA-F结构
- **主要实体**: TemporalEntity, SpatialEntity, Event, Action, Condition
- **测试准确率**: 85.7%

## 🔧 使用指南

### 基本使用
```python
from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder

# 启用动态Schema功能
builder = SchemaBasedKGBuilder(use_enhanced_detector=True)

# 构建知识图谱
kg = builder.build_knowledge_graph(
    document_path="document.txt",
    user_query="用户查询意图"  # 可选，用于动态生成
)
```

### 高级配置
```python
# 配置动态Schema参数
config = {
    'enable_schema_evolution': True,
    'force_dynamic_discovery': False,
    'merge_similar_schemas': True,
    'user_interaction_mode': 'interactive'
}

detector = EnhancedSchemaDetector(config=config)
```

## 📊 版本管理

### 版本控制
```python
from ontology.managers.schema_version_manager import SchemaVersionManager

version_manager = SchemaVersionManager()

# 创建新版本
version_id = version_manager.create_version(
    schema=new_schema,
    description="添加量子算法概念"
)

# 回滚到指定版本
version_manager.rollback_to_version(version_id)
```

### 会话管理
```python
from ontology.managers.schema_persistence_manager import SchemaPersistenceManager

persistence_manager = SchemaPersistenceManager()

# 保存临时Schema
temp_id = persistence_manager.save_temp_schema(schema)

# 持久化Schema
persistence_manager.persist_temp_schema(temp_id)
```

## 🎯 最佳实践

### 1. Schema设计原则
- **领域专一**: 每个Schema专注一个领域
- **层次清晰**: 实体关系层次分明
- **扩展性强**: 支持后续扩展
- **语义明确**: 描述清晰无歧义

### 2. 动态发现策略
- **渐进式**: 从简单到复杂逐步扩展
- **用户驱动**: 重要决策让用户参与
- **质量优先**: 宁可保守也要保证质量
- **可回滚**: 支持撤销和重做操作

### 3. 性能优化
- **缓存机制**: 缓存常用Schema和检测结果
- **批量处理**: 批量处理相似文档
- **异步执行**: LLM调用使用异步模式
- **资源管理**: 合理管理内存和计算资源

## 🔍 故障排除

### 常见问题
1. **Schema检测失败**: 检查关键词匹配和阈值设置
2. **动态生成质量差**: 优化Prompt模板和示例
3. **合并冲突多**: 调整语义相似度阈值
4. **性能问题**: 启用缓存和批量处理

### 调试工具
```python
# 启用调试模式
detector = EnhancedSchemaDetector(debug=True)

# 查看检测详情
results = detector.detect_schema(text, debug_info=True)
for result in results:
    print(f"Schema: {result.schema_file}")
    print(f"置信度: {result.confidence}")
    print(f"证据: {result.evidence}")
```

## 📈 扩展开发

### 添加新的检测方法
```python
class CustomSchemaDetector(EnhancedSchemaDetector):
    def _custom_detection_method(self, text, schema):
        # 实现自定义检测逻辑
        score = self._calculate_custom_score(text, schema)
        return score > self.custom_threshold
```

### 集成新的LLM
```python
from ontology.llm.base_llm import BaseLLM

class CustomLLM(BaseLLM):
    def generate_schema(self, prompt):
        # 实现自定义LLM调用
        return self.model.generate(prompt)
```

这个完整指南整合了原来分散在多个文档中的内容，提供了统一的参考。
