import os
from typing import Any

from docs_processing.parsing import PDFLoader, WordDocumentLoader, ZipLoader, RecursiveDirectoryLoader
from langchain_core.document_loaders import BaseLoader

from chroma_rag.rag.pipeline.docs_processing.entities import LoaderType, LangChainDocumentLoader
from chroma_rag.rag.pipeline.docs_processing.exceptions import FileExtensionError


def get_loader(documents_collection_path: str, loader_params: dict[str, Any]) -> BaseLoader:
    doc_extension = documents_collection_path.lower().split('.')[-1]
    if os.path.isdir(documents_collection_path):
        doc_extension = LoaderType.directory
    match doc_extension:
        case LoaderType.pdf:
            return PDFLoader(**loader_params)
        case LoaderType.json:
            return LangChainDocumentLoader(**loader_params)
        case LoaderType.docx | LoaderType.doc | LoaderType.rtf | LoaderType.odt:
            return WordDocumentLoader(**loader_params)

    parsing_scheme = loader_params.pop('parsing_scheme', 'lines')
    extract_images = loader_params.pop('extract_images', False)
    extract_tables = loader_params.pop('extract_tables', False)
    parse_formulas = loader_params.pop('parse_formulas', False)
    remove_service_info = loader_params.pop('remove_service_info', False)
    loader_params = dict(
        pdf_parsing_scheme=parsing_scheme,
        pdf_extract_images=extract_images,
        pdf_extract_tables=extract_tables,
        pdf_parse_formulas=parse_formulas,
        pdf_remove_service_info=remove_service_info,
        word_doc_parsing_scheme=parsing_scheme,
        word_doc_extract_images=extract_images,
        word_doc_extract_tables=extract_tables,
        word_doc_parse_formulas=parse_formulas,
        word_doc_remove_service_info=remove_service_info,
        **loader_params,
    )
    match doc_extension:
        case LoaderType.zip:
            return ZipLoader(**loader_params)
        case LoaderType.directory:
            return RecursiveDirectoryLoader(**loader_params)
        case _:
            raise FileExtensionError(f'File with extension {doc_extension} has not been implemented yet.')
