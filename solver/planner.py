"""
Decomposes questions into sub-steps for complex queries.
"""
class Planner:
    def plan(self, question):
        # Dummy: split by 'and' for sub-questions
        return [q.strip() for q in question.split('and')]
