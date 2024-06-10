import logging
from copy import deepcopy
from itertools import islice
from typing import Iterable, Callable, Any

import chromadb
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings.huggingface_hub import HuggingFaceHubEmbeddings
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.vectorstores import utils as chromautils
from langchain_core.documents import Document, BaseDocumentTransformer
from pydantic_settings import BaseSettings

from modules.rag.pipeline.docs_processing.exceptions import PathIsNotAssigned
from modules.rag.pipeline.docs_processing.utils import get_loader
from modules.rag.settings.settings import settings as default_settings

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)


class DocsExtractPipeline:
    def __init__(self, pipeline_settings: 'PipelineSettings'):
        self._config_dict = pipeline_settings.config_structure
        self._pipeline_settings = pipeline_settings

    def load_docs(self, docs_collection_path: str | None = None):
        logger.info('Initialize parsing process')
        if docs_collection_path is None and self._config_dict.loader.doc_path == '':
            raise PathIsNotAssigned('Input file (directory) path is not assigned')
        if docs_collection_path is None:
            load_path = self._config_dict.loader.doc_path
        else:
            load_path = docs_collection_path

        parser_params = deepcopy(self._config_dict.loader.parsing_params)
        parser_params['file_path'] = load_path

        loader = get_loader(load_path, parser_params)
        return loader.lazy_load()

    def go_to_next_step(self, docs_collection_path: str | None = None) -> 'DocsTransformPipeline':
        return DocsTransformPipeline(self._pipeline_settings, self.load_docs(docs_collection_path))


class DocsTransformPipeline:
    def __init__(self, pipeline_settings: 'PipelineSettings', docs_generator: Iterable[Document]):
        self._docs_generator: Iterable[Document] = docs_generator
        self._transformers: list[BaseDocumentTransformer] = pipeline_settings.transformers

        def transformation(docs: list[Document]) -> list[Document]:
            for transformer in self._transformers:
                docs = transformer.transform_documents(docs)
            return docs

        self._transformation: Callable[[list[Document]], list[Document]] = transformation

    def update_docs_transformers(self, **kwargs: dict[str, Any]) -> 'DocsTransformPipeline':
        if self._transformers is not None:
            if kwargs:
                for transformer in self._transformers:
                    for key, value in kwargs.items():
                        if key in transformer.__dict__:
                            transformer.__dict__[key] = value
                        if f'_{key}' in transformer.__dict__:
                            transformer.__dict__[f'_{key}'] = value

            def transformation(docs: list[Document]) -> list[Document]:
                for transformer in self._transformers:
                    docs = transformer.transform_documents(docs)
                return docs

            self._transformation = transformation
        return self

    def transform(self, batch_size: int | None = None) -> Iterable[list[Document]]:
        if batch_size is None:
            batch_size = 1
        batch_size = max(batch_size, 1)
        while batch := list(islice(self._docs_generator, batch_size)):
            docs = self._transformation(batch)
            yield docs

    def go_to_next_step(self, batch_size: int | None = None) -> 'DocsLoadPipeline':
        logger.info('Initialize transformation process')
        return DocsLoadPipeline(self.transform(batch_size))


class DocsLoadPipeline:
    def __init__(self, docs_generator: Iterable[list[Document]]):
        self._docs_generator: Iterable[list[Document]] = docs_generator
        self._store_settings: BaseSettings = default_settings

    def store_settings(self, settings: BaseSettings | None = None) -> 'DocsLoadPipeline':
        self._store_settings: BaseSettings = settings
        return self

    def load(self, loading_batch_size: int | None = None,
             collection_name: str | None = None) -> None:
        logger.info('Initialize loading process')
        if loading_batch_size is None:
            loading_batch_size = 32
        if self._store_settings.embedding_host:
            embedding_function = HuggingFaceHubEmbeddings(model=self._store_settings.embedding_host)
        else:
            embedding_function = HuggingFaceEmbeddings(model_name=self._store_settings.embedding_name)

        # Creating Chroma DB Client
        chroma_client = chromadb.HttpClient(host=self._store_settings.chroma_host,
                                            port=self._store_settings.chroma_port,
                                            settings=chromadb.Settings(allow_reset=self._store_settings.allow_reset))

        if collection_name is None:
            collection_name = self._store_settings.collection_name
        else:
            collection_name = collection_name
        chroma_store = Chroma(collection_name=collection_name,
                              embedding_function=embedding_function,
                              client=chroma_client,
                              collection_metadata={"hnsw:space": self._store_settings.distance_fn})

        # Add processed documents to the defined Chroma collection
        loading_batch_size = max(loading_batch_size, 1)
        for docs_batch in self._docs_generator:
            if isinstance(docs_batch, list):
                loading_batches = [docs_batch[i:i + loading_batch_size] for i in
                                   range(0, len(docs_batch), loading_batch_size)]
            else:
                loading_batches = [chromautils.filter_complex_metadata([docs_batch])]
            for batch in loading_batches:
                chroma_store.add_documents(batch)
