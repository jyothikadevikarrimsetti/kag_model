"""
Convert extracted metadata to knowledge graph format (nodes/edges) and push to Neo4j.
"""
import json
import os
import networkx as nx
import pickle
from builder.neo4j_connector import Neo4jConnector
import re
import multiprocessing
import requests
import hashlib

# --- Advanced Relation Extraction ---
def extract_relations(text, entities):
    """
    Extract relations using patterns and (optionally) transformer models.
    Returns list of (src, relation, tgt).
    """
    relations = []
    # Simple pattern: 'X sued Y', 'X acquired Y', 'X vs Y'
    patterns = [
        (r"(\b[A-Z][a-z]+\b) (sued|acquired|merged with|vs) (\b[A-Z][a-z]+\b)", 1, 2, 3),
    ]
    for pat, s_idx, rel_idx, t_idx in patterns:
        for m in re.finditer(pat, text):
            src = m.group(s_idx)
            rel = m.group(rel_idx).upper().replace(' ', '_')
            tgt = m.group(t_idx)
            relations.append((src, rel, tgt))
    # TODO: Integrate transformer-based RE (e.g., spaCy, transformers)
    # Example: Use a pre-trained RE model to extract (src, rel, tgt)
    # ...
    return relations

WIKIDATA_API = "https://www.wikidata.org/w/api.php"

_entity_cache = {}

def cross_doc_coref(entity, doc_id=None):
    """Stub for cross-document coreference resolution. Returns canonical entity for the corpus."""
    # TODO: Use a coreference model or KB to resolve entity across docs
    return entity

def canonicalize_entity(entity, candidates=None):
    """Stub for full canonicalization pipeline. Returns (canonical_entity, confidence_score)."""
    # TODO: Use clustering, string similarity, and KB linking for canonicalization
    return entity, 1.0

def link_entity(entity, doc_id=None):
    """
    Link entity to external KB (Wikidata), cross-doc coref, and canonicalize with confidence.
    Returns canonical entity name or Wikidata QID if found, else a hash-based canonical name.
    """
    entity = cross_doc_coref(entity, doc_id)
    canon, conf = canonicalize_entity(entity)
    if canon in _entity_cache:
        return _entity_cache[canon]
    # Try Wikidata search
    params = {
        'action': 'wbsearchentities',
        'search': canon,
        'language': 'en',
        'format': 'json',
        'limit': 1
    }
    try:
        resp = requests.get(WIKIDATA_API, params=params, timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if data.get('search'):
                qid = data['search'][0]['id']
                _entity_cache[canon] = qid
                return qid
    except Exception:
        pass
    # Fallback: hash-based canonicalization
    canon_hash = f"{canon}__{hashlib.md5(canon.encode()).hexdigest()[:8]}"
    _entity_cache[canon] = canon_hash
    return canon_hash

def build_graph(meta, text=None):
    G = nx.MultiDiGraph()  # Directed, multi-edge graph for richer relations
    entities = meta.get("entities", [])
    for ent, label in entities:
        ent_canon = link_entity(ent)
        G.add_node(ent_canon, label=label)
    # Add simple co-occurrence edges
    ents = [link_entity(ent) for ent, _ in entities]
    for i in range(len(ents)-1):
        G.add_edge(ents[i], ents[i+1], type='CO_OCCUR')
    # Add extracted relations if text is provided
    if text:
        for src, rel, tgt in extract_relations(text, entities):
            G.add_edge(link_entity(src), link_entity(tgt), type=rel)
    return G

def push_graph_to_neo4j(G, db):
    for node, data in G.nodes(data=True):
        db.create_node(data.get('label', 'Entity'), {'name': node})
    for u, v, edge_data in G.edges(data=True):
        rel_type = edge_data.get('type', 'RELATED_TO')
        with db.driver.session() as session:
            session.run(f"""
                MATCH (a {{name: $u}}), (b {{name: $v}})
                MERGE (a)-[r:{rel_type}]->(b)
            """, u=u, v=v)

def process_file(args):
    fname, input_dir, output_dir, text_dir = args
    import json
    import pickle
    import os
    meta_path = os.path.join(input_dir, fname)
    with open(meta_path, encoding='utf-8') as f:
        meta = json.load(f)
    text = None
    if text_dir:
        text_file = os.path.join(text_dir, fname.replace('.json', '.txt'))
        if os.path.exists(text_file):
            with open(text_file, encoding='utf-8') as tf:
                text = tf.read()
    G = build_graph(meta, text)
    gpickle_path = os.path.join(output_dir, fname.replace('.json', '.gpickle'))
    with open(gpickle_path, 'wb') as f:
        pickle.dump(G, f)
    return G

def process_dir(input_dir, output_dir, text_dir=None, num_workers=4):
    os.makedirs(output_dir, exist_ok=True)
    db = Neo4jConnector()
    files = [fname for fname in os.listdir(input_dir) if fname.endswith('.json')]
    args = [(fname, input_dir, output_dir, text_dir) for fname in files]
    with multiprocessing.Pool(num_workers) as pool:
        graphs = pool.map(process_file, args)
    # Push all graphs to Neo4j (sequentially, to avoid connection issues)
    for G in graphs:
        push_graph_to_neo4j(G, db)
    db.close()

# --- Truly Advanced Relation Extraction (Transformer-based, Event, Temporal, Coreference) ---
from typing import List, Tuple
try:
    from transformers import pipeline
    _re_model = pipeline('relation-extraction', model='Babelscape/rebel-large', device=-1)
except Exception:
    _re_model = None

def transformer_relation_extraction(text: str) -> List[Tuple[str, str, str]]:
    """Use a transformer model to extract (src, rel, tgt) triples from text."""
    if not _re_model:
        return []
    try:
        results = _re_model(text)
        triples = [(r['head'], r['type'], r['tail']) for r in results]
        return triples
    except Exception:
        return []

def extract_events_temporal_coref(text: str, entities: List[Tuple[str, str]]):
    """Stub for event, temporal, and coreference extraction."""
    # TODO: Integrate event extraction (e.g., using OpenIE, AllenNLP), temporal taggers, and coreference models
    return []

# Update extract_relations to use all methods

def extract_relations(text, entities):
    relations = []
    # Regex-based
    patterns = [
        (r"(\b[A-Z][a-z]+\b) (sued|acquired|merged with|vs) (\b[A-Z][a-z]+\b)", 1, 2, 3),
    ]
    for pat, s_idx, rel_idx, t_idx in patterns:
        for m in re.finditer(pat, text):
            src = m.group(s_idx)
            rel = m.group(rel_idx).upper().replace(' ', '_')
            tgt = m.group(t_idx)
            relations.append((src, rel, tgt))
    # Transformer-based
    relations.extend(transformer_relation_extraction(text))
    # Event/temporal/coref
    relations.extend(extract_events_temporal_coref(text, entities))
    return relations

# --- Scalability/Robustness: Distributed, Sharding, Real-time, Error Recovery ---
# TODO: For distributed graph storage, consider using Neo4j Fabric, DGL, or TigerGraph.
# TODO: For sharding, partition graphs by document or entity type.
# TODO: For real-time updates, use message queues (e.g., Kafka) and event-driven ingestion.
# TODO: For error recovery, add try/except blocks and logging throughout the pipeline.

if __name__ == "__main__":
    # Now expects the extracted text dir for relation extraction
    process_dir("../data/output_json", "../data/graphs", text_dir="../data/extracted_texts")
