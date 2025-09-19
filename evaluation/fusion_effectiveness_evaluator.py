# evaluation/fusion_effectiveness_evaluator.py

class FusionEffectivenessEvaluator:
    """
    对齐融合效果评估器
    """

    @staticmethod
    def evaluate(pred_pairs, ground_truth):
        """
        计算 Precision / Recall / F1
        pred_pairs: list of (source_entity, target_entity, score)
        ground_truth: list of (source_entity, target_entity)
        """
        pred_set = set((s, t) for s, t, _ in pred_pairs)
        gt_set = set(ground_truth)

        tp = len(pred_set & gt_set)
        precision = tp / len(pred_set) if pred_set else 0
        recall = tp / len(gt_set) if gt_set else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        return {"precision": precision, "recall": recall, "f1": f1}
