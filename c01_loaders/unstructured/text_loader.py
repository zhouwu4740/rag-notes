from unstructured.partition.text import partition_text

elements = partition_text("../../data/黑悟空/设定.txt")
for element in elements:
    print(element.text)
    print("-"*100)