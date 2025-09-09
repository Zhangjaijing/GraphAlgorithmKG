#!/usr/bin/env python3
"""
自定义Schema测试示例
测试新创建的时空知识图谱和DODAF状态变化Schema
"""

import sys
import os
import tempfile
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder
from ontology.managers.enhanced_schema_detector import EnhancedSchemaDetector


def test_geospatial_schema():
    """测试时空知识图谱Schema"""
    print("🌍 测试时空知识图谱Schema")
    print("=" * 60)
    
    # 测试文档 - 地理监测相关
    test_document = """
    长江流域水文监测系统包含多个监测站点。三峡监测站位于长江干流，
    负责监测水位、流量和水质数据。该监测站配备了自动化水位计，
    每小时记录一次水位数据。在2024年汛期期间，监测站记录了
    历史最高水位28.5米，持续时间为6小时。
    
    洞庭湖监测站位于长江支流，主要监测湖泊水位变化。
    该站点与三峡监测站之间距离约200公里，两站数据存在
    明显的时空相关性。当上游水位上升时，下游水位通常
    在12-24小时后也会上升。
    """
    
    print("📄 测试文档:")
    print(test_document.strip())
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_document)
        temp_doc_path = f.name
    
    try:
        # 创建KG构建器
        kg_builder = SchemaBasedKGBuilder(use_enhanced_detector=True)
        
        # 构建知识图谱
        print("\n🏗️ 构建知识图谱...")
        kg = kg_builder.build_knowledge_graph(
            document_path=temp_doc_path,
            user_query="分析地理监测站的时空关系"
        )
        
        if kg and len(kg.entities) > 0:
            print("✅ 知识图谱构建成功!")
            print(f"   实体数: {len(kg.entities)}")
            print(f"   关系数: {len(kg.relations)}")
            
            # 显示部分实体
            print("\n📋 主要实体:")
            for i, entity in enumerate(kg.entities[:5], 1):
                print(f"   {i}. {entity.name} ({entity.type})")
            
            # 显示部分关系
            print("\n🔗 主要关系:")
            for i, relation in enumerate(kg.relations[:5], 1):
                print(f"   {i}. {relation.subject} --[{relation.predicate}]--> {relation.object}")
            
            return True
        else:
            print("❌ 知识图谱构建失败")
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中出现错误: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_doc_path):
            os.unlink(temp_doc_path)


def test_dodaf_state_schema():
    """测试DODAF状态变化Schema"""
    print("\n🔄 测试DODAF状态变化Schema")
    print("=" * 60)
    
    # 测试文档 - 状态变化相关
    test_document = """
    玩家执行打开宝箱的动作序列。首先，玩家需要获取青铜钥匙，
    钥匙的初始状态是未获取。通过完成任务，玩家成功获取了钥匙，
    钥匙状态变为已获取。
    
    接下来，玩家来到木制宝箱前。宝箱的初始状态是锁定的，
    无法直接打开。玩家使用青铜钥匙对宝箱执行解锁动作，
    宝箱状态从锁定变为解锁。
    
    最后，玩家执行打开动作，成功打开了宝箱。整个过程的结果是
    打开成功，玩家获得了宝箱内的奖励物品。这个动作序列展示了
    典型的条件-动作-状态变化的时序关系。
    """
    
    print("📄 测试文档:")
    print(test_document.strip())
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(test_document)
        temp_doc_path = f.name
    
    try:
        # 创建KG构建器
        kg_builder = SchemaBasedKGBuilder(use_enhanced_detector=True)
        
        # 构建知识图谱
        print("\n🏗️ 构建知识图谱...")
        kg = kg_builder.build_knowledge_graph(
            document_path=temp_doc_path,
            user_query="分析动作和状态变化的时序关系"
        )
        
        if kg and len(kg.entities) > 0:
            print("✅ 知识图谱构建成功!")
            print(f"   实体数: {len(kg.entities)}")
            print(f"   关系数: {len(kg.relations)}")
            
            # 显示部分实体
            print("\n📋 主要实体:")
            for i, entity in enumerate(kg.entities[:5], 1):
                print(f"   {i}. {entity.name} ({entity.type})")
            
            # 显示部分关系
            print("\n🔗 主要关系:")
            for i, relation in enumerate(kg.relations[:5], 1):
                print(f"   {i}. {relation.subject} --[{relation.predicate}]--> {relation.object}")
            
            return True
        else:
            print("❌ 知识图谱构建失败")
            return False
            
    except Exception as e:
        print(f"❌ 构建过程中出现错误: {e}")
        return False
    finally:
        # 清理临时文件
        if os.path.exists(temp_doc_path):
            os.unlink(temp_doc_path)


def test_schema_detection():
    """测试Schema检测功能"""
    print("\n🔍 测试Schema检测功能")
    print("=" * 60)
    
    detector = EnhancedSchemaDetector()
    
    # 测试地理监测文档
    geo_text = "长江流域监测站记录了水位和流量数据，显示了明显的时空相关性。"
    print("📄 地理监测文档:")
    print(geo_text)
    
    results = detector.detect_schema(geo_text, use_llm=True)
    print(f"\n🎯 检测结果: {len(results)} 个候选Schema")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result.schema_file} (置信度: {result.confidence:.3f})")
    
    # 测试状态变化文档
    state_text = "玩家使用钥匙打开宝箱，钥匙状态从未获取变为已获取，宝箱状态从锁定变为解锁。"
    print(f"\n📄 状态变化文档:")
    print(state_text)
    
    results = detector.detect_schema(state_text, use_llm=True)
    print(f"\n🎯 检测结果: {len(results)} 个候选Schema")
    for i, result in enumerate(results, 1):
        print(f"   {i}. {result.schema_file} (置信度: {result.confidence:.3f})")


def main():
    """主函数"""
    print("🚀 开始自定义Schema测试")
    print("\n这个示例将测试新创建的两个专门Schema：")
    print("1. 时空知识图谱Schema - 用于地理监测")
    print("2. DODAF状态变化Schema - 用于状态变化时序建模")
    
    success_count = 0
    total_tests = 3
    
    # 测试1: 时空知识图谱Schema
    if test_geospatial_schema():
        success_count += 1
    
    # 测试2: DODAF状态变化Schema  
    if test_dodaf_state_schema():
        success_count += 1
    
    # 测试3: Schema检测
    try:
        test_schema_detection()
        success_count += 1
    except Exception as e:
        print(f"❌ Schema检测测试失败: {e}")
    
    # 总结
    print(f"\n📊 测试总结")
    print("=" * 60)
    print(f"✅ 成功: {success_count}/{total_tests} 个测试")
    print(f"📈 成功率: {success_count/total_tests*100:.1f}%")
    
    if success_count == total_tests:
        print("🎉 所有测试通过！您的自定义Schema工作正常。")
    else:
        print("⚠️ 部分测试失败，建议检查Schema配置。")
    
    print("\n💡 提示:")
    print("   - 您可以在 ontology/schemas/spatiotemporal/ 目录中找到Schema文件")
    print("   - 可以根据实际使用效果继续优化Schema")
    print("   - 使用交互式工具创建更多自定义Schema")


if __name__ == "__main__":
    main()
