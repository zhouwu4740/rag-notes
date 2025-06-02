import bs4
from langchain_community.document_loaders import WebBaseLoader
page_url = "https://zh.wikipedia.org/wiki/黑神话：悟空"
loader = WebBaseLoader(web_paths=[page_url])
docs = loader.load()
print(docs[0].metadata)
print("-"*100)
print(docs[0].page_content)