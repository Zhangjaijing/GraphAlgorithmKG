# run_alignment.py
import pandas as pd
import torch
import torch.nn.functional as F
import sys
import os

# 添加包路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "ontology", "alignment"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "evaluation"))

from ontology.alignment.semantic_aligner import SemanticAligner
from ontology.alignment.structural_aligner import StructuralAligner
from ontology.alignment.llm_assisted_aligner import LLMAssistedAligner
from ontology.alignment.hybrid_evaluator import HybridEvaluator
from evaluation.cognitive_alignment_analyzer import CognitiveAlignmentAnalyzer
from evaluation.fusion_effectiveness_evaluator import FusionEffectivenessEvaluator

# =========================
# 定义相似度函数
# =========================
def compute_similarity(h1, h2):
    h1_norm = F.normalize(h1, p=2, dim=1)
    h2_norm = F.normalize(h2, p=2, dim=1)
    return h1_norm @ h2_norm.t()

# =========================
# 1. 读取三元组 CSV 数据
# =========================
triples_df = pd.read_csv("data/knowledge/seed/kg_expansion_triples.csv")

# =========================
# 2. 构建实体列表
# =========================
entities_set = set(triples_df['subject']).union(set(triples_df['object']))
entities_list = [{"id": e, "type": "Class", "description": e} for e in entities_set]

# =========================
# 3. 构建三元组列表
# =========================
triples_list = triples_df.to_dict('records')
for t in triples_list:
    t['weight'] = float(t['confidence'])

# =========================
# 4. 语义对齐
# =========================
semantic_aligner = SemanticAligner()
semantic_pairs = semantic_aligner.align(entities_list, entities_list)  # CPU 版 align 不传 top_k

# =========================
# 5. 结构对齐
# =========================
node_list = [e['id'] for e in entities_list]
node2idx = {n: i for i, n in enumerate(node_list)}
x = torch.eye(len(node_list))
edges = [[node2idx[r['subject']], node2idx[r['object']]] for r in triples_list]
edge_index = torch.tensor(edges).t().contiguous()

structural_model = StructuralAligner(in_dim=len(node_list), hidden_dim=8, out_dim=4)
h = structural_model(x, edge_index)
sim_matrix = compute_similarity(h, h)

structural_pairs = [
    (entities_list[i]['id'], entities_list[i]['id'], float(sim_matrix[i, i].detach()))
    for i in range(len(entities_list))
]

# =========================
# 6. LLM 辅助对齐（模拟）
# =========================
class DummyLLM:
    def generate(self, prompt):
        return [{"match_id": "Ant_Colony", "score": 0.9}]

llm_aligner = DummyLLM()
llm_pairs = [(e['id'], "Ant_Colony", 0.9) for e in entities_list]

# =========================
# 7. 融合对齐
# =========================
hybrid_evaluator = HybridEvaluator()
fused_pairs = hybrid_evaluator.fuse(semantic_pairs, structural_pairs, llm_pairs)

# =========================
# 8. 认知分析过滤冲突
# =========================
cognitive_analyzer = CognitiveAlignmentAnalyzer()
final_pairs = cognitive_analyzer.filter_conflicts(fused_pairs)

# =========================
# 9. 输出结果
# =========================
print("=== Predicted Alignment Pairs ===")
for pair in final_pairs:
    print(pair)

# =========================
# 10. 评估指标（如果有 Ground Truth）
# =========================
try:
    ground_truth_df = pd.read_csv("data/knowledge/seed/ground_truth.csv")
    ground_truth = [tuple(row) for row in ground_truth_df[['source_entity', 'target_entity']].values]
    metrics = FusionEffectivenessEvaluator.evaluate(final_pairs, ground_truth)
    print("\n=== Evaluation Metrics ===")
    print(metrics)
except FileNotFoundError:
    print("\nNo ground truth file found. Skipping evaluation.")
