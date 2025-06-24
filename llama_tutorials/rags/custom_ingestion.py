from llama_index.core import SimpleDirectoryReader
from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import TokenTextSplitter
from llama_index.core import VectorStoreIndex

documents = SimpleDirectoryReader(
    input_files=["../../data/黑悟空/设定.txt"]).load_data()

pipeline = IngestionPipeline(
    transformations=[TokenTextSplitter(chunk_size=100, chunk_overlap=20)])

nodes = pipeline.run(documents=documents)

index = VectorStoreIndex(nodes)

qe = index.as_query_engine()

response = qe.query("悟空的设定是什么？")

print(response)
