# 数据管理系统

本目录包含GraphAlgorithmKG项目的所有数据文件，采用统一的数据管理结构。

## 📁 目录结构

```
data/
├── documents/              # 原始文档数据
│   ├── samples/           # 示例文档
│   ├── dodaf/             # DODAF相关文档
│   ├── dodaf_enterprise_architecture.json
│   ├── dodaf_spatiotemporal.json
│   └── pure_dodaf_structure.json
├── knowledge/              # 知识数据
│   ├── seed/              # 种子知识
│   │   ├── graph_algorithm_triples.csv
│   │   └── kg_expansion_triples.csv
│   └── generated/         # 生成的知识
├── training/               # 训练数据
│   ├── raw/               # 原始训练数据
│   ├── processed/         # 处理后数据
│   └── splits/            # 数据分割
├── test/                   # 测试专用数据
│   ├── scenarios/         # 场景测试数据
│   └── fixtures/          # 测试固件
├── cache/                  # 缓存数据
│   ├── schemas/           # Schema缓存
│   └── entities/          # 实体缓存
├── data_manager.py         # 数据管理工具
└── README.md              # 本文档
```

## 🔧 数据管理工具

### 使用DataManager类

```python
from data.data_manager import DataManager

# 创建数据管理器
dm = DataManager()

# 加载文档数据
documents = dm.load_documents('samples')  # 或 'dodaf', 'test'

# 加载知识数据
knowledge = dm.load_knowledge_data('seed')  # 或 'generated', 'all'

# 加载训练数据
training = dm.load_training_data('train')  # 或 'val', 'test', 'all'

# 加载测试数据
test_data = dm.load_test_data('scenarios')  # 或 'fixtures', 'all'

# 验证数据完整性
validation = dm.validate_data_integrity()

# 清理缓存
cleaned = dm.clean_cache()

# 获取数据概览
summary = dm.get_data_summary()
```

### 直接运行数据管理工具

```bash
# 运行数据管理工具演示
python data/data_manager.py
```

## 📊 数据类型说明

### 文档数据 (documents/)
- **格式**: JSON, Markdown, Text
- **用途**: 原始文档，用于知识图谱构建和Schema检测
- **示例**: DODAF架构文档、技术规范文档

### 知识数据 (knowledge/)
- **seed/**: 人工标注的种子知识，CSV格式的三元组
- **generated/**: 系统生成的知识，JSON格式
- **用途**: 知识图谱构建的基础数据

### 训练数据 (training/)
- **raw/**: 原始训练数据
- **processed/**: 预处理后的训练数据
- **splits/**: 训练/验证/测试数据分割
- **用途**: 机器学习模型训练

### 测试数据 (test/)
- **scenarios/**: 特定场景的测试数据
- **fixtures/**: 测试固件和模拟数据
- **用途**: 单元测试、集成测试、系统测试

### 缓存数据 (cache/)
- **schemas/**: Schema检测结果缓存
- **entities/**: 实体识别结果缓存
- **用途**: 提高系统性能，避免重复计算

## 🔍 数据文件详情

### 重要数据文件

#### 文档数据
- `dodaf_enterprise_architecture.json`: 企业架构DODAF文档
- `dodaf_spatiotemporal.json`: 时空DODAF文档
- `pure_dodaf_structure.json`: 纯DODAF结构文档

#### 知识数据
- `graph_algorithm_triples.csv`: 图算法知识三元组
- `kg_expansion_triples.csv`: 知识图谱扩展三元组

### 数据格式规范

#### JSON文档格式
```json
{
  "title": "文档标题",
  "content": "文档内容",
  "metadata": {
    "author": "作者",
    "date": "日期",
    "type": "文档类型"
  },
  "expected_schema": "期望的Schema类型",
  "expected_triples": [
    {
      "subject": "主语",
      "predicate": "谓语", 
      "object": "宾语"
    }
  ]
}
```

#### CSV三元组格式
```csv
subject,predicate,object
实体1,关系,实体2
算法,属于,深度学习
```

## 🛠️ 数据维护

### 添加新数据
1. 将数据文件放入相应的目录
2. 确保文件格式符合规范
3. 运行数据完整性验证
4. 更新相关的索引文件

### 数据备份
- 重要数据文件应定期备份
- 使用版本控制管理数据变更
- 缓存数据可以重新生成，不需要备份

### 数据清理
```python
# 清理缓存数据
dm = DataManager()
cleaned_count = dm.clean_cache()
print(f"清理了 {cleaned_count['total']} 个缓存文件")

# 验证数据完整性
validation = dm.validate_data_integrity()
if validation['status'] != 'success':
    print("数据完整性检查发现问题:")
    for error in validation['errors']:
        print(f"  错误: {error}")
    for warning in validation['warnings']:
        print(f"  警告: {warning}")
```

## 📈 数据统计

当前数据概览：
- 文档数据: 4个JSON文件
- 知识数据: 2个CSV文件
- 训练数据: 待添加
- 测试数据: 待添加
- 总大小: ~150KB

## 🔒 数据安全

### 访问控制
- 敏感数据应设置适当的文件权限
- 不要在版本控制中包含敏感信息
- 使用环境变量管理API密钥等配置

### 数据隐私
- 确保测试数据不包含真实的敏感信息
- 对个人信息进行匿名化处理
- 遵循相关的数据保护法规

## 🚀 性能优化

### 缓存策略
- 启用Schema检测结果缓存
- 缓存实体识别结果
- 定期清理过期缓存

### 数据加载优化
- 使用懒加载避免内存浪费
- 批量处理大量数据
- 压缩存储大文件

## 📞 获取帮助

如果在使用数据管理系统时遇到问题：

1. 查看本文档的相关部分
2. 运行数据完整性验证
3. 检查日志文件
4. 联系项目维护者

---

💡 **提示**: 使用DataManager类可以方便地管理所有数据操作，避免直接操作文件系统。
