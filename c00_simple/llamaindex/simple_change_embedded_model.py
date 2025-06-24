from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
# pip install llama_index_embeddings_huggingface
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
import os

from openai import files


os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"

# 1. 加载嵌入模型(local)
embedding = HuggingFaceEmbedding(
    model_name="BAAI/bge-small-zh"
)

# 2. 加载文档
docs = SimpleDirectoryReader(files=["../../data/黑悟空/黑悟空wiki.txt"]).load_data()

# 3. 创建索引
index = VectorStoreIndex.from_documents(
    documents=docs,
    embedding=embedding
)

# 4. 创建查询引擎
query_engine = index.as_query_engine()

# 5. 查询
response = query_engine.query(
    "What's the main idea of the document? response in Chinese")

# 6. 输出结果
print(response)
