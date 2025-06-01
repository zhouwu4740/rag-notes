from langchain_community.document_loaders import TextLoader

loader = TextLoader("../data/黑悟空/设定.txt")
docs = loader.load()
printout = [str(len(docs)), "-" * 30, str(docs[0].metadata),
            "-"*30, docs[0].page_content]
print("\n\n".join(printout))
