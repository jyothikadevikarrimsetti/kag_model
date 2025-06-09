"""
Final response generation and summarization for KAG.
Supports extractive (TF-IDF, entity-aware) and optional abstractive (LLM) modes.
"""
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class Summarizer:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        try:
            import nltk
            nltk.data.find('tokenizers/punkt')
            self.sent_tokenize = nltk.sent_tokenize
        except Exception:
            self.sent_tokenize = lambda text: text.split('. ')

    def summarize(self, text, query=None, max_sentences=6, max_chars=1200, entities=None, abstractive_llm=None):
        """
        Summarize text using extractive (default) or abstractive (if LLM provided) mode.
        - query: focus summary on this query
        - entities: list of entity strings to highlight in summary
        - abstractive_llm: callable (prompt:str)->str for LLM-based summary
        """
        if not text or not text.strip():
            return "[No content to summarize]"
        # Abstractive mode if LLM provided
        if abstractive_llm:
            prompt = f"Summarize the following in {max_sentences} sentences (max {max_chars} chars):\n{text}"
            return abstractive_llm(prompt)[:max_chars]
        # Extractive mode
        try:
            sentences = self.sent_tokenize(text)
        except Exception:
            sentences = text.split('. ')
        if not sentences or len(sentences) == 1:
            return text[:max_chars]
        # If query, rank by relevance
        if query:
            X = self.vectorizer.fit_transform(sentences + [query])
            query_vec = X[-1]
            sent_vecs = X[:-1]
            scores = sent_vecs @ query_vec.T
            ranked = np.argsort(-scores.toarray().flatten())
            selected = [sentences[i] for i in ranked[:max_sentences]]
        else:
            selected = sentences[:max_sentences]
        summary = '. '.join(selected).strip()
        # Optionally highlight entities
        if entities:
            for ent in entities:
                summary = summary.replace(ent, f"**{ent}**")
        return summary[:max_chars]
