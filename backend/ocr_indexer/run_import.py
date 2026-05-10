import os
import pandas as pd
from ocr_indexer.importer import import_document

meta_file = "/Users/alessio/PycharmProjects/volcanos-data/data/list.tsv"
base_path = "/Users/alessio/Downloads/principe/Archive/"

# import_document(
#     title="Studio termico di fumarole vesuviane",
#     author="Giuseppe Imbò",
#     folder_path="/Users/alessio/Downloads/principe/Archive/art/BF02719518.out"
# )

df = pd.read_csv(meta_file, sep='\t', header=0)
for _, row in df.iterrows():
    full_filename = os.path.join(base_path, row['Folder'], row['File'])
    full_filename = full_filename[:-4] + ".out"
    import_document(title=row['Title'], author=row['Author'], folder_path=full_filename)
