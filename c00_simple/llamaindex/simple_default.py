from llama_index.core import SimpleDirectoryReader, VectorStoreIndex

# 1. 读取数据
docs = SimpleDirectoryReader(
    input_files=['../../data/黑悟空/黑悟空wiki.txt']).load_data()

# 2. 创建索引
index = VectorStoreIndex.from_documents(docs)

# 3. 创建查询引擎
query_engine = index.as_query_engine()

# 4. 查询
response = query_engine.query(
    "What's the main idea of the document? response in Chinese")

# 5. 输出结果
print(response)
