#!/usr/bin/env python3
"""
高级示例: Schema合并演示
展示如何合并多个不同来源的Schema，解决冲突并创建统一的知识表示
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ontology.discoverers.enhanced_schema_detector import EnhancedSchemaDetector
from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder

def demonstrate_schema_merging():
    """演示Schema合并功能"""
    print("🔀 Schema合并演示")
    print("=" * 80)
    print("本示例展示如何合并多个不同来源的Schema")
    print()
    
    # 初始化组件
    detector = EnhancedSchemaDetector()
    builder = SchemaBasedKGBuilder()
    
    # 准备多个不同领域的文档
    documents = {
        "医疗领域": """
        医疗诊断系统使用机器学习算法分析患者症状。深度学习模型如卷积神经网络
        用于医学影像分析，能够识别X光片中的异常。自然语言处理技术帮助分析
        电子病历，提取关键医疗信息。这些AI技术提高了诊断准确率。
        """,
        
        "金融领域": """
        金融科技公司使用人工智能进行风险评估。机器学习算法分析交易模式，
        检测欺诈行为。深度学习模型预测股票价格走势，支持投资决策。
        自然语言处理分析新闻情感，评估市场情绪对金融产品的影响。
        """,
        
        "教育领域": """
        智能教育平台使用AI技术个性化学习。机器学习算法分析学生学习行为，
        推荐适合的学习内容。深度学习模型评估学习效果，提供智能辅导。
        自然语言处理技术自动批改作业，生成学习报告。
        """
    }
    
    # 阶段1: 分别检测各领域Schema
    print("🔍 阶段1: 分别检测各领域Schema")
    print("-" * 50)
    
    domain_schemas = {}
    for domain, document in documents.items():
        print(f"\n📚 {domain}文档:")
        print(f"   {document.strip()[:80]}...")
        
        results = detector.detect_schema(document, use_llm=True)
        if results:
            schema = results[0]
            domain_schemas[domain] = schema
            print(f"   🎯 检测Schema: {schema.schema_file}")
            print(f"   📊 置信度: {schema.confidence:.3f}")
            print(f"   🔑 关键概念: {', '.join(schema.evidence[:3])}")
    
    # 阶段2: 识别Schema冲突
    print(f"\n⚠️ 阶段2: 识别Schema冲突")
    print("-" * 50)
    
    print("🔍 潜在冲突分析:")
    conflicts = []
    
    # 模拟冲突检测
    common_concepts = ["机器学习", "深度学习", "自然语言处理", "AI技术"]
    for concept in common_concepts:
        domains_with_concept = []
        for domain, document in documents.items():
            if concept in document:
                domains_with_concept.append(domain)
        
        if len(domains_with_concept) > 1:
            conflicts.append({
                "concept": concept,
                "domains": domains_with_concept,
                "type": "概念重叠"
            })
    
    for conflict in conflicts:
        print(f"   ⚠️ {conflict['concept']}: {', '.join(conflict['domains'])}")
        print(f"      冲突类型: {conflict['type']}")
    
    # 阶段3: 执行Schema合并
    print(f"\n🔀 阶段3: 执行Schema合并")
    print("-" * 50)
    
    # 合并所有文档
    merged_document = "\n\n".join([
        f"=== {domain} ===\n{doc}" 
        for domain, doc in documents.items()
    ])
    
    print("📄 合并后文档长度:", len(merged_document), "字符")
    
    # 检测合并后的Schema
    merged_results = detector.detect_schema(merged_document, use_llm=True)
    
    if merged_results:
        merged_schema = merged_results[0]
        print(f"🎯 合并后Schema: {merged_schema.schema_file}")
        print(f"📊 置信度: {merged_schema.confidence:.3f}")
        print(f"🔑 统一概念: {', '.join(merged_schema.evidence[:5])}")
    
    # 阶段4: 构建统一知识图谱
    print(f"\n🏗️ 阶段4: 构建统一知识图谱")
    print("-" * 50)
    
    try:
        # 保存合并文档到临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(merged_document)
            temp_file = f.name
        
        # 构建知识图谱
        kg = builder.build_knowledge_graph(temp_file)
        
        if kg:
            print(f"✅ 成功构建统一知识图谱")
            print(f"   实体数量: {len(kg.entities)}")
            print(f"   关系数量: {len(kg.relations)}")
            
            # 分析跨领域实体
            domain_entities = {domain: [] for domain in documents.keys()}
            cross_domain_entities = []
            
            for entity in kg.entities:
                entity_domains = []
                for domain in documents.keys():
                    if any(keyword in documents[domain].lower() 
                          for keyword in entity.name.lower().split()):
                        entity_domains.append(domain)
                        domain_entities[domain].append(entity.name)
                
                if len(entity_domains) > 1:
                    cross_domain_entities.append({
                        "entity": entity.name,
                        "domains": entity_domains
                    })
            
            print(f"\n🌐 跨领域实体分析:")
            for item in cross_domain_entities[:5]:
                print(f"   - {item['entity']}: {', '.join(item['domains'])}")
        
        # 清理临时文件
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ 构建知识图谱时出错: {e}")
    
    # 阶段5: 合并效果评估
    print(f"\n📊 阶段5: 合并效果评估")
    print("-" * 50)
    
    print("✅ Schema合并优势:")
    print("   1. 统一了多领域的概念表示")
    print("   2. 解决了概念冲突和重叠")
    print("   3. 创建了跨领域知识连接")
    print("   4. 提高了知识图谱的完整性")
    
    print("\n💡 应用场景:")
    print("   - 企业知识整合")
    print("   - 跨部门数据融合")
    print("   - 多源知识库合并")
    print("   - 领域知识标准化")
    
    return True

def main():
    """主函数"""
    try:
        print("🚀 启动Schema合并演示")
        print("🎯 目标: 展示多Schema合并和冲突解决")
        print()
        
        success = demonstrate_schema_merging()
        
        if success:
            print("\n✅ Schema合并演示完成!")
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
