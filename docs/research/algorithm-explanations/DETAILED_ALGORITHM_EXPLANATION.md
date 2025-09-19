# Schema系统四个场景详细算法说明

## 概览

Schema系统包含四个核心应用场景，每个场景都有特定的触发条件、算法流程和用户参与点。

---

## 场景1: 问题驱动Schema生成

### 🎯 触发条件
- **输入**: 无预定义Schema + 用户查询
- **示例**: 用户问"我想了解这些文档中的算法性能关系"，但系统中没有匹配的Schema

### 🔄 算法流程

#### 步骤1: 常规Schema检测 (无LLM)
```python
# 算法: 基于关键词匹配和本体相似度
def detect_schema(text, use_llm=False):
    results = []
    for schema_file, manager in ontology_managers.items():
        # 1. 本体匹配 (40%权重)
        ontology_score = calculate_entity_keyword_overlap(text, manager)
        
        # 2. 文档结构匹配 (30%权重) 
        document_score = analyze_document_structure(text, manager)
        
        # 3. 综合评分
        final_score = 0.4 * ontology_score + 0.3 * document_score
        
        if final_score > 0.05:  # 阈值检查
            results.append(DetectionResult(schema_file, final_score))
    
    return results
```

#### 步骤2: 动态Schema发现 (使用LLM)
```python
# 算法: LLM分析文档内容生成定制Schema
def dynamic_schema_discovery(text, user_query):
    # 1. LLM分析文档内容
    prompt = f"""
    分析以下文档内容和用户查询，生成适合的Schema:
    用户查询: {user_query}
    文档内容: {text}
    
    请生成包含实体类型和关系类型的Schema
    """
    
    # 2. LLM生成Schema结构
    llm_response = call_llm(prompt)
    
    # 3. 解析并创建Schema对象
    schema = parse_llm_response_to_schema(llm_response)
    
    return DetectionResult("dynamic_generated", 0.95, schema=schema)
```

### 👤 用户参与点
- **输入阶段**: 用户提供查询和文档
- **确认阶段**: 用户确认生成的Schema是否符合需求

### 📊 测试结果解读
- **输入**: 算法性能相关文档 + 查询
- **输出**: 生成了包含Algorithm、PerformanceMetric、Dataset实体的Schema
- **置信度**: 0.950 (非常高)

---

## 场景2: Schema增量演化

### 🎯 触发条件
- **输入**: 现有Schema + 发现新概念
- **示例**: 已有算法Schema，但文档中出现"量子算法"等新概念

### 🔄 算法流程

#### 步骤1: 匹配现有Schema (无LLM)
```python
# 算法: 与场景1相同的检测算法
existing_results = detect_schema(text, use_llm=False)
if existing_results and existing_results[0].confidence > 0.05:
    base_schema = existing_results[0].schema
```

#### 步骤2: 新概念识别 (使用LLM)
```python
# 算法: LLM识别文档中的新概念
def identify_new_concepts(text, existing_schema):
    existing_entities = [e.name for e in existing_schema.entity_types]
    
    prompt = f"""
    现有Schema实体: {existing_entities}
    文档内容: {text}
    
    识别文档中不在现有Schema中的新概念
    """
    
    new_concepts = call_llm(prompt)
    return parse_concepts(new_concepts)
```

#### 步骤3: Schema演化 (使用LLM)
```python
# 算法: 基于新概念扩展Schema
def evolve_schema(base_schema, new_concepts):
    prompt = f"""
    基础Schema: {base_schema.to_dict()}
    新发现概念: {new_concepts}
    
    请扩展Schema，添加新的实体类型和关系类型
    """
    
    evolved_schema_data = call_llm(prompt)
    return create_evolved_schema(base_schema, evolved_schema_data)
```

### 👤 用户参与点
- **确认阶段**: 用户确认识别出的新概念是否正确
- **选择阶段**: 用户选择如何将新概念集成到Schema中

### 📊 测试结果解读
- **输入**: 基础算法Schema + 量子算法文档
- **输出**: 从2个实体扩展到4个实体，新增QuantumAlgorithm、QuantumComputer
- **新关系**: runs_on、quantum_version_of

---

## 场景3: Schema自动合并

### 🎯 触发条件
- **输入**: 多个相似Schema产生冲突
- **示例**: 同时匹配到"算法Schema"和"计算方法Schema"

### 🔄 算法流程

#### 步骤1: 冲突检测 (无LLM)
```python
# 算法: 基于名称和语义相似度检测冲突
def detect_conflicts(schemas):
    conflicts = []
    
    for i, schema1 in enumerate(schemas):
        for j, schema2 in enumerate(schemas[i+1:], i+1):
            # 检测实体名称冲突
            for entity1 in schema1.entity_types:
                for entity2 in schema2.entity_types:
                    if entity1.name == entity2.name:
                        # 计算语义相似度
                        similarity = calculate_semantic_similarity(
                            entity1.description, entity2.description
                        )
                        
                        if similarity < 0.8:  # 语义差异阈值
                            conflicts.append(SemanticConflict(
                                entity1, entity2, 1.0 - similarity
                            ))
    
    return conflicts
```

#### 步骤2: 语义对齐 (使用LLM)
```python
# 算法: LLM分析冲突实体的语义关系
def semantic_alignment(conflict):
    prompt = f"""
    实体1: {conflict.entity1.name} - {conflict.entity1.description}
    实体2: {conflict.entity2.name} - {conflict.entity2.description}
    
    分析这两个实体的语义关系，建议合并策略
    """
    
    alignment_strategy = call_llm(prompt)
    return parse_alignment_strategy(alignment_strategy)
```

#### 步骤3: 自动合并 (部分使用LLM)
```python
# 算法: 基于冲突解决策略合并Schema
def merge_schemas(schemas, conflicts):
    merged_schema = Schema()
    
    # 1. 合并无冲突的实体 (无LLM)
    for schema in schemas:
        for entity in schema.entity_types:
            if not has_conflict(entity, conflicts):
                merged_schema.add_entity(entity)
    
    # 2. 解决冲突实体 (使用LLM)
    for conflict in conflicts:
        if conflict.auto_resolvable:
            resolved_entity = auto_resolve_conflict(conflict)
        else:
            resolved_entity = llm_resolve_conflict(conflict)
        
        merged_schema.add_entity(resolved_entity)
    
    return merged_schema
```

### 👤 用户参与点
- **选择阶段**: 用户选择冲突解决策略
- **确认阶段**: 用户确认合并后的Schema

### 📊 测试结果解读
- **输入**: 算法性能Schema + 机器学习算法Schema
- **冲突**: 检测到2个语义冲突 (Algorithm、Performance实体)
- **输出**: 合并后的统一Schema，保留4个实体3个关系

---

## 场景4: 交互式Schema优化

### 🎯 触发条件
- **输入**: 用户对当前Schema不满意
- **示例**: 用户说"这个分类不够细致"

### 🔄 算法流程

#### 步骤1: 主动询问 (使用LLM)
```python
# 算法: LLM生成针对性问题
def generate_optimization_questions(current_schema, user_feedback):
    prompt = f"""
    当前Schema: {current_schema.to_dict()}
    用户反馈: {user_feedback}
    
    生成5个问题来了解用户的具体优化需求
    """
    
    questions = call_llm(prompt)
    return parse_questions(questions)
```

#### 步骤2: 细化建议 (使用LLM)
```python
# 算法: 基于用户反馈生成优化建议
def generate_refinement_suggestions(schema, feedback, requirements):
    prompt = f"""
    当前Schema: {schema.to_dict()}
    用户反馈: {feedback}
    优化需求: {requirements}
    
    生成具体的Schema优化建议，包括:
    1. 实体类型的拆分/合并/新增
    2. 关系类型的调整
    3. 优化理由
    """
    
    suggestions = call_llm(prompt)
    return parse_suggestions(suggestions)
```

#### 步骤3: 迭代优化 (使用LLM)
```python
# 算法: 基于建议生成优化后的Schema
def optimize_schema(current_schema, suggestions):
    optimized_schema = current_schema.copy()
    
    # 应用实体优化
    for entity_suggestion in suggestions.entity_refinements:
        if entity_suggestion.action == 'split':
            optimized_schema.split_entity(
                entity_suggestion.original,
                entity_suggestion.new_entities
            )
        elif entity_suggestion.action == 'add':
            for new_entity in entity_suggestion.new_entities:
                optimized_schema.add_entity(create_entity(new_entity))
    
    # 应用关系优化
    for relation_suggestion in suggestions.relation_refinements:
        if relation_suggestion.action == 'add':
            for new_relation in relation_suggestion.new_relations:
                optimized_schema.add_relation(create_relation(new_relation))
    
    return optimized_schema
```

### 👤 用户参与点
- **反馈阶段**: 用户提供对当前Schema的不满意点
- **回答阶段**: 用户回答系统的优化问题
- **确认阶段**: 用户确认优化后的Schema

### 📊 测试结果解读
- **输入**: 基础算法Schema (2实体1关系) + 用户不满意反馈
- **过程**: 系统提出5个问题，生成2个实体建议1个关系建议
- **输出**: 精细化Schema (7实体6关系)，包含DeepLearningAlgorithm等专业分类

---

## LLM使用总结

### 🤖 使用LLM的场景
1. **场景1**: 动态Schema生成 (步骤2)
2. **场景2**: 新概念识别 + Schema演化 (步骤2,3)
3. **场景3**: 语义对齐 + 冲突解决 (步骤2,3部分)
4. **场景4**: 主动询问 + 细化建议 + 迭代优化 (步骤1,2,3)

### 🔧 不使用LLM的场景
1. **所有场景**: 基础Schema检测 (关键词匹配、本体相似度)
2. **场景3**: 冲突检测 (名称匹配、语义相似度计算)
3. **场景3**: 简单冲突的自动解决

---

## 会话文件说明

每个场景的测试结果都保存在对应的JSON文件中，包含：
- **输入数据**: 用户查询、文档内容、Schema定义
- **处理过程**: 算法执行步骤、中间结果
- **输出结果**: 生成/优化后的Schema、置信度、统计信息

用户可以通过查看这些文件了解每个场景的完整执行流程。
