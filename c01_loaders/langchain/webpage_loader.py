from langchain_unstructured import UnstructuredLoader

page_url = "https://zh.wikipedia.org/wiki/黑神话：悟空"
loader = UnstructuredLoader(web_url=page_url)
docs = loader.load()
print(docs[0].metadata)
print("-"*100)
print(docs[0].page_content)
print("-"*100)
for doc in docs[:5]:
    print(doc)