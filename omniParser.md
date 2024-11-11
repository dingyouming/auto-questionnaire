# AI驱动的自动问卷填写项目设计

### 1. 项目架构设计

```
auto-questionnaire/
├── src/
│   ├── parser/
│   │   ├── ui_parser.py      # UI解析模块
│   │   └── element_finder.py # 元素定位模块
│   ├── ai/
│   │   ├── groq_handler.py   # Groq API处理模块
│   │   └── prompt_builder.py # 提示词构建模块
├── data/
│   ├── context_db.json      # 上下文数据库
│   └── templates/           # 问卷模板
├── utils/
│   ├── screenshot.py        # 截图工具
│   └── auto_fill.py        # 自动填写模块
├── config/
│   └── model_config.py     # 模型配置
└── main.py                 # 主程序
```

### 2. 核心功能模块

1. **Groq处理模块**：
```python:src/ai/groq_handler.py
import groq

class GroqHandler:
    def __init__(self, api_key):
        self.client = groq.Client(api_key=api_key)
        self.model = "llama-70b-v2"  # Llama-3-70b模型
        
    def generate_response(self, question, context=None):
        """使用Llama-3-70b模型生成答案"""
        prompt = self._build_prompt(question, context)
        
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "你是一个专业的问卷填写助手。请根据问题和上下文生成真实、自然的回答。"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return completion.choices[0].message.content
        except Exception as e:
            print(f"Groq API调用错误: {e}")
            return None

    def _build_prompt(self, question, context):
        """构建提示词"""
        base_prompt = f"请针对以下问题生成一个自然的回答：\n问题：{question}\n"
        if context:
            base_prompt += f"参考上下文：{context}\n"
        base_prompt += "\n请确保回答：\n1. 符合问题类型和格式要求\n2. 保持自然真实\n3. 与上下文保持一致"
        return base_prompt
```

2. **配置模块**：
```python:src/config/model_config.py
class ModelConfig:
    GROQ_API_KEY = "your-groq-api-key"
    MODEL_PARAMS = {
        "temperature": 0.7,
        "max_tokens": 1000,
        "top_p": 0.9,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0
    }
```

3. **自动填写模块**：
```python:src/utils/auto_fill.py
class AutoFiller:
    def __init__(self, groq_handler, context_db):
        self.groq_handler = groq_handler
        self.context_db = context_db
    
    def generate_answer(self, question_type, question_text):
        """根据问题类型和内容生成答案"""
        context = self.context_db.get_relevant_context(question_text)
        
        # 根据问题类型调整提示词
        if question_type == 'radio':
            context += "\n请只选择一个选项作为答案。"
        elif question_type == 'checkbox':
            context += "\n可以选择多个适合的选项。"
        elif question_type == 'text':
            context += "\n请生成一段适当长度的文字回答。"
            
        return self.groq_handler.generate_response(question_text, context)
```

### 3. 使用示例

```python:main.py
from auto_questionnaire.parser.ui_parser import QuestionnaireParser
from auto_questionnaire.utils.auto_fill import AutoFiller
from auto_questionnaire.ai.groq_handler import GroqHandler
from auto_questionnaire.config.model_config import ModelConfig
from auto_questionnaire.utils.screenshot import take_screenshot

def main():
    # 初始化组件
    groq_handler = GroqHandler(api_key=ModelConfig.GROQ_API_KEY)
    parser = QuestionnaireParser()
    filler = AutoFiller(groq_handler, context_db='data/context_db.json')
    
    # 获取问卷截图
    screenshot_path = take_screenshot()
    
    # 解析问卷
    elements = parser.parse_page(screenshot_path)
    
    # AI辅助填写
    for element_type, elements_list in elements.items():
        for element in elements_list:
            answer = filler.generate_answer(element_type, element.text)
            if answer:
                # 执行填写操作
                print(f"问题类型: {element_type}")
                print(f"问题: {element.text}")
                print(f"生成的答案: {answer}\n")
```

### 4. 实现建议

1. **Llama模型优化**：
   - 根据问卷类型调整temperature参数
   - 优化提示词以充分利用Llama-3-70b的能力
   - 实现答案一致性检查

2. **性能优化**：
   - 实现答案缓存机制
   - 批量处理问题以提高效率
   - 优化API调用频率

3. **错误处理**：
   - 实现API调用重试机制
   - 添加备用答案生成策略
   - 记录详细的错误日志

### 5. 注意事项

1. **API使用**：
   - 注意Groq API的调用限制
   - 实现请求速率控制
   - 监控API使用成本

2. **答案质量**：
   - 定期评估生成答案的质量
   - 建立答案质量评分机制
   - 收集并分析失败案例

3. **系统扩展**：
   - 支持切换不同的模型版本
   - 预留其他LLM接口
   - 优化上下文管理

### 下一步建议

1. 建立完善的提示词模板库
2. 实现答案质量自动评估
3. 优化API调用策略
4. 建立模型效果对比分析