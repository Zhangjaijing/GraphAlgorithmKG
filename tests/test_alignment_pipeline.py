"""
Semantic aligner (offline TF-IDF version).
Replaces SentenceTransformer with simple TF-IDF + cosine similarity
to avoid HuggingFace model download issues.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class SemanticAligner:
    def __init__(self):
        # 初始化 TF-IDF 向量器
        self.vectorizer = TfidfVectorizer()

    def align(self, entity_a: str, entity_b: str) -> float:
        """
        Compute semantic similarity between two entities using TF-IDF + cosine similarity.
        """
        try:
            vectors = self.vectorizer.fit_transform([entity_a, entity_b])
            score = cosine_similarity(vectors[0], vectors[1])[0][0]
            return float(score)
        except Exception as e:
            print(f"[SemanticAligner] Error: {e}")
            return 0.0
