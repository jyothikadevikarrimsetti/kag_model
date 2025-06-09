"""
Store semantic chunks in a vector database (Pinecone or FAISS).
"""
import os
import faiss
import numpy as np

# Dummy embedder for demonstration
from sklearn.feature_extraction.text import TfidfVectorizer

class SimpleIndexer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer()
        self.index = None
        self.texts = []
    def fit(self, texts):
        X = self.vectorizer.fit_transform(texts).toarray().astype('float32')
        self.index = faiss.IndexFlatL2(X.shape[1])
        self.index.add(X)
        self.texts = texts
    def search(self, query, k=3):
        Xq = self.vectorizer.transform([query]).toarray().astype('float32')
        D, I = self.index.search(Xq, k)
        return [self.texts[i] for i in I[0]]

def process_dir(input_dir):
    texts = []
    for fname in os.listdir(input_dir):
        if fname.endswith('.txt'):
            with open(os.path.join(input_dir, fname), encoding='utf-8') as f:
                texts.extend(f.read().split('\n---\n'))
    # Remove empty or whitespace-only texts
    texts = [t.strip() for t in texts if t.strip()]
    if not texts:
        print("[Indexer] No valid text chunks found in directory. Skipping indexing.")
        return None
    indexer = SimpleIndexer()
    indexer.fit(texts)
    return indexer

if __name__ == "__main__":
    indexer = process_dir("../data/chunks")
    print(indexer.search("machine learning"))
