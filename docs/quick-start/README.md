# 快速开始指南

本目录包含快速开始的教程和示例，帮助新用户快速上手系统。

## 🚀 5分钟快速开始

### 1. 环境准备
```bash
# 激活环境
conda activate GraphAlgorithmKG

# 检查依赖
pip install -r requirements.txt
```

### 2. 配置API
```bash
# 复制配置模板
cp config.json.template config.json

# 编辑配置文件，填入API密钥
vim config.json
```

### 3. 运行第一个示例
```bash
# 基础知识图谱构建
python examples/basic/01_simple_kg_building.py

# Schema检测示例
python examples/basic/02_schema_detection.py
```

## 📋 示例说明

### 基础示例 (examples/basic/)
- `01_simple_kg_building.py` - 简单知识图谱构建
- `02_schema_detection.py` - Schema自动检测
- `03_custom_schema_test.py` - 自定义Schema测试

### 高级示例 (examples/advanced/)
- `05_schema_evolution.py` - Schema演化示例
- `06_schema_merging.py` - Schema合并示例

### 完整示例 (examples/complete/)
- `09_end_to_end_pipeline.py` - 端到端流程演示

### 交互示例 (examples/interactive/)
- `11_interactive_kg_building.py` - 交互式知识图谱构建

## 🎯 学习路径

### 新手路径
1. 运行 `01_simple_kg_building.py` 了解基本功能
2. 尝试 `02_schema_detection.py` 理解Schema检测
3. 查看生成的结果文件理解输出格式

### 进阶路径
1. 运行 `03_custom_schema_test.py` 学习自定义Schema
2. 尝试 `09_end_to_end_pipeline.py` 了解完整流程
3. 使用 `11_interactive_kg_building.py` 体验交互功能

## 📊 结果查看

### 生成的文件
- `results/knowledge_graphs/` - 知识图谱JSON文件
- `results/sessions/` - 详细会话记录
- `results/analysis/` - 分析结果

### 查看命令
```bash
# 查看最新生成的知识图谱
ls -la results/knowledge_graphs/general/

# 查看会话详情
cat results/sessions/*/05_final_kg.json | jq '.entities | length'
```

## ❓ 常见问题

### 1. API配置问题
确保 `config.json` 中的API密钥正确配置。

### 2. 依赖问题
运行 `pip install -r requirements.txt` 安装所有依赖。

### 3. 权限问题
确保对 `results/` 目录有写权限。

## 🔗 下一步
- 阅读 [用户指南](../user-guides/) 了解详细功能
- 查看 [开发文档](../development/) 了解技术细节
- 参考 [研究文档](../research/) 了解算法原理
