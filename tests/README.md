# 测试系统说明

本目录包含GraphAlgorithmKG项目的所有测试文件，采用分层测试架构。

## 🏗️ 测试结构

```
tests/
├── unit/                           # 单元测试
│   ├── test_dynamic_features.py    # 动态Schema功能测试
│   ├── test_kg_builder.py          # KG构建器测试
│   ├── test_schema_system.py       # Schema系统测试
│   └── test_session_system.py      # 会话系统测试
├── integration/                    # 集成测试
│   ├── test_four_scenarios.py      # 四个Schema场景集成测试
│   └── test_multi_schema_kg.py     # 多Schema集成测试
├── system/                         # 系统测试
│   └── test_complete_pipeline.py   # 完整Pipeline测试
├── data/                           # 测试数据（空目录，数据已迁移）
├── run_all_tests.py                # 原测试运行器（保留兼容性）
├── run_tests.py                    # 新统一测试运行器
└── README.md                       # 本文档
```

## 🚀 运行测试

### 使用新的统一测试运行器（推荐）

```bash
# 运行所有测试
python tests/run_tests.py

# 运行特定类型的测试
python tests/run_tests.py --type unit        # 单元测试
python tests/run_tests.py --type integration # 集成测试
python tests/run_tests.py --type system      # 系统测试

# 运行指定测试文件
python tests/run_tests.py --file tests/unit/test_dynamic_features.py

# 列出所有可用测试
python tests/run_tests.py --list
```

## 📊 测试数据

测试数据已统一迁移到项目根目录的 `data/` 目录中：
- `data/documents/`: 测试文档
- `data/test/`: 测试专用数据
- `data/training/`: 训练数据

## 运行测试

### 运行所有测试
```bash
python tests/run_all_tests.py
```

### 运行单个测试
```bash
# 系统测试
python tests/system/test_complete_pipeline.py

# 单元测试
python tests/unit/test_kg_builder.py
python tests/unit/test_schema_system.py
python tests/unit/test_session_system.py

# 集成测试
python tests/integration/test_multi_schema_kg.py
```

### 使用测试工具
```bash
# 清理结果目录
python tests/utils/cleanup_results.py

# 重组Schema分类
python tests/utils/reorganize_by_schema.py

# 快速启动
python tests/utils/quick_start.py
```

## 测试结果
- 测试报告: `tests/test_report.md`
- 测试日志: `logs/` 目录
- 测试数据: `tests/data/` 目录

## 预期结果
- Schema检测准确率: 100%
- 实体推断准确率: >80%
- 关系验证准确率: 100%
- 端到端处理时间: <5s/文档
