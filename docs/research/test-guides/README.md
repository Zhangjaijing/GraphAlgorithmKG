# 测试指南和结果解读

本目录包含测试相关的指南文档，帮助理解测试结果和用户交互流程。

## 📚 文档列表

- [`SIMPLE_TEST_RESULTS_GUIDE.md`](SIMPLE_TEST_RESULTS_GUIDE.md) - **测试结果简化解读指南**
  - 四个场景测试结果一览
  - 会话文件快速查看方法
  - 关键指标解读
  - 性能数据分析

- [`USER_INTERACTION_GUIDE.md`](USER_INTERACTION_GUIDE.md) - **用户交互指南**
  - 四个场景的用户参与流程
  - 每个阶段的用户操作说明
  - 交互界面和选择说明
  - 会话文件内容解读

## 🧪 测试运行指南

### 运行基础测试
```bash
# 单元测试
python tests/unit/test_schema_system.py

# 集成测试
python tests/integration/test_four_scenarios.py

# 系统测试
python tests/system/test_complete_pipeline.py
```

### 运行示例测试
```bash
# 基础功能测试
python examples/basic/01_simple_kg_building.py
python examples/basic/02_schema_detection.py

# 高级功能测试
python examples/advanced/05_schema_evolution.py
python examples/complete/09_end_to_end_pipeline.py
```

## 📊 结果解读

### 测试成功指标
- ✅ **Schema检测成功**: 置信度 > 0.05
- ✅ **知识图谱构建成功**: 实体数 > 0, 关系数 > 0
- ✅ **动态Schema生成成功**: 置信度 > 0.8
- ✅ **用户交互成功**: 用户确认率 > 80%

### 性能基准
- **处理速度**: < 10秒/文档 (中等长度)
- **内存使用**: < 500MB (单文档处理)
- **准确率**: > 85% (Schema检测)
- **召回率**: > 80% (实体识别)

## 🔍 调试指南

### 常见问题排查
1. **Schema检测失败**
   - 检查关键词匹配
   - 验证置信度阈值
   - 查看LLM响应日志

2. **实体推断错误**
   - 检查6层推断日志
   - 验证本体配置
   - 查看缓存状态

3. **三元组抽取不足**
   - 检查规则匹配结果
   - 验证LLM抽取质量
   - 查看合并去重过程

### 日志查看
```bash
# 查看详细会话日志
cat results/sessions/*/01_document_input.json
cat results/sessions/*/02_schema_detection.json
cat results/sessions/*/03_triple_extraction.json

# 查看错误日志
grep "ERROR" logs/*.log
```

## 📈 性能分析

### 关键指标监控
- **Schema检测置信度分布**
- **实体推断层次使用统计**
- **三元组抽取方法占比**
- **LLM调用次数和耗时**

### 优化建议
1. **提高检测准确率**: 优化关键词库和模式匹配
2. **减少LLM调用**: 改进规则抽取覆盖率
3. **加速处理**: 启用智能缓存和并行处理
4. **降低内存**: 优化数据结构和垃圾回收

## 🔗 相关资源
- [算法说明](../algorithm-explanations/) - 详细算法原理
- [研究分析](../RESEARCH_ANALYSIS.md) - 消融实验设计
- [开发文档](../../development/) - 技术实现细节
- [测试代码](../../../tests/) - 完整测试套件
