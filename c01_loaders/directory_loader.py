from langchain_community.document_loaders import DirectoryLoader
""" libmagic 但它可以帮助检测文件类型。建议安装 libmagic，以获得更好的文件类型识别效果。
    安装方法：
    sudo apt-get install libmagic-dev
    pip install python-magic
"""
# loader = DirectoryLoader("../data/黑悟空", glob="**/*.txt")
loader = DirectoryLoader("../data/黑悟空")
docs = loader.load()
for doc in docs:
    print(doc.metadata)
    print(doc.page_content)
    print("-" * 30)
