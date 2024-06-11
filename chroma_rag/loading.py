from copy import deepcopy

import chromadb
from langchain_community.vectorstores.chroma import Chroma
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from langchain_community.embeddings.huggingface_hub import HuggingFaceHubEmbeddings

from chroma_rag.rag.stores.chroma.chroma_loader import load_documents_to_chroma_db
from chroma_rag.rag.settings.settings import settings as default_settings


class ChromaConnector:
    def __init__(self):
        self.chroma_client = chromadb.HttpClient(host=default_settings.chroma_host,
                                            port=default_settings.chroma_port,
                                            settings=chromadb.Settings(allow_reset=default_settings.allow_reset))
        # self.embedding_function = HuggingFaceEmbeddings(model_name=default_settings.embedding_host)
        self.embedding_function = HuggingFaceHubEmbeddings(model=default_settings.embedding_host)


    def chroma_loading(self, path: str, collection_name: str):
        # Загружает данные в Хрому

        default_settings.collection_name = collection_name
        default_settings.docs_collection_path = path
        processing_batch_size = 32
        loading_batch_size = 32
        settings = deepcopy(default_settings)
        load_documents_to_chroma_db(settings=settings,
                                    processing_batch_size=processing_batch_size,
                                    loading_batch_size=loading_batch_size)

        # chroma_client = chromadb.HttpClient(host=default_settings.chroma_host,
        #                                     port=default_settings.chroma_port,
        #                                     settings=chromadb.Settings(allow_reset=default_settings.allow_reset))
        #
        # collections = chroma_client.list_collections()
        #
        # chroma_collection = Chroma(collection_name, client=chroma_client)
        #
        # if collection_name in [c.name for c in collections]:
        #     print(f'{collection_name} in collections')


    def chroma_view(self, query: str, collection_name: str, k: int = 1):
        # Выдаёт k самых похожих на запрос (query) чанков

        default_settings.collection_name = collection_name

        chroma_collection = Chroma(collection_name=collection_name,
                                   embedding_function=self.embedding_function,
                                   client=self.chroma_client)

        # collection = chroma_client.get_collection("main_collection", embedding_function=embedder)

        return chroma_collection.similarity_search_with_score(query, k)
        # print(query)
        # for i in range(k):
        #     print(f'Ответ {i}: {result[i][0].page_content}')
        #     print(f'Похожесть: {round(result[i][1], 2)}')


    def delete_collection(self, collection_name: str):
        # Удаляет коллекцию
        self.chroma_client.delete_collection(collection_name)


if __name__ == "__main__":
    collection_name = 'my_collection2'
    query = 'Кто научный руководитель?'
    query = 'This is a query document about hawaii'
    # query = 'Какие основные приоритеты социально-экономического развития Санкт-Петербурга ' \
    #         'выделены в стратегии на период до 2035 года?'
    # chroma_view(query, collection_name)

    # chroma_loading('./docs/example.docx')
    # chroma_view(query, 4)
    # delete_collection(collection_name=collection_name)

    # Load data
    # collection_name = 'strategy'
    # path = '/Users/lizzy/Documents/WORK/projects/BIAM-Urb/chroma_rag/docs/strategy.pdf'
    # chroma_loading(path, collection_name)

    collection_name = 'strategy'
    query = 'Какие проблемы демографического развития Санкт-Петербурга?'
    chroma_inst = ChromaConnector()
    res = chroma_inst.chroma_view(query, collection_name)
    print(res[0][0].page_content)
