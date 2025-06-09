"""
Decomposes questions into sub-steps for complex queries.
"""
import re
class Planner:
    def plan(self, question):
        # Split by 'and', 'then', or '?', and clean up
        parts = re.split(r'\band\b|\bthen\b|\?', question, flags=re.IGNORECASE)
        return [q.strip() for q in parts if q.strip()]
