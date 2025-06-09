"""
Stores intermediate reasoning steps for multi-hop QA.
"""
class MemoryManager:
    def __init__(self):
        self.memory = []
    def add(self, step):
        self.memory.append(step)
    def get_all(self):
        return self.memory
