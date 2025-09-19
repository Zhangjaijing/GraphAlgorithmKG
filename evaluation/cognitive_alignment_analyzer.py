# evaluation/cognitive_alignment_analyzer.py

class CognitiveAlignmentAnalyzer:
    """
    认知对齐分析器（Cognitive Alignment Analyzer）
    
    功能：
    - 对融合后的对齐结果进行冲突过滤
    - 保证每个实体只能匹配一次
    - 优先保留得分高的匹配
    """

    def __init__(self):
        pass

    def filter_conflicts(self, fused_pairs):
        """
        对融合对齐结果进行冲突过滤
        
        参数:
        - fused_pairs: list of tuples (entity1, entity2, score)
        
        返回:
        - filtered: list of tuples (entity1, entity2, score)，已过滤冲突
        """
        filtered = []
        matched = set()  # 已匹配的实体集合

        # 按得分降序排序，优先保留高分匹配
        for e1, e2, score in sorted(fused_pairs, key=lambda x: -x[2]):
            if e1 not in matched and e2 not in matched:
                filtered.append((e1, e2, score))
                matched.add(e1)
                matched.add(e2)

        return filtered
