from llama_index.core import SimpleDirectoryReader
from llama_index.readers.file import PagedCSVReader

# 读取目录下所有文件
# reader = SimpleDirectoryReader("../../data/黑悟空")
# docs = reader.load_data()
# print(docs)

# 读取图片
# reader = SimpleDirectoryReader(input_files=["../../data/黑悟空/黑悟空英文.jpg"])
# docs = reader.load_data()
# print(docs)

# 读取markdown
# reader = SimpleDirectoryReader(input_files=["../../data/黑悟空/黑悟空版本介绍.md"])
# docs = reader.load_data()
# print(docs[0].text)

# 读取txt
# reader = SimpleDirectoryReader(input_files=["../../data/黑悟空/设定.txt"])
# docs = reader.load_data()
# print(docs[0].text)

# 读取pdf
# reader = SimpleDirectoryReader(input_files=["../../data/黑悟空/黑神话悟空.pdf"])
# docs = reader.load_data()
# print(docs[0].text)

# 读取csv
reader = PagedCSVReader()
docs = reader.load_data(
    file="../../data/黑悟空/黑神话悟空.csv",
    delimiter=",",
    quotechar='"'
)
# print(docs[0].text)
for doc in docs:
    print(doc.text)