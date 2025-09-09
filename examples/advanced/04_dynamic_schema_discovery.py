#!/usr/bin/env python3
"""
高级示例4: 动态Schema发现
演示问题驱动的Schema生成功能
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ontology.managers.enhanced_schema_detector import EnhancedSchemaDetector
from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder


def dynamic_schema_discovery_demo():
    """动态Schema发现演示"""
    print("🔍 高级示例4: 动态Schema发现")
    print("=" * 60)
    
    # 创建增强Schema检测器
    detector = EnhancedSchemaDetector()
    
    # 准备测试场景
    scenarios = [
        {
            "name": "新兴技术领域",
            "query": "我想了解量子计算算法的性能特点",
            "document": """
            量子计算是一种基于量子力学原理的新型计算范式。量子算法如Shor算法和Grover算法
            在特定问题上展现出指数级的加速效果。量子退火算法在优化问题中表现出色，
            能够找到全局最优解。量子机器学习结合了量子计算和机器学习的优势，
            在某些任务上比经典算法快100倍。这些算法需要在量子计算机上运行，
            如IBM的量子处理器和Google的Sycamore芯片。
            """
        },
        {
            "name": "跨领域融合",
            "query": "分析生物信息学中的算法应用",
            "document": """
            生物信息学是计算机科学与生物学的交叉领域。序列比对算法如BLAST用于基因序列分析，
            准确率达到95%。系统发育算法构建进化树，帮助理解物种关系。
            蛋白质结构预测算法如AlphaFold在蛋白质折叠预测中取得突破性进展。
            这些算法处理的数据包括DNA序列、蛋白质序列和基因表达数据。
            """
        },
        {
            "name": "新兴应用场景",
            "query": "了解边缘计算中的优化算法",
            "document": """
            边缘计算将计算任务从云端迁移到网络边缘。资源调度算法优化计算资源分配，
            降低延迟至10ms以下。负载均衡算法确保边缘节点的高效利用。
            缓存算法决定数据在边缘节点的存储策略，命中率达到85%。
            这些算法需要考虑带宽限制、能耗约束和实时性要求。
            """
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 场景 {i}: {scenario['name']}")
        print("-" * 50)
        print(f"用户查询: {scenario['query']}")
        print(f"文档内容: {scenario['document'][:100]}...")
        print()
        
        try:
            # 强制启用动态发现
            config = {'force_dynamic_discovery': True}
            
            print("🔍 执行动态Schema发现...")
            detection_results = detector.detect_schema(
                text=scenario['document'],
                use_llm=True,
                user_query=scenario['query'],
                config=config
            )
            
            if detection_results:
                result = detection_results[0]
                print(f"✅ 动态生成Schema成功!")
                print(f"   置信度: {result.confidence:.3f}")
                print(f"   生成方法: {result.method}")
                
                # 显示生成的Schema信息
                if hasattr(result, 'schema') and result.schema:
                    schema = result.schema
                    print(f"   Schema名称: {schema.name}")
                    print(f"   实体类型数: {len(schema.entity_types)}")
                    print(f"   关系类型数: {len(schema.relation_types)}")
                    
                    # 显示实体类型
                    print(f"   实体类型: {[e.name for e in schema.entity_types[:5]]}")
                    if len(schema.entity_types) > 5:
                        print(f"             ... 还有 {len(schema.entity_types) - 5} 个")
                
                results.append({
                    "scenario": scenario['name'],
                    "success": True,
                    "confidence": result.confidence,
                    "method": result.method,
                    "schema": result.schema if hasattr(result, 'schema') else None
                })
                
            else:
                print("❌ 动态Schema发现失败")
                results.append({
                    "scenario": scenario['name'],
                    "success": False,
                    "confidence": 0.0,
                    "method": "failed",
                    "schema": None
                })
                
        except Exception as e:
            print(f"❌ 发现过程中出现错误: {e}")
            results.append({
                "scenario": scenario['name'],
                "success": False,
                "confidence": 0.0,
                "method": "error",
                "schema": None,
                "error": str(e)
            })
    
    return results


def demonstrate_schema_customization():
    """演示Schema定制化功能"""
    print("\n🎨 Schema定制化演示:")
    print("=" * 60)
    
    # 模拟用户定制需求
    customization_requests = [
        {
            "domain": "医疗诊断",
            "requirements": [
                "包含疾病、症状、治疗方法实体",
                "支持诊断关系和治疗关系",
                "包含置信度和准确率属性"
            ]
        },
        {
            "domain": "金融风控",
            "requirements": [
                "包含风险因子、评估模型、决策规则",
                "支持风险评估和决策制定关系",
                "包含风险等级和概率属性"
            ]
        }
    ]
    
    for i, request in enumerate(customization_requests, 1):
        print(f"\n📋 定制需求 {i}: {request['domain']}")
        print("需求详情:")
        for req in request['requirements']:
            print(f"   - {req}")
        
        # 这里可以扩展实际的定制化逻辑
        print("✅ 定制化Schema生成完成（模拟）")


def build_kg_with_dynamic_schema(results):
    """使用动态生成的Schema构建知识图谱"""
    print("\n🏗️ 使用动态Schema构建知识图谱:")
    print("=" * 60)
    
    kg_builder = SchemaBasedKGBuilder(use_enhanced_detector=True)
    
    # 选择第一个成功的结果进行演示
    successful_result = next((r for r in results if r['success']), None)
    
    if not successful_result:
        print("❌ 没有成功的动态Schema可用于构建知识图谱")
        return None
    
    print(f"📋 使用场景: {successful_result['scenario']}")
    
    # 准备测试文档
    test_document = """
    量子机器学习算法在优化问题中展现出强大的能力。
    量子支持向量机在分类任务中准确率达到98%，比传统SVM提升了6%。
    量子神经网络在图像识别任务中处理速度提升了50倍。
    这些算法在IBM量子计算机上运行，使用了16个量子比特。
    """
    
    try:
        print("🏗️ 构建知识图谱...")
        kg = kg_builder.build_knowledge_graph(
            document_content=test_document,
            user_query="分析量子机器学习算法性能"
        )
        
        if kg and len(kg.nodes()) > 0:
            print("✅ 知识图谱构建成功!")
            print(f"   节点数: {len(kg.nodes())}")
            print(f"   边数: {len(kg.edges())}")
            
            # 显示部分节点
            print("   主要节点:")
            for i, (node, data) in enumerate(list(kg.nodes(data=True))[:5], 1):
                node_type = data.get('type', '未知')
                print(f"     {i}. {node} ({node_type})")
            
            return kg
        else:
            print("❌ 知识图谱构建失败")
            return None
            
    except Exception as e:
        print(f"❌ 构建过程中出现错误: {e}")
        return None


def analyze_discovery_results(results):
    """分析动态发现结果"""
    print("\n📊 动态发现结果分析:")
    print("=" * 60)
    
    # 成功率统计
    successful = [r for r in results if r['success']]
    success_rate = len(successful) / len(results) * 100 if results else 0
    
    print(f"📈 发现成功率: {len(successful)}/{len(results)} ({success_rate:.1f}%)")
    
    if successful:
        # 置信度统计
        confidences = [r['confidence'] for r in successful]
        avg_confidence = sum(confidences) / len(confidences)
        
        print(f"📊 平均置信度: {avg_confidence:.3f}")
        
        # Schema复杂度统计
        schema_complexities = []
        for result in successful:
            if result['schema']:
                complexity = len(result['schema'].entity_types) + len(result['schema'].relation_types)
                schema_complexities.append(complexity)
        
        if schema_complexities:
            avg_complexity = sum(schema_complexities) / len(schema_complexities)
            print(f"📊 平均Schema复杂度: {avg_complexity:.1f} (实体+关系数)")
    
    # 详细结果表格
    print(f"\n📋 详细结果:")
    print(f"{'场景':<15} {'成功':<6} {'置信度':<8} {'方法':<15}")
    print("-" * 50)
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        confidence = result['confidence'] if result['success'] else 0.0
        method = result['method'][:14] if len(result['method']) <= 14 else result['method'][:11] + "..."
        
        print(f"{result['scenario'][:14]:<15} {status:<6} {confidence:<8.3f} {method:<15}")


def save_discovery_results(results, output_dir="results/examples"):
    """保存动态发现结果"""
    print(f"\n💾 保存发现结果到 {output_dir}/")
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        result_file = output_path / "dynamic_schema_discovery_results.txt"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write("动态Schema发现结果\n")
            f.write("=" * 50 + "\n\n")
            
            for result in results:
                f.write(f"场景: {result['scenario']}\n")
                f.write(f"成功: {'是' if result['success'] else '否'}\n")
                f.write(f"置信度: {result['confidence']:.3f}\n")
                f.write(f"方法: {result['method']}\n")
                
                if result['schema']:
                    schema = result['schema']
                    f.write(f"Schema名称: {schema.name}\n")
                    f.write(f"实体类型: {[e.name for e in schema.entity_types]}\n")
                    f.write(f"关系类型: {[r.name for r in schema.relation_types]}\n")
                
                if 'error' in result:
                    f.write(f"错误: {result['error']}\n")
                
                f.write("-" * 30 + "\n")
        
        print(f"✅ 结果已保存: {result_file}")
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")


def main():
    """主函数"""
    print("🚀 开始动态Schema发现示例")
    print()
    
    # 执行动态Schema发现
    results = dynamic_schema_discovery_demo()
    
    # 演示Schema定制化
    demonstrate_schema_customization()
    
    # 使用动态Schema构建知识图谱
    kg = build_kg_with_dynamic_schema(results)
    
    # 分析结果
    analyze_discovery_results(results)
    
    # 保存结果
    save_discovery_results(results)
    
    print("\n🎉 示例运行完成!")
    print("💡 提示:")
    print("   - 动态Schema发现适用于新兴领域和跨领域应用")
    print("   - 可以根据用户查询自动生成定制化Schema")
    print("   - 查看 results/examples/ 目录获取详细结果")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
