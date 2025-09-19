#!/usr/bin/env python3
"""
四种动态Schema场景的专门测试数据
每种场景都有精心设计的触发条件和预期结果
"""

# 场景1: 问题驱动Schema生成
# 触发条件: 无预定义Schema + 用户查询
SCENARIO_1_DATA = {
    "name": "问题驱动Schema生成",
    "trigger_condition": "无预定义Schema + 用户查询",
    "user_query": "我想了解这些文档中的算法性能关系",
    "documents": [
        """
        深度学习算法在图像识别任务中表现出色。ResNet网络在ImageNet数据集上达到了95%的准确率，
        训练时间为24小时，使用了8块GPU。VGG网络虽然准确率稍低(92%)，但模型更简单，
        推理速度比ResNet快30%。在内存使用方面，ResNet需要4GB显存，而VGG只需要2GB。
        """,
        """
        自然语言处理领域，BERT模型在GLUE基准测试中获得了88.5分，但训练成本高达数万美元。
        GPT-3模型参数量达到1750亿，推理延迟为2秒，但生成质量极高。
        T5模型在文本摘要任务上F1分数达到0.85，训练时间相对较短，只需要72小时。
        """,
        """
        强化学习算法在游戏AI中表现突出。AlphaGo使用蒙特卡洛树搜索，胜率达到99%，
        但每步决策需要30秒思考时间。DQN算法在Atari游戏中平均得分超过人类水平200%，
        训练稳定性好，收敛速度快。PPO算法在连续控制任务中表现优异，样本效率比传统方法高3倍。
        """
    ],
    "expected_schema": {
        "entity_types": ["Algorithm", "Dataset", "Metric", "Hardware", "Task"],
        "relation_types": ["achieves_performance", "requires_resource", "outperforms", "used_for"]
    },
    "expected_behavior": "RAG检索相关概念 + LLM生成Schema",
    "expected_output": "定制化算法性能Schema"
}

# 场景2: Schema增量演化  
# 触发条件: 现有Schema + 发现新概念
SCENARIO_2_DATA = {
    "name": "Schema增量演化",
    "trigger_condition": "现有Schema + 发现新概念",
    "base_schema": "general",  # 使用通用Schema作为基础
    "user_input": "处理文档时发现'量子算法'概念",
    "documents": [
        """
        传统机器学习算法包括支持向量机、决策树、随机森林等。这些算法在结构化数据上表现良好，
        训练速度快，可解释性强。支持向量机在小样本数据上效果优异，决策树易于理解和实现。
        """,
        """
        量子机器学习是一个新兴领域，量子支持向量机(QSVM)利用量子核函数进行分类。
        量子神经网络(QNN)通过量子门操作实现非线性变换。变分量子特征值求解器(VQE)
        可以求解优化问题。量子近似优化算法(QAOA)在组合优化中显示出量子优势。
        """,
        """
        量子算法的优势在于指数级加速，Shor算法可以高效分解大整数，
        Grover算法提供平方根级的搜索加速。量子模拟算法能够模拟复杂的量子系统，
        在材料科学和药物发现中具有巨大潜力。
        """
    ],
    "new_concepts": ["量子算法", "量子机器学习", "量子优势", "量子模拟"],
    "expected_behavior": "概念分类 + 用户确认 + Schema更新",
    "expected_output": "扩展后的算法Schema"
}

# 场景3: Schema自动合并
# 触发条件: 多个相似Schema冲突
SCENARIO_3_DATA = {
    "name": "Schema自动合并", 
    "trigger_condition": "多个相似Schema冲突",
    "user_input": "同时匹配到'算法'和'计算方法'Schema",
    "documents": [
        """
        计算方法是解决数学和工程问题的系统化步骤。数值计算方法包括有限元法、有限差分法、
        蒙特卡洛方法等。有限元法广泛应用于结构分析，计算精度高但计算量大。
        有限差分法实现简单，适合求解偏微分方程。蒙特卡洛方法基于随机采样，
        在高维积分计算中表现出色。
        """,
        """
        机器学习算法是从数据中学习模式的计算方法。监督学习算法如线性回归、逻辑回归
        需要标注数据进行训练。无监督学习算法如K-means聚类、主成分分析(PCA)
        可以发现数据中的隐藏结构。强化学习算法通过与环境交互学习最优策略。
        """,
        """
        优化算法用于寻找函数的最优解。梯度下降法是最基础的优化方法，
        Adam优化器结合了动量和自适应学习率。遗传算法模拟生物进化过程，
        适合解决复杂的组合优化问题。粒子群优化算法模拟鸟群觅食行为，
        在连续优化问题中表现良好。
        """
    ],
    "conflicting_schemas": ["algorithm_schema", "computational_method_schema"],
    "expected_behavior": "语义对齐 + 冲突解决 + 用户选择",
    "expected_output": "合并后的统一Schema"
}

# 场景4: 交互式Schema优化
# 触发条件: 用户对当前Schema不满意
SCENARIO_4_DATA = {
    "name": "交互式Schema优化",
    "trigger_condition": "用户对当前Schema不满意", 
    "user_feedback": "这个分类不够细致，算法应该按照应用领域分类",
    "initial_schema": "general",
    "documents": [
        """
        计算机视觉算法专注于图像和视频理解。目标检测算法如YOLO、R-CNN能够识别图像中的物体。
        图像分割算法如U-Net、Mask R-CNN可以精确分割目标区域。人脸识别算法如FaceNet、ArcFace
        在安防和身份验证中广泛应用。光学字符识别(OCR)算法能够从图像中提取文本信息。
        """,
        """
        自然语言处理算法处理文本数据。命名实体识别(NER)算法识别文本中的人名、地名等实体。
        情感分析算法判断文本的情感倾向。机器翻译算法如Transformer实现跨语言转换。
        文本摘要算法能够提取文档的关键信息。问答系统算法理解问题并生成答案。
        """,
        """
        推荐系统算法为用户推荐相关内容。协同过滤算法基于用户行为相似性进行推荐。
        内容过滤算法分析物品特征进行匹配。深度学习推荐算法如Wide&Deep、DeepFM
        能够学习复杂的用户-物品交互模式。知识图谱推荐算法利用实体关系提升推荐精度。
        """
    ],
    "user_iterations": [
        {
            "feedback": "算法分类太粗糙，应该按应用领域细分",
            "suggestion": "分为计算机视觉算法、NLP算法、推荐算法等"
        },
        {
            "feedback": "性能指标应该更具体",
            "suggestion": "区分准确率、速度、内存使用等不同类型的指标"
        },
        {
            "feedback": "缺少算法的适用场景描述",
            "suggestion": "添加应用场景和使用条件"
        }
    ],
    "expected_behavior": "主动询问 + 细化建议 + 迭代优化",
    "expected_output": "用户满意的精细Schema"
}

# 测试数据集合
TEST_SCENARIOS = {
    "scenario_1": SCENARIO_1_DATA,
    "scenario_2": SCENARIO_2_DATA, 
    "scenario_3": SCENARIO_3_DATA,
    "scenario_4": SCENARIO_4_DATA
}

# 问答对数据
QA_PAIRS = [
    {
        "question": "我想了解深度学习算法的性能表现",
        "documents": SCENARIO_1_DATA["documents"],
        "expected_schema_type": "algorithm_performance",
        "expected_entities": ["ResNet", "VGG", "BERT", "GPT-3", "T5"],
        "expected_relations": ["achieves_accuracy", "requires_time", "uses_memory"]
    },
    {
        "question": "这些量子算法有什么特殊的优势？",
        "documents": SCENARIO_2_DATA["documents"][1:],  # 只用包含量子概念的文档
        "expected_schema_type": "quantum_algorithm",
        "expected_entities": ["QSVM", "QNN", "VQE", "QAOA", "Shor算法"],
        "expected_relations": ["provides_advantage", "enables_speedup", "solves_problem"]
    },
    {
        "question": "计算方法和机器学习算法有什么区别？",
        "documents": SCENARIO_3_DATA["documents"],
        "expected_schema_type": "unified_computational_method",
        "expected_entities": ["有限元法", "K-means", "梯度下降", "遗传算法"],
        "expected_relations": ["is_type_of", "applies_to", "optimizes"]
    },
    {
        "question": "能否按照应用领域对这些算法进行分类？",
        "documents": SCENARIO_4_DATA["documents"],
        "expected_schema_type": "domain_specific_algorithm",
        "expected_entities": ["YOLO", "BERT", "协同过滤", "Wide&Deep"],
        "expected_relations": ["belongs_to_domain", "used_in_task", "achieves_goal"]
    }
]

def get_scenario_data(scenario_name: str):
    """获取指定场景的测试数据"""
    return TEST_SCENARIOS.get(scenario_name)

def get_all_scenarios():
    """获取所有场景数据"""
    return TEST_SCENARIOS

def get_qa_pairs():
    """获取问答对数据"""
    return QA_PAIRS

if __name__ == "__main__":
    print("🧪 动态Schema测试数据集")
    print("=" * 50)
    
    for scenario_name, data in TEST_SCENARIOS.items():
        print(f"\n📋 {data['name']}")
        print(f"   触发条件: {data['trigger_condition']}")
        print(f"   文档数量: {len(data['documents'])}")
        if 'user_query' in data:
            print(f"   用户查询: {data['user_query']}")
        if 'expected_schema' in data:
            print(f"   预期实体: {len(data['expected_schema']['entity_types'])}个")
            print(f"   预期关系: {len(data['expected_schema']['relation_types'])}个")
    
    print(f"\n📝 问答对数量: {len(QA_PAIRS)}")
    print("✅ 测试数据准备完成！")
