from llama_index.core import Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.core import Document
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex

documents = SimpleDirectoryReader("./data").load_data()


document = Document(text="Hello, world!")

text_splitter = SentenceSplitter(chunk_size=100, chunk_overlap=20)


Settings.text_splitter = text_splitter

# per index
VectorStoreIndex.from_documents(documents, transformations=[text_splitter])
