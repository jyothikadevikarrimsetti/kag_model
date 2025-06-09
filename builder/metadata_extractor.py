"""
Extract metadata (NER, skills, experience) from text chunks.
"""
import os
import spacy
import json

nlp = spacy.load("en_core_web_sm")

def extract_metadata(text):
    doc = nlp(text)
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    return {"entities": entities}

def process_dir(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        if fname.endswith('.txt'):
            with open(os.path.join(input_dir, fname), encoding='utf-8') as f:
                text = f.read()
            meta = extract_metadata(text)
            with open(os.path.join(output_dir, fname.replace('.txt', '.json')), 'w', encoding='utf-8') as f:
                json.dump(meta, f, indent=2)

if __name__ == "__main__":
    process_dir("../data/chunks", "../data/output_json")
