from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, get_response_synthesizer
from llama_index.core.retrievers import VectorIndexRetriever
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.postprocessor import SimilarityPostprocessor

documents = SimpleDirectoryReader(
    input_files="../../data/黑悟空/黑悟空wiki.txt").load_data(show_progress=True)
# 创建索引
index = VectorStoreIndex.from_documents(documents)
# 创建检索器
retriever = VectorIndexRetriever(index=index, similarity_top_k=5)

# response synthesizer
response_synthesizer = get_response_synthesizer()

qe = RetrieverQueryEngine(
    retriever=retriever,
    response_synthesizer=response_synthesizer,
    node_postprocessors=[SimilarityPostprocessor(similarity_cutoff=0.7)]
)

response = qe.query("讲述一下黑悟空的介绍")
print(response)
