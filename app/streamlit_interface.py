"""
Streamlit interface for interactive question answering using the KAG system.
"""
import streamlit as st
from builder.indexer import process_dir as index_process
from solver.retriever import Retriever
from solver.logical_form_solver import LogicalFormSolver
from model.azure_openai_client import AzureOpenAIClient
from model.instruction_tuner import InstructionTuner
from model.summarizer import Summarizer
from solver.graph_reasoner import GraphReasoner
import pickle
import os
import networkx as nx
import json
import spacy

nlp = spacy.load("en_core_web_sm")

def load_graphs(graph_dir):
    """
    Fast load: Only load the first .gpickle file for performance.
    For large-scale, consider merging offline and loading a single file.
    """
    for fname in os.listdir(graph_dir):
        if fname.endswith('.gpickle'):
            with open(os.path.join(graph_dir, fname), 'rb') as f:
                return pickle.load(f)
    return None
# Optionally, to load all and merge (slow):
#    graphs = []
#    for fname in os.listdir(graph_dir):
#        if fname.endswith('.gpickle'):
#            with open(os.path.join(graph_dir, fname), 'rb') as f:
#                graphs.append(pickle.load(f))
#    if graphs:
#        return nx.compose_all(graphs)
#    return None

def retrain_from_feedback(feedback_file="data/feedback.json"):
    """Stub for active learning/retraining from user feedback."""
    # TODO: Use feedback to retrain retrieval, summarization, or LLM prompt models
    if not os.path.exists(feedback_file):
        return "No feedback to use."
    with open(feedback_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    # Example: print feedback summary
    pos = sum(1 for d in data if d['rating'] == '👍')
    neg = sum(1 for d in data if d['rating'] == '👎')
    return f"Feedback summary: {pos} positive, {neg} negative. (Retraining not yet implemented)"

def log_audit_event(user, action, details=None):
    """Stub for audit logging."""
    # TODO: Write to secure audit log
    print(f"[AUDIT] User: {user}, Action: {action}, Details: {details}")

def interactive_graph_explorer(graph):
    """Interactive graph visualization using pyvis in Streamlit."""
    from pyvis.network import Network
    import streamlit.components.v1 as components
    st.subheader("Interactive Graph Explorer")
    net = Network(height="600px", width="100%", notebook=False, directed=True)
    for node, data in graph.nodes(data=True):
        net.add_node(node, label=str(node), title=str(data.get('label', node)))
    for src, tgt, data in graph.edges(data=True):
        net.add_edge(src, tgt, label=data.get('type', ''))
    net.repulsion(node_distance=120, central_gravity=0.33, spring_length=110, spring_strength=0.10, damping=0.95)
    net.show_buttons(filter_=['physics'])
    net.save_graph("graph.html")
    with open("graph.html", "r", encoding="utf-8") as f:
        html = f.read()
    components.html(html, height=650, scrolling=True)

def show_advanced_analytics(graph):
    """Stub for advanced analytics (e.g., centrality, community detection)."""
    st.subheader("Graph Analytics (stub)")
    st.write("Top 5 nodes by degree:")
    degrees = sorted(graph.degree, key=lambda x: x[1], reverse=True)[:5]
    for node, deg in degrees:
        st.write(f"{node}: degree {deg}")
    # TODO: Add more analytics (pagerank, clustering, etc.)

def store_feedback(question, answer, rating, feedback_file="data/feedback.json"):
    os.makedirs(os.path.dirname(feedback_file), exist_ok=True)
    entry = {"question": question, "answer": answer, "rating": rating}
    if os.path.exists(feedback_file):
        with open(feedback_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = []
    data.append(entry)
    with open(feedback_file, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def extract_entities_spacy(text):
    """Extract entities from text using spaCy NER."""
    doc = nlp(text)
    return list(set(ent.text for ent in doc.ents))

def main():
    st.title("KAG: Knowledge-Augmented Graph QA")
    st.write("Ask questions over your document knowledge graph!")

    # Load indexer and graph
    indexer = index_process("data/chunks")
    graph = load_graphs("data/graphs")
    retriever = Retriever(indexer=indexer, graph=graph)
    solver = LogicalFormSolver()
    llm = AzureOpenAIClient()
    tuner = InstructionTuner()
    summarizer = Summarizer()
    reasoner = GraphReasoner(graph) if graph else None

    # --- UI/UX: Interactive Graph Explorer and Analytics ---
    if graph:
        if st.sidebar.button("Explore Graph"):
            interactive_graph_explorer(graph)
        if st.sidebar.button("Show Analytics"):
            show_advanced_analytics(graph)
    else:
        st.warning("No graph data found. Please upload graph data files.")

    question = st.text_input("Ask a question:")
    k = st.slider("Top-k Chunks", 1, 10, 3)
    hops = st.slider("Multi-hop Hops", 1, 3, 2)

    get_answer_clicked = st.button("Get Answer", key="get_answer_main")
    if get_answer_clicked and question and graph:
        answers = solver.solve(question, retriever, k=k, hops=hops)
        for idx, ans in enumerate(answers):
            prompt = tuner.build_prompt(ans['sub_question'], ans['context'])
            response = llm.generate(prompt)
            summary = summarizer.summarize(response)
            st.markdown(f"**Sub-question:** {ans['sub_question']}")
            st.markdown(f"**Answer:** {summary}")
            with st.expander("Show context"):
                st.write(ans['context'])
            # --- Reasoning trace ---
            if reasoner:
                # Use spaCy NER for entity extraction
                summary_entities = extract_entities_spacy(summary)
                graph_nodes = list(graph.nodes)
                # Find which extracted entities are in the graph
                present_entities = [e for e in summary_entities if e in graph_nodes]
                if len(present_entities) >= 2:
                    trace = reasoner.explain_answer(present_entities)
                    if trace == "No path found.":
                        # Show closest nodes (by string similarity)
                        import difflib
                        closest = []
                        for ent in present_entities:
                            matches = difflib.get_close_matches(ent, graph_nodes, n=3, cutoff=0.6)
                            if matches:
                                closest.append(f"{ent} → {matches}")
                        st.warning(f"No path found. Closest nodes: {closest if closest else 'None'}")
                        st.info(f"Graph nodes: {graph_nodes[:10]} ... (total {len(graph_nodes)})")
                        st.info(f"Graph edges: {list(graph.edges)[:10]} ... (total {len(graph.edges)})")
                    else:
                        st.info(f"Reasoning trace: {trace}")
                elif len(present_entities) == 1:
                    st.warning("Not enough entities in answer for reasoning trace. Only one entity found.")
                    st.info(f"Entity found: {present_entities[0]}")
                else:
                    st.warning("Not enough entities in answer for reasoning trace. No entities found in graph.")
                    st.info(f"Entities extracted from answer: {summary_entities}")
            # --- Feedback ---
            rating = st.radio(f"Rate this answer to '{ans['sub_question']}':", ["👍", "👎", "🤔"], key=f"rating_{idx}")
            if st.button(f"Submit Feedback for '{ans['sub_question']}'", key=f"submit_{idx}"):
                store_feedback(ans['sub_question'], summary, rating)
                st.success("Feedback submitted!")
                log_audit_event("user", "feedback", {"question": ans['sub_question'], "rating": rating})
    elif get_answer_clicked and not graph:
        st.warning("No graph data found. Please upload graph data files.")
    # --- Evaluation/Feedback: Retraining ---
    if st.sidebar.button("Retrain from Feedback"):
        msg = retrain_from_feedback()
        st.sidebar.info(msg)
    # else:
    #     st.warning("No graph data found. Please upload graph data files.")

if __name__ == "__main__":
    main()
