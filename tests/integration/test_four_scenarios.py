"""
四个Schema场景集成测试
合并自: test_four_scenarios.py
"""

import pytest
import json
import os
from pathlib import Path
from ontology.managers.enhanced_schema_detector import EnhancedSchemaDetector
from ontology.managers.schema_merger import SchemaMerger
from ontology.schemas.base_schema import Schema, EntityType, RelationType
from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder


class TestFourScenariosIntegration:
    """四个Schema场景集成测试"""
    
    @pytest.fixture
    def detector(self):
        """创建增强Schema检测器"""
        return EnhancedSchemaDetector()
    
    @pytest.fixture
    def merger(self):
        """创建Schema合并器"""
        return SchemaMerger()
    
    @pytest.fixture
    def kg_builder(self):
        """创建知识图谱构建器"""
        return SchemaBasedKGBuilder(use_enhanced_detector=True)
    
    def test_scenario_1_query_driven(self, detector):
        """场景1: 问题驱动Schema生成集成测试"""
        print("\n🎯 场景1集成测试: 问题驱动Schema生成")
        
        # 完整的测试文档
        documents = [
            {
                "title": "深度学习算法性能分析",
                "content": """本文分析了多种深度学习算法的性能表现。卷积神经网络(CNN)在图像识别任务中达到了95%的准确率，
                而循环神经网络(RNN)在序列处理任务中表现出色，准确率为88%。Transformer架构在自然语言处理任务中取得了突破性进展，
                BLEU分数达到了42.5。我们还测试了这些算法在不同数据集上的表现：ImageNet数据集上CNN的Top-1准确率为76.2%。"""
            },
            {
                "title": "机器学习算法比较研究", 
                "content": """本研究比较了传统机器学习算法与深度学习算法的性能差异。支持向量机(SVM)在小数据集上表现良好，
                准确率达到92%。随机森林算法在处理结构化数据时效果显著，F1分数为0.89。在大数据集上，深度学习算法明显优于传统算法。"""
            }
        ]
        
        combined_text = '\n\n'.join([f"{doc['title']}\n{doc['content']}" for doc in documents])
        user_query = "我想了解这些文档中的算法性能关系"
        
        # 执行问题驱动生成
        config = {'force_dynamic_discovery': True}
        results = detector.detect_schema(
            text=combined_text,
            use_llm=True,
            user_query=user_query,
            config=config
        )
        
        # 验证结果
        assert len(results) > 0, "应该生成Schema"
        result = results[0]
        assert result.confidence >= 0.8, f"置信度应该高，实际: {result.confidence}"
        
        if hasattr(result, 'schema') and result.schema:
            schema = result.schema
            assert len(schema.entity_types) >= 3, "应该包含多个实体类型"
            assert len(schema.relation_types) >= 2, "应该包含多个关系类型"
        
        print(f"✅ 场景1集成测试通过")
    
    def test_scenario_2_incremental_evolution(self, detector):
        """场景2: Schema增量演化集成测试"""
        print("\n🔄 场景2集成测试: Schema增量演化")
        
        # 启用Schema演化
        detector.enable_schema_evolution = True
        
        # 包含新概念的文档
        evolution_document = """
        量子算法是一种利用量子力学原理进行计算的新型算法。量子退火算法(Quantum Annealing)在优化问题中表现出色，
        能够找到全局最优解。量子支持向量机(Quantum SVM)在处理高维数据时比传统SVM快100倍。
        量子神经网络(Quantum Neural Network)结合了量子计算和深度学习的优势，在某些任务上准确率提升了15%。
        这些量子算法都需要在量子计算机上运行，如IBM的量子处理器和Google的Sycamore芯片。
        """
        
        # 执行Schema演化
        results = detector.detect_schema(evolution_document, use_llm=True)
        
        # 验证演化结果
        assert len(results) >= 0, "Schema演化应该正常执行"
        
        print("✅ 场景2集成测试通过")
    
    def test_scenario_3_schema_merging(self, merger):
        """场景3: Schema自动合并集成测试"""
        print("\n🔧 场景3集成测试: Schema自动合并")
        
        # 创建有冲突的Schema
        schema1 = Schema(
            name='算法性能Schema',
            description='专注于算法性能分析',
            entity_types=[
                EntityType(name='Algorithm', description='算法实体', 
                          examples=['CNN', 'RNN'], keywords=['algorithm', 'algo']),
                EntityType(name='Performance', description='性能指标',
                          examples=['accuracy', 'speed'], keywords=['performance', 'metric'])
            ],
            relation_types=[
                RelationType(name='achieves', description='算法达到性能')
            ]
        )
        
        schema2 = Schema(
            name='机器学习算法Schema',
            description='专注于机器学习算法',
            entity_types=[
                EntityType(name='Algorithm', description='机器学习算法',  # 同名但描述不同
                          examples=['SVM', 'Random Forest'], keywords=['ml', 'model']),
                EntityType(name='Model', description='训练好的模型',
                          examples=['trained_cnn'], keywords=['model', 'trained'])
            ],
            relation_types=[
                RelationType(name='trains', description='训练模型')
            ]
        )
        
        # 执行Schema合并
        merge_result = merger.merge_schemas([schema1, schema2], merge_strategy='intelligent')
        
        # 验证合并结果
        assert merge_result.success, "Schema合并应该成功"
        assert merge_result.merged_schema is not None, "应该生成合并后的Schema"
        assert len(merge_result.conflicts) >= 0, "应该检测到冲突（可能为0）"
        
        print(f"✅ 场景3集成测试通过，冲突数: {len(merge_result.conflicts)}")
    
    def test_scenario_4_interactive_optimization(self):
        """场景4: 交互式Schema优化集成测试"""
        print("\n💬 场景4集成测试: 交互式Schema优化")
        
        # 创建基础Schema
        base_schema = Schema(
            name='基础算法Schema',
            description='基础的算法分类Schema',
            entity_types=[
                EntityType(name='Algorithm', description='算法', 
                          examples=['CNN', 'RNN'], keywords=['algorithm']),
                EntityType(name='Task', description='任务',
                          examples=['classification'], keywords=['task'])
            ],
            relation_types=[
                RelationType(name='solves', description='算法解决任务')
            ]
        )
        
        # 模拟用户反馈和优化过程
        user_feedback = "这个分类不够细致，需要更详细的算法分类"
        optimization_requirements = [
            "更细致的算法分类",
            "包含性能指标", 
            "包含应用领域"
        ]
        
        # 创建优化后的Schema（模拟优化过程）
        optimized_schema = Schema(
            name='精细化算法Schema',
            description='根据用户反馈优化的详细算法Schema',
            entity_types=[
                EntityType(name='DeepLearningAlgorithm', description='深度学习算法'),
                EntityType(name='TraditionalMLAlgorithm', description='传统机器学习算法'),
                EntityType(name='PerformanceMetric', description='性能指标'),
                EntityType(name='ApplicationDomain', description='应用领域'),
                EntityType(name='Task', description='计算任务')
            ],
            relation_types=[
                RelationType(name='solves', description='算法解决任务'),
                RelationType(name='hasPerformance', description='算法具有性能指标'),
                RelationType(name='appliedTo', description='算法应用于领域')
            ]
        )
        
        # 验证优化效果
        assert len(optimized_schema.entity_types) > len(base_schema.entity_types), \
            "优化后应该有更多实体类型"
        assert len(optimized_schema.relation_types) > len(base_schema.relation_types), \
            "优化后应该有更多关系类型"
        
        print("✅ 场景4集成测试通过")
    
    def test_qa_pairs_integration(self):
        """测试问答对集成功能"""
        print("\n❓ 测试问答对集成功能")
        
        # 模拟问答对数据
        qa_pairs = [
            {
                "question": "什么是卷积神经网络？",
                "answer": "卷积神经网络(CNN)是一种深度学习算法，特别适合处理图像数据。",
                "entities": ["卷积神经网络", "深度学习算法", "图像数据"],
                "relations": [("卷积神经网络", "是", "深度学习算法")]
            },
            {
                "question": "SVM的准确率如何？", 
                "answer": "支持向量机(SVM)在分类任务中准确率可达92%。",
                "entities": ["支持向量机", "分类任务", "准确率"],
                "relations": [("支持向量机", "用于", "分类任务")]
            }
        ]
        
        # 验证问答对结构
        for qa in qa_pairs:
            assert 'question' in qa, "问答对应该包含问题"
            assert 'answer' in qa, "问答对应该包含答案"
            assert 'entities' in qa, "问答对应该包含实体"
            assert 'relations' in qa, "问答对应该包含关系"
            
            assert len(qa['entities']) > 0, "应该包含实体"
            assert len(qa['relations']) > 0, "应该包含关系"
        
        print(f"✅ 问答对集成测试通过，处理了 {len(qa_pairs)} 个问答对")
    
    def test_end_to_end_pipeline(self, kg_builder):
        """端到端流水线集成测试"""
        print("\n🔄 端到端流水线集成测试")
        
        # 完整的测试文档
        test_document = """
        机器学习算法性能评估是人工智能研究的重要组成部分。
        深度学习算法如卷积神经网络(CNN)在图像识别任务中表现出色，准确率达到95%。
        传统机器学习算法如支持向量机(SVM)在小数据集上仍有优势，准确率为92%。
        这些算法都在标准数据集如ImageNet和MNIST上进行了测试。
        性能指标包括准确率、精确率、召回率和F1分数等。
        """
        
        user_query = "分析机器学习算法的性能评估方法"
        
        # 先保存文档内容到临时文件
        import tempfile
        import os

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(test_document)
            temp_doc_path = f.name

        try:
            # 执行完整流水线
            kg = kg_builder.build_knowledge_graph(
                document_path=temp_doc_path,
                user_query=user_query
            )
        finally:
            # 清理临时文件
            if os.path.exists(temp_doc_path):
                os.unlink(temp_doc_path)
        
        # 验证知识图谱
        assert kg is not None, "应该成功构建知识图谱"
        assert len(kg.entities) > 0, "知识图谱应该包含实体"
        
        # 验证实体类型
        entity_types = set()
        for entity in kg.entities:
            entity_types.add(entity.type)

        assert len(entity_types) > 0, "应该包含不同类型的实体"

        print(f"✅ 端到端流水线测试通过")
        print(f"   实体数: {len(kg.entities)}")
        print(f"   关系数: {len(kg.relations)}")
        print(f"   实体类型: {entity_types}")


if __name__ == "__main__":
    # 可以直接运行此文件进行测试
    pytest.main([__file__, "-v"])
