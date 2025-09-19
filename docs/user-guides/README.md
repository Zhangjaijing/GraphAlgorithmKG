# 用户指南

本目录包含面向用户的使用指南和教程。

## 📚 文档列表

### 核心指南
- [`HANDOVER_GUIDE.md`](HANDOVER_GUIDE.md) - **项目交接指南** (推荐首读)
  - 项目概述和核心特点
  - 完整目录结构说明
  - 数据流向和处理流程
  - 扩展建议和科研方向

- [`SCHEMA_SYSTEM_GUIDE.md`](SCHEMA_SYSTEM_GUIDE.md) - **Schema系统使用指南**
  - 四种核心场景详解
  - 快速开始示例
  - 支持的本体类型
  - 使用方法和配置

- [`ONTOLOGY_GUIDE.md`](ONTOLOGY_GUIDE.md) - **本体设计和使用**
  - 支持的本体类型
  - 实体和关系定义
  - 本体选择建议
  - 自定义本体创建

## 🎯 阅读建议

### 新用户
1. 先读 `HANDOVER_GUIDE.md` 了解项目全貌
2. 再读 `SCHEMA_SYSTEM_GUIDE.md` 学习核心功能
3. 参考 `ONTOLOGY_GUIDE.md` 了解本体系统

### 使用者
1. 直接查看 `SCHEMA_SYSTEM_GUIDE.md` 的快速开始
2. 根据需要参考 `ONTOLOGY_GUIDE.md` 选择合适本体

### 研究者
1. 重点阅读 `HANDOVER_GUIDE.md` 的扩展建议部分
2. 了解 `SCHEMA_SYSTEM_GUIDE.md` 的四种核心场景
3. 参考 `ONTOLOGY_GUIDE.md` 进行本体设计

## 🚀 快速开始

### 基础使用
```python
from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder

# 创建构建器
builder = SchemaBasedKGBuilder()

# 构建知识图谱
kg = builder.build_knowledge_graph("your_document.txt")
print(f"构建完成！实体数: {len(kg.entities)}, 关系数: {len(kg.relations)}")
```

### 动态Schema生成
```python
# 带用户查询的构建
kg = builder.build_knowledge_graph(
    document_path="document.txt",
    user_query="我想了解算法性能关系"
)
```

### 查看处理结果
```python
# 查看会话记录
from pipeline.session_manager import SessionManager
sm = SessionManager()
sessions = sm.list_recent_sessions()
print("最近的会话:", sessions[:5])
```

## 🔗 相关链接
- [快速开始](../quick-start/) - 5分钟快速上手
- [开发文档](../development/) - 技术架构和API
- [研究文档](../research/) - 算法说明和实验指南
- [示例代码](../../examples/) - 完整使用示例
