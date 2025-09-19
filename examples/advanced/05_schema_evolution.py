#!/usr/bin/env python3
"""
高级示例: Schema演化演示
展示Schema如何根据新数据自动演化和扩展
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ontology.discoverers.enhanced_schema_detector import EnhancedSchemaDetector
from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder

def demonstrate_schema_evolution():
    """演示Schema演化功能"""
    print("🔄 Schema演化演示")
    print("=" * 80)
    print("本示例展示Schema如何根据新数据自动演化和扩展")
    print()
    
    # 初始化组件
    detector = EnhancedSchemaDetector()
    builder = SchemaBasedKGBuilder()
    
    # 阶段1: 基础Schema建立
    print("📚 阶段1: 建立基础Schema")
    print("-" * 40)
    
    base_document = """
    机器学习是人工智能的一个重要分支。监督学习算法如线性回归和决策树
    在分类和回归任务中表现良好。无监督学习算法如K-means聚类和主成分分析
    用于数据挖掘和降维。这些算法都需要在训练数据集上进行训练。
    """
    
    print("📄 基础文档内容:")
    print(f"   {base_document.strip()[:100]}...")
    
    # 检测基础Schema
    base_results = detector.detect_schema(base_document, use_llm=True)
    if base_results:
        base_schema = base_results[0].schema_file
        print(f"🎯 检测到基础Schema: {base_schema}")
        print(f"   置信度: {base_results[0].confidence:.3f}")
    
    # 阶段2: 引入新概念
    print("\n🆕 阶段2: 引入新概念")
    print("-" * 40)
    
    evolution_document = """
    深度学习是机器学习的新发展方向。卷积神经网络(CNN)在计算机视觉任务中
    表现出色，循环神经网络(RNN)适合处理序列数据。Transformer架构革命性地
    改变了自然语言处理领域。这些深度学习模型需要GPU加速训练，使用反向传播
    算法优化参数。预训练模型如BERT和GPT在多个任务上都有优异表现。
    """
    
    print("📄 演化文档内容:")
    print(f"   {evolution_document.strip()[:100]}...")
    
    # 启用Schema演化
    detector.enable_schema_evolution = True
    
    # 检测演化后的Schema
    evolution_results = detector.detect_schema(evolution_document, use_llm=True)
    
    print("\n🔍 Schema演化结果:")
    if evolution_results:
        for i, result in enumerate(evolution_results[:3], 1):
            print(f"   {i}. {result.schema_file}")
            print(f"      置信度: {result.confidence:.3f}")
            print(f"      新概念: {', '.join(result.evidence[:3])}")
    
    # 阶段3: 构建演化后的知识图谱
    print("\n🏗️ 阶段3: 构建演化后的知识图谱")
    print("-" * 40)
    
    try:
        # 保存演化文档到临时文件
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
            f.write(evolution_document)
            temp_file = f.name
        
        # 构建知识图谱
        kg = builder.build_knowledge_graph(temp_file)
        
        if kg:
            print(f"✅ 成功构建演化后的知识图谱")
            print(f"   实体数量: {len(kg.entities)}")
            print(f"   关系数量: {len(kg.relations)}")
            print(f"   使用Schema: {kg.metadata.get('schema', 'Unknown')}")
            
            # 分析新概念
            new_concepts = []
            for entity in kg.entities:
                if any(keyword in entity.name.lower() for keyword in 
                      ['深度学习', 'cnn', 'rnn', 'transformer', 'bert', 'gpt']):
                    new_concepts.append(entity.name)
            
            if new_concepts:
                print(f"\n🆕 识别到的新概念:")
                for concept in new_concepts[:5]:
                    print(f"   - {concept}")
        
        # 清理临时文件
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ 构建知识图谱时出错: {e}")
    
    # 阶段4: 演化效果分析
    print("\n📊 阶段4: 演化效果分析")
    print("-" * 40)
    
    print("🔍 Schema演化特点:")
    print("   1. 自动识别新概念和关系")
    print("   2. 保持与原有Schema的兼容性")
    print("   3. 动态调整实体类型和属性")
    print("   4. 支持增量式知识扩展")
    
    print("\n💡 应用场景:")
    print("   - 新兴技术领域的知识图谱构建")
    print("   - 跨领域知识整合")
    print("   - 动态知识库维护")
    print("   - 概念演化追踪")
    
    return True

def main():
    """主函数"""
    try:
        print("🚀 启动Schema演化演示")
        print("🎯 目标: 展示Schema如何适应新概念和领域")
        print()
        
        success = demonstrate_schema_evolution()
        
        if success:
            print("\n✅ Schema演化演示完成!")
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
