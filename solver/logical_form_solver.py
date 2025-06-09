"""
Multi-hop logic: retrieval, sort, deduce, etc.
"""
from .memory_manager import MemoryManager
from .planner import Planner

class LogicalFormSolver:
    def __init__(self):
        self.memory = MemoryManager()
        self.planner = Planner()

    def solve(self, query, retriever, k=3, hops=2):
        """
        Decompose the query, retrieve for each sub-question, store steps, and aggregate answers.
        """
        sub_questions = self.planner.plan(query)
        answers = []
        for subq in sub_questions:
            context = retriever.retrieve(subq, k=k, hops=hops)
            self.memory.add({'question': subq, 'context': context})
            answers.append({'sub_question': subq, 'context': context})
        return answers
