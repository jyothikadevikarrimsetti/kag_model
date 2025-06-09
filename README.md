# Knowledge Augmented Graph (KAG) System

This project extracts knowledge from documents, builds a knowledge graph, and enables advanced question answering using LLMs and graph reasoning.

## Structure
- `builder/`: Extraction, chunking, metadata, graph building
- `solver/`: Reasoning, planning, retrieval
- `model/`: LLM and prompt handling
- `ingestion/`: End-to-end pipeline
- `app/`: CLI/API and visualization

## Setup
1. Fill in `config/.env` with your credentials.
2. Install dependencies: `pip install -r requirements.txt`
3. Run the pipeline: `python ingestion/pipeline.py`
