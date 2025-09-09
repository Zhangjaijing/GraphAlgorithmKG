# 开发文档

本目录包含面向开发者的技术文档，包括系统架构、API接口、配置指南等。

## 📚 文档列表

### 系统架构
- [`technical_architecture.md`](technical_architecture.md) - **技术架构详解**
  - 核心技术组件详解
  - 6层分层实体推断
  - 混合三元组抽取
  - 动态Schema发现架构

- [`system_flowchart.md`](system_flowchart.md) - **系统流程图**
  - 完整处理流程图
  - 科研架构图
  - 数据流向图
  - Mermaid图表定义

### 接口和配置
- [`API_INTERFACES.md`](API_INTERFACES.md) - **API接口和扩展点**
  - 核心接口列表
  - 扩展点说明
  - 接口使用示例
  - 自定义组件开发

- [`NEO4J_SETUP.md`](NEO4J_SETUP.md) - **Neo4j数据库配置**
  - 快速开始指南
  - 数据导入导出
  - 连接配置
  - 常见问题解决

## 🎯 阅读建议

### 系统开发者
1. 先读 `technical_architecture.md` 了解整体架构
2. 查看 `system_flowchart.md` 理解数据流程
3. 参考 `API_INTERFACES.md` 进行组件开发

### 集成开发者
1. 重点关注 `API_INTERFACES.md` 的接口定义
2. 参考 `NEO4J_SETUP.md` 配置数据库
3. 查看架构文档了解系统边界

### 运维人员
1. 主要参考 `NEO4J_SETUP.md` 进行环境配置
2. 了解 `technical_architecture.md` 中的部署要求

## 🛠️ 开发工具

### 代码结构
```
pipeline/                    # 核心处理管道
├── schema_based_kg_builder.py    # 主构建器
├── enhanced_entity_inferer.py    # 6层实体推断
├── hybrid_triple_extractor.py    # 混合抽取器
├── llm_client.py                 # LLM统一接口
└── session_manager.py            # 会话管理

ontology/                    # 本体管理系统
├── managers/                     # Schema管理器
├── discoverers/                  # Schema发现器
├── evolvers/                     # Schema演化器
└── interactions/                 # 用户交互管理
```

### 开发环境配置
```bash
# 安装依赖
pip install -r requirements.txt

# 配置LLM API
cp config.json.template config.json
# 编辑config.json添加API密钥

# 启动Neo4j数据库
# 参考 NEO4J_SETUP.md

# 运行测试
python tests/run_tests.py --type unit
```

### 调试工具
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 使用会话管理器查看中间结果
from pipeline.session_manager import SessionManager
sm = SessionManager()
session_id = sm.start_session("test_doc.txt")
# 查看 results/sessions/{session_id}/ 目录
```

## 🔗 相关链接
- [用户指南](../user-guides/) - 使用教程和指南
- [研究文档](../research/) - 算法原理和实验
- [快速开始](../quick-start/) - 5分钟快速上手
- [示例代码](../../examples/) - 实际使用示例
- [测试代码](../../tests/) - 单元和集成测试
