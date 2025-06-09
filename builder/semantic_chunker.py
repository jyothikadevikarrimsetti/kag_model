"""
Break text into semantic chunks for downstream processing.
"""
import os
import re

def chunk_text(text, chunk_size=500):
    sentences = re.split(r'(?<=[.!?]) +', text)
    chunks, chunk = [], ''
    for sent in sentences:
        if len(chunk) + len(sent) < chunk_size:
            chunk += sent + ' '
        else:
            chunks.append(chunk.strip())
            chunk = sent + ' '
    if chunk:
        chunks.append(chunk.strip())
    return chunks

def process_dir(input_dir, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for fname in os.listdir(input_dir):
        if fname.endswith('.txt'):
            with open(os.path.join(input_dir, fname), encoding='utf-8') as f:
                text = f.read()
            chunks = chunk_text(text)
            with open(os.path.join(output_dir, fname), 'w', encoding='utf-8') as f:
                f.write('\n---\n'.join(chunks))

if __name__ == "__main__":
    process_dir("../data/extracted_texts", "../data/chunks")
