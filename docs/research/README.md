# 研究扩展文档

本目录包含面向研究者的文档，包括科研分析、算法说明、实验指南等。

## 📚 文档列表

### 科研分析
- [`RESEARCH_ANALYSIS.md`](RESEARCH_ANALYSIS.md) - **科研重点与消融实验分析**
  - 科研问题表格
  - 消融实验设计矩阵
  - 已完成实验组合
  - 待设计的关键实验

### 算法说明
- [`algorithm-explanations/`](algorithm-explanations/) - **算法详细说明**
  - [`DETAILED_ALGORITHM_EXPLANATION.md`](algorithm-explanations/DETAILED_ALGORITHM_EXPLANATION.md) - Schema系统四个场景详细算法

### 测试指南
- [`test-guides/`](test-guides/) - **测试指南和结果解读**
  - [`SIMPLE_TEST_RESULTS_GUIDE.md`](test-guides/SIMPLE_TEST_RESULTS_GUIDE.md) - 测试结果简化解读
  - [`USER_INTERACTION_GUIDE.md`](test-guides/USER_INTERACTION_GUIDE.md) - 用户交互指南

## 🎯 研究方向

### 核心科研问题
1. **跨领域本体选择** - 多Schema智能识别
2. **动态Schema发现** - 问题驱动生成和演化
3. **分层实体推断** - 6层渐进式推断算法
4. **符号神经混合** - 规则+LLM混合推理
5. **本体感知LLM** - Schema约束的语言模型

### 消融实验方向
- Schema检测器对比实验
- 实体推断层数影响分析
- 三元组抽取策略对比
- LLM模型类型影响研究
- 缓存策略性能分析

## 🧪 实验指南

### 运行测试
```bash
# 运行四个场景测试
python tests/integration/test_four_scenarios.py

# 查看测试结果
cat results/sessions/scenario_*_test_result.json
```

### 查看实验数据
- 会话数据: `results/sessions/`
- 知识图谱: `results/knowledge_graphs/`
- 分析结果: `results/analysis/`

## 🔗 相关链接
- [用户指南](../user-guides/) - 基础使用方法
- [开发文档](../development/) - 技术实现细节
- [测试代码](../../tests/) - 完整测试套件
- [训练数据](../../training/) - 模型训练相关
