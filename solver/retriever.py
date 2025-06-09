"""
Hybrid retriever from graph and vector chunks.
"""
class Retriever:
    def __init__(self, indexer=None, graph=None):
        self.indexer = indexer
        self.graph = graph
    def retrieve(self, query):
        # Dummy: use indexer if available
        if self.indexer:
            return self.indexer.search(query)
        return []
