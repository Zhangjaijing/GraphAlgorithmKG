#!/usr/bin/env python3
"""
基础示例1: 简单知识图谱构建
演示最基本的知识图谱构建流程
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder
import networkx as nx


def simple_kg_building_demo():
    """简单知识图谱构建演示"""
    print("🏗️ 基础示例1: 简单知识图谱构建")
    print("=" * 60)
    
    # 准备测试文档
    document_content = """
    机器学习是人工智能的一个重要分支。深度学习是机器学习的子领域。
    卷积神经网络(CNN)是深度学习中的重要算法，主要用于图像识别任务。
    循环神经网络(RNN)适合处理序列数据，如自然语言处理任务。
    支持向量机(SVM)是传统机器学习算法，在小数据集上表现良好。
    """
    
    print("📄 输入文档:")
    print(document_content.strip())
    print()
    
    # 创建知识图谱构建器
    print("🔧 创建知识图谱构建器...")
    kg_builder = SchemaBasedKGBuilder()
    
    # 先保存文档内容到临时文件
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(document_content)
        temp_doc_path = f.name

    # 构建知识图谱
    print("🏗️ 构建知识图谱...")
    try:
        kg = kg_builder.build_knowledge_graph(
            document_path=temp_doc_path
        )
        
        if kg and len(kg.entities) > 0:
            print("✅ 知识图谱构建成功!")

            # 显示基本统计信息
            print(f"📊 图谱统计:")
            print(f"   实体数量: {len(kg.entities)}")
            print(f"   关系数量: {len(kg.relations)}")

            # 显示实体信息
            print(f"\n🔍 实体详情:")
            for i, entity in enumerate(kg.entities, 1):
                print(f"   {i:2d}. {entity.name} (类型: {entity.type})")

            # 显示关系信息
            print(f"\n🔗 关系详情:")
            for i, relation in enumerate(kg.relations, 1):
                print(f"   {i:2d}. {relation.subject_name} --[{relation.predicate}]--> {relation.object_name}")

            return kg
            
        else:
            print("❌ 知识图谱构建失败或为空")
            return None
            
    except Exception as e:
        print(f"❌ 构建过程中出现错误: {e}")
        return None
    finally:
        # 清理临时文件
        if 'temp_doc_path' in locals() and os.path.exists(temp_doc_path):
            os.unlink(temp_doc_path)


def analyze_kg_structure(kg):
    """分析知识图谱结构"""
    if not kg or not kg.entities:
        return

    print("\n🔍 图谱结构分析:")
    print("-" * 40)

    # 实体度分析（基于关系统计）
    entity_degrees = {}
    for relation in kg.relations:
        # 统计每个实体的连接数
        entity_degrees[relation.subject_name] = entity_degrees.get(relation.subject_name, 0) + 1
        entity_degrees[relation.object_name] = entity_degrees.get(relation.object_name, 0) + 1

    if entity_degrees:
        max_degree_entity = max(entity_degrees, key=entity_degrees.get)
        print(f"📈 最高连接度实体: {max_degree_entity} (连接数: {entity_degrees[max_degree_entity]})")

    # 实体类型统计
    entity_types = {}
    for entity in kg.entities:
        entity_type = entity.type
        entity_types[entity_type] = entity_types.get(entity_type, 0) + 1

    print(f"📊 实体类型分布:")
    for entity_type, count in sorted(entity_types.items()):
        print(f"   {entity_type}: {count} 个")

    # 关系类型统计
    relation_types = {}
    for relation in kg.relations:
        relation_type = relation.predicate
        relation_types[relation_type] = relation_types.get(relation_type, 0) + 1

    print(f"🔗 关系类型分布:")
    for relation_type, count in sorted(relation_types.items()):
        print(f"   {relation_type}: {count} 个")


def save_kg_results(kg, output_dir="results/examples"):
    """保存知识图谱结果"""
    if not kg:
        return

    print(f"\n💾 保存结果到 {output_dir}/")

    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    try:
        # 保存实体和关系的详细信息
        info_file = output_path / "simple_kg_info.txt"
        with open(info_file, 'w', encoding='utf-8') as f:
            f.write("知识图谱信息\n")
            f.write("=" * 40 + "\n\n")

            f.write(f"实体数量: {len(kg.entities)}\n")
            f.write(f"关系数量: {len(kg.relations)}\n\n")

            f.write("实体列表:\n")
            for entity in kg.entities:
                f.write(f"  - {entity.name} (类型: {entity.type})\n")

            f.write("\n关系列表:\n")
            for relation in kg.relations:
                f.write(f"  - {relation.subject_name} --[{relation.predicate}]--> {relation.object_name}\n")
        
        print(f"✅ 详细信息已保存: {info_file}")
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")


def main():
    """主函数"""
    print("🚀 开始基础知识图谱构建示例")
    print()
    
    # 构建知识图谱
    kg = simple_kg_building_demo()
    
    if kg:
        # 分析图谱结构
        analyze_kg_structure(kg)
        
        # 保存结果
        save_kg_results(kg)
        
        print("\n🎉 示例运行完成!")
        print("💡 提示: 查看 results/examples/ 目录获取详细结果")
    else:
        print("\n❌ 示例运行失败")
        return 1
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
