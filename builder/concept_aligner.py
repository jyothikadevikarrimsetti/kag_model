"""
Aligns concepts (synonyms, types) for knowledge graph consistency.
"""
import json
import os

# Example synonym map
SYNONYM_MAP = {
    "AI": "Artificial Intelligence",
    "ML": "Machine Learning",
}

def align_concepts(meta):
    aligned = []
    for ent, label in meta.get("entities", []):
        ent_aligned = SYNONYM_MAP.get(ent, ent)
        aligned.append((ent_aligned, label))
    return {"entities": aligned}

def process_dir(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        if fname.endswith('.json'):
            with open(os.path.join(input_dir, fname), encoding='utf-8') as f:
                meta = json.load(f)
            aligned = align_concepts(meta)
            with open(os.path.join(output_dir, fname), 'w', encoding='utf-8') as f:
                json.dump(aligned, f, indent=2)

if __name__ == "__main__":
    process_dir("../data/output_json", "../data/output_json")
