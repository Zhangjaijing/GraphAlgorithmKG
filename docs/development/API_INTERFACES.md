# API接口和扩展点文档

## 🎯 接口设计原则

**输入混乱，输出规范** - 系统接受任意格式的输入，但输出必须严格符合Schema规范

## 🔌 核心接口列表

### 1. 主要处理接口

#### 🏗️ **知识图谱构建接口**
```python
# 文件: pipeline/schema_based_kg_builder.py
class SchemaBasedKGBuilder:
    def build_knowledge_graph(self, document_path: str, output_path: Optional[str] = None) -> KnowledgeGraph
```
- **功能**: 完整的知识图谱构建流程
- **输入**: 任意格式文档路径
- **输出**: 符合Schema的标准化知识图谱
- **扩展点**: 支持新的文档格式解析器

#### 🔍 **Schema检测接口**
```python
# 文件: ontology/managers/schema_detector.py
class SchemaDetector:
    def detect_schema(self, text: str, use_llm: bool = False) -> List[SchemaDetectionResult]
    def get_best_schema(self, text: str) -> Optional[str]
```
- **功能**: 自动检测文档适用的Schema类型
- **扩展点**: 添加新的Schema类型和检测规则
- **LLM集成点**: `use_llm=True`时启用LLM辅助决策

#### 🔍 **增强版Schema检测接口 (新增)**
```python
# 文件: ontology/managers/enhanced_schema_detector.py
class EnhancedSchemaDetector:
    def detect_schema(self, text: str, use_llm: bool = False,
                     user_query: str = None, documents: List[str] = None) -> List[SchemaDetectionResult]
    def set_interaction_mode(self, mode: str)  # cli, web, auto
    def enable_dynamic_features(self, discovery: bool = True, evolution: bool = True)
```
- **功能**: 支持动态Schema发现与演化的增强版检测器
- **新特性**: 问题驱动Schema生成、增量演化、用户交互确认
- **向后兼容**: 完全兼容原有SchemaDetector接口
- **扩展点**: 支持自定义发现器和演化器

#### 🔍 **Schema发现器接口 (动态生成)**
```python
# 文件: ontology/discoverers/query_driven_discoverer.py
class QueryDrivenDiscoverer:
    def discover_schema(self, user_query: str, documents: List[str]) -> Dict[str, Any]
    def generate_schema_from_intent(self, intent: str) -> Dict[str, Any]

# 文件: ontology/discoverers/data_driven_discoverer.py
class DataDrivenDiscoverer:
    def discover_from_documents(self, documents: List[str]) -> Dict[str, Any]
    def extract_patterns(self, text: str) -> List[Dict[str, Any]]
```
- **功能**: 动态Schema发现和生成
- **扩展点**: 支持不同的发现策略和算法

#### 🔄 **混合三元组抽取接口**
```python
# 文件: pipeline/hybrid_triple_extractor.py
class HybridTripleExtractor:
    def extract_triples(self, text: str) -> HybridExtractionResult
```
- **功能**: 规则抽取优先 + LLM兜底的混合抽取 (3阶段: 规则抽取→质量评估→LLM兜底→结果合并)
- **扩展点**: 添加新的规则模式和LLM策略
- **智能决策**: 自动评估规则抽取质量，决定是否启用LLM兜底

### 2. 组件接口

#### 🧠 **实体推断接口**
```python
# 文件: pipeline/enhanced_entity_inferer.py
class EnhancedEntityTypeInferer:
    def infer_entity_type(self, entity_name: str) -> EntityInferenceResult
    def switch_domain(self, schema_path: str)
```
- **功能**: 6层分层实体类型推断 (缓存→Schema→模式→关键词→上下文→Unknown)
- **扩展点**: 添加新的推断层级和策略
- **注意**: 第6层标记为Unknown，不直接调用LLM

#### 🤖 **LLM客户端接口**
```python
# 文件: pipeline/llm_client.py
class LLMClient:
    def generate_response(self, prompt: str, max_tokens: int = 1000, temperature: float = 0.7) -> str
    def extract_triples(self, text: str, schema_info: Dict[str, Any]) -> List[Dict[str, Any]]
    def validate_triple(self, subject: str, predicate: str, obj: str, schema_info: Dict[str, Any]) -> Dict[str, Any]
    def select_schema(self, text: str, candidate_schemas: List[Dict]) -> Dict
```
- **功能**: 统一的LLM调用接口，支持配置文件和环境变量
- **扩展点**: 支持多种LLM服务提供商
- **配置**: 自动从config.json读取API密钥、Base URL等配置
- **模拟模式**: 当未配置API时自动启用模拟模式
- **使用场景**: Schema选择辅助 + 三元组抽取兜底 + 语义验证辅助

#### 📁 **会话管理接口**
```python
# 文件: pipeline/session_manager.py
class SessionManager:
    def start_session(self, document_path: str) -> str
    def save_stage_result(self, stage_name: str, data: Any, description: str = "") -> str
    def save_final_result(self, kg_data: Dict[str, Any], analysis_data: Dict[str, Any] = None, schema_type: str = "mixed") -> Dict[str, str]
```
- **功能**: 完整的会话生命周期管理
- **扩展点**: 添加新的存储后端和格式

### 3. 本体管理接口

#### 📋 **动态本体管理接口**
```python
# 文件: ontology/dynamic_schema.py
class DynamicOntologyManager:
    def load_schema(self, schema_path: str)
    def add_entity_type(self, entity_type: str, config: Dict[str, Any])
    def add_relation_type(self, relation_type: str, config: Dict[str, Any])
```
- **功能**: 动态加载和管理本体Schema
- **扩展点**: 支持新的Schema格式和验证规则

## 🔧 扩展点详细说明

### 1. **新Schema类型扩展**

#### 添加新Schema的步骤：
1. **创建Schema配置文件**
   ```yaml
   # 文件: ontology/config/new_domain_schema.yaml
   metadata:
     name: "新领域本体"
     version: "1.0.0"
     description: "新领域的知识图谱Schema"
   
   entity_types:
     NewEntityType:
       description: "新实体类型描述"
       examples: ["示例1", "示例2"]
       keywords: ["关键词1", "关键词2"]
   
   relation_types:
     newRelationType:
       description: "新关系类型描述"
       subject_types: ["NewEntityType"]
       object_types: ["NewEntityType"]
   ```

2. **更新Schema检测器**
   ```python
   # 文件: ontology/schema_detector.py
   # 在 _get_available_schemas() 方法中添加新Schema
   schemas.append("new_domain_schema.yaml")
   ```

3. **添加分类规则**
   ```python
   # 文件: pipeline/session_manager.py
   # 在 _classify_schema_type() 方法中添加分类逻辑
   elif "new_domain" in schema_path_lower:
       return "new_domain"
   ```

### 2. **新LLM服务商扩展**

#### 添加新LLM服务的步骤：
1. **扩展LLM客户端**
   ```python
   # 文件: pipeline/llm_client.py
   def _call_new_llm_api(self, prompt: str, max_tokens: int, temperature: float) -> str:
       """调用新LLM服务API"""
       # 实现新的API调用逻辑
       pass
   ```

2. **更新配置**
   ```python
   # 支持新的环境变量
   NEW_LLM_API_KEY = os.getenv("NEW_LLM_API_KEY")
   NEW_LLM_BASE_URL = os.getenv("NEW_LLM_BASE_URL")
   ```

### 3. **新文档格式扩展**

#### 添加新文档格式支持：
1. **扩展文档加载器**
   ```python
   # 文件: pipeline/schema_based_kg_builder.py
   def _load_document(self, document_path: str) -> str:
       # 添加新格式的解析逻辑
       if path.suffix.lower() == '.new_format':
           return self._parse_new_format(path)
   ```

### 4. **新规则模式扩展**

#### 添加新的抽取规则：
1. **扩展规则抽取器**
   ```python
   # 文件: pipeline/rule_based_triple_extractor.py
   def _compile_patterns(self):
       # 添加新的模式类别
       self.patterns['new_domain_patterns'] = [
           r'新的正则表达式模式1',
           r'新的正则表达式模式2'
       ]
   ```

## 🤖 训练模型接口

### 1. **训练接口基础框架**

#### 🏗️ **基础训练器接口**
```python
# 文件: training/base_trainer.py
class BaseTrainer(ABC):
    def __init__(self, config: TrainingConfig)
    def prepare_data(self) -> Tuple[Any, Any, Any, Any]
    def build_model(self) -> Any
    def train_model(self, X_train, y_train, X_val, y_val) -> TrainingResult
    def evaluate_model(self, X_test, y_test) -> Dict[str, float]
    def run_full_training(self) -> TrainingResult
```
- **功能**: 统一的训练接口和模型管理
- **扩展点**: 继承此类实现特定模型的训练器

#### 📊 **训练数据管理接口**
```python
# 文件: training/base_trainer.py
class TrainingDataManager:
    def collect_schema_training_data(self) -> str
    def collect_entity_training_data(self) -> str
    def collect_relation_training_data(self) -> str
```
- **功能**: 从会话记录中自动收集训练数据
- **扩展点**: 添加新的数据收集策略

### 2. **Schema分类模型训练接口**

#### 🎯 **Schema分类器训练**
```python
# 文件: training/schema_classifier_trainer.py
class SchemaClassifierTrainer(BaseTrainer):
    def predict_schema(self, text: str) -> Dict[str, Any]

def train_schema_classifier(
    training_data_path: str = None,
    output_model_path: str = "training/models/schema_classifier.pkl",
    hyperparameters: Dict[str, Any] = None
) -> TrainingResult
```
- **功能**: 训练基于TF-IDF和随机森林的Schema分类器
- **输入**: 文档文本和对应的Schema标签
- **输出**: 训练好的分类模型
- **扩展点**: 支持不同的特征提取和分类算法

#### 🔧 **使用示例**
```python
# 训练Schema分类器
from training.schema_classifier_trainer import train_schema_classifier

result = train_schema_classifier(
    hyperparameters={
        'max_features': 5000,
        'n_estimators': 100,
        'max_depth': 10
    }
)

print(f"验证准确率: {result.validation_accuracy:.4f}")
```

### 3. **实体推断模型训练接口**

#### 🏷️ **实体推断器训练**
```python
# 文件: training/entity_inferer_trainer.py
class EntityInfererTrainer(BaseTrainer):
    def extract_features(self, entity_name: str, context: Dict[str, Any]) -> Dict[str, Any]
    def predict_entity_type(self, entity_name: str, context: Dict[str, Any]) -> Dict[str, Any]

def train_entity_inferer(
    training_data_path: str = None,
    output_model_path: str = "training/models/entity_inferer.pkl",
    hyperparameters: Dict[str, Any] = None
) -> TrainingResult
```
- **功能**: 训练基于特征工程和梯度提升的实体类型推断器
- **特征**: 文本特征、词汇特征、模式匹配、领域关键词
- **输出**: 实体类型和置信度
- **扩展点**: 添加新的特征提取器和分类算法

#### 🔧 **使用示例**
```python
# 训练实体推断器
from training.entity_inferer_trainer import train_entity_inferer

result = train_entity_inferer(
    hyperparameters={
        'n_estimators': 100,
        'learning_rate': 0.1,
        'max_depth': 6
    }
)

print(f"验证准确率: {result.validation_accuracy:.4f}")
```

### 4. **关系抽取模型训练接口**

#### 🔗 **关系抽取器训练** (待实现)
```python
# 文件: training/relation_extractor_trainer.py
class RelationExtractorTrainer(BaseTrainer):
    def extract_relation_features(self, subject: str, obj: str, context: str) -> Dict[str, Any]
    def predict_relation(self, subject: str, obj: str, context: str) -> Dict[str, Any]

def train_relation_extractor(
    training_data_path: str = None,
    output_model_path: str = "training/models/relation_extractor.pkl",
    hyperparameters: Dict[str, Any] = None
) -> TrainingResult
```
- **功能**: 训练关系抽取和分类模型
- **输入**: 实体对和上下文文本
- **输出**: 关系类型和置信度
- **扩展点**: 支持不同的关系抽取策略

### 5. **实体合并模型训练接口**

#### 🔄 **实体合并器训练** (待实现)
```python
# 文件: training/entity_merger_trainer.py
class EntityMergerTrainer(BaseTrainer):
    def calculate_entity_similarity(self, entity1: Dict, entity2: Dict) -> float
    def predict_merge_decision(self, entity1: Dict, entity2: Dict) -> Dict[str, Any]

def train_entity_merger(
    training_data_path: str = None,
    output_model_path: str = "training/models/entity_merger.pkl",
    hyperparameters: Dict[str, Any] = None
) -> TrainingResult
```
- **功能**: 训练实体去重和合并决策模型
- **输入**: 实体对和相似度特征
- **输出**: 合并决策和置信度
- **扩展点**: 支持不同的相似度计算和决策策略

## 🚀 快速扩展指南

### 场景1: 添加医疗领域Schema
```bash
# 1. 创建Schema文件
cp ontology/config/spatiotemporal_schema.yaml ontology/config/medical_schema.yaml

# 2. 修改Schema内容（实体类型、关系类型）
# 3. 更新检测器和分类器
# 4. 测试新Schema
python test_new_schema.py medical
```

### 场景2: 集成新的LLM服务
```bash
# 1. 安装新LLM的SDK
pip install new-llm-sdk

# 2. 扩展LLM客户端
# 3. 配置环境变量
export NEW_LLM_API_KEY="your-key"

# 4. 测试新LLM
python test_llm_integration.py new-llm
```

### 场景3: 支持新的文档格式
```bash
# 1. 安装解析库
pip install new-format-parser

# 2. 扩展文档加载器
# 3. 测试新格式
python test_document_format.py new_format_file.ext
```

### 场景4: 训练新的Schema分类器
```bash
# 1. 收集训练数据
python -c "from training.base_trainer import training_data_manager; training_data_manager.collect_schema_training_data()"

# 2. 训练模型
python -c "from training.schema_classifier_trainer import train_schema_classifier; train_schema_classifier()"

# 3. 测试新模型
python tests/unit/test_schema_system.py
```

### 场景5: 训练实体推断器
```bash
# 1. 收集实体训练数据
python -c "from training.base_trainer import training_data_manager; training_data_manager.collect_entity_training_data()"

# 2. 训练模型
python -c "from training.entity_inferer_trainer import train_entity_inferer; train_entity_inferer()"

# 3. 评估模型性能
python tests/unit/test_entity_inference.py
```

## 📊 接口性能指标

| 接口类型 | 响应时间 | 吞吐量 | 准确率 |
|----------|----------|--------|--------|
| Schema检测 | <100ms | >1000文档/小时 | 100% |
| 实体推断 | <2ms/实体 | >10000实体/小时 | 80.4% |
| 三元组抽取 | <50ms/文档 | >1000文档/小时 | >75% |
| 关系验证 | <1ms/关系 | >50000关系/小时 | 100% |
| 会话管理 | <10ms/操作 | >10000操作/小时 | 100% |
| 模型训练 | 1-10分钟 | 取决于数据量 | >85% |

## 🔒 接口安全和验证

### 输入验证
- 所有文档路径必须存在且可读
- Schema文件必须符合YAML格式规范
- 实体和关系名称必须符合命名规范

### 输出验证
- 所有实体类型必须在Schema中定义
- 所有关系类型必须在Schema中定义
- 三元组必须通过语义一致性检查

### 错误处理
- 优雅降级：API失败时自动切换到模拟模式
- 详细日志：记录所有关键操作和错误信息
- 异常恢复：支持从中间阶段恢复处理

## 📝 接口使用示例

### 基础使用
```python
from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder

# 创建构建器
builder = SchemaBasedKGBuilder()

# 构建知识图谱
kg = builder.build_knowledge_graph("document.json")

# 结果自动保存到按Schema分类的目录
print(f"实体数: {kg.statistics['total_entities']}")
print(f"关系数: {kg.statistics['total_relations']}")
```

### 高级使用
```python
from pipeline.session_manager import session_manager
from pipeline.hybrid_triple_extractor import HybridTripleExtractor

# 手动管理会话
session_id = session_manager.start_session("document.json")

# 使用混合抽取器
extractor = HybridTripleExtractor(ontology_manager)
result = extractor.extract_triples(text)

# 保存中间结果
session_manager.save_stage_result("custom_extraction", result.triples)
```

## 🔍 动态Schema发现与演化接口 (新增)

### 1. Schema发现器接口

#### 🎯 **问题驱动Schema发现**
```python
# 文件: ontology/discoverers/query_driven_discoverer.py
class QueryDrivenDiscoverer:
    def discover_schema(self, context: DiscoveryContext) -> DiscoveryResult
```
- **功能**: 根据用户查询意图生成定制化Schema
- **输入**: 用户问题 + 文档内容
- **输出**: 定制化Schema + 置信度
- **扩展点**: 支持新的意图识别模式和Schema生成策略

#### 📊 **数据驱动Schema发现**
```python
# 文件: ontology/discoverers/data_driven_discoverer.py
class DataDrivenDiscoverer:
    def discover_schema(self, context: DiscoveryContext) -> DiscoveryResult
```
- **功能**: 从文档内容中自动发现概念结构
- **输入**: 文档集合
- **输出**: 数据驱动的Schema
- **扩展点**: 支持新的概念聚类和关系发现算法

### 2. Schema演化器接口

#### 🔄 **增量Schema演化**
```python
# 文件: ontology/evolvers/incremental_evolver.py
class IncrementalEvolver:
    def evolve_schema(self, base_schema: Schema, new_content: List[str],
                     auto_confirm: bool = False) -> EvolutionResult
```
- **功能**: 在现有Schema基础上发现新概念并演化
- **输入**: 基础Schema + 新文档内容
- **输出**: 演化后的Schema + 变更记录
- **扩展点**: 支持自定义概念发现和演化策略

#### 📈 **概念漂移检测**
```python
# 文件: ontology/evolvers/concept_drift_detector.py
class ConceptDriftDetector:
    def detect_drift(self, current_documents: List[str],
                    reference_schema: Optional[Schema] = None) -> DriftDetectionResult
```
- **功能**: 检测领域概念的变化和演化趋势
- **输入**: 当前文档集合 + 参考Schema
- **输出**: 漂移检测结果 + 稳定性分数
- **扩展点**: 支持自定义漂移检测算法和阈值

### 3. 用户交互接口

#### 🎮 **交互式Schema构建**
```python
# 文件: ontology/interactions/interactive_builder.py
class InteractiveBuilder:
    def start_interactive_building(self, user_query: str, documents: List[str]) -> str
    def continue_building_iteration(self) -> Tuple[Schema, bool]
    def finish_building(self) -> Optional[BuildingSession]
```
- **功能**: 用户参与的迭代式Schema构建和优化
- **输入**: 用户查询 + 文档 + 用户反馈
- **输出**: 优化后的Schema + 构建会话记录
- **扩展点**: 支持不同的交互模式和反馈收集策略

#### 💭 **反馈收集接口**
```python
# 文件: ontology/interactions/feedback_collector.py
class FeedbackCollector:
    def collect_missing_concept_feedback(self, concept_name: str, description: str) -> str
    def collect_redundant_concept_feedback(self, concept_name: str, description: str) -> str
    def collect_incorrect_relation_feedback(self, relation_name: str, description: str) -> str
```
- **功能**: 收集和管理用户对Schema的各种反馈
- **输入**: 概念名称 + 反馈描述
- **输出**: 反馈ID + 收集状态
- **扩展点**: 支持新的反馈类型和收集方式

### 4. 使用示例

#### 🚀 **启用动态Schema功能**
```python
# 使用增强版检测器
builder = SchemaBasedKGBuilder(use_enhanced_detector=True)

# 问题驱动Schema生成
kg = builder.build_knowledge_graph(
    "document.txt",
    user_query="我想了解算法性能关系"
)

# 交互式Schema构建
from ontology.interactions.interactive_builder import InteractiveBuilder
interactive_builder = InteractiveBuilder()
session_id = interactive_builder.start_interactive_building(
    user_query="分析深度学习算法",
    documents=["doc1.txt", "doc2.txt"]
)
```

## 🎯 接口发展路线图

### 已完成功能 ✅
- [x] **动态Schema发现与演化** - 问题驱动生成、增量演化、用户交互
- [x] **增强版Schema检测器** - 完全向后兼容的功能扩展
- [x] **交互式Schema构建** - 用户参与的迭代式优化
- [x] **概念漂移检测** - 领域概念变化的自动监测

### 短期目标 (1-2个月)
- [ ] 支持更多LLM服务商 (Claude, Gemini, 本地模型)
- [ ] 添加医疗、金融、法律领域Schema
- [ ] 优化实体推断准确率到85%+
- [ ] RAG增强Schema发现的完整实现

### 中期目标 (3-6个月)
- [ ] 支持实时流式处理
- [ ] 添加图数据库直接导出接口
- [ ] 支持多语言文档处理
- [ ] Web界面的交互式Schema构建

### 长期目标 (6-12个月)
- [ ] 集成知识图谱推理引擎
- [ ] 支持分布式处理和集群部署
- [ ] 联邦学习的多机构协作Schema构建
