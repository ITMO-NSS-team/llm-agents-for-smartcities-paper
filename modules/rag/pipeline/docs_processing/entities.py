from enum import Enum
from json import load
from typing import Iterator

from langchain_core.document_loaders import BaseLoader
from langchain_core.documents import Document
from langchain_core.load import load as ln_load

from docs_processing.splitting import ListHierarchySplitter, HierarchicalMerger
from langchain_text_splitters import RecursiveCharacterTextSplitter


transformer_object_dict = {
    'recursive_character': RecursiveCharacterTextSplitter,
    'list_hierarchy': ListHierarchySplitter,
    'hierarchical_merger': HierarchicalMerger
}


class LoaderType(str, Enum):
    docx = 'docx'
    doc = 'doc'
    odt = 'odt'
    rtf = 'rtf'
    pdf = 'pdf'
    directory = 'directory'
    zip = 'zip'
    json = 'json'


class LangChainDocumentLoader(BaseLoader):
    def __init__(self, file_path: str):
        self.file_path = file_path

    def lazy_load(self) -> Iterator[Document]:
        with open(self.file_path, 'r') as f:
            for i, doc_dict in load(f).items():
                yield ln_load(doc_dict)
