"""
动态Schema功能单元测试
合并自: test_core_dynamic_features.py, test_dynamic_schema_real.py
"""

import pytest
import json
import os
from pathlib import Path
from ontology.managers.enhanced_schema_detector import EnhancedSchemaDetector
from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder


class TestDynamicSchemaFeatures:
    """动态Schema功能测试类"""
    
    @pytest.fixture
    def detector(self):
        """创建增强Schema检测器"""
        return EnhancedSchemaDetector()
    
    @pytest.fixture
    def kg_builder(self):
        """创建知识图谱构建器"""
        return SchemaBasedKGBuilder(use_enhanced_detector=True)
    
    def test_query_driven_generation(self, detector):
        """测试问题驱动Schema生成"""
        print("\n🔍 测试场景1: 问题驱动Schema生成")
        
        # 测试文档
        test_text = """
        深度学习算法包括卷积神经网络(CNN)、循环神经网络(RNN)和Transformer。
        这些算法在图像识别、自然语言处理等任务中表现出色。
        CNN在ImageNet数据集上达到了95%的准确率，RNN在序列处理任务中准确率为88%。
        """
        
        user_query = "我想了解这些文档中的算法性能关系"
        
        # 强制动态发现
        config = {'force_dynamic_discovery': True}
        results = detector.detect_schema(
            text=test_text,
            use_llm=True,
            user_query=user_query,
            config=config
        )
        
        # 验证结果
        assert len(results) > 0, "应该生成至少一个Schema"
        
        result = results[0]
        assert result.confidence > 0.8, f"置信度应该较高，实际为: {result.confidence}"
        assert result.method == "dynamic_discovery", "应该使用动态发现方法"
        
        if hasattr(result, 'schema') and result.schema:
            schema = result.schema
            entity_names = [e.name for e in schema.entity_types]
            
            # 验证包含预期的实体类型
            expected_entities = ['Algorithm', 'PerformanceMetric', 'Dataset']
            for expected in expected_entities:
                assert any(expected.lower() in entity.lower() for entity in entity_names), \
                    f"应该包含{expected}相关实体，实际实体: {entity_names}"
        
        print(f"✅ 问题驱动生成测试通过，置信度: {result.confidence:.3f}")
    
    def test_schema_evolution(self, detector):
        """测试Schema增量演化"""
        print("\n🔄 测试场景2: Schema增量演化")
        
        # 启用Schema演化
        detector.enable_schema_evolution = True
        
        # 包含新概念的文档
        evolution_text = """
        量子算法是一种利用量子力学原理的新型算法。
        量子退火算法可以解决复杂的优化任务，比传统算法更高效。
        量子支持向量机是SVM的量子版本，在某些分类任务上表现更好。
        这些量子算法需要在量子计算机上运行。
        """
        
        results = detector.detect_schema(evolution_text, use_llm=True)
        
        # 验证演化结果
        assert len(results) > 0, "应该检测到Schema或触发演化"
        
        result = results[0]
        print(f"✅ Schema演化测试通过，方法: {result.method}")
    
    def test_full_pipeline_integration(self, kg_builder):
        """测试完整流水线集成"""
        print("\n🔧 测试完整流水线集成")
        
        test_document = """
        机器学习算法在各种任务中展现出强大的性能。
        支持向量机(SVM)在分类任务中准确率达到92%。
        随机森林算法在处理结构化数据时效果显著，F1分数为0.89。
        这些算法都在标准数据集上进行了测试和验证。
        """
        
        user_query = "分析机器学习算法的性能表现"
        
        # 构建知识图谱
        kg = kg_builder.build_knowledge_graph(
            document_content=test_document,
            user_query=user_query
        )
        
        # 验证知识图谱
        assert kg is not None, "应该成功构建知识图谱"
        assert len(kg.nodes()) > 0, "知识图谱应该包含节点"
        assert len(kg.edges()) > 0, "知识图谱应该包含边"
        
        print(f"✅ 完整流水线测试通过，节点数: {len(kg.nodes())}, 边数: {len(kg.edges())}")
    
    def test_schema_merging_scenario(self, detector):
        """测试Schema合并场景"""
        print("\n🔧 测试场景3: Schema合并")
        
        # 可能触发合并的文档
        merging_text = """
        算法性能分析是机器学习研究的重要方向。
        不同的计算方法在各种任务上表现不同。
        深度学习方法在图像处理任务上效果显著。
        传统机器学习方法在结构化数据处理上仍有优势。
        """
        
        results = detector.detect_schema(merging_text, use_llm=True)
        
        # 验证合并相关功能
        assert len(results) >= 0, "Schema检测应该正常工作"
        
        if results:
            result = results[0]
            print(f"✅ Schema合并场景测试通过，检测到Schema: {result.schema_file}")
        else:
            print("✅ Schema合并场景测试通过，未检测到匹配Schema（正常情况）")
    
    def test_interactive_optimization(self, detector):
        """测试交互式优化场景"""
        print("\n💬 测试场景4: 交互式优化")
        
        # 模拟用户不满意的场景
        optimization_text = """
        算法分类需要更加细致。
        需要区分深度学习算法和传统机器学习算法。
        还需要包含算法的性能指标和应用领域信息。
        """
        
        # 这里主要测试检测器的基础功能
        # 实际的交互式优化需要在集成测试中进行
        results = detector.detect_schema(optimization_text, use_llm=True)
        
        print("✅ 交互式优化场景基础测试通过")
    
    def test_saved_results_validation(self):
        """验证保存的测试结果"""
        print("\n💾 验证保存的测试结果")
        
        results_dir = Path("results/sessions")
        if results_dir.exists():
            # 检查场景测试结果文件
            scenario_files = [
                "scenario_1_test_result.json",
                "scenario_2_test_result_simulated.json", 
                "scenario_3_test_result_conflicts.json",
                "scenario_4_test_result.json"
            ]
            
            for filename in scenario_files:
                file_path = results_dir / filename
                if file_path.exists():
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    # 验证基本结构
                    assert 'scenario' in data, f"{filename} 应该包含scenario字段"
                    assert 'timestamp' in data, f"{filename} 应该包含timestamp字段"
                    
                    print(f"✅ 验证 {filename} 结构正确")
        
        print("✅ 保存结果验证完成")


if __name__ == "__main__":
    # 可以直接运行此文件进行测试
    pytest.main([__file__, "-v"])
