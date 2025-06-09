"""
Visualize the knowledge graph using NetworkX and Matplotlib.
"""
import networkx as nx
import matplotlib.pyplot as plt
import os

def visualize_graph(graph_path):
    G = nx.read_gpickle(graph_path)
    plt.figure(figsize=(10,7))
    nx.draw(G, with_labels=True, node_color='lightblue', edge_color='gray')
    plt.show()

if __name__ == "__main__":
    graphs_dir = "../data/graphs"
    for fname in os.listdir(graphs_dir):
        if fname.endswith('.gpickle'):
            print(f"Visualizing {fname}")
            visualize_graph(os.path.join(graphs_dir, fname))
