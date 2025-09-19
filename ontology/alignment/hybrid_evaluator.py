# ontology/alignment/hybrid_evaluator.py
class HybridEvaluator:
    def __init__(self, w_sem=0.5, w_str=0.4, w_llm=0.1):
        self.w_sem = w_sem
        self.w_str = w_str
        self.w_llm = w_llm

    def fuse(self, semantic_pairs, structural_pairs, llm_pairs):
        fused_scores = {}
        for (e1,e2,score) in semantic_pairs:
            fused_scores[(e1,e2)] = fused_scores.get((e1,e2),0) + self.w_sem*score
        for (e1,e2,score) in structural_pairs:
            fused_scores[(e1,e2)] = fused_scores.get((e1,e2),0) + self.w_str*score
        for (e1,e2,score) in llm_pairs:
            fused_scores[(e1,e2)] = fused_scores.get((e1,e2),0) + self.w_llm*score
        return [(k[0], k[1], v) for k,v in fused_scores.items()]