#!/usr/bin/env python3
"""
交互式示例10: 用户引导Schema生成
演示需要用户参与的Schema生成和优化过程
"""

import sys
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from ontology.managers.enhanced_schema_detector import EnhancedSchemaDetector
from ontology.schemas.base_schema import Schema, EntityType, RelationType


def get_user_input(prompt, options=None, default=None):
    """获取用户输入的辅助函数"""
    if options:
        print(f"\n{prompt}")
        for i, option in enumerate(options, 1):
            print(f"  {i}. {option}")
        
        while True:
            try:
                choice = input(f"请选择 (1-{len(options)})" + (f" [默认: {default}]" if default else "") + ": ").strip()
                
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
        response = input(f"\n{prompt}" + (f" [默认: {default}]" if default else "") + ": ").strip()
        return response if response else default


def interactive_schema_generation():
    """交互式Schema生成"""
    print("🎯 交互式Schema生成")
    print("=" * 60)
    
    print("👋 欢迎使用交互式Schema生成工具!")
    print("我将引导您创建一个定制化的Schema。")
    
    # 步骤1: 选择领域
    domain_options = [
        "时空知识图谱",
        "DODAF状态变化",
        "其他（自定义）"
    ]
    
    selected_domain = get_user_input(
        "请选择您的应用领域:",
        domain_options,
        "时空知识图谱"
    )
    
    if selected_domain == "其他（自定义）":
        custom_domain = get_user_input("请输入您的自定义领域:", default="自定义领域")
        selected_domain = custom_domain

    print(f"✅ 已选择领域: {selected_domain}")

    # 检查是否是预定义的专门Schema
    if selected_domain == "时空知识图谱":
        schema_result = create_geospatial_schema()
        if schema_result:
            return schema_result, selected_domain
        # 如果用户选择不使用预定义Schema，继续自定义流程
    elif selected_domain == "DODAF状态变化":
        schema_result = create_dodaf_state_schema()
        if schema_result:
            return schema_result, selected_domain
        # 如果用户选择不使用预定义Schema，继续自定义流程

    # 步骤2: 定义核心实体
    print(f"\n📋 为 '{selected_domain}' 领域定义核心实体类型")
    print("请输入3-5个核心实体类型（例如：动作、道具、状态）")
    
    entities = []
    for i in range(5):
        entity_name = get_user_input(f"实体类型 {i+1}" + (" (可选)" if i >= 3 else ""))
        if entity_name:
            # 获取实体描述
            entity_desc = get_user_input(f"请描述 '{entity_name}' 实体", default=f"{entity_name}相关实体")
            
            # 获取示例
            examples_input = get_user_input(f"请提供 '{entity_name}' 的示例（用逗号分隔）", default="示例1,示例2")
            examples = [ex.strip() for ex in examples_input.split(',') if ex.strip()]
            
            entities.append({
                'name': entity_name,
                'description': entity_desc,
                'examples': examples
            })
        elif i < 3:
            print("❌ 前3个实体类型是必需的，请输入")
            i -= 1  # 重新输入
        else:
            break
    
    print(f"✅ 已定义 {len(entities)} 个实体类型")
    
    # 步骤3: 定义关系类型
    print(f"\n🔗 定义实体间的关系类型")
    print("请定义实体之间的关系（例如：诊断、治疗、包含）")
    
    relations = []
    for i in range(3):
        relation_name = get_user_input(f"关系类型 {i+1}" + (" (可选)" if i >= 2 else ""))
        if relation_name:
            # 获取关系描述
            relation_desc = get_user_input(f"请描述 '{relation_name}' 关系", default=f"{relation_name}关系")
            
            # 选择主语和宾语类型
            if len(entities) >= 2:
                entity_names = [e['name'] for e in entities]
                print(f"请选择 '{relation_name}' 关系的主语类型:")
                subject_type = get_user_input("主语类型:", entity_names, entity_names[0])
                
                print(f"请选择 '{relation_name}' 关系的宾语类型:")
                object_type = get_user_input("宾语类型:", entity_names, entity_names[1])
                
                relations.append({
                    'name': relation_name,
                    'description': relation_desc,
                    'subject_types': [subject_type],
                    'object_types': [object_type]
                })
            else:
                relations.append({
                    'name': relation_name,
                    'description': relation_desc,
                    'subject_types': [],
                    'object_types': []
                })
        elif i < 2:
            print("❌ 前2个关系类型是必需的，请输入")
            i -= 1  # 重新输入
        else:
            break
    
    print(f"✅ 已定义 {len(relations)} 个关系类型")
    
    # 步骤4: 生成Schema
    print(f"\n🏗️ 生成Schema...")
    
    schema_name = f"{selected_domain}知识图谱Schema"
    schema_description = f"用户定制的{selected_domain}领域Schema"
    
    # 创建EntityType对象
    entity_types = []
    for entity in entities:
        entity_type = EntityType(
            name=entity['name'],
            description=entity['description'],
            examples=entity['examples'],
            keywords=[entity['name'].lower()]
        )
        entity_types.append(entity_type)
    
    # 创建RelationType对象
    relation_types = []
    for relation in relations:
        relation_type = RelationType(
            name=relation['name'],
            description=relation['description'],
            subject_types=relation['subject_types'],
            object_types=relation['object_types']
        )
        relation_types.append(relation_type)
    
    # 创建Schema对象
    custom_schema = Schema(
        name=schema_name,
        description=schema_description,
        entity_types=entity_types,
        relation_types=relation_types
    )
    
    return custom_schema, selected_domain


def review_and_optimize_schema(schema, domain):
    """审查和优化Schema"""
    print(f"\n📋 Schema审查和优化")
    print("=" * 60)
    
    # 显示生成的Schema
    print(f"📄 生成的Schema: {schema.name}")
    print(f"📝 描述: {schema.description}")
    print(f"📊 实体类型数: {len(schema.entity_types)}")
    print(f"📊 关系类型数: {len(schema.relation_types)}")
    
    print(f"\n🏷️ 实体类型详情:")
    for i, entity in enumerate(schema.entity_types, 1):
        print(f"  {i}. {entity.name}: {entity.description}")
        if entity.examples:
            print(f"     示例: {', '.join(entity.examples[:3])}")
    
    print(f"\n🔗 关系类型详情:")
    for i, relation in enumerate(schema.relation_types, 1):
        print(f"  {i}. {relation.name}: {relation.description}")
        if relation.subject_types and relation.object_types:
            print(f"     格式: {relation.subject_types[0]} --[{relation.name}]--> {relation.object_types[0]}")
    
    # 询问用户是否满意
    satisfaction_options = [
        "非常满意，直接使用",
        "基本满意，需要小幅调整", 
        "不太满意，需要重新设计",
        "完全不满意，重新开始"
    ]
    
    satisfaction = get_user_input(
        "您对生成的Schema满意吗？",
        satisfaction_options,
        "基本满意，需要小幅调整"
    )
    
    if satisfaction == "非常满意，直接使用":
        print("✅ Schema确认完成!")
        return schema, True
    
    elif satisfaction == "基本满意，需要小幅调整":
        print("\n🔧 进行小幅调整...")
        
        # 询问具体调整需求
        adjustment_options = [
            "添加新的实体类型",
            "添加新的关系类型",
            "修改实体描述",
            "修改关系描述",
            "完成调整"
        ]
        
        while True:
            adjustment = get_user_input(
                "请选择调整类型:",
                adjustment_options,
                "完成调整"
            )
            
            if adjustment == "完成调整":
                break
            elif adjustment == "添加新的实体类型":
                new_entity_name = get_user_input("新实体类型名称:")
                if new_entity_name:
                    new_entity_desc = get_user_input("新实体描述:", default=f"{new_entity_name}相关实体")
                    new_entity = EntityType(
                        name=new_entity_name,
                        description=new_entity_desc,
                        examples=[new_entity_name],
                        keywords=[new_entity_name.lower()]
                    )
                    schema.entity_types.append(new_entity)
                    print(f"✅ 已添加实体类型: {new_entity_name}")
            
            elif adjustment == "添加新的关系类型":
                new_relation_name = get_user_input("新关系类型名称:")
                if new_relation_name:
                    new_relation_desc = get_user_input("新关系描述:", default=f"{new_relation_name}关系")
                    new_relation = RelationType(
                        name=new_relation_name,
                        description=new_relation_desc
                    )
                    schema.relation_types.append(new_relation)
                    print(f"✅ 已添加关系类型: {new_relation_name}")
        
        print("✅ Schema调整完成!")
        return schema, True
    
    else:
        print("❌ 需要重新设计Schema")
        return schema, False


def test_schema_with_sample_text(schema, domain):
    """使用示例文本测试Schema"""
    print(f"\n🧪 Schema测试")
    print("=" * 60)
    
    # 提供示例文本或让用户输入
    use_sample_options = [
        "使用系统提供的示例文本",
        "输入自定义测试文本"
    ]
    
    choice = get_user_input(
        "请选择测试方式:",
        use_sample_options,
        "使用系统提供的示例文本"
    )
    
    if choice == "使用系统提供的示例文本":
        # 根据领域提供示例文本
        sample_texts = {
            "医疗健康": "患者张三被诊断为高血压，医生建议采用药物治疗方案，包括降压药和生活方式调整。",
            "金融科技": "客户申请贷款，风控系统评估信用等级为A级，批准贷款额度为50万元。",
            "教育培训": "学生李四参加Python编程课程，通过在线学习平台完成了基础模块的学习。",
            "智能制造": "生产线设备运行正常，质量检测系统发现产品合格率达到98%。",
            "环境监测": "监测站记录显示PM2.5浓度为35μg/m³，空气质量等级为良好。"
        }
        
        test_text = sample_texts.get(domain, "这是一个测试文档，包含了相关的实体和关系信息。")
    else:
        test_text = get_user_input("请输入测试文本:", default="测试文档内容")
    
    print(f"📄 测试文本: {test_text}")
    
    # 模拟Schema测试过程
    print(f"\n🔍 使用Schema分析文本...")
    print(f"✅ 检测到 {len(schema.entity_types)} 种可能的实体类型")
    print(f"✅ 检测到 {len(schema.relation_types)} 种可能的关系类型")
    
    # 询问测试结果满意度
    test_satisfaction = get_user_input(
        "您对测试结果满意吗？",
        ["满意", "不满意"],
        "满意"
    )
    
    return test_satisfaction == "满意"


def save_custom_schema(schema, domain, output_dir="results/examples"):
    """保存自定义Schema"""
    print(f"\n💾 保存自定义Schema")
    print("=" * 60)
    
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    try:
        # 保存Schema配置
        schema_file = output_path / f"custom_schema_{domain.replace(' ', '_')}.yaml"
        
        # 这里应该实现实际的YAML保存逻辑
        # 现在先保存为文本格式
        with open(schema_file.with_suffix('.txt'), 'w', encoding='utf-8') as f:
            f.write(f"自定义Schema: {schema.name}\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"领域: {domain}\n")
            f.write(f"描述: {schema.description}\n\n")
            
            f.write("实体类型:\n")
            for entity in schema.entity_types:
                f.write(f"  - {entity.name}: {entity.description}\n")
                if entity.examples:
                    f.write(f"    示例: {', '.join(entity.examples)}\n")
            
            f.write("\n关系类型:\n")
            for relation in schema.relation_types:
                f.write(f"  - {relation.name}: {relation.description}\n")
                if relation.subject_types and relation.object_types:
                    f.write(f"    格式: {relation.subject_types[0]} -> {relation.object_types[0]}\n")
        
        print(f"✅ Schema已保存: {schema_file.with_suffix('.txt')}")
        
        # 保存使用说明
        guide_file = output_path / f"schema_usage_guide_{domain.replace(' ', '_')}.txt"
        with open(guide_file, 'w', encoding='utf-8') as f:
            f.write(f"{domain} Schema使用指南\n")
            f.write("=" * 50 + "\n\n")
            f.write("1. 将Schema文件放入 ontology/schemas/ 目录\n")
            f.write("2. 更新Schema索引文件\n")
            f.write("3. 使用SchemaBasedKGBuilder构建知识图谱\n")
            f.write("4. 根据实际使用情况调整Schema配置\n")
        
        print(f"✅ 使用指南已保存: {guide_file}")
        
    except Exception as e:
        print(f"❌ 保存失败: {e}")


def main():
    """主函数"""
    print("🚀 开始交互式Schema生成")
    print()
    
    try:
        # 交互式Schema生成
        schema, domain = interactive_schema_generation()
        
        # 检查是否是预定义Schema文件名
        if isinstance(schema, str) and schema.endswith('.yaml'):
            # 预定义Schema，直接使用
            print(f"\n✅ 使用预定义Schema: {schema}")
            print("🎉 交互式Schema生成完成!")
            return 0

        # 审查和优化
        final_schema, approved = review_and_optimize_schema(schema, domain)
        
        if approved:
            # 测试Schema
            test_passed = test_schema_with_sample_text(final_schema, domain)
            
            if test_passed:
                # 保存Schema
                save_custom_schema(final_schema, domain)
                
                print("\n🎉 交互式Schema生成完成!")
                print("💡 提示:")
                print("   - 您的自定义Schema已保存到 results/examples/ 目录")
                print("   - 可以将Schema集成到系统中使用")
                print("   - 根据实际使用效果继续优化Schema")
            else:
                print("\n🔄 建议重新调整Schema以获得更好的效果")
        else:
            print("\n🔄 请重新运行程序设计Schema")
    
    except KeyboardInterrupt:
        print("\n\n👋 用户取消操作，程序退出")
        return 1
    except Exception as e:
        print(f"\n❌ 程序运行出错: {e}")
        return 1
    
    return 0


def create_geospatial_schema():
    """创建时空知识图谱Schema"""
    print("\n🌍 创建时空知识图谱Schema")
    print("=" * 60)

    print("📋 这是一个专门用于地理监测的时空知识图谱Schema，包含：")
    print("   🏞️  地理要素: 水系、河流、流域、监测站")
    print("   📍 空间类: 几何形状、位置信息")
    print("   ⏰ 时间类: 时间点、时间段、持续长度、时间粒度")
    print("   📊 测量类: 降水量、径流量、水位")
    print("   🎯 事件类: 监测事件、自然事件")

    confirm = get_user_input("是否使用此预定义Schema？", ["是", "否"], "是")

    if confirm == "是":
        print("✅ 已选择时空知识图谱Schema")
        print("📁 Schema文件: ontology/schemas/spatiotemporal/geospatial_monitoring_schema.yaml")
        return "geospatial_monitoring_schema.yaml"
    else:
        print("🔄 返回自定义Schema创建流程...")
        return None


def create_dodaf_state_schema():
    """创建DODAF状态变化Schema"""
    print("\n🔄 创建DODAF状态变化时序知识图谱Schema")
    print("=" * 60)

    print("📋 这是一个基于DODAF架构的状态变化时序Schema，包含：")
    print("   ⚡ 动作类: 打开、关闭、获取、放置、激活")
    print("   🔧 道具类: 钥匙、工具、武器、材料")
    print("   📦 容器类: 宝箱、箱子、柜子、仓库")
    print("   🎭 状态类: 获取状态、锁定状态、激活状态")
    print("   🎯 结果类: 操作结果、执行效果")
    print("   ⏱️  时序类: 时序节点、状态机、因果关系")

    confirm = get_user_input("是否使用此预定义Schema？", ["是", "否"], "是")

    if confirm == "是":
        print("✅ 已选择DODAF状态变化Schema")
        print("📁 Schema文件: ontology/schemas/spatiotemporal/dodaf_state_change_schema.yaml")
        return "dodaf_state_change_schema.yaml"
    else:
        print("🔄 返回自定义Schema创建流程...")
        return None


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
