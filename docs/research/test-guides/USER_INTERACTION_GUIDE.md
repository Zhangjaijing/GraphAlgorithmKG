# 用户交互指南 - Schema系统四个场景

## 🎯 用户参与点总览

每个场景都有明确的用户参与点，用户需要在特定阶段提供输入或确认。

---

## 场景1: 问题驱动Schema生成

### 👤 用户参与流程

#### 阶段1: 初始输入 (用户主导)
```
用户操作: 提供查询和相关文档
示例输入:
- 查询: "我想了解这些文档中的算法性能关系"
- 文档: 包含CNN、RNN、准确率、数据集等内容的技术文档
```

#### 阶段2: 系统处理 (自动化)
```
系统操作: 
1. 尝试匹配现有Schema (无匹配结果)
2. 触发动态Schema生成 (LLM分析)
3. 生成定制化Schema
```

#### 阶段3: 结果确认 (用户参与)
```
系统展示: 生成的Schema包含
- 实体类型: Algorithm, PerformanceMetric, Dataset
- 关系类型: hasPerformance, testedOn
- 置信度: 0.950

用户选择:
[ ] 接受生成的Schema
[ ] 要求修改某些实体/关系
[ ] 重新生成
```

### 📁 会话文件内容
- **输入文件**: `scenario_1_test_input.json` - 包含用户查询和文档
- **输出文件**: `scenario_1_test_result.json` - 包含生成的Schema和置信度

---

## 场景2: Schema增量演化

### 👤 用户参与流程

#### 阶段1: 触发条件 (系统检测)
```
系统检测: 
- 现有Schema: 基础算法Schema (Algorithm, Task实体)
- 新文档: 包含"量子算法"、"量子计算机"等新概念
```

#### 阶段2: 概念确认 (用户参与)
```
系统提示: 发现以下新概念
- 量子算法
- 量子退火算法  
- 量子支持向量机
- 量子神经网络
- 量子计算机

用户确认:
[✓] 量子算法 - 确认添加
[✓] 量子计算机 - 确认添加
[ ] 量子退火算法 - 太具体，暂不添加
```

#### 阶段3: 演化策略选择 (用户参与)
```
系统建议: Schema演化方案
方案A: 添加QuantumAlgorithm作为Algorithm的子类
方案B: 创建独立的QuantumAlgorithm实体
方案C: 创建QuantumTechnology上级分类

用户选择: [✓] 方案B - 创建独立实体
```

#### 阶段4: 结果确认 (用户参与)
```
系统展示: 演化后的Schema
- 原有: Algorithm, Task (2实体)
- 新增: QuantumAlgorithm, QuantumComputer (4实体)
- 新关系: runs_on, quantum_version_of

用户确认: [✓] 接受演化结果
```

### 📁 会话文件内容
- **输入文件**: `scenario_2_test_input.json` - 包含现有Schema和新文档
- **输出文件**: `scenario_2_test_result_simulated.json` - 包含演化过程和结果

---

## 场景3: Schema自动合并

### 👤 用户参与流程

#### 阶段1: 冲突检测 (系统自动)
```
系统检测: 发现Schema冲突
- Schema1: 算法性能Schema (Algorithm: "算法实体")
- Schema2: 机器学习Schema (Algorithm: "机器学习算法")
- 冲突: 同名实体但语义不同
```

#### 阶段2: 冲突解决策略选择 (用户参与)
```
系统提示: 检测到2个语义冲突

冲突1: Algorithm实体
- Schema1定义: "算法实体" (通用)
- Schema2定义: "机器学习算法" (特定)
- 置信度: 0.600

解决选项:
[ ] 保留Schema1定义 (通用)
[ ] 保留Schema2定义 (特定)  
[✓] 合并定义 (综合描述)
[ ] 创建层次结构

冲突2: Performance实体
- Schema1: "性能指标"
- Schema2: "评估指标"
- 置信度: 0.500

解决选项:
[✓] 合并为"性能评估指标"
```

#### 阶段3: 合并结果确认 (用户参与)
```
系统展示: 合并后的统一Schema
- 实体数: 4个 (Algorithm, Performance, Dataset, Model)
- 关系数: 3个 (achieves, tested_on, trains)
- 冲突解决: 2个语义冲突已处理

用户确认: [✓] 接受合并结果
```

### 📁 会话文件内容
- **输入文件**: `scenario_3_test_input.json` - 包含冲突的Schema定义
- **输出文件**: `scenario_3_test_result_conflicts.json` - 包含冲突检测和合并结果

---

## 场景4: 交互式Schema优化

### 👤 用户参与流程

#### 阶段1: 不满意反馈 (用户主导)
```
用户反馈: "这个分类不够细致，我需要更详细的算法分类，
比如深度学习算法、传统机器学习算法、优化算法等，
还需要包含算法的性能指标和应用领域"

当前Schema: 基础算法Schema (2实体1关系)
```

#### 阶段2: 系统主动询问 (交互式)
```
系统提问: 基于您的反馈，我需要了解更多细节

问题1: 您希望如何细分算法类型？
用户回答: 分为深度学习、传统ML、优化算法三大类

问题2: 需要包含哪些性能指标？  
用户回答: 准确率、精确率、召回率、F1分数等

问题3: 关注哪些应用领域？
用户回答: 计算机视觉、自然语言处理、推荐系统

问题4: 是否需要算法复杂度信息？
用户回答: 是的，时间和空间复杂度都需要

问题5: 是否需要算法适用数据类型？
用户回答: 需要，图像、文本、表格、时序数据
```

#### 阶段3: 细化建议确认 (用户参与)
```
系统建议: 基于您的回答，建议以下优化

实体优化:
- 拆分Algorithm → DeepLearningAlgorithm, TraditionalMLAlgorithm, OptimizationAlgorithm
- 新增PerformanceMetric, ApplicationDomain, DataType实体

关系优化:  
- 新增hasPerformance, appliedTo, suitableFor关系

用户确认: [✓] 接受所有建议
```

#### 阶段4: 优化结果确认 (用户参与)
```
系统展示: 优化后的精细Schema
- 实体数: 7个 (从2个增加)
- 关系数: 6个 (从1个增加)
- 新增专业分类和性能指标

用户满意度评价:
[✓] 非常满意 - 分类更细致，符合需求
[ ] 基本满意 - 还需要小调整
[ ] 不满意 - 需要重新优化
```

### 📁 会话文件内容
- **输入文件**: `scenario_4_test_input.json` - 包含当前Schema和用户反馈
- **输出文件**: `scenario_4_test_result.json` - 包含优化过程和最终Schema

---

## 🔍 会话文件解读指南

### 文件结构说明
每个会话文件都包含以下部分：

```json
{
  "scenario": "场景名称",
  "timestamp": "测试时间",
  "input": {
    "user_input": "用户输入的原始数据",
    "trigger_condition": "触发条件"
  },
  "process": {
    "steps": "处理步骤",
    "llm_calls": "LLM调用记录",
    "intermediate_results": "中间结果"
  },
  "output": {
    "final_schema": "最终Schema",
    "confidence": "置信度",
    "statistics": "统计信息"
  }
}
```

### 关键指标解读
- **置信度**: 0.0-1.0，越高表示结果越可靠
- **实体数量**: Schema包含的实体类型数量
- **关系数量**: Schema包含的关系类型数量
- **处理时间**: 算法执行耗时
- **LLM调用次数**: 使用AI的频率

### 用户决策点识别
在会话文件中查找以下标记：
- `"user_confirmation_required": true` - 需要用户确认
- `"user_choice_options": [...]` - 用户选择选项
- `"user_feedback": "..."` - 用户反馈内容

---

## 💡 使用建议

1. **场景1**: 适合探索性需求，当不确定需要什么Schema时使用
2. **场景2**: 适合已有基础Schema，需要扩展新领域时使用  
3. **场景3**: 适合整合多个相关Schema，统一数据模型时使用
4. **场景4**: 适合精细化调优，对Schema质量要求很高时使用

每个场景都可以根据实际需求调整用户参与的深度和频率。
