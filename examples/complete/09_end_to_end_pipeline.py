#!/usr/bin/env python3
"""
完整示例: 端到端流水线演示
展示从原始文档到最终知识图谱的完整处理流程
"""

import sys
import os
from pathlib import Path
import json
import time

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder
from pipeline.session_manager import session_manager
from ontology.discoverers.enhanced_schema_detector import EnhancedSchemaDetector

def demonstrate_end_to_end_pipeline():
    """演示完整的端到端流水线"""
    print("🔄 端到端流水线演示")
    print("=" * 80)
    print("本示例展示从原始文档到知识图谱的完整处理流程")
    print()
    
    # 准备测试文档
    test_document = """
    人工智能技术在现代社会中发挥着越来越重要的作用。机器学习作为AI的核心技术，
    包括监督学习、无监督学习和强化学习三大类别。深度学习是机器学习的一个重要分支，
    使用多层神经网络来模拟人脑的学习过程。
    
    在计算机视觉领域，卷积神经网络(CNN)能够有效识别图像中的对象和模式。
    在自然语言处理领域，循环神经网络(RNN)和Transformer架构处理文本数据表现出色。
    
    目前，预训练语言模型如BERT、GPT系列在多个NLP任务上都取得了突破性进展。
    这些模型通过在大规模文本语料上预训练，学习到了丰富的语言表示。
    
    AI技术的应用场景包括：
    - 智能推荐系统：分析用户行为，推荐个性化内容
    - 自动驾驶：使用计算机视觉和传感器数据进行路径规划
    - 医疗诊断：分析医学影像，辅助医生诊断疾病
    - 金融风控：检测异常交易，防范金融风险
    
    随着技术的不断发展，AI将在更多领域发挥重要作用，推动社会进步。
    """
    
    # 阶段1: 文档预处理
    print("📄 阶段1: 文档预处理")
    print("-" * 40)
    
    print(f"原始文档长度: {len(test_document)} 字符")
    print(f"文档预览: {test_document[:100]}...")
    
    # 保存文档到临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_document)
        temp_file = f.name
    
    print(f"✅ 文档已保存到临时文件: {temp_file}")
    
    # 阶段2: Schema检测
    print(f"\n🔍 阶段2: Schema检测")
    print("-" * 40)
    
    detector = EnhancedSchemaDetector()
    
    print("正在检测最适合的Schema...")
    start_time = time.time()
    
    schema_results = detector.detect_schema(test_document, use_llm=True)
    
    detection_time = time.time() - start_time
    print(f"⏱️ Schema检测耗时: {detection_time:.2f}秒")
    
    if schema_results:
        best_schema = schema_results[0]
        print(f"🎯 最佳Schema: {best_schema.schema_file}")
        print(f"📊 置信度: {best_schema.confidence:.3f}")
        print(f"🔑 关键证据: {', '.join(best_schema.evidence[:3])}")
        
        print(f"\n📋 所有候选Schema:")
        for i, result in enumerate(schema_results[:3], 1):
            print(f"   {i}. {result.schema_file} (置信度: {result.confidence:.3f})")
    else:
        print("❌ 未检测到合适的Schema")
        return False
    
    # 阶段3: 知识图谱构建
    print(f"\n🏗️ 阶段3: 知识图谱构建")
    print("-" * 40)
    
    builder = SchemaBasedKGBuilder()
    
    print("正在构建知识图谱...")
    start_time = time.time()
    
    try:
        kg = builder.build_knowledge_graph(temp_file)
        
        build_time = time.time() - start_time
        print(f"⏱️ 构建耗时: {build_time:.2f}秒")
        
        if kg:
            print(f"✅ 知识图谱构建成功!")
            print(f"   实体数量: {len(kg.entities)}")
            print(f"   关系数量: {len(kg.relations)}")
            print(f"   使用Schema: {kg.metadata.get('schema', 'Unknown')}")
            
            # 分析实体类型分布
            entity_types = {}
            for entity in kg.entities:
                entity_type = entity.type
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
            
            print(f"\n📊 实体类型分布:")
            for entity_type, count in sorted(entity_types.items(), key=lambda x: x[1], reverse=True):
                print(f"   - {entity_type}: {count}个")
            
            # 显示高置信度实体
            high_confidence_entities = [e for e in kg.entities if e.confidence > 0.8]
            print(f"\n🎯 高置信度实体 (>0.8):")
            for entity in high_confidence_entities[:5]:
                print(f"   - {entity.name} ({entity.type}, 置信度: {entity.confidence:.3f})")
        
    except Exception as e:
        print(f"❌ 知识图谱构建失败: {e}")
        return False
    
    # 阶段4: 结果分析和验证
    print(f"\n📊 阶段4: 结果分析和验证")
    print("-" * 40)
    
    # 获取会话信息
    latest_session = session_manager.get_latest_session()
    if latest_session:
        session_path = latest_session["session_path"]
        print(f"📁 会话目录: {session_path}")
        
        # 检查生成的文件
        session_files = list(Path(session_path).glob("*.json"))
        print(f"📄 生成文件数量: {len(session_files)}")
        
        for file_path in session_files:
            file_size = file_path.stat().st_size
            print(f"   - {file_path.name}: {file_size} bytes")
    
    # 阶段5: 质量评估
    print(f"\n✅ 阶段5: 质量评估")
    print("-" * 40)
    
    if kg:
        # 计算质量指标
        total_entities = len(kg.entities)
        high_conf_entities = len([e for e in kg.entities if e.confidence > 0.7])
        avg_confidence = sum(e.confidence for e in kg.entities) / total_entities if total_entities > 0 else 0
        
        total_relations = len(kg.relations)
        high_conf_relations = len([r for r in kg.relations if r.confidence > 0.7])
        avg_rel_confidence = sum(r.confidence for r in kg.relations) / total_relations if total_relations > 0 else 0
        
        print(f"📈 质量指标:")
        print(f"   实体平均置信度: {avg_confidence:.3f}")
        print(f"   高置信度实体比例: {high_conf_entities/total_entities*100:.1f}%")
        print(f"   关系平均置信度: {avg_rel_confidence:.3f}")
        print(f"   高置信度关系比例: {high_conf_relations/total_relations*100:.1f}%")
        
        # 评估覆盖度
        doc_words = set(test_document.lower().split())
        entity_words = set()
        for entity in kg.entities:
            entity_words.update(entity.name.lower().split())
        
        coverage = len(entity_words.intersection(doc_words)) / len(doc_words) * 100
        print(f"   概念覆盖度: {coverage:.1f}%")
    
    # 清理临时文件
    os.unlink(temp_file)
    
    # 阶段6: 总结和建议
    print(f"\n🎉 阶段6: 流水线总结")
    print("-" * 40)
    
    total_time = detection_time + build_time
    print(f"⏱️ 总处理时间: {total_time:.2f}秒")
    print(f"📊 处理效率: {len(test_document)/total_time:.0f} 字符/秒")
    
    print(f"\n💡 流水线特点:")
    print("   ✅ 自动化程度高，无需人工干预")
    print("   ✅ 支持多种文档格式和Schema")
    print("   ✅ 提供详细的中间结果和质量评估")
    print("   ✅ 具备良好的可扩展性和容错性")
    
    print(f"\n🚀 应用建议:")
    print("   - 批量处理大量文档时使用此流水线")
    print("   - 根据质量指标调整处理参数")
    print("   - 定期更新Schema以适应新领域")
    print("   - 结合人工审核提高结果质量")
    
    return True

def main():
    """主函数"""
    try:
        print("🚀 启动端到端流水线演示")
        print("🎯 目标: 展示完整的知识图谱构建流程")
        print()
        
        success = demonstrate_end_to_end_pipeline()
        
        if success:
            print("\n✅ 端到端流水线演示完成!")
            print("💡 提示: 查看results/sessions/latest/目录获取详细结果")
        else:
            print("\n❌ 演示过程中出现问题")
            
    except KeyboardInterrupt:
        print("\n⏹️ 用户中断演示")
    except Exception as e:
        print(f"\n❌ 演示出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
