from llama_index.llms.openai import OpenAI
from llama_index.core.llms import ChatMessage

llm = OpenAI(model="gpt-4o-mini")
requirements = """
- 西红柿
- 鸡蛋
"""

messages = [
    ChatMessage(role="system", content="你是一个美食大师，擅长各种中西美食的制作"),
    ChatMessage(
        role="user", content="请根据以下需求，给出一份详细的食谱：\n" + requirements)
]

response = llm.stream_chat(messages)
for token in response:
    print(token.delta, end="", flush=True)
print()
