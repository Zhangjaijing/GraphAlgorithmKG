# GraphAlgorithmKG 示例系统

## 📁 示例分类 (11个示例文件)

### 🟢 基础示例 (basic/) - 3个文件
适合初学者，展示核心功能的基本使用方法。

### 🟡 高级示例 (advanced/) - 3个文件
展示高级功能和复杂场景的使用方法。

### 🔵 完整示例 (complete/) - 2个文件
展示完整的端到端流程，包含多个功能的组合使用。

### 🟣 交互示例 (interactive/) - 2个文件
需要用户参与的交互式示例，展示用户参与点。

### 🛠️ 运行器 (1个文件)
统一的示例运行管理工具。

## 🏗️ 示例结构

```
examples/
├── basic/                          # 基础示例 (3个)
│   ├── 01_simple_kg_building.py    # 简单知识图谱构建
│   ├── 02_schema_detection.py      # Schema检测演示
│   └── 03_custom_schema_test.py    # 定制Schema测试
├── advanced/                       # 高级示例 (3个)
│   ├── 04_dynamic_schema_discovery.py # 动态Schema发现
│   ├── 05_schema_evolution.py      # Schema演化演示
│   └── 06_schema_merging.py        # Schema合并演示
├── complete/                       # 完整流程示例 (2个)
│   ├── 08_four_scenarios_demo.py   # 四个场景完整演示
│   └── 09_end_to_end_pipeline.py   # 端到端流水线演示
├── interactive/                    # 交互式示例 (2个)
│   ├── 10_user_guided_schema.py    # 用户引导Schema生成
│   └── 11_interactive_kg_building.py # 交互式知识图谱构建
├── README.md                       # 本文档
└── run_examples.py                 # 示例运行器 (1个)
```

## 🚀 快速开始

### 方法1: 使用示例运行器（推荐）

```bash
# 运行示例运行器
python examples/run_examples.py

# 列出所有可用示例
python examples/run_examples.py --list

# 运行特定类别的示例
python examples/run_examples.py --category basic
python examples/run_examples.py --category advanced
python examples/run_examples.py --category complete
python examples/run_examples.py --category interactive

# 运行特定示例
python examples/run_examples.py --example 01_simple_kg_building
```

### 方法2: 直接运行示例文件

```bash
# 基础示例
python examples/basic/01_simple_kg_building.py
python examples/basic/02_schema_detection.py
python examples/basic/03_custom_schema_test.py

# 高级示例
python examples/advanced/04_dynamic_schema_discovery.py
python examples/advanced/05_schema_evolution.py
python examples/advanced/06_schema_merging.py

# 完整示例
python examples/complete/08_four_scenarios_demo.py
python examples/complete/09_end_to_end_pipeline.py

# 交互式示例（需要用户输入）
python examples/interactive/10_user_guided_schema.py
python examples/interactive/11_interactive_kg_building.py
```

## 📚 示例详细说明

### 🔰 基础示例 (basic/)

适合初学者，演示核心功能的基本使用方法。

#### 01_simple_kg_building.py - 简单知识图谱构建
- **功能**: 演示最基本的知识图谱构建流程
- **输入**: 简单的文本文档
- **输出**: 知识图谱文件和统计信息
- **学习要点**: 
  - SchemaBasedKGBuilder的基本使用
  - 知识图谱的节点和边分析
  - 结果保存和可视化
- **运行时间**: ~30秒
- **依赖**: 无特殊依赖

#### 02_schema_detection.py - Schema检测演示
- **功能**: 演示如何检测文档适合的Schema类型
- **输入**: 不同类型的测试文档
- **输出**: Schema检测结果和置信度分析
- **学习要点**:
  - SchemaDetector的使用方法
  - 不同文档类型的Schema匹配
  - 检测结果的分析和评估
- **运行时间**: ~45秒
- **依赖**: 需要预定义的Schema文件

### 🚀 高级示例 (advanced/)

适合有一定基础的用户，演示高级功能和复杂场景。

#### 04_dynamic_schema_discovery.py - 动态Schema发现
- **功能**: 演示问题驱动的Schema生成功能
- **输入**: 新兴领域的文档和用户查询
- **输出**: 动态生成的Schema和知识图谱
- **学习要点**:
  - EnhancedSchemaDetector的高级功能
  - 动态Schema生成的原理和应用
  - 跨领域知识图谱构建
- **运行时间**: ~2分钟
- **依赖**: 需要LLM支持（可使用模拟模式）

#### 05_schema_evolution.py - Schema演化演示
- **功能**: 展示Schema如何根据新数据自动演化和扩展
- **输入**: 基础文档和包含新概念的演化文档
- **输出**: 演化后的Schema和知识图谱
- **学习要点**:
  - Schema自动演化机制
  - 新概念识别和整合
  - 知识图谱的动态扩展
- **运行时间**: ~1.5分钟
- **依赖**: 需要LLM支持

#### 06_schema_merging.py - Schema合并演示
- **功能**: 演示如何合并多个不同来源的Schema
- **输入**: 多个不同领域的文档
- **输出**: 统一的Schema和跨领域知识图谱
- **学习要点**:
  - 多Schema冲突检测和解决
  - 跨领域概念映射
  - 统一知识表示构建
- **运行时间**: ~2分钟
- **依赖**: 需要LLM支持

### 🔄 完整流程示例 (complete/)

演示完整的端到端流程，适合了解系统整体能力。

#### 08_four_scenarios_demo.py - 四个场景完整演示
- **功能**: 演示所有四个动态Schema场景
- **场景覆盖**:
  - 场景1: 问题驱动Schema生成
  - 场景2: Schema增量演化
  - 场景3: Schema自动合并
  - 场景4: 交互式Schema优化
- **输出**: 各场景执行结果和综合知识图谱
- **学习要点**:
  - 动态Schema系统的完整能力
  - 不同场景的适用条件
  - 系统性能评估方法
- **运行时间**: ~3分钟
- **依赖**: 需要完整的系统组件

#### 09_end_to_end_pipeline.py - 端到端流水线演示
- **功能**: 展示从原始文档到最终知识图谱的完整处理流程
- **输入**: 复杂的多主题文档
- **输出**: 完整的知识图谱和质量评估报告
- **学习要点**:
  - 完整流水线的各个阶段
  - 质量评估和性能分析
  - 自动化处理的最佳实践
- **运行时间**: ~2分钟
- **依赖**: 需要完整的系统组件

### 💬 交互式示例 (interactive/)

需要用户参与的示例，演示人机交互功能。

#### 10_user_guided_schema.py - 用户引导Schema生成
- **功能**: 交互式创建定制化Schema
- **交互内容**:
  - 选择应用领域
  - 定义实体和关系类型
  - 审查和优化Schema
  - 测试Schema效果
- **输出**: 用户定制的Schema配置文件
- **学习要点**:
  - 用户参与的Schema设计流程
  - Schema定制化的最佳实践
  - 交互式系统设计原理
- **运行时间**: 5-15分钟（取决于用户输入）
- **依赖**: 需要用户交互输入

#### 11_interactive_kg_building.py - 交互式知识图谱构建
- **功能**: 用户可以实时参与知识图谱构建过程
- **交互内容**:
  - 选择输入方式和文档
  - 参与Schema选择和参数配置
  - 实时审查和调整构建结果
  - 选择导出格式和保存选项
- **输出**: 用户定制的知识图谱
- **学习要点**:
  - 交互式构建流程设计
  - 用户参与点的优化
  - 实时反馈和调整机制
- **运行时间**: 10-20分钟（取决于用户输入）
- **依赖**: 需要用户交互输入

## ⚙️ 运行环境要求

### 基本要求
- Python 3.8+
- 项目依赖包（见requirements.txt）
- 至少2GB可用内存

### 可选要求
- OpenAI API密钥（用于真实LLM功能，无密钥时使用模拟模式）
- Neo4j数据库（用于图数据库存储，可选）
- 网络连接（用于下载模型或API调用）

### 安装依赖
```bash
# 安装基本依赖
pip install -r requirements.txt

# 安装可选依赖
pip install openai neo4j
```

## 📊 示例输出说明

### 输出目录结构
```
results/examples/
├── simple_kg.graphml              # 知识图谱文件
├── simple_kg_info.txt             # 图谱详细信息
├── schema_detection_results.txt   # Schema检测结果
├── dynamic_schema_discovery_results.txt # 动态发现结果
├── four_scenarios_demo_results.txt # 四场景演示结果
└── custom_schema_*.txt             # 用户定制Schema
```

### 结果文件说明
- **GraphML文件**: 可用NetworkX、Gephi等工具打开的图文件
- **信息文件**: 包含节点、边、统计信息的文本文件
- **结果文件**: 包含执行过程和结果分析的详细报告
- **Schema文件**: 可集成到系统中使用的Schema配置

## 🔧 故障排除

### 常见问题

#### 1. 导入错误
```
ModuleNotFoundError: No module named 'ontology'
```
**解决方案**: 确保从项目根目录运行示例，或设置PYTHONPATH

#### 2. 数据文件缺失
```
FileNotFoundError: Schema file not found
```
**解决方案**: 确保data目录和Schema文件完整

#### 3. 内存不足
```
MemoryError: Unable to allocate memory
```
**解决方案**: 关闭其他程序，或使用更小的测试数据

#### 4. LLM API错误
```
OpenAI API error: Authentication failed
```
**解决方案**: 设置正确的API密钥，或使用模拟模式

### 调试技巧
1. 使用 `--verbose` 参数获得详细输出
2. 检查 `logs/` 目录中的日志文件
3. 逐步运行示例的各个部分
4. 使用较小的测试数据进行调试

## 📈 性能优化建议

### 提高运行速度
1. 使用SSD存储
2. 增加系统内存
3. 使用GPU加速（如果支持）
4. 启用缓存机制

### 减少资源消耗
1. 使用较小的测试文档
2. 限制并发处理数量
3. 定期清理临时文件
4. 使用轻量级模型

## 🎯 学习路径建议

### 初学者路径
1. **01_simple_kg_building.py** - 了解基本概念
2. **02_schema_detection.py** - 理解Schema机制
3. **03_custom_schema_test.py** - 学习定制Schema
4. **09_end_to_end_pipeline.py** - 掌握完整流程

### 进阶用户路径
1. **04_dynamic_schema_discovery.py** - 学习动态发现
2. **05_schema_evolution.py** - 理解Schema演化
3. **06_schema_merging.py** - 掌握Schema合并
4. **08_four_scenarios_demo.py** - 综合应用场景

### 交互式体验路径
1. **10_user_guided_schema.py** - 体验Schema定制
2. **11_interactive_kg_building.py** - 参与构建过程
3. 根据需求定制交互流程

### 开发者路径
1. 阅读所有示例代码
2. 理解系统架构设计
3. 扩展和定制功能
4. 贡献新的示例

## 🤝 贡献指南

欢迎贡献新的示例！请遵循以下规范：

1. **文件命名**: 使用数字前缀和描述性名称
2. **代码结构**: 包含完整的文档字符串和错误处理
3. **输出格式**: 提供清晰的进度提示和结果展示
4. **依赖管理**: 明确列出所需依赖
5. **测试验证**: 确保示例在不同环境下正常运行

## 📞 获取帮助

如果遇到问题或需要帮助：

1. 查看本文档的故障排除部分
2. 检查项目的主README文档
3. 查看相关的技术文档
4. 提交Issue或联系维护者

---

🎉 **开始探索GraphAlgorithmKG的强大功能吧！**
