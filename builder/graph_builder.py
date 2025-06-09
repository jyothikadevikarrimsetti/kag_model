"""
Convert extracted metadata to knowledge graph format (nodes/edges).
"""
import json
import os
import networkx as nx

def build_graph(meta):
    G = nx.Graph()
    for ent, label in meta.get("entities", []):
        G.add_node(ent, label=label)
    # Example: add edges between all entities
    ents = [ent for ent, _ in meta.get("entities", [])]
    for i in range(len(ents)-1):
        G.add_edge(ents[i], ents[i+1])
    return G

def process_dir(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        if fname.endswith('.json'):
            with open(os.path.join(input_dir, fname), encoding='utf-8') as f:
                meta = json.load(f)
            G = build_graph(meta)
            nx.write_gpickle(G, os.path.join(output_dir, fname.replace('.json', '.gpickle')))

if __name__ == "__main__":
    process_dir("../data/output_json", "../data/graphs")
