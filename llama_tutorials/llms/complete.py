from llama_index.llms.openai import OpenAI

llm = OpenAI(model="gpt-4o-mini")

# 一次请求
# print(llm.complete("请介绍一下中国的龙舟赛"))

# 流式输出
handle = llm.stream_complete("请介绍一下中国的龙舟赛")
for token in handle:
    print(token.delta, end="", flush=True)
print()
