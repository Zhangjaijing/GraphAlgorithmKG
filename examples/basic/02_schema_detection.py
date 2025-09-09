#!/usr/bin/env python3
"""
基础示例2: Schema检测
演示如何检测文档适合的Schema类型
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ontology.managers.schema_detector import SchemaDetector


def schema_detection_demo():
    """Schema检测演示"""
    print("🔍 基础示例2: Schema检测")
    print("=" * 60)
    
    # 创建Schema检测器
    detector = SchemaDetector()
    
    # 准备不同类型的测试文档
    test_documents = [
        {
            "name": "算法性能文档",
            "content": """
            深度学习算法在图像识别任务中表现出色。卷积神经网络(CNN)在ImageNet数据集上
            达到了95%的准确率。循环神经网络(RNN)在序列处理任务中准确率为88%。
            这些算法都使用了GPU加速技术来提高训练速度。
            """,
            "expected_schema": "通用算法Schema"
        },
        {
            "name": "时空事件文档", 
            "content": """
            2024年夏季，长江流域发生了严重的洪水事件。监测站记录显示，
            7月15日上午8点，水位达到了警戒线以上。应急响应系统立即启动，
            疏散了沿岸居民。这次事件持续了3天时间。
            """,
            "expected_schema": "时空Schema"
        },
        {
            "name": "企业架构文档",
            "content": """
            企业架构框架定义了系统的整体结构。操作视图(OV-1)描述了业务流程，
            系统视图(SV-1)展示了技术架构。这些视图帮助理解系统的不同层面，
            支持决策制定和系统设计。
            """,
            "expected_schema": "DO-DA-F Schema"
        }
    ]
    
    results = []
    
    for i, doc in enumerate(test_documents, 1):
        print(f"\n📄 测试文档 {i}: {doc['name']}")
        print("-" * 40)
        print(f"内容: {doc['content'].strip()}")
        print()
        
        # 执行Schema检测
        print("🔍 执行Schema检测...")
        try:
            detection_results = detector.detect_schema(doc['content'])
            
            if detection_results:
                print(f"✅ 检测到 {len(detection_results)} 个匹配的Schema:")
                
                for j, result in enumerate(detection_results, 1):
                    print(f"   {j}. Schema文件: {result.schema_file}")
                    print(f"      置信度: {result.confidence:.3f}")
                    print(f"      匹配方法: {result.method}")
                    
                    if hasattr(result, 'evidence') and result.evidence:
                        print(f"      证据: {result.evidence[:100]}...")
                
                # 记录最佳匹配
                best_result = detection_results[0]
                results.append({
                    "document": doc['name'],
                    "detected_schema": best_result.schema_file,
                    "confidence": best_result.confidence,
                    "expected": doc['expected_schema'],
                    "success": True
                })
                
            else:
                print("❌ 未检测到匹配的Schema")
                results.append({
                    "document": doc['name'],
                    "detected_schema": "无",
                    "confidence": 0.0,
                    "expected": doc['expected_schema'],
                    "success": False
                })
                
        except Exception as e:
            print(f"❌ 检测过程中出现错误: {e}")
            results.append({
                "document": doc['name'],
                "detected_schema": "错误",
                "confidence": 0.0,
                "expected": doc['expected_schema'],
                "success": False
            })
    
    return results


def analyze_detection_results(results):
    """分析检测结果"""
    print("\n📊 检测结果分析:")
    print("=" * 60)
    
    # 统计成功率
    successful_detections = sum(1 for r in results if r['success'])
    total_detections = len(results)
    success_rate = successful_detections / total_detections * 100 if total_detections > 0 else 0
    
    print(f"📈 检测成功率: {successful_detections}/{total_detections} ({success_rate:.1f}%)")
    print()
    
    # 详细结果表格
    print("📋 详细结果:")
    print(f"{'文档':<15} {'检测到的Schema':<25} {'置信度':<8} {'状态':<6}")
    print("-" * 60)
    
    for result in results:
        status = "✅" if result['success'] else "❌"
        schema_name = result['detected_schema']
        if len(schema_name) > 24:
            schema_name = schema_name[:21] + "..."
        
        print(f"{result['document']:<15} {schema_name:<25} {result['confidence']:<8.3f} {status:<6}")
    
    # 置信度分析
    if results:
        confidences = [r['confidence'] for r in results if r['success']]
        if confidences:
            avg_confidence = sum(confidences) / len(confidences)
            max_confidence = max(confidences)
            min_confidence = min(confidences)
            
            print(f"\n📊 置信度统计:")
            print(f"   平均置信度: {avg_confidence:.3f}")
            print(f"   最高置信度: {max_confidence:.3f}")
            print(f"   最低置信度: {min_confidence:.3f}")


def demonstrate_schema_details():
    """演示Schema详细信息"""
    print("\n🔍 Schema详细信息演示:")
    print("=" * 60)
    
    detector = SchemaDetector()
    
    # 获取可用的Schema列表
    try:
        available_schemas = detector.get_available_schemas()
        
        if available_schemas:
            print(f"📚 系统中共有 {len(available_schemas)} 个可用Schema:")
            
            for i, schema_info in enumerate(available_schemas, 1):
                print(f"\n{i}. {schema_info.get('name', '未知Schema')}")
                print(f"   文件: {schema_info.get('file', '未知')}")
                print(f"   描述: {schema_info.get('description', '无描述')}")
                
                # 显示实体类型
                entity_types = schema_info.get('entity_types', [])
                if entity_types:
                    print(f"   实体类型 ({len(entity_types)}个): {', '.join(entity_types[:5])}")
                    if len(entity_types) > 5:
                        print(f"                     ... 还有 {len(entity_types) - 5} 个")
                
                # 显示关系类型
                relation_types = schema_info.get('relation_types', [])
                if relation_types:
                    print(f"   关系类型 ({len(relation_types)}个): {', '.join(relation_types[:3])}")
                    if len(relation_types) > 3:
                        print(f"                     ... 还有 {len(relation_types) - 3} 个")
        else:
            print("❌ 未找到可用的Schema")
            
    except Exception as e:
        print(f"❌ 获取Schema信息时出现错误: {e}")


def save_detection_results(results, output_dir="results/examples"):
    """保存检测结果"""
    print(f"\n💾 保存检测结果到 {output_dir}/")
    
    # 创建输出目录
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # 保存为文本文件
        result_file = output_path / "schema_detection_results.txt"
        with open(result_file, 'w', encoding='utf-8') as f:
            f.write("Schema检测结果\n")
            f.write("=" * 40 + "\n\n")
            
            for result in results:
                f.write(f"文档: {result['document']}\n")
                f.write(f"检测到的Schema: {result['detected_schema']}\n")
                f.write(f"置信度: {result['confidence']:.3f}\n")
                f.write(f"预期Schema: {result['expected']}\n")
                f.write(f"检测成功: {'是' if result['success'] else '否'}\n")
                f.write("-" * 30 + "\n")
        
        print(f"✅ 结果已保存: {result_file}")
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")


def main():
    """主函数"""
    print("🚀 开始Schema检测示例")
    print()
    
    # 执行Schema检测演示
    results = schema_detection_demo()
    
    # 分析结果
    analyze_detection_results(results)
    
    # 演示Schema详细信息
    demonstrate_schema_details()
    
    # 保存结果
    save_detection_results(results)
    
    print("\n🎉 示例运行完成!")
    print("💡 提示: 查看 results/examples/ 目录获取详细结果")
    
    return 0


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
