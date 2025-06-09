"""
CLI interface for question answering using the KAG system.
"""
from solver.retriever import Retriever
from solver.logical_form_solver import LogicalFormSolver
from model.azure_openai_client import AzureOpenAIClient
from model.instruction_tuner import InstructionTuner
from model.summarizer import Summarizer
from builder.indexer import process_dir as index_process

if __name__ == "__main__":
    indexer = index_process("data/chunks")
    if not indexer:
        print("[Error] No valid chunks to index. Please check your PDF extraction and chunking steps.")
        exit(1)
    retriever = Retriever(indexer=indexer)
    solver = LogicalFormSolver()
    llm = AzureOpenAIClient()
    tuner = InstructionTuner()
    summarizer = Summarizer()
    
    question = input("Ask a question: ")
    answers = solver.solve(question, retriever)
    for ans in answers:
        prompt = tuner.build_prompt(ans['sub_question'], ans['context'])
        response = llm.generate(prompt)
        summary = summarizer.summarize(response)
        print(f"Sub-question: {ans['sub_question']}")
        print(f"Answer: {summary}\n")