from llama_index.llms.ollama import Ollama

from llama_index.llms.ollama import Ollama

# 模型
llm = Ollama(
    model="deepseek-r1:1.5b",
    request_timeout=60,
    context_window=8000
)

response = llm.stream_complete("请介绍一下中国的赛龙舟")

for chunk in response:
    print(chunk.delta, end="", flush=True)
