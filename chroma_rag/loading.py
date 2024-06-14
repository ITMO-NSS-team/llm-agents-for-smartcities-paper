from copy import deepcopy
from typing import List

import chromadb
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings.huggingface_hub import HuggingFaceHubEmbeddings

from chroma_rag.rag.stores.chroma.chroma_loader import load_documents_to_chroma_db
from chroma_rag.rag.settings.settings import settings as default_settings


def chroma_loading(path: str, collection: str) -> None:
    # Loads data to ChromaDB

    default_settings.collection_name = collection
    default_settings.docs_collection_path = path
    processing_batch_size = 32
    loading_batch_size = 32
    settings = deepcopy(default_settings)
    load_documents_to_chroma_db(settings=settings,
                                processing_batch_size=processing_batch_size,
                                loading_batch_size=loading_batch_size)


def chroma_view(query: str, collection: str, k: int = 1) -> List:
    # Returns k chunks that are closest to the query
    # TODO: check if it'll be better to use a pool of connections
    chroma_client = chromadb.HttpClient(host=default_settings.chroma_host,
                                        port=default_settings.chroma_port,
                                        settings=chromadb.Settings(allow_reset=default_settings.allow_reset))
    # embedding_function = HuggingFaceEmbeddings(model_name=default_settings.embedding_host)
    embedding_function = HuggingFaceHubEmbeddings(model=default_settings.embedding_host)

    default_settings.collection_name = collection

    chroma_collection = Chroma(collection_name=collection,
                               embedding_function=embedding_function,
                               client=chroma_client)

    return chroma_collection.similarity_search_with_score(query, k)


def delete_collection(collection: str) -> None:
    # Deletes the collection
    chroma_client = chromadb.HttpClient(host=default_settings.chroma_host,
                                        port=default_settings.chroma_port,
                                        settings=chromadb.Settings(allow_reset=default_settings.allow_reset))
    chroma_client.delete_collection(collection)  # TODO: check if collection exists first


def list_collections() -> List:
    # Returns a list of all collections
    chroma_client = chromadb.HttpClient(host=default_settings.chroma_host,
                                        port=default_settings.chroma_port,
                                        settings=chromadb.Settings(allow_reset=default_settings.allow_reset))
    return chroma_client.list_collections()


if __name__ == "__main__":
    # Load data
    # collection_name = 'strategy-spb'
    # path = '/Users/lizzy/Documents/WORK/projects/BIAM-Urb/chroma_rag/docs/strategy.docx'
    # chroma_loading(path, collection_name)

    # List collections
    print(list_collections())

    # Query data
    collection_name = 'strategy-spb'
    query = 'Какие проблемы демографического развития Санкт-Петербурга?'
    res = chroma_view(query, collection_name)
    print(res[0][0].page_content)

    # Delete collection
    # collection_name = 'test'
    # delete_collection(collection_name)
    # print(f'Removed {collection_name} collection')
