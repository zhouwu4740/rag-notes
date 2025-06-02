from llama_index.llms.openai import OpenAI
from llama_index.core.llms import (
    ChatMessage,
    TextBlock,
    ImageBlock,
)

llm = OpenAI(model="gpt-4o-mini")

messages = [
    ChatMessage(role="user", blocks=[
        TextBlock(text="请用中文描述图片内容，要求在100字以内"),
        ImageBlock(path="../../data/黑悟空/黑悟空英文.jpg")
    ])
]

response = llm.stream_chat(messages)
for token in response:
    print(token.delta, end="", flush=True)
print()
