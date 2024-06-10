from copy import deepcopy

import chromadb
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings

from modules.rag.stores.chroma.chroma_loader import load_documents_to_chroma_db
from modules.rag.settings.settings import settings as default_settings


def chroma_loading(pth: str, collection_name: str):
    # Загружает данные в Хрому

    default_settings.collection_name = collection_name
    default_settings.docs_collection_path = pth
    processing_batch_size = 32
    loading_batch_size = 32
    settings = deepcopy(default_settings)
    load_documents_to_chroma_db(settings=settings,
                                processing_batch_size=processing_batch_size,
                                loading_batch_size=loading_batch_size)

    chroma_client = chromadb.HttpClient(host=default_settings.chroma_host,
                                        port=default_settings.chroma_port,
                                        settings=chromadb.Settings(allow_reset=default_settings.allow_reset))

    collections = chroma_client.list_collections()

    chroma_collection = Chroma(collection_name, client=chroma_client)

    if collection_name in [c.name for c in collections]:
        print(f'{collection_name} in collections')


def chroma_view(query: str, collection_name: str, k: int = 1):
    # Выдаёт k самых похожих на запрос (query) чанков

    default_settings.collection_name = collection_name
    chroma_client = chromadb.HttpClient(host=default_settings.chroma_host,
                                        port=default_settings.chroma_port,
                                        settings=chromadb.Settings(allow_reset=default_settings.allow_reset))
    embedding_function = HuggingFaceEmbeddings(model_name=default_settings.embedding_name)
    chroma_collection = Chroma(collection_name=collection_name,
                               embedding_function=embedding_function,
                               client=chroma_client)

    collection = chroma_collection.get()
    result = chroma_collection.similarity_search_with_score(query, k)
    print(query)
    for i in range(k):
        print(f'Ответ {i}: {result[i][0].page_content}')
        print(f'Похожесть: {round(result[i][1], 2)}')


def delete_collection(collection_name: str):
    # Удаляет коллекцию

    chroma_client = chromadb.HttpClient(host=default_settings.chroma_host,
                                        port=default_settings.chroma_port,
                                        settings=chromadb.Settings(allow_reset=default_settings.allow_reset))
    chroma_client.delete_collection(collection_name)


# collection_name = 'test'
# query = 'Кто научный руководитель?'
# query = 'Какие основные приоритеты социально-экономического развития Санкт-Петербурга ' \
#         'выделены в стратегии на период до 2035 года?'

# chroma_loading('./docs/example.docx')
# chroma_view(query, 4)
# delete_collection(collection_name=collection_name)
