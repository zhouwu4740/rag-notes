from langchain_community.document_loaders import UnstructuredMarkdownLoader

loader = UnstructuredMarkdownLoader("../data/黑悟空/黑悟空版本介绍.md", mode="single")
docs = loader.load()
for doc in docs:
    print(doc.metadata)
    print(doc.page_content)
    print("-" * 30)