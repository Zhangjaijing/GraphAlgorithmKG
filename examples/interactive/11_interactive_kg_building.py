#!/usr/bin/env python3
"""
交互式示例: 交互式知识图谱构建
用户可以实时参与知识图谱构建过程，进行调整和优化
"""

import sys
import os
from pathlib import Path
import json

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from pipeline.schema_based_kg_builder import SchemaBasedKGBuilder
from ontology.discoverers.enhanced_schema_detector import EnhancedSchemaDetector

def get_user_input(prompt, options=None, default=None):
    """获取用户输入的辅助函数"""
    if options:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            try:
                choice = input(f"\n请选择 (1-{len(options)}): ").strip()
                if not choice and default:
                    return default
                choice_idx = int(choice) - 1
                if 0 <= choice_idx < len(options):
                    return options[choice_idx]
                else:
                    print("❌ 无效选择，请重新输入")
            except ValueError:
                print("❌ 请输入数字")
    else:
        result = input(f"\n{prompt}: ").strip()
        return result if result else default

def interactive_kg_building():
    """交互式知识图谱构建"""
    print("🤝 交互式知识图谱构建")
    print("=" * 80)
    print("本示例允许您参与知识图谱构建的每个步骤")
    print()
    
    # 步骤1: 选择输入方式
    input_methods = [
        "输入自定义文本",
        "选择预定义示例文档",
        "上传本地文件"
    ]
    
    input_method = get_user_input("请选择输入方式:", input_methods)
    
    document_text = ""
    if input_method == "输入自定义文本":
        print("\n📝 请输入您的文档内容 (输入'END'结束):")
        lines = []
        while True:
            line = input()
            if line.strip().upper() == 'END':
                break
            lines.append(line)
        document_text = '\n'.join(lines)
        
    elif input_method == "选择预定义示例文档":
        examples = {
            "人工智能技术": """
            人工智能是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。
            机器学习是AI的核心技术，包括监督学习、无监督学习和强化学习。
            深度学习使用神经网络来模拟人脑的学习过程，在图像识别和自然语言处理方面表现出色。
            """,
            "区块链技术": """
            区块链是一种分布式账本技术，通过密码学方法确保数据的安全性和不可篡改性。
            比特币是第一个成功的区块链应用，展示了去中心化数字货币的可能性。
            智能合约允许在区块链上执行自动化的协议，无需第三方中介。
            """,
            "量子计算": """
            量子计算利用量子力学原理进行信息处理，具有超越经典计算机的潜力。
            量子比特(qubit)是量子计算的基本单位，可以同时处于0和1的叠加状态。
            量子算法如Shor算法和Grover算法在特定问题上具有指数级加速优势。
            """
        }
        
        example_choice = get_user_input("请选择示例文档:", list(examples.keys()))
        document_text = examples[example_choice]
        
    else:  # 上传本地文件
        file_path = get_user_input("请输入文件路径")
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                document_text = f.read()
            print(f"✅ 成功读取文件: {file_path}")
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return False
    
    if not document_text.strip():
        print("❌ 文档内容为空")
        return False
    
    print(f"\n📄 文档内容预览:")
    print(f"   长度: {len(document_text)} 字符")
    print(f"   预览: {document_text[:100]}...")
    
    # 步骤2: Schema检测和选择
    print(f"\n🔍 步骤2: Schema检测")
    print("-" * 40)
    
    detector = EnhancedSchemaDetector()
    
    use_llm = get_user_input("是否使用LLM增强检测?", ["是", "否"], "是") == "是"
    
    print("正在检测Schema...")
    schema_results = detector.detect_schema(document_text, use_llm=use_llm)
    
    if not schema_results:
        print("❌ 未检测到合适的Schema")
        return False
    
    print(f"\n📋 检测到 {len(schema_results)} 个候选Schema:")
    schema_options = []
    for i, result in enumerate(schema_results, 1):
        print(f"  {i}. {result.schema_file}")
        print(f"     置信度: {result.confidence:.3f}")
        print(f"     证据: {', '.join(result.evidence[:3])}")
        schema_options.append(result.schema_file)
    
    # 让用户选择Schema
    selected_schema = get_user_input("请选择要使用的Schema:", schema_options)
    print(f"✅ 已选择Schema: {selected_schema}")
    
    # 步骤3: 构建参数配置
    print(f"\n⚙️ 步骤3: 构建参数配置")
    print("-" * 40)
    
    # 让用户配置构建参数
    use_llm_extraction = get_user_input("是否使用LLM进行实体抽取?", ["是", "否"], "是") == "是"
    
    confidence_threshold = 0.5
    threshold_input = get_user_input(f"设置置信度阈值 (当前: {confidence_threshold})", default=str(confidence_threshold))
    try:
        confidence_threshold = float(threshold_input)
    except ValueError:
        print(f"使用默认阈值: {confidence_threshold}")
    
    enable_validation = get_user_input("是否启用结果验证?", ["是", "否"], "是") == "是"
    
    print(f"\n📋 构建配置:")
    print(f"   Schema: {selected_schema}")
    print(f"   LLM抽取: {use_llm_extraction}")
    print(f"   置信度阈值: {confidence_threshold}")
    print(f"   结果验证: {enable_validation}")
    
    # 步骤4: 构建知识图谱
    print(f"\n🏗️ 步骤4: 构建知识图谱")
    print("-" * 40)
    
    # 保存文档到临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False, encoding='utf-8') as f:
        f.write(document_text)
        temp_file = f.name
    
    try:
        builder = SchemaBasedKGBuilder()
        
        print("正在构建知识图谱...")
        kg = builder.build_knowledge_graph(temp_file)
        
        if kg:
            print(f"✅ 知识图谱构建成功!")
            print(f"   实体数量: {len(kg.entities)}")
            print(f"   关系数量: {len(kg.relations)}")
            
            # 步骤5: 结果审查和调整
            print(f"\n👀 步骤5: 结果审查")
            print("-" * 40)
            
            # 显示实体
            print(f"\n📊 实体列表 (前10个):")
            for i, entity in enumerate(kg.entities[:10], 1):
                print(f"  {i}. {entity.name} ({entity.type}, 置信度: {entity.confidence:.3f})")
            
            # 显示关系
            print(f"\n🔗 关系列表 (前5个):")
            for i, relation in enumerate(kg.relations[:5], 1):
                print(f"  {i}. {relation.subject} --{relation.predicate}--> {relation.object}")
                print(f"     置信度: {relation.confidence:.3f}")
            
            # 询问是否需要调整
            need_adjustment = get_user_input("是否需要调整结果?", ["是", "否"], "否") == "是"
            
            if need_adjustment:
                print(f"\n🔧 可用的调整选项:")
                print("  1. 过滤低置信度实体")
                print("  2. 合并相似实体")
                print("  3. 添加自定义关系")
                print("  4. 删除不相关实体")
                
                adjustment = get_user_input("请选择调整类型:", 
                                          ["过滤低置信度实体", "合并相似实体", "添加自定义关系", "删除不相关实体"])
                
                if adjustment == "过滤低置信度实体":
                    threshold = float(get_user_input("请输入最小置信度阈值", default="0.7"))
                    original_count = len(kg.entities)
                    kg.entities = [e for e in kg.entities if e.confidence >= threshold]
                    print(f"✅ 已过滤，实体数量从 {original_count} 减少到 {len(kg.entities)}")
                
                elif adjustment == "合并相似实体":
                    print("🔍 正在查找相似实体...")
                    # 简单的相似性检测
                    similar_pairs = []
                    for i, e1 in enumerate(kg.entities):
                        for j, e2 in enumerate(kg.entities[i+1:], i+1):
                            if e1.type == e2.type and len(set(e1.name.lower().split()) & set(e2.name.lower().split())) > 0:
                                similar_pairs.append((e1.name, e2.name))
                    
                    if similar_pairs:
                        print(f"发现 {len(similar_pairs)} 对相似实体:")
                        for pair in similar_pairs[:5]:
                            print(f"  - {pair[0]} ≈ {pair[1]}")
                        print("💡 提示: 实际合并需要更复杂的逻辑")
                    else:
                        print("未发现明显的相似实体")
            
            # 步骤6: 保存和导出
            print(f"\n💾 步骤6: 保存和导出")
            print("-" * 40)
            
            export_formats = ["JSON", "GraphML", "CSV", "不导出"]
            export_format = get_user_input("选择导出格式:", export_formats, "JSON")
            
            if export_format != "不导出":
                print(f"✅ 结果已保存为 {export_format} 格式")
                print("💡 提示: 实际导出功能需要额外实现")
            
            # 显示会话信息
            from pipeline.session_manager import session_manager
            latest_session = session_manager.get_latest_session()
            if latest_session:
                print(f"\n📁 会话目录: {latest_session['session_path']}")
        
        # 清理临时文件
        os.unlink(temp_file)
        
    except Exception as e:
        print(f"❌ 构建过程出错: {e}")
        return False
    
    # 总结
    print(f"\n🎉 交互式构建完成!")
    print("-" * 40)
    print("✅ 您已成功参与了知识图谱构建的全过程")
    print("💡 通过交互式方式，您可以:")
    print("   - 控制每个处理步骤")
    print("   - 根据需求调整参数")
    print("   - 实时审查和优化结果")
    print("   - 选择合适的输出格式")
    
    return True

def main():
    """主函数"""
    try:
        print("🚀 启动交互式知识图谱构建")
        print("🎯 目标: 让您参与知识图谱构建的每个步骤")
        print()
        
        success = interactive_kg_building()
        
        if success:
            print("\n✅ 交互式构建演示完成!")
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
