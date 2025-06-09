"""
Full pipeline: PDF → Chunk → Graph + Vector
"""
from builder.extract_text import batch_extract
from builder.semantic_chunker import process_dir as chunk_process
from builder.metadata_extractor import process_dir as meta_process
from builder.concept_aligner import process_dir as align_process
from builder.graph_builder import process_dir as graph_process
from builder.indexer import process_dir as index_process

if __name__ == "__main__":
    # batch_extract("data/raw_pdfs", "data/extracted_texts")
    chunk_process("data/extracted_texts", "data/chunks")
    meta_process("data/chunks", "data/output_json")
    align_process("data/output_json", "data/output_json")
    graph_process("data/output_json", "data/graphs")
    index_process("data/chunks")
    print("Pipeline complete.")
