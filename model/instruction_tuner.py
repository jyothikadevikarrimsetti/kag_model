"""
Task-specific prompt construction for LLMs.
"""
class InstructionTuner:
    def build_prompt(self, question, context):
        return f"Answer the following based on context: {question}\nContext: {context}"
