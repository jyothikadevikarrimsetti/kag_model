"""
Single entrypoint for the KAG system.
Usage:
    python main.py pipeline      # Run the full data pipeline
    python main.py query         # Run extraction, chunking, metadata, and start the CLI for question answering
    python main.py visualize     # Visualize the knowledge graph
"""
import sys
import subprocess
import os

def ensure_data_dirs():
    # Ensure all required data directories exist (absolute paths)
    base = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data'))
    for sub in ['raw_pdfs', 'extracted_texts', 'output_json', 'chunks', 'graphs']:
        os.makedirs(os.path.join(base, sub), exist_ok=True)

if __name__ == "__main__":
    ensure_data_dirs()
    if len(sys.argv) < 2:
        print("Usage: python main.py [pipeline|query|visualize]")
        sys.exit(1)
    cmd = sys.argv[1].lower()
    if cmd == "pipeline":
        subprocess.run([sys.executable, "ingestion/pipeline.py"])
    elif cmd == "query":
        # Run extraction, chunking, and metadata steps consecutively before CLI
        subprocess.run([sys.executable, "builder/extract_text.py"])
        subprocess.run([sys.executable, "builder/semantic_chunker.py"])
        subprocess.run([sys.executable, "builder/metadata_extractor.py"])
        subprocess.run([sys.executable, "app/query_interface.py"])
    elif cmd == "visualize":
        subprocess.run([sys.executable, "app/visualization.py"])
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: python main.py [pipeline|query|visualize]")
        sys.exit(1)
