from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

from chroma_rag.loading import ChromaConnector

# import chromadb
# from chromadb.utils.embedding_functions import HuggingFaceEmbeddingServer
# chroma_client = chromadb.HttpClient(host='10.32.1.34', port=9941)
# ef = HuggingFaceEmbeddingServer(url="http://10.32.1.34:9942/embed")


class Question(BaseModel):
    question_body: str


app = FastAPI()


# @app.get("/")
# def read_root():
#     return {"Hello": "World"}
#
#
# @app.get("/question/{item_id}")
# def read_item(item_id: int, q: Union[str, None] = None):
#     return {"item_id": item_id, "q": q}


@app.post("/question")
def read_item(question: Question):
    # collection = chroma_client.get_collection("my_collection2", embedding_function=ef)
    # results = collection.query(
    #     query_texts=[question.question_body],  # Chroma will embed this for you
    #     n_results=2  # how many results to return
    # )

    collection_name = 'strategy'
    chroma_inst = ChromaConnector()
    res = chroma_inst.chroma_view(question.question_body, collection_name)
    context = res[0][0].page_content
    # return res[0][0].page_content
    return context
