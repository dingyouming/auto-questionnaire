class PromptBuilder:
    def __init__(self):
        self.system_prompt = "你是一个问卷填写助手。"
        
    def build_prompt(self, question_text):
        return f"""
        {self.system_prompt}
        
        问题：{question_text}
        
        请提供一个合适的答案。
        """ 