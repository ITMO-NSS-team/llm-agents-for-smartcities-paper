import logging
import os

import chroma_rag.loading as chroma_connector
from models.new_web_api import NewWebAssistant
from models.prompts.strategy_prompt import strategy_sys_prompt


logger = logging.getLogger(__name__)


def retrieve_context_from_chroma(q: str, collect_name: str, c_num: int) -> str:
    """Retrieves the given number of chunks from ChromaDB based on the user question"""
    res = chroma_connector.chroma_view(q, collect_name, c_num)
    context = ""
    context_list = []
    metadata = []
    for ind, chunk in enumerate(res):
        context = f"{context}Отрывок {ind}: {chunk[0].page_content} "
        context_list.append(chunk[0].page_content)
        metadata.append(
            (
                chunk[0].metadata["chapter"],
                os.path.basename(chunk[0].metadata["source"]),
            )
        )
    logger.info(f"Chunk metadata from ChromaDB: {metadata}")
    return context


# TODO: move function to another module
def generate_answer(q: str, s_p: str, c: str) -> str:
    """Calls LLM with correct params and returns the answer"""
    model = NewWebAssistant()
    model.set_sys_prompt(s_p)
    model.add_context(c)
    response = model(q, as_json=True)
    return response


def strategy_development_pipeline(question: str,
                                  chunk_num: int = 4,) -> str:
    """ Pipeline designed to handle strategy development data.
    Extracts the context from ChromaDB and passes it to the LLM to answer the question.

    Args:
        question: a question from the user
        chunk_num: number of chunks that will be returned by the DB

    Returns: answer to the question
    """
    collection_name = 'strategy-spb'
    logging.info(f'Strategy RAG: Chroma collection name: {collection_name}')
    logging.info(f'Strategy RAG: Question: {question}')
    logging.info(f'Strategy RAG: Chunks num: {chunk_num}')
    # Get context from ChromaDB
    context = retrieve_context_from_chroma(
        question, collection_name, chunk_num
    )
    # Get question answer from Llama
    response = generate_answer(question, strategy_sys_prompt, context)

    return response


if __name__ == "__main__":
    question = "Какие проблемы демографического развития Санкт-Петербурга?"
    print(strategy_development_pipeline(question))
