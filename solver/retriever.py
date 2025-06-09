"""
Hybrid retriever from graph and vector chunks.
"""
class Retriever:
    def __init__(self, indexer=None, graph=None):
        self.indexer = indexer
        self.graph = graph
    def retrieve(self, query, k=3, hops=2):
        """
        Multi-hop retrieval: retrieves top-k chunks for the query, then expands search using entities from those chunks.
        """
        if not self.indexer:
            return ["[No relevant context found]"]
        # First hop: retrieve top-k chunks for the original query
        results = self.indexer.search(query, k=k)
        if not self.graph or hops < 2:
            return results
        # Second hop: extract entities from first-hop results and retrieve more
        node_names = set(self.graph.nodes) if self.graph else set()
        found_entities = set()
        for chunk in results:
            for node in node_names:
                if node in chunk:
                    found_entities.add(node)
        # For each found entity, retrieve more chunks
        expanded_chunks = set(results)
        for entity in found_entities:
            more = self.indexer.search(entity, k=1)
            expanded_chunks.update(more)
        return list(expanded_chunks)[:k]
