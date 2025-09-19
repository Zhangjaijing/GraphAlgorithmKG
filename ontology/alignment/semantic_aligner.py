# ontology/alignment/semantic_aligner.py
from sentence_transformers import SentenceTransformer
import numpy as np

class SemanticAligner:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)

    def embed_entities(self, entities):
        texts = [e.get('description','') + ' ' + ' '.join([f"{k}:{v}" for k,v in e.items() if k not in ['id','description']]) 
                 for e in entities]
        embeddings = self.model.encode(texts, normalize_embeddings=True)
        return embeddings

    def align(self, entities1, entities2, top_k=1):
        emb1 = self.embed_entities(entities1)
        emb2 = self.embed_entities(entities2)
        sim_matrix = np.dot(emb1, emb2.T)
        pairs = []
        for i, row in enumerate(sim_matrix):
            top_idx = row.argsort()[-top_k:][::-1]
            for idx in top_idx:
                pairs.append((entities1[i]['id'], entities2[idx]['id'], float(row[idx])))
        return pairs