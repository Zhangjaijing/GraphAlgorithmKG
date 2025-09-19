# 多领域知识图谱构建系统 - 项目交接指南

## 🎯 项目概述

这是一个**基于LLM的多领域知识图谱构建系统**，核心特点是：

- **输入混乱，输出规范** - 接受任意格式输入，输出严格符合Schema
- **多Schema智能识别** - 自动识别文档类型并选择合适的本体
- **动态Schema发现** - 问题驱动生成、增量演化、自动合并
- **混合抽取架构** - 规则抽取优先，LLM智能兜底
- **交互式构建** - 用户参与的迭代式Schema优化
- **完整会话管理** - 全流程可追溯，支持断点恢复
- **真实LLM集成** - 支持配置文件和模拟模式，混合Prompt验证通过

### **🔍 动态Schema发现的四种情况**

| 情况类型                            | 触发条件                        | 技术方案              | 输入                    | 输出         | 用户交互         |
| ----------------------------------- | ------------------------------- | --------------------- | ----------------------- | ------------ | ---------------- |
| **情况1: 问题驱动Schema生成** | 无预定义Schema + 用户查询意图   | RAG + LLM Schema生成  | 用户问题 + 文档内容     | 定制化Schema | 确认生成的Schema |
| **情况2: Schema增量演化**     | 匹配到预定义Schema + 发现新概念 | 概念发现 + 用户确认   | 现有Schema + 新抽取内容 | 扩展后Schema | 确认新概念/关系  |
| **情况3: Schema自动合并**     | 多个相似Schema冲突              | 语义相似度 + 自动对齐 | 多个候选Schema          | 合并后Schema | 解决冲突选择     |
| **情况4: Schema渐进式学习**   | 处理过程中持续发现模式          | 在线学习 + 模式识别   | 处理历史 + 当前文档     | 优化后Schema | 定期Review确认   |

## 📚 第一部分：文档体系说明

### **📁 docs/ 目录结构与数据流向**

```
docs/
├── README.md                    # 📋 文档导航中心
├── quick-start/                 # 🚀 快速开始指南
│   └── README.md               # 5分钟快速开始教程
├── user-guides/                 # 📚 用户使用指南
│   ├── README.md               # 用户指南导航
│   ├── HANDOVER_GUIDE.md       # 项目交接指南 (本文档)
│   ├── SCHEMA_SYSTEM_GUIDE.md  # Schema系统使用指南
│   └── ONTOLOGY_GUIDE.md       # 本体设计和使用
├── development/                 # 💻 开发技术文档
│   ├── README.md               # 开发文档导航
│   ├── technical_architecture.md  # 技术架构详解
│   ├── system_flowchart.md     # 系统流程图
│   ├── API_INTERFACES.md       # API接口和扩展点
│   └── NEO4J_SETUP.md          # 数据库配置指南
└── research/                    # 🔬 研究扩展文档
    ├── README.md               # 研究文档导航
    ├── RESEARCH_ANALYSIS.md    # 科研重点与消融实验
    ├── algorithm-explanations/ # 算法详细说明
    └── test-guides/            # 测试指南和结果解读
```

### **🔄 大模块数据流向**

#### **主要数据流**

```
📊 核心处理流向:
输入文档 → pipeline/ → results/knowledge_graphs/

📊 训练数据流向:
results/sessions/ → training/data/raw/ → training/data/processed/ → training/models/

🔄 模型使用流向:
training/models/ → pipeline/ → results/

📊 本体管理流向:
ontology/schemas/ → ontology/managers/ → pipeline/

🔄 会话管理流向:
pipeline/ → results/sessions/ → results/knowledge_graphs/
```

#### **详细数据流说明**

1. **文档处理流**: `输入文档 → document_processor → text_splitter → 标准文本块`
2. **Schema检测流**: `文本块 → schema_detector → dynamic_schema → 本体配置`
3. **实体推断流**: `实体名称 → enhanced_entity_inferer → 6层推断 → 实体类型`
4. **三元组抽取流**: `文本 → hybrid_triple_extractor → rule_extractor + llm_extractor → 三元组`
5. **知识图谱构建流**: `三元组 → kg_builder → session_manager → 结构化存储`

## 📁 第二部分：项目目录结构详解

### **🌟 完整项目目录结构**

```
GraphAlgorithmKG/                                    # 多领域知识图谱构建系统根目录
├── main.py                                          # 系统主入口，命令行接口和批处理入口
├── config.json                                      # 全局配置文件，包含LLM API密钥、Base URL等核心配置
├── config.json.template                             # 配置文件模板，用于初始化配置
├── setup.py                                         # Python包安装脚本
├── README.md                                        # 项目总览，快速开始指南和核心功能介绍
├── requirements.txt                                 # Python依赖包列表，包含所有必需的第三方库
│
├── pipeline/                                        # 🏗️ 核心处理管道，系统的心脏
│   ├── schema_based_kg_builder.py                   # 主要KG构建器，协调整个构建流程的核心组件
│   ├── session_manager.py                           # 会话管理器，负责文件保存、目录结构和流程追踪
│   ├── document_processor.py                        # 文档处理器，支持多格式文档解析和标准化
│   ├── text_splitter.py                            # 文本分割器，智能分块保持语义完整性
│   ├── enhanced_entity_inferer.py                   # 增强实体推断器，6层分层推断算法核心
│   ├── hybrid_triple_extractor.py                   # 混合三元组抽取器，规则+LLM的智能抽取策略
│   ├── rule_based_triple_extractor.py               # 基于规则的三元组抽取器，快速模式匹配
│   ├── llm_extractor.py                            # LLM三元组抽取器，语义理解和复杂关系抽取
│   ├── llm_validator.py                            # LLM验证器，三元组质量验证和修复
│   ├── llm_client.py                               # LLM客户端，统一的LLM调用接口和配置管理
│   ├── triple_cleaner.py                           # 三元组清理器，数据清洗和标准化
│   ├── triple_enricher.py                          # 三元组增强器，语义信息补充和属性扩展
│   ├── dynamic_mapper.py                           # 动态映射器，实体和关系的本体对齐
│   ├── entity_type_inferer.py                      # 基础实体类型推断器，简单规则匹配
│   ├── schema_reviewer.py                          # Schema审查器，质量控制和一致性检查
│   ├── neo4j_connector.py                          # Neo4j连接器，图数据库操作和查询接口
│   ├── kg_retriever.py                             # KG检索器，知识图谱查询和信息检索
│   ├── kg_updater.py                               # KG更新器，增量更新和维护功能
│   ├── progress_monitor.py                         # 进度监控器，实时处理状态和用户反馈
│   └── stage_saver.py                              # 阶段保存器，分阶段结果保存和恢复
│
├── examples/                                        # 🎯 示例系统，分类示例和演示代码
│   ├── README.md                                    # 示例系统说明和使用指南
│   ├── run_examples.py                              # 示例运行器，统一执行各类示例
│   ├── basic/                                       # 基础示例，入门级功能演示
│   │   ├── 01_simple_kg_building.py                 # 简单知识图谱构建示例
│   │   ├── 02_schema_detection.py                   # Schema检测功能示例
│   │   └── 03_custom_schema_test.py                 # 自定义Schema测试示例
│   ├── advanced/                                    # 高级示例，复杂功能演示
│   │   ├── 04_dynamic_schema_discovery.py           # 动态Schema发现示例
│   │   ├── 05_schema_evolution.py                   # Schema演化功能示例
│   │   └── 06_schema_merging.py                     # Schema合并功能示例
│   ├── complete/                                    # 完整示例，端到端流程演示
│   │   ├── 08_four_scenarios_demo.py                # 四种场景完整演示
│   │   └── 09_end_to_end_pipeline.py                # 端到端管道演示
│   └── interactive/                                 # 交互示例，用户交互功能演示
│       ├── 10_user_guided_schema.py                 # 用户引导Schema构建
│       └── 11_interactive_kg_building.py            # 交互式知识图谱构建
│
├── ontology/                                        # 🧠 本体管理系统，知识表示和Schema管理
│   ├── schema_index.json                            # Schema索引文件，记录所有可用Schema
│   ├── schemas/                                     # Schema定义文件目录，支持多领域本体
│   │   ├── general/                                 # 通用领域Schema，企业架构和框架概念
│   │   │   └── schema_config.yaml                   # 通用本体定义，包含实体类型和关系类型
│   │   ├── spatiotemporal/                          # 时空领域Schema，时空概念和DO-DA-F结构
│   │   │   ├── spatiotemporal_schema.yaml           # 时空本体定义，时间空间实体和关系
│   │   │   ├── dodaf_state_change_schema.yaml       # DODAF状态变化Schema
│   │   │   └── geospatial_monitoring_schema.yaml    # 地理空间监测Schema
│   │   └── domain_specific/                         # 领域特定Schema目录，预留扩展空间
│   ├── managers/                                    # Schema管理器，动态加载和切换
│   │   ├── config_manager.py                        # 配置管理器，全局配置和参数管理
│   │   ├── dynamic_schema.py                        # 动态Schema管理器，运行时加载和切换
│   │   ├── schema_detector.py                       # Schema检测器，智能文档类型识别
│   │   ├── enhanced_schema_detector.py              # 增强版Schema检测器，支持动态发现和演化
│   │   ├── schema_merger.py                         # Schema合并器，多本体融合和冲突解决
│   │   ├── schema_persistence_manager.py            # Schema持久化管理器，存储和版本控制
│   │   └── schema_version_manager.py                # Schema版本管理器，版本控制和回滚
│   ├── configs/                                     # 本体配置文件目录
│   ├── discoverers/                                 # Schema发现器模块
│   ├── evolvers/                                    # Schema演化器模块
│   ├── interactions/                                # 用户交互模块
│   ├── sessions/                                    # 会话管理目录
│   ├── temp_schemas/                                # 临时Schema存储
│   ├── templates/                                   # Schema模板目录
│   └── versions/                                    # Schema版本控制目录
│
├── training/                                        # 🎓 模型训练系统，机器学习和模型优化
│   ├── README.md                                    # 训练系统说明文档
│   ├── base_trainer.py                              # 基础训练器类
│   ├── entity_inferer_trainer.py                    # 实体推断器训练器
│   ├── schema_classifier_trainer.py                 # Schema分类器训练器
│   ├── configs/                                     # 训练配置文件目录
│   ├── data/                                        # 训练数据目录
│   ├── experiments/                                 # 实验记录和结果
│   ├── models/                                      # 训练好的模型存储
│   └── scripts/                                     # 训练脚本目录
│
├── data/                                            # 📊 数据管理系统，统一数据存储和管理
│   ├── README.md                                    # 数据系统说明文档
│   ├── data_manager.py                              # 数据管理器，统一数据访问接口
│   ├── documents/                                   # 原始文档存储
│   ├── knowledge/                                   # 知识数据存储
│   ├── test/                                        # 测试数据集
│   └── cache/                                       # 数据缓存目录
│
├── results/                                         # 📈 结果存储系统，处理结果和分析报告
│   ├── README.md                                    # 结果系统说明文档
│   ├── END_TO_END_TEST_REPORT.md                    # 端到端测试报告
│   ├── SCHEMA_BOUNDARIES.md                         # Schema边界分析报告
│   ├── sessions/                                    # 会话结果存储
│   ├── knowledge_graphs/                            # 知识图谱结果存储
│   ├── analysis/                                    # 分析结果存储
│   ├── exports/                                     # 导出文件存储
│   └── cache/                                       # 结果缓存目录
│
├── tests/                                           # 🧪 测试系统，全面的质量保证
│   ├── README.md                                    # 测试系统说明文档
│   ├── run_tests.py                                 # 测试运行器
│   ├── run_all_tests.py                             # 全量测试运行器
│   ├── unit/                                        # 单元测试
│   ├── integration/                                 # 集成测试
│   ├── system/                                      # 系统测试
│   └── fixtures/                                    # 测试固件和数据
│
├── scripts/                                         # 🔧 工具脚本系统，运维和管理工具
│   ├── README.md                                    # 脚本系统说明文档
│   ├── cache_manager.py                             # 缓存管理工具
│   ├── kg_expansion_tool.py                         # 知识图谱扩展工具
│   └── stage_recovery_tool.py                       # 阶段恢复工具
│
├── docs/                                            # 📚 文档系统，完整的项目文档
│   ├── README.md                                    # 文档系统导航
│   ├── user-guides/                                 # 用户指南
│   │   ├── README.md                                # 用户指南导航
│   │   ├── HANDOVER_GUIDE.md                        # 项目交接指南
│   │   ├── SCHEMA_SYSTEM_GUIDE.md                   # Schema系统指南
│   │   └── ONTOLOGY_GUIDE.md                        # 本体指南
│   ├── development/                                 # 开发文档
│   │   ├── README.md                                # 开发文档导航
│   │   ├── technical_architecture.md                # 技术架构文档
│   │   ├── system_flowchart.md                      # 系统流程图
│   │   ├── API_INTERFACES.md                        # API接口文档
│   │   └── NEO4J_SETUP.md                           # Neo4j设置指南
│   ├── research/                                    # 研究文档
│   │   ├── README.md                                # 研究文档导航
│   │   ├── RESEARCH_ANALYSIS.md                     # 研究分析报告
│   │   └── ONTOLOGY_FOCUSED_RESEARCH_PLAN.md        # 本体前沿研究计划
│   └── quick-start/                                 # 快速开始指南
│       └── README.md                                # 5分钟快速开始
│
└── logs/                                            # 📝 日志系统，运行日志和调试信息
```

## 📊 第三部分：系统功能流程表

| 模块                   | 功能                     | 算法/技术                                                           | 处理问题(难点)           | 功能衔接        |
| ---------------------- | ------------------------ | ------------------------------------------------------------------- | ------------------------ | --------------- |
| **文档处理**     | 多格式文档解析和清洗     | python-docx, PyPDF2, 正则表达式                                     | 不同格式统一、编码问题   | → Schema检测   |
| **Schema检测**   | 智能识别文档类型         | TF-IDF, 正则匹配, LLM辅助决策                                       | 多Schema置信度相近时决策 | → 本体管理     |
| **本体管理**     | 动态Schema切换和配置     | YAML解析, 动态加载                                                  | 多本体一致性维护         | → 实体推断     |
| **6层实体推断**  | 分层实体类型推断         | 缓存查找→Schema匹配→模式识别→关键词匹配→上下文分析→Unknown标记 | 推断准确性与效率平衡     | → 混合抽取     |
| **规则抽取**     | 基于规则的快速三元组抽取 | 正则表达式, 模式匹配                                                | 规则覆盖度与准确性       | → 混合抽取     |
| **混合抽取协调** | 规则优先+LLM兜底策略     | 质量评估, 智能决策, 结果合并                                        | 抽取效率与质量的平衡     | → 语义验证     |
| **LLM兜底抽取**  | 规则不充分时的语义抽取   | GPT-4, 动态Prompt生成                                               | 成本控制与质量保证       | → 混合抽取     |
| **LLM辅助决策**  | Schema选择和语义验证     | 语义理解, 置信度评估                                                | 关键决策点的准确性       | → 各相关模块   |
| **语义验证**     | 三元组质量验证和修复     | Schema约束检查, 关系映射                                            | 保证Schema一致性         | → 本体映射     |
| **本体映射**     | 实体和关系的本体对齐     | 动态映射, 类型推断                                                  | 多本体间的语义对齐       | → 知识图谱构建 |
| **知识图谱构建** | 最终KG生成和优化         | 图结构构建, 统计分析                                                | 大规模图的构建效率       | → 实时监控     |
| **实时监控**     | 处理过程监控和进度跟踪   | 进度条, 状态管理                                                    | 用户体验优化             | → 会话管理     |
| **会话管理**     | 全流程记录和结果存储     | 文件系统管理, 分类存储                                              | 大量会话的组织管理       | → 结果输出     |

## 🚀 第四部分：系统扩展建议

基于当前系统架构和科研需求，以下是推荐的扩展方向：

### **🎯 核心功能扩展**

#### **1. Schema系统扩展**

- **扩展位置**: `ontology/schemas/` 目录
- **扩展内容**:
  - [ ] **领域特定Schema**: 医学、法律、金融等垂直领域
  - [ ] **多语言Schema**: 支持中文、英文等多语言本体
  - [ ] **层次化Schema**: 支持Schema继承和组合
  - [ ] **动态Schema学习**: 从数据中自动发现新的实体和关系类型
- **科研价值**: 支持跨领域知识图谱研究，探索本体演化机制

#### **2. LLM服务扩展**

- **扩展位置**: `pipeline/llm_client.py`
- **扩展内容**:
  - [ ] **多模型支持**: Claude, Gemini, 本地模型等
  - [ ] **模型路由**: 根据任务类型智能选择最优模型
  - [ ] **成本优化**: 基于质量-成本权衡的模型选择
  - [ ] **批处理优化**: 支持批量请求和并发处理
- **科研价值**: 比较不同LLM在知识抽取任务上的性能差异

### **🔬 科研导向扩展**

#### **3. 知识图谱智能检索**

- **扩展位置**: 新建 `retrieval/` 目录
- **扩展内容**:
  - [ ] **语义检索**: 基于向量相似度的实体和关系检索
  - [ ] **图剪枝算法**: 智能子图提取和路径发现
  - [ ] **LightRAG集成**: 轻量级检索增强生成
  - [ ] **多跳推理**: 支持复杂查询的多步推理
- **科研价值**: 研究大规模知识图谱的高效检索和推理方法

## **🔧 动态Schema配置说明**

在 `config.json`中新增的动态Schema配置项：

```json
{
  "dynamic_schema": {
    "enable_dynamic_discovery": true,        // 启用动态Schema发现
    "enable_schema_evolution": true,         // 启用Schema演化
    "interaction_mode": "cli",               // 交互模式: cli, web, auto
    "confidence_threshold": 0.7,             // 置信度阈值
    "auto_confirm_evolution": false,         // 是否自动确认演化
    "min_concept_frequency": 3,              // 最小概念频率
    "max_new_concepts_per_session": 10       // 每次会话最大新概念数
  }
}
```

**配置项说明**:

- `enable_dynamic_discovery`: 是否启用问题驱动的Schema生成
- `enable_schema_evolution`: 是否启用增量Schema演化
- `interaction_mode`: 用户交互模式，cli为命令行，web为网页界面，auto为自动确认
- `confidence_threshold`: 概念发现的最低置信度阈值
- `auto_confirm_evolution`: 是否自动确认Schema演化，false需要用户手动确认
- `min_concept_frequency`: 概念在文档中的最小出现频率才被考虑
- `max_new_concepts_per_session`: 单次会话中最多发现的新概念数量

#### **常见问题解决**

1. **Mock模式**: 如果LLM未配置，系统自动启用模拟模式
2. **Schema检测失败**: 检查文档内容是否包含足够的领域关键词
3. **实体推断准确率低**: 可以通过添加领域词库提升
4. **处理速度慢**: 可以调整LLM调用策略或增加规则覆盖度
