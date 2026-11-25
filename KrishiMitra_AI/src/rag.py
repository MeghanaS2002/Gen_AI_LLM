from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .utils import split_text

class KnowledgeBase:
    def __init__(self, folder):
        self.items = []
        folder = Path(folder)
        for path in sorted(folder.glob("*.txt")):
            text = path.read_text(encoding="utf-8", errors="ignore")
            self.items.extend({"title": path.stem.replace("_", " ").title(), "text": c} for c in split_text(text))
        self._fit()

    def _fit(self):
        corpus = [x["text"] for x in self.items]
        self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        self.matrix = self.vectorizer.fit_transform(corpus) if corpus else None

    def add_chunks(self, chunks):
        self.items.extend(chunks)
        self._fit()

    def search(self, query, top_k=4):
        if not self.items or self.matrix is None:
            return []
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix).ravel()
        indices = scores.argsort()[::-1][:top_k]
        return [dict(self.items[i], score=float(scores[i])) for i in indices if scores[i] > 0.01]
